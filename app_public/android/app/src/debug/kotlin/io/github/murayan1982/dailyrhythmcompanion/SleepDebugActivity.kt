package io.github.murayan1982.dailyrhythmcompanion

import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.IOException

class SleepDebugActivity : MainActivity() {
    private var minaAudio: DebugMinaAudio? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        minaAudio = DebugMinaAudio(flutterEngine.dartExecutor.binaryMessenger, cacheDir)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "drc/debug_character_images")
            .setMethodCallHandler { call, result ->
                if (call.method == "load") {
                    result.success(loadCharacterPortraits())
                } else {
                    result.notImplemented()
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

    override fun onDestroy() {
        minaAudio?.close()
        minaAudio = null
        super.onDestroy()
    }
}
