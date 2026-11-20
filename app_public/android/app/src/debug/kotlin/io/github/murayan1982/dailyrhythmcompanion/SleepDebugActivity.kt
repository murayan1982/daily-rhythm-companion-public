package io.github.murayan1982.dailyrhythmcompanion

import android.app.Activity
import android.content.pm.PackageManager
import android.health.connect.HealthConnectException
import android.health.connect.HealthConnectManager
import android.health.connect.ReadRecordsRequestUsingFilters
import android.health.connect.ReadRecordsResponse
import android.health.connect.TimeInstantRangeFilter
import android.health.connect.datatypes.SleepSessionRecord
import android.os.Build
import android.os.Bundle
import android.os.OutcomeReceiver
import android.widget.TextView
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.IOException
import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

class SleepDebugActivity : FlutterActivity() {
    private var pending: MethodChannel.Result? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "drc/debug_character_images")
            .setMethodCallHandler { call, result ->
                if (call.method == "load") {
                    result.success(loadCharacterPortraits())
                } else {
                    result.notImplemented()
                }
            }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "drc/sleep_debug")
            .setMethodCallHandler { call, result ->
                when {
                    call.method != "read" -> result.notImplemented()
                    pending != null -> result.error("busy", null, null)
                    Build.VERSION.SDK_INT < 34 -> result.success(mapOf("status" to "unavailable"))
                    else -> {
                        pending = result
                        try {
                            when {
                                getSystemService(HealthConnectManager::class.java) == null ->
                                    complete("unavailable")
                                checkSelfPermission(READ_SLEEP) == PackageManager.PERMISSION_GRANTED ->
                                    readLastNight()
                                else -> requestPermissions(arrayOf(READ_SLEEP), SLEEP_REQUEST)
                            }
                        } catch (_: RuntimeException) {
                            complete("error")
                        }
                    }
                }
            }
    }

    private fun loadCharacterPortraits(): Map<String, ByteArray> =
        listOf("gentle_mina", "cheerful_sora", "cool_rei").mapNotNull { id ->
            try {
                id to assets.open("character_portraits/${id}_demo.png").use { it.readBytes() }
            } catch (_: IOException) {
                null
            }
        }.toMap()

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray,
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode != SLEEP_REQUEST || pending == null) return
        if (Build.VERSION.SDK_INT >= 34 &&
            checkSelfPermission(READ_SLEEP) == PackageManager.PERMISSION_GRANTED
        ) {
            readLastNight()
        } else {
            complete("denied")
        }
    }

    @android.annotation.TargetApi(34)
    private fun readLastNight() {
        val zone = ZoneId.systemDefault()
        val today = LocalDate.now(zone)
        val start = today.minusDays(1).atTime(18, 0).atZone(zone).toInstant()
        val latestStart = today.atTime(6, 0).atZone(zone).toInstant()
        val earliestEnd = today.atStartOfDay(zone).toInstant()
        val end = Instant.now()
        val manager = getSystemService(HealthConnectManager::class.java)
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
                manager.readRecords(request, mainExecutor,
                    object : OutcomeReceiver<ReadRecordsResponse<SleepSessionRecord>, HealthConnectException> {
                        override fun onResult(response: ReadRecordsResponse<SleepSessionRecord>) {
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
                                complete("ok", mapOf(
                                    "start" to best.startTime.toEpochMilli(),
                                    "end" to best.endTime.toEpochMilli(),
                                    "minutes" to Duration.between(best.startTime, best.endTime).toMinutes(),
                                ))
                            }
                        }

                        override fun onError(error: HealthConnectException) {
                            complete(if (checkSelfPermission(READ_SLEEP) != PackageManager.PERMISSION_GRANTED)
                                "denied" else "error")
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

    override fun onDestroy() {
        complete("error")
        super.onDestroy()
    }

    private companion object {
        const val READ_SLEEP = "android.permission.health.READ_SLEEP"
        const val SLEEP_REQUEST = 71
    }
}

class SleepPermissionUsageActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (24 * resources.displayMetrics.density).toInt()
        setContentView(TextView(this).apply {
            setPadding(padding, padding, padding, padding)
            text = "昨夜の睡眠記録を端末内に表示するため、睡眠の読み取り許可を使います。" +
                "記録は保存・送信しません。許可は Android の設定で取り消せます。"
        })
    }
}
