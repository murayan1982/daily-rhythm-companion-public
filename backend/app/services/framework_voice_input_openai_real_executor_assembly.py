from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    FrameworkVoiceInputFakeHandoffError,
    _FrameworkVoiceInputPublicApi,
    framework_voice_input_public_api_context,
)


PrivateCredentialBuilder = Callable[[type[Any]], Any]


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest:
    """Explicit operator-only request to assemble FW's real OpenAI executor."""

    model: str = "gpt-4o-mini-transcribe"
    max_audio_bytes: int = 1048576
    timeout_seconds: float = 120.0
    max_retries: int = 0
    operator_handoff_enabled: bool = False
    allow_provider_execution: bool = False
    credentials_available: bool = False
    allow_provider_sdk_import: bool = False
    allow_provider_client_creation: bool = False
    allow_real_provider_execution: bool = False

    def __post_init__(self) -> None:
        model = str(self.model).strip()
        if not model:
            raise ValueError("model must be non-empty")
        if self.max_audio_bytes <= 0:
            raise ValueError("max_audio_bytes must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        object.__setattr__(self, "model", model)


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIRealExecutorAssembly:
    """Public-safe snapshot plus an opaque executor for a later private handoff."""

    status: str
    request_state: str
    provider: str
    model: str
    framework_api_name: str
    adapter_name: str
    executor_name: str
    operator_handoff_only: bool
    explicit_opt_in_complete: bool
    credential_object_injected: bool
    credential_value_read_by_drc: bool
    provider_sdk_imported: bool
    provider_client_created: bool
    network_request_executed: bool
    real_provider_execution_executed: bool
    audio_read: bool
    microphone_accessed: bool
    private_path_exposed: bool
    raw_audio_exposed: bool
    provider_payload_exposed: bool
    _executor: Any = field(repr=False, compare=False)

    @property
    def private_operator_executor(self) -> Any:
        """Return the assembled executor without invoking it."""

        return self._executor


class FrameworkVoiceInputOpenAIRealExecutorAssemblyError(RuntimeError):
    """Typed public-safe failure for the DRC real-executor assembly boundary."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class FrameworkVoiceInputOpenAIRealExecutorAssembler:
    """Assemble FW v5.4.0 public real-STT objects without executing them.

    Credential resolution remains outside this class. A private operator caller
    supplies a builder that receives the released public credential type and
    returns one opaque credential object. DRC never reads the credential value.

    Assembly does not import the OpenAI SDK, invoke the real client factory,
    create a provider client, read audio, access a microphone, or execute STT.
    """

    def __init__(
        self,
        config: AppConfig,
        *,
        public_api_context_factory: Callable[[Path], Any] | None = None,
    ) -> None:
        self._config = config
        self._public_api_context_factory = (
            public_api_context_factory or framework_voice_input_public_api_context
        )

    def assemble_for_private_operator(
        self,
        request: FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest,
        *,
        private_credential_builder: PrivateCredentialBuilder,
    ) -> FrameworkVoiceInputOpenAIRealExecutorAssembly:
        self._require_explicit_operator_opt_in(request)
        if not callable(private_credential_builder):
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "private_credential_builder_required",
                "Private operator handoff requires a credential-object builder.",
                retryable=False,
            )

        framework_root = self._resolve_framework_root()

        try:
            with self._public_api_context_factory(framework_root) as public_api:
                module = self._require_real_executor_contract(public_api)
                credential_type = module.OpenAIVoiceInputPrivateCredential
                try:
                    credential = private_credential_builder(credential_type)
                except Exception as exc:
                    raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                        "private_credential_builder_failed",
                        "Private credential object could not be prepared safely.",
                        retryable=False,
                    ) from exc

                if not isinstance(credential, credential_type):
                    raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                        "private_credential_object_invalid",
                        "Private operator handoff returned an invalid credential object.",
                        retryable=False,
                    )

                execution_config = (
                    module.resolve_voice_input_provider_execution_config(
                        provider="openai",
                        allow_provider_execution=request.allow_provider_execution,
                        credentials_available=request.credentials_available,
                    )
                )
                if not bool(getattr(execution_config, "configured", False)):
                    raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                        "provider_execution_config_not_ready",
                        "FW provider execution configuration is not ready.",
                        retryable=False,
                    )

                policy = module.OpenAIVoiceInputRealProviderPolicy(
                    max_audio_bytes=request.max_audio_bytes,
                    timeout_seconds=request.timeout_seconds,
                    max_retries=request.max_retries,
                    allow_provider_sdk_import=request.allow_provider_sdk_import,
                    allow_provider_client_creation=(
                        request.allow_provider_client_creation
                    ),
                    allow_real_provider_execution=(
                        request.allow_real_provider_execution
                    ),
                    runtime_mode=module.OpenAIVoiceInputRuntimeMode.REAL,
                )
                client_factory = module.OpenAIVoiceInputRealClientFactory(
                    credential=credential,
                    policy=policy,
                )
                adapter = module.OpenAIVoiceInputProviderAdapter(
                    execution_config=execution_config,
                    model=request.model,
                    client_factory=client_factory,
                    public_metadata={
                        "host_app": "DRC",
                        "assembly_mode": "private_operator_handoff",
                        "credential_value_read_by_drc": False,
                        "operator_handoff_only": True,
                    },
                )
                executor = module.OpenAIVoiceInputRealProviderExecutor(
                    adapter=adapter,
                )

                if getattr(adapter, "client", None) is not None:
                    raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                        "unexpected_direct_provider_client",
                        "Real-executor assembly unexpectedly contains a direct client.",
                        retryable=False,
                    )
                if getattr(adapter, "client_factory", None) is not client_factory:
                    raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                        "unexpected_real_executor_assembly_contract",
                        "FW real-executor assembly returned an unexpected contract.",
                        retryable=False,
                    )

                return FrameworkVoiceInputOpenAIRealExecutorAssembly(
                    status="assembled",
                    request_state="private_operator_handoff_ready",
                    provider="openai",
                    model=request.model,
                    framework_api_name=(
                        "OpenAIVoiceInputRealProviderExecutor"
                    ),
                    adapter_name="openai",
                    executor_name="openai_real_provider",
                    operator_handoff_only=True,
                    explicit_opt_in_complete=True,
                    credential_object_injected=True,
                    credential_value_read_by_drc=False,
                    provider_sdk_imported=False,
                    provider_client_created=False,
                    network_request_executed=False,
                    real_provider_execution_executed=False,
                    audio_read=False,
                    microphone_accessed=False,
                    private_path_exposed=False,
                    raw_audio_exposed=False,
                    provider_payload_exposed=False,
                    _executor=executor,
                )
        except FrameworkVoiceInputOpenAIRealExecutorAssemblyError:
            raise
        except FrameworkVoiceInputFakeHandoffError as exc:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                exc.code,
                str(exc),
                retryable=exc.retryable,
            ) from exc
        except Exception as exc:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "framework_real_executor_assembly_failed",
                "Framework real-executor assembly failed safely.",
                retryable=True,
            ) from exc

    @staticmethod
    def _require_explicit_operator_opt_in(
        request: FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest,
    ) -> None:
        if not request.operator_handoff_enabled:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "private_operator_handoff_required",
                "Real-executor assembly requires explicit private operator handoff.",
                retryable=False,
            )

        required_flags = (
            request.allow_provider_execution,
            request.credentials_available,
            request.allow_provider_sdk_import,
            request.allow_provider_client_creation,
            request.allow_real_provider_execution,
        )
        if not all(required_flags):
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "real_executor_opt_in_incomplete",
                "Real-executor assembly requires every explicit execution gate.",
                retryable=False,
            )

    def _resolve_framework_root(self) -> Path:
        configured = self._config.framework_project_root
        if not configured:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "framework_root_not_configured",
                "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                retryable=True,
            )

        try:
            root = Path(configured).expanduser().resolve()
        except OSError as exc:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "framework_root_invalid",
                "Configured Framework root could not be resolved.",
                retryable=True,
            ) from exc

        if not root.is_dir() or not (root / "framework" / "__init__.py").is_file():
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "framework_root_invalid",
                "Configured Framework root does not expose the public framework package.",
                retryable=True,
            )
        return root

    @staticmethod
    def _require_real_executor_contract(
        public_api: _FrameworkVoiceInputPublicApi,
    ) -> Any:
        module = public_api.module
        required = (
            "resolve_voice_input_provider_execution_config",
            "OpenAIVoiceInputPrivateCredential",
            "OpenAIVoiceInputRealProviderPolicy",
            "OpenAIVoiceInputRuntimeMode",
            "OpenAIVoiceInputRealClientFactory",
            "OpenAIVoiceInputProviderAdapter",
            "OpenAIVoiceInputRealProviderExecutor",
        )
        missing = (
            required
            if module is None
            else tuple(name for name in required if not hasattr(module, name))
        )
        if missing:
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "public_openai_real_executor_contract_missing",
                "Configured Framework is missing the public real-executor contract.",
                retryable=True,
            )

        credential_type = getattr(module, "OpenAIVoiceInputPrivateCredential")
        if not isinstance(credential_type, type):
            raise FrameworkVoiceInputOpenAIRealExecutorAssemblyError(
                "public_openai_real_executor_contract_missing",
                "Configured Framework exposes an invalid private credential type.",
                retryable=True,
            )
        return module
