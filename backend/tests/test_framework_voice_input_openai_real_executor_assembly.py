from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
)
from app.services.framework_voice_input_openai_real_executor_assembly import (
    FrameworkVoiceInputOpenAIRealExecutorAssembler,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyError,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest,
)


def _framework_root(tmp_path: Path) -> Path:
    root = tmp_path / "fw"
    package = root / "framework"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        "# synthetic public package\n",
        encoding="utf-8",
    )
    return root


def _config(root: Path) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=str(root),
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
        voice_input_staging_max_bytes=1024,
    )


class _State:
    def __init__(self) -> None:
        self.context_entries = 0
        self.builder_calls = 0
        self.client_factory_calls = 0
        self.executor_calls = 0
        self.policy = None
        self.execution_config = None
        self.adapter = None
        self.executor = None


def _context_factory(
    state: _State,
    *,
    contract_missing: bool = False,
):
    @contextmanager
    def context(_root: Path):
        state.context_entries += 1

        class Credential:
            pass

        class RuntimeMode:
            REAL = "real"

        class Policy:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)
                state.policy = self

        class ClientFactory:
            def __init__(self, *, credential, policy) -> None:
                self.credential = credential
                self.policy = policy

            def __call__(self):
                state.client_factory_calls += 1
                raise AssertionError("client factory must not be invoked in RT-3d2c")

        class Adapter:
            def __init__(
                self,
                *,
                execution_config,
                model,
                client_factory,
                public_metadata,
            ) -> None:
                self.execution_config = execution_config
                self.model = model
                self.client = None
                self.client_factory = client_factory
                self.public_metadata = public_metadata
                state.adapter = self

        class Executor:
            def __init__(self, *, adapter) -> None:
                self.adapter = adapter
                state.executor = self

            def execute(self, **_kwargs):
                state.executor_calls += 1
                raise AssertionError("executor must not run in RT-3d2c")

        def resolve_config(**kwargs):
            state.execution_config = SimpleNamespace(
                configured=(
                    kwargs["provider"] == "openai"
                    and kwargs["allow_provider_execution"] is True
                    and kwargs["credentials_available"] is True
                ),
                **kwargs,
            )
            return state.execution_config

        module = (
            SimpleNamespace()
            if contract_missing
            else SimpleNamespace(
                resolve_voice_input_provider_execution_config=resolve_config,
                OpenAIVoiceInputPrivateCredential=Credential,
                OpenAIVoiceInputRealProviderPolicy=Policy,
                OpenAIVoiceInputRuntimeMode=RuntimeMode,
                OpenAIVoiceInputRealClientFactory=ClientFactory,
                OpenAIVoiceInputProviderAdapter=Adapter,
                OpenAIVoiceInputRealProviderExecutor=Executor,
            )
        )
        yield _FrameworkVoiceInputPublicApi(
            VoiceInputAudioFormat=object,
            VoiceInputAudioSource=object,
            VoiceInputRequest=object,
            FakeVoiceInputProviderAdapter=object,
            create_voice_input_session=lambda **_kwargs: None,
            module=module,
        )

    return context


def _fully_opted_in_request() -> FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest:
    return FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest(
        model="gpt-4o-mini-transcribe",
        max_audio_bytes=1024,
        timeout_seconds=30.0,
        max_retries=0,
        operator_handoff_enabled=True,
        allow_provider_execution=True,
        credentials_available=True,
        allow_provider_sdk_import=True,
        allow_provider_client_creation=True,
        allow_real_provider_execution=True,
    )


def test_assembles_public_real_executor_without_executing_runtime(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    state = _State()
    assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
        _config(root),
        public_api_context_factory=_context_factory(state),
    )

    def build_credential(credential_type):
        state.builder_calls += 1
        return credential_type()

    result = assembler.assemble_for_private_operator(
        _fully_opted_in_request(),
        private_credential_builder=build_credential,
    )

    assert result.status == "assembled"
    assert result.request_state == "private_operator_handoff_ready"
    assert result.provider == "openai"
    assert result.framework_api_name == "OpenAIVoiceInputRealProviderExecutor"
    assert result.adapter_name == "openai"
    assert result.executor_name == "openai_real_provider"
    assert result.operator_handoff_only is True
    assert result.explicit_opt_in_complete is True
    assert result.credential_object_injected is True
    assert result.credential_value_read_by_drc is False
    assert result.provider_sdk_imported is False
    assert result.provider_client_created is False
    assert result.network_request_executed is False
    assert result.real_provider_execution_executed is False
    assert result.audio_read is False
    assert result.microphone_accessed is False
    assert result.private_path_exposed is False
    assert result.raw_audio_exposed is False
    assert result.provider_payload_exposed is False

    assert state.context_entries == 1
    assert state.builder_calls == 1
    assert state.client_factory_calls == 0
    assert state.executor_calls == 0
    assert state.execution_config.configured is True
    assert state.policy.runtime_mode == "real"
    assert state.adapter.client is None
    assert state.adapter.client_factory is not None
    assert result.private_operator_executor is state.executor

    assert "credential" not in repr(result.private_operator_executor).lower()
    assert "staging_id" not in result.__dict__
    assert "path" not in result.__dict__
    assert "transcript" not in result.__dict__
    assert str(tmp_path) not in repr(result)


def test_operator_handoff_guard_runs_before_framework_import(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    state = _State()
    assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
        _config(root),
        public_api_context_factory=_context_factory(state),
    )
    request = _fully_opted_in_request()
    request = FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest(
        model=request.model,
        max_audio_bytes=request.max_audio_bytes,
        timeout_seconds=request.timeout_seconds,
        max_retries=request.max_retries,
        operator_handoff_enabled=False,
        allow_provider_execution=True,
        credentials_available=True,
        allow_provider_sdk_import=True,
        allow_provider_client_creation=True,
        allow_real_provider_execution=True,
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealExecutorAssemblyError
    ) as error:
        assembler.assemble_for_private_operator(
            request,
            private_credential_builder=lambda _credential_type: (
                pytest.fail("credential builder must not run")
            ),
        )

    assert error.value.code == "private_operator_handoff_required"
    assert state.context_entries == 0
    assert state.builder_calls == 0


def test_incomplete_opt_in_guard_runs_before_credential_builder(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    state = _State()
    assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
        _config(root),
        public_api_context_factory=_context_factory(state),
    )
    request = FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest(
        operator_handoff_enabled=True,
        allow_provider_execution=True,
        credentials_available=True,
        allow_provider_sdk_import=True,
        allow_provider_client_creation=True,
        allow_real_provider_execution=False,
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealExecutorAssemblyError
    ) as error:
        assembler.assemble_for_private_operator(
            request,
            private_credential_builder=lambda _credential_type: (
                pytest.fail("credential builder must not run")
            ),
        )

    assert error.value.code == "real_executor_opt_in_incomplete"
    assert state.context_entries == 0


def test_missing_public_contract_does_not_prepare_credential(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    state = _State()
    assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
        _config(root),
        public_api_context_factory=_context_factory(
            state,
            contract_missing=True,
        ),
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealExecutorAssemblyError
    ) as error:
        assembler.assemble_for_private_operator(
            _fully_opted_in_request(),
            private_credential_builder=lambda _credential_type: (
                pytest.fail("credential builder must not run")
            ),
        )

    assert error.value.code == "public_openai_real_executor_contract_missing"
    assert error.value.retryable is True
    assert state.context_entries == 1
    assert state.client_factory_calls == 0
    assert state.executor_calls == 0


def test_invalid_private_credential_object_fails_before_factory_assembly(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    state = _State()
    assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
        _config(root),
        public_api_context_factory=_context_factory(state),
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealExecutorAssemblyError
    ) as error:
        assembler.assemble_for_private_operator(
            _fully_opted_in_request(),
            private_credential_builder=lambda _credential_type: object(),
        )

    assert error.value.code == "private_credential_object_invalid"
    assert state.context_entries == 1
    assert state.client_factory_calls == 0
    assert state.executor_calls == 0
