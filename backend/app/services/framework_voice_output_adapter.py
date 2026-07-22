from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterator


@dataclass(frozen=True)
class FrameworkVoiceOutputRequest:
    """Neutral DRC-to-framework voice output request.

    This request intentionally contains only app-level fields. Provider voice
    IDs, API keys, endpoint parameters, and raw provider payloads remain AI
    Character Framework responsibilities.
    """

    text: str
    voice_profile_id: str | None
    requested_audio_format: str | None
    character_id: str | None
    utterance_purpose: str


@dataclass(frozen=True)
class FrameworkVoiceOutputResult:
    """Safe normalized result from a guarded framework voice output call.

    The generated/playable contract mirrors the FW v5 public boundary:
    generated + audio_ready + exactly one audio handoff is a Web playback
    candidate. Everything else remains non-playable and non-evidence.
    """

    status: str
    message: str
    audio_url: str | None = None
    audio_artifact_ref: str | None = None
    audio_format: str | None = None
    audio_ready: bool = False
    audio_handoff_kind: str = "none"
    has_audio_handoff: bool = False
    is_generated: bool = False
    framework_api_name: str | None = None
    runtime_notes: tuple[str, ...] = ()


class FrameworkVoiceOutputAdapter:
    """Call an AI Character Framework public voice output boundary when opted in.

    The adapter imports only public framework modules and sends a neutral
    request. It does not contain provider-specific TTS code and it does not log
    private synthesis text, provider payloads, API keys, or generated audio.
    """

    _PUBLIC_MODULE_CANDIDATES: tuple[str, ...] = (
        "framework",
        "framework.facade",
        "framework.app_sdk",
        "framework.public",
        "framework.api",
    )

    _DIRECT_CALLABLE_CANDIDATES: tuple[str, ...] = (
        "synthesize_text",
        "speak_text",
        "text_to_speech",
    )

    _SESSION_FACTORY_CANDIDATES: tuple[str, ...] = (
        "create_voice_output_session",
        "create_tts_session",
    )

    _SESSION_METHOD_CANDIDATES: tuple[str, ...] = (
        "create_output",
        "synthesize",
        "synthesize_text",
        "speak_text",
        "generate_audio",
    )

    def __init__(
        self,
        framework_root: Path,
        *,
        real_tts_enabled: bool,
        artifact_dir: Path | None = None,
    ) -> None:
        self._framework_root = framework_root
        self._real_tts_enabled = real_tts_enabled
        self._artifact_dir = artifact_dir

    def synthesize(self, request: FrameworkVoiceOutputRequest) -> FrameworkVoiceOutputResult:
        """Try the public FW voice output API and normalize the result safely."""

        if not self._framework_root.exists():
            return FrameworkVoiceOutputResult(
                status="framework_root_missing",
                message="Configured framework root does not exist.",
            )

        with self._framework_import_context():
            modules = self._import_public_modules()
            if not modules:
                return FrameworkVoiceOutputResult(
                    status="public_framework_import_failed",
                    message="No public framework module could be imported.",
                )

            direct_result = self._try_direct_public_callables(modules, request)
            if direct_result is not None:
                return direct_result

            session_result = self._try_session_public_callables(modules, request)
            if session_result is not None:
                return session_result

        return FrameworkVoiceOutputResult(
            status="public_voice_output_callable_missing",
            message=(
                "Public framework modules imported, but no supported voice "
                "output/TTS callable was available."
            ),
        )

    @contextmanager
    def _framework_import_context(self) -> Iterator[None]:
        """Temporarily import FW from the configured root without cache bleed."""

        original_sys_path = list(sys.path)
        saved_framework_modules = {
            name: module
            for name, module in sys.modules.items()
            if name == "framework" or name.startswith("framework.")
        }

        for name in saved_framework_modules:
            sys.modules.pop(name, None)

        sys.path.insert(0, str(self._framework_root))
        importlib.invalidate_caches()

        try:
            yield
        finally:
            for name in list(sys.modules):
                if name == "framework" or name.startswith("framework."):
                    sys.modules.pop(name, None)
            sys.modules.update(saved_framework_modules)
            sys.path[:] = original_sys_path
            importlib.invalidate_caches()

    def _import_public_modules(self) -> tuple[ModuleType, ...]:
        modules: list[ModuleType] = []
        for module_name in self._PUBLIC_MODULE_CANDIDATES:
            try:
                modules.append(importlib.import_module(module_name))
            except Exception:
                # Keep the public response safe: do not expose import errors that
                # may contain private local paths or provider details.
                continue
        return tuple(modules)

    def _try_direct_public_callables(
        self,
        modules: tuple[ModuleType, ...],
        request: FrameworkVoiceOutputRequest,
    ) -> FrameworkVoiceOutputResult | None:
        for module in modules:
            for callable_name in self._DIRECT_CALLABLE_CANDIDATES:
                callable_obj = getattr(module, callable_name, None)
                if not callable(callable_obj):
                    continue

                result = self._safe_call(
                    callable_obj,
                    request,
                    module,
                    framework_api_name=f"{module.__name__}.{callable_name}",
                )
                if result.status != "framework_voice_output_call_failed":
                    return result

        return None

    def _try_session_public_callables(
        self,
        modules: tuple[ModuleType, ...],
        request: FrameworkVoiceOutputRequest,
    ) -> FrameworkVoiceOutputResult | None:
        for module in modules:
            for factory_name in self._SESSION_FACTORY_CANDIDATES:
                factory = getattr(module, factory_name, None)
                if not callable(factory):
                    continue

                try:
                    session = self._call_factory(factory, request)
                except Exception:
                    continue

                for method_name in self._SESSION_METHOD_CANDIDATES:
                    method = getattr(session, method_name, None)
                    if not callable(method):
                        continue

                    result = self._safe_call(
                        method,
                        request,
                        module,
                        framework_api_name=(
                            f"{module.__name__}.{factory_name}().{method_name}"
                        ),
                    )
                    if result.status != "framework_voice_output_call_failed":
                        return result

        return None

    def _call_factory(
        self,
        factory: Callable[..., Any],
        request: FrameworkVoiceOutputRequest,
    ) -> Any:
        kwargs = self._accepted_kwargs(
            factory,
            {
                "project_root": self._framework_root,
                "default_voice_profile_id": request.voice_profile_id or "default",
                "real_tts_enabled": self._real_tts_enabled,
                "artifact_dir": self._artifact_dir,
                # Legacy public factory compatibility remains fallback-only.
                "voice_profile_id": request.voice_profile_id,
                "character_id": request.character_id,
                "utterance_purpose": request.utterance_purpose,
            },
        )
        return factory(**kwargs)

    def _safe_call(
        self,
        callable_obj: Callable[..., Any],
        request: FrameworkVoiceOutputRequest,
        module: ModuleType,
        *,
        framework_api_name: str,
    ) -> FrameworkVoiceOutputResult:
        try:
            call_result = self._call_with_neutral_contract(callable_obj, request, module)
        except Exception:
            return FrameworkVoiceOutputResult(
                status="framework_voice_output_call_failed",
                message="Framework voice output call failed. See private operator logs only.",
                framework_api_name=framework_api_name,
            )

        return self._normalize_result(call_result, request, framework_api_name)

    def _call_with_neutral_contract(
        self,
        callable_obj: Callable[..., Any],
        request: FrameworkVoiceOutputRequest,
        module: ModuleType,
    ) -> Any:
        fw_request = self._build_framework_public_request(module, request)
        if fw_request is not None:
            request_call = self._call_with_request_object(callable_obj, fw_request)
            if request_call is not _CALL_NOT_SUPPORTED:
                return request_call

        candidate_kwargs = {
            "text": request.text,
            "message": request.text,
            "input_text": request.text,
            "voice_profile_id": request.voice_profile_id,
            "requested_audio_format": request.requested_audio_format,
            "audio_format": request.requested_audio_format,
            "character_id": request.character_id,
            "utterance_purpose": request.utterance_purpose,
            "language_code": "ja",
        }
        kwargs = self._accepted_kwargs(callable_obj, candidate_kwargs)

        if not self._callable_accepts_text_keyword(callable_obj, kwargs):
            return callable_obj(request.text, **kwargs)

        return callable_obj(**kwargs)

    def _build_framework_public_request(
        self,
        module: ModuleType,
        request: FrameworkVoiceOutputRequest,
    ) -> Any | None:
        request_class = getattr(module, "VoiceOutputRequest", None)
        if request_class is None:
            try:
                framework_module = importlib.import_module("framework")
            except Exception:
                framework_module = None
            request_class = getattr(framework_module, "VoiceOutputRequest", None)

        if request_class is None or not callable(request_class):
            return None

        candidate_kwargs = {
            "text": request.text,
            "voice_profile_id": request.voice_profile_id,
            "requested_audio_format": request.requested_audio_format,
            "utterance_purpose": request.utterance_purpose,
            "language_code": "ja",
        }
        kwargs = self._accepted_kwargs(request_class, candidate_kwargs)

        try:
            return request_class(**kwargs)
        except Exception:
            return None

    def _call_with_request_object(self, callable_obj: Callable[..., Any], request: Any) -> Any:
        try:
            signature = inspect.signature(callable_obj)
        except (TypeError, ValueError):
            try:
                return callable_obj(request)
            except TypeError:
                return _CALL_NOT_SUPPORTED

        parameters = signature.parameters
        if "request" in parameters:
            return callable_obj(request=request)

        positional_candidates = [
            param
            for param in parameters.values()
            if param.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            and param.default is inspect.Parameter.empty
        ]
        if len(positional_candidates) == 1:
            return callable_obj(request)

        if any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in parameters.values()):
            return callable_obj(request)

        return _CALL_NOT_SUPPORTED

    def _accepted_kwargs(
        self,
        callable_obj: Callable[..., Any],
        candidate_kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        filtered = {key: value for key, value in candidate_kwargs.items() if value is not None}

        try:
            signature = inspect.signature(callable_obj)
        except (TypeError, ValueError):
            return filtered

        parameters = signature.parameters
        if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()):
            return filtered

        return {key: value for key, value in filtered.items() if key in parameters}

    def _callable_accepts_text_keyword(
        self,
        callable_obj: Callable[..., Any],
        kwargs: dict[str, Any],
    ) -> bool:
        if any(key in kwargs for key in ("text", "message", "input_text")):
            return True

        try:
            signature = inspect.signature(callable_obj)
        except (TypeError, ValueError):
            return True

        return any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in signature.parameters.values()
        )

    def _normalize_result(
        self,
        raw_result: Any,
        request: FrameworkVoiceOutputRequest,
        framework_api_name: str,
    ) -> FrameworkVoiceOutputResult:
        audio_url = self._extract_optional_string(
            raw_result,
            "audio_url",
            "audio_uri",
            "url",
            "public_audio_url",
        )
        audio_artifact_ref = self._extract_optional_string(
            raw_result,
            "audio_artifact_ref",
            "artifact_ref",
            "audio_ref",
            "audio_file_ref",
        )
        audio_format = self._extract_optional_string(
            raw_result,
            "audio_format",
            "format",
            "requested_audio_format",
            "mime_type",
        ) or request.requested_audio_format
        raw_state = self._extract_optional_string(
            raw_result,
            "request_state",
            "state",
            "status",
        )
        request_state = self._normalize_framework_state(raw_state)
        audio_ready = self._extract_optional_bool(raw_result, "audio_ready") or False
        handoff_count = int(audio_url is not None) + int(audio_artifact_ref is not None)
        has_audio_handoff = handoff_count == 1
        audio_handoff_kind = self._resolve_audio_handoff_kind(audio_url, audio_artifact_ref)
        is_generated = request_state == "generated"

        if isinstance(raw_result, (bytes, bytearray)):
            return FrameworkVoiceOutputResult(
                status="audio_generated_unserved",
                message=(
                    "Framework voice output returned audio bytes, but DRC does not "
                    "expose raw audio bytes through this safe Web contract."
                ),
                audio_format=audio_format,
                framework_api_name=framework_api_name,
                runtime_notes=(
                    "Add a safe backend audio-serving contract before counting Web playback.",
                ),
            )

        if is_generated and audio_ready and has_audio_handoff:
            return FrameworkVoiceOutputResult(
                status="generated",
                message=(
                    "Framework voice output returned a generated audio handoff. Web playback "
                    "still requires operator confirmation and private screenshot evidence."
                ),
                audio_url=audio_url,
                audio_artifact_ref=audio_artifact_ref,
                audio_format=audio_format,
                audio_ready=True,
                audio_handoff_kind=audio_handoff_kind,
                has_audio_handoff=True,
                is_generated=True,
                framework_api_name=framework_api_name,
                runtime_notes=(
                    "Do not commit raw audio URLs, audio artifact refs, or generated audio artifacts.",
                    "This backend response alone is not v2.0.0 acceptance evidence.",
                ),
            )

        if is_generated and audio_ready and handoff_count != 1:
            return FrameworkVoiceOutputResult(
                status="generated_handoff_invalid",
                message=(
                    "Framework voice output reported generated audio, but the Web handoff "
                    "was not exactly one of audio_url or audio_artifact_ref."
                ),
                audio_url=audio_url,
                audio_artifact_ref=audio_artifact_ref,
                audio_format=audio_format,
                audio_ready=audio_ready,
                audio_handoff_kind=audio_handoff_kind,
                has_audio_handoff=False,
                is_generated=True,
                framework_api_name=framework_api_name,
                runtime_notes=(
                    "Generated output without an unambiguous Web handoff must not count as evidence.",
                ),
            )

        if request_state in {"unavailable", "skipped", "rejected", "failed"}:
            return FrameworkVoiceOutputResult(
                status=request_state,
                message=(
                    "Framework voice output returned a non-playable state. "
                    "This must not count as real TTS Web audio evidence."
                ),
                audio_format=audio_format,
                audio_ready=audio_ready,
                audio_handoff_kind=audio_handoff_kind,
                has_audio_handoff=has_audio_handoff,
                is_generated=False,
                framework_api_name=framework_api_name,
            )

        if audio_url and raw_state is None:
            return FrameworkVoiceOutputResult(
                status="legacy_audio_ready",
                message=(
                    "Framework voice output returned an audio URL without the FW v5 "
                    "generated/audio_ready state. Treating it as a legacy playback candidate only."
                ),
                audio_url=audio_url,
                audio_format=audio_format,
                audio_ready=True,
                audio_handoff_kind="url",
                has_audio_handoff=True,
                is_generated=False,
                framework_api_name=framework_api_name,
                runtime_notes=(
                    "Legacy audio URL responses are not FW v5 generated evidence by themselves.",
                ),
            )

        if request_state == "generated":
            return FrameworkVoiceOutputResult(
                status="audio_generated_unserved",
                message=(
                    "Framework voice output reported generated audio, but it was not ready "
                    "with a safe Web audio handoff."
                ),
                audio_url=audio_url,
                audio_artifact_ref=audio_artifact_ref,
                audio_format=audio_format,
                audio_ready=audio_ready,
                audio_handoff_kind=audio_handoff_kind,
                has_audio_handoff=has_audio_handoff,
                is_generated=True,
                framework_api_name=framework_api_name,
                runtime_notes=(
                    "Generated-without-Web-playback must not count as real TTS evidence.",
                ),
            )

        return FrameworkVoiceOutputResult(
            status="framework_result_without_audio",
            message=(
                "Framework voice output callable returned without a FW v5 generated "
                "audio handoff."
            ),
            audio_format=audio_format,
            audio_handoff_kind=audio_handoff_kind,
            has_audio_handoff=has_audio_handoff,
            framework_api_name=framework_api_name,
        )

    def _normalize_framework_state(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower().replace("-", "_")
        if normalized in {"ok", "success", "audio_ready"}:
            return "generated"
        return normalized

    def _resolve_audio_handoff_kind(
        self,
        audio_url: str | None,
        audio_artifact_ref: str | None,
    ) -> str:
        if audio_url and audio_artifact_ref:
            return "conflicting"
        if audio_url:
            return "url"
        if audio_artifact_ref:
            return "artifact_ref"
        return "none"

    def _extract_optional_string(self, raw_result: Any, *names: str) -> str | None:
        if raw_result is None:
            return None

        for name in names:
            value: Any
            if isinstance(raw_result, dict):
                value = raw_result.get(name)
            else:
                value = getattr(raw_result, name, None)

            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        if isinstance(raw_result, str):
            text = raw_result.strip()
            if text.startswith(("http://", "https://", "/")):
                return text

        return None

    def _extract_optional_bool(self, raw_result: Any, *names: str) -> bool | None:
        if raw_result is None:
            return None

        for name in names:
            if isinstance(raw_result, dict):
                value = raw_result.get(name)
            else:
                value = getattr(raw_result, name, None)

            if value is None:
                continue
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"1", "true", "yes", "y", "on"}:
                    return True
                if normalized in {"0", "false", "no", "n", "off"}:
                    return False

        return None


class _CallNotSupported:
    pass


_CALL_NOT_SUPPORTED = _CallNotSupported()
