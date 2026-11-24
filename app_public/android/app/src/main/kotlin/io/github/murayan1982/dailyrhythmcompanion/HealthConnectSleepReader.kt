package io.github.murayan1982.dailyrhythmcompanion

import android.app.Activity
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.health.connect.HealthConnectException
import android.health.connect.HealthConnectManager
import android.health.connect.ReadRecordsRequestUsingFilters
import android.health.connect.ReadRecordsResponse
import android.health.connect.TimeInstantRangeFilter
import android.health.connect.datatypes.SleepSessionRecord
import android.health.connect.datatypes.SleepSessionRecord.StageType
import android.os.Bundle
import android.os.OutcomeReceiver
import android.widget.ScrollView
import android.widget.TextView
import io.flutter.plugin.common.MethodChannel
import java.time.Duration
import java.time.Instant
import java.time.ZoneId

@android.annotation.TargetApi(34)
internal class HealthConnectSleepReader(private val activity: Activity) {
    private var pending: MethodChannel.Result? = null
    private var includeActualSleep = false

    fun read(result: MethodChannel.Result, includeActualSleep: Boolean = false) {
        if (pending != null) {
            result.error("busy", null, null)
            return
        }
        pending = result
        this.includeActualSleep = includeActualSleep
        try {
            when {
                activity.getSystemService(HealthConnectManager::class.java) == null ->
                    complete("unavailable")
                hasPermission() -> readLastNight()
                else -> activity.requestPermissions(arrayOf(READ_SLEEP), SLEEP_REQUEST)
            }
        } catch (_: SecurityException) {
            complete("denied")
        } catch (_: RuntimeException) {
            complete("error")
        }
    }

    fun onRequestPermissionsResult(requestCode: Int) {
        if (requestCode != SLEEP_REQUEST || pending == null) return
        try {
            if (hasPermission()) readLastNight() else complete("denied")
        } catch (_: SecurityException) {
            complete("denied")
        } catch (_: RuntimeException) {
            complete("error")
        }
    }

    fun close() = complete("error")

    private fun hasPermission() =
        activity.checkSelfPermission(READ_SLEEP) == PackageManager.PERMISSION_GRANTED

    private fun readLastNight() {
        val zone = ZoneId.systemDefault()
        val end = Instant.now()
        val today = end.atZone(zone).toLocalDate()
        val start = today.minusDays(1).atTime(18, 0).atZone(zone).toInstant()
        val latestStart = today.atTime(6, 0).atZone(zone).toInstant()
        val earliestEnd = today.atStartOfDay(zone).toInstant()
        val manager = activity.getSystemService(HealthConnectManager::class.java)
        if (manager == null) {
            complete("unavailable")
            return
        }
        val range = TimeInstantRangeFilter.Builder().setStartTime(start).setEndTime(end).build()
        val order = compareBy<SleepSessionRecord> { Duration.between(it.startTime, it.endTime) }
            .thenBy { it.endTime }

        fun readPage(pageToken: Long, previous: SleepSessionRecord?) {
            if (pending == null) return
            try {
                val request = ReadRecordsRequestUsingFilters.Builder(SleepSessionRecord::class.java)
                    .setTimeRangeFilter(range)
                    .setPageToken(pageToken)
                    .build()
                manager.readRecords(request, activity.mainExecutor,
                    object : OutcomeReceiver<ReadRecordsResponse<SleepSessionRecord>, HealthConnectException> {
                        override fun onResult(response: ReadRecordsResponse<SleepSessionRecord>) {
                            if (pending == null) return
                            if (!hasPermission()) {
                                complete("denied")
                                return
                            }
                            val best = response.records.asSequence()
                                .filter {
                                    it.startTime >= start && it.startTime < latestStart &&
                                        it.endTime > earliestEnd && it.endTime <= end
                                }
                                .plus(listOfNotNull(previous))
                                .maxWithOrNull(order)
                            if (response.nextPageToken != -1L) {
                                readPage(response.nextPageToken, best)
                            } else if (best == null) {
                                complete("empty")
                            } else {
                                complete("ok", buildMap {
                                    put("start", best.startTime.toEpochMilli())
                                    put("end", best.endTime.toEpochMilli())
                                    put("minutes", Duration.between(best.startTime, best.endTime).toMinutes())
                                    if (includeActualSleep) {
                                        actualSleepMinutes(best)?.let { put("actualSleepMinutes", it) }
                                    }
                                })
                            }
                        }

                        override fun onError(error: HealthConnectException) {
                            complete(if (hasPermission()) "error" else "denied")
                        }
                    },
                )
            } catch (_: SecurityException) {
                complete("denied")
            } catch (_: RuntimeException) {
                complete("error")
            }
        }

        readPage(-1L, null)
    }

    private fun complete(status: String, data: Map<String, Any> = emptyMap()) {
        val result = pending
        pending = null
        result?.success(data + ("status" to status))
    }

    private fun actualSleepMinutes(session: SleepSessionRecord): Long? =
        session.stages.fold(Duration.ZERO) { total, stage ->
            when (stage.type) {
                StageType.STAGE_TYPE_SLEEPING,
                StageType.STAGE_TYPE_SLEEPING_LIGHT,
                StageType.STAGE_TYPE_SLEEPING_DEEP,
                StageType.STAGE_TYPE_SLEEPING_REM,
                -> total.plus(Duration.between(stage.startTime, stage.endTime))
                else -> total
            }
        }.toMinutes().takeIf { it in 1L..1440L }

    private companion object {
        const val READ_SLEEP = "android.permission.health.READ_SLEEP"
        const val SLEEP_REQUEST = 71
    }
}

class SleepPermissionUsageActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (24 * resources.displayMetrics.density).toInt()
        val description = TextView(this).apply {
            setPadding(padding, padding, padding, padding)
            val sleepUse = if ((applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
                "開始・終了時刻と睡眠ステージの明細は保存・送信しません。" +
                    "開発版で「睡眠時間をアドバイスに使う」をオンにして生成した場合のみ、集計した分数を生成先に送信します。"
            } else {
                "記録は保存・送信しません。"
            }
            text = "昨夜の睡眠記録を端末内に表示するため、睡眠の読み取り許可を使います。" +
                sleepUse + "許可は Android の設定で取り消せます。"
        }
        setContentView(ScrollView(this).apply { addView(description) })
    }
}
