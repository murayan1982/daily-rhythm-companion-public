from __future__ import annotations

import httpx


MINA_VOICE_OUTPUT_MODE = "elevenlabs_mina"
MINA_CHARACTER_ID = "gentle_mina"
MINA_FIXED_ADVICE = "ひと息ついてから、できることを一つ選びましょう。"
_MAX_MP3_BYTES = 2 * 1024 * 1024


class DebugVoiceSynthesisError(RuntimeError):
    """Safe failure at the direct development TTS boundary."""


def synthesize_debug_mp3(*, message: str, api_key: str, voice_id: str) -> bytes:
    """Synthesize a message already validated by the development voice service."""
    try:
        from elevenlabs.client import ElevenLabs

        with httpx.Client(timeout=10.0, follow_redirects=False) as http_client:
            client = ElevenLabs(api_key=api_key, httpx_client=http_client, timeout=10.0)
            audio = bytearray()
            for chunk in client.text_to_speech.convert(
                voice_id=voice_id,
                text=message,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                request_options={"max_retries": 0},
            ):
                if len(audio) + len(chunk) > _MAX_MP3_BYTES:
                    raise DebugVoiceSynthesisError("Audio exceeded the size limit.")
                audio.extend(chunk)
            if not audio:
                raise DebugVoiceSynthesisError("Audio was empty.")
            return bytes(audio)
    except DebugVoiceSynthesisError:
        raise
    except Exception:
        # Provider exceptions can contain request details or a raw response body.
        raise DebugVoiceSynthesisError("Voice synthesis failed.") from None
