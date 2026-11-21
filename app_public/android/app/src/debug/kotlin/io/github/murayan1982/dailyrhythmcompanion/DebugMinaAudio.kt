package io.github.murayan1982.dailyrhythmcompanion

import android.media.MediaPlayer
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.IOException

internal class DebugMinaAudio(messenger: BinaryMessenger, private val cacheDir: File) {
    private val channel = MethodChannel(messenger, "drc/debug_mina_audio")
    private var player: MediaPlayer? = null
    private var pending: MethodChannel.Result? = null

    init {
        channel.setMethodCallHandler { call, result ->
            when (call.method) {
                "play" -> {
                    val audio = call.arguments as? ByteArray
                    if (audio == null || audio.isEmpty() || audio.size > 2 * 1024 * 1024) {
                        result.error("invalid_audio", null, null)
                    } else {
                        play(audio, result)
                    }
                }
                "stop" -> {
                    finish()
                    result.success(null)
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun play(audio: ByteArray, result: MethodChannel.Result) {
        finish()
        pending = result
        try {
            val media = MediaPlayer()
            player = media
            val file = File.createTempFile("mina-", ".mp3", cacheDir)
            try {
                file.writeBytes(audio)
                file.inputStream().use { media.setDataSource(it.fd) }
            } finally {
                file.delete()
            }
            media.setOnPreparedListener {
                if (player === it) {
                    try {
                        it.start()
                    } catch (_: RuntimeException) {
                        finish(failed = true)
                    }
                }
            }
            media.setOnCompletionListener {
                if (player === it) finish()
            }
            media.setOnErrorListener { failedPlayer, _, _ ->
                if (player === failedPlayer) finish(failed = true)
                true
            }
            media.prepareAsync()
        } catch (_: IOException) {
            finish(failed = true)
        } catch (_: RuntimeException) {
            finish(failed = true)
        }
    }

    private fun finish(failed: Boolean = false) {
        val current = player
        val result = pending
        player = null
        pending = null
        current?.release()
        if (failed) result?.error("playback_failed", null, null)
        else result?.success(null)
    }

    fun close() {
        channel.setMethodCallHandler(null)
        finish()
    }
}
