package io.github.murayan1982.dailyrhythmcompanion

import android.os.Build
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

open class MainActivity : FlutterActivity() {
    private var sleepReader: HealthConnectSleepReader? = null
    private var sleepChannel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        val channel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger, "drc/health_connect_sleep",
        )
        sleepChannel = channel
        channel.setMethodCallHandler { call, result ->
            when {
                call.method != "read" -> result.notImplemented()
                Build.VERSION.SDK_INT < 34 -> result.success(mapOf("status" to "unavailable"))
                else -> {
                    val reader = sleepReader ?: HealthConnectSleepReader(this).also { sleepReader = it }
                    reader.read(result)
                }
            }
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray,
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (Build.VERSION.SDK_INT >= 34) sleepReader?.onRequestPermissionsResult(requestCode)
    }

    override fun cleanUpFlutterEngine(flutterEngine: FlutterEngine) {
        sleepChannel?.setMethodCallHandler(null)
        sleepChannel = null
        if (Build.VERSION.SDK_INT >= 34) sleepReader?.close()
        sleepReader = null
        super.cleanUpFlutterEngine(flutterEngine)
    }
}
