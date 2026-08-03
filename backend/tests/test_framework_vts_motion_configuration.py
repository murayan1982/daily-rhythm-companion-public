"""RT-7d private configuration remains bounded and fail closed."""

from app.config import load_config


def test_vts_configuration_defaults_are_closed(monkeypatch) -> None:
    for key in (
        "DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION",
        "DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION",
        "DRC_RT7_VTS_RUNTIME_AVAILABLE",
        "DRC_RT7_VTS_MODEL_SELECTED",
        "DRC_RT7_VTS_ENDPOINT_HOST",
        "DRC_RT7_VTS_ENDPOINT_PORT",
        "DRC_RT7_VTS_AUTHENTICATION_TOKEN",
        "DRC_RT7_VTS_HOTKEY_BINDINGS_JSON",
    ):
        monkeypatch.delenv(key, raising=False)
    config = load_config()
    assert config.framework_vts_motion_enabled is False
    assert config.framework_vts_motion_allow_provider_execution is False
    assert config.framework_vts_motion_runtime_available is False
    assert config.framework_vts_motion_model_selected is False
    assert config.framework_vts_motion_endpoint_host == ""
    assert config.framework_vts_motion_endpoint_port is None
    assert config.framework_vts_motion_authentication_token == ""
    assert config.framework_vts_motion_hotkey_bindings == {}
    assert config.framework_vts_motion_configuration_error is None


def test_vts_configuration_loads_explicit_private_values(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION", "true")
    monkeypatch.setenv("DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION", "1")
    monkeypatch.setenv("DRC_RT7_VTS_RUNTIME_AVAILABLE", "yes")
    monkeypatch.setenv("DRC_RT7_VTS_MODEL_SELECTED", "on")
    monkeypatch.setenv("DRC_RT7_VTS_ENDPOINT_HOST", " 127.0.0.1 ")
    monkeypatch.setenv("DRC_RT7_VTS_ENDPOINT_PORT", "8001")
    monkeypatch.setenv("DRC_RT7_VTS_AUTHENTICATION_TOKEN", " private-token ")
    monkeypatch.setenv(
        "DRC_RT7_VTS_HOTKEY_BINDINGS_JSON",
        '{"expression:smile":"private-hotkey"}',
    )
    config = load_config()
    assert config.framework_vts_motion_enabled is True
    assert config.framework_vts_motion_allow_provider_execution is True
    assert config.framework_vts_motion_runtime_available is True
    assert config.framework_vts_motion_model_selected is True
    assert config.framework_vts_motion_endpoint_host == "127.0.0.1"
    assert config.framework_vts_motion_endpoint_port == 8001
    assert config.framework_vts_motion_hotkey_bindings == {
        "expression:smile": "private-hotkey"
    }
    assert config.framework_vts_motion_configuration_error is None
    rendered = repr(config)
    assert "private-token" not in rendered
    assert "private-hotkey" not in rendered


def test_unknown_boolean_values_remain_false(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION", "false")
    monkeypatch.setenv("DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION", "unknown")
    config = load_config()
    assert config.framework_vts_motion_enabled is False
    assert config.framework_vts_motion_allow_provider_execution is False


def test_invalid_port_is_public_safe_configuration_error(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_VTS_ENDPOINT_PORT", "not-a-port")
    config = load_config()
    assert config.framework_vts_motion_configuration_error == "invalid_endpoint_port"
    assert config.framework_vts_motion_endpoint_host == ""
    assert config.framework_vts_motion_hotkey_bindings == {}


def test_invalid_hotkey_json_is_public_safe_configuration_error(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_VTS_HOTKEY_BINDINGS_JSON", "{private")
    config = load_config()
    assert config.framework_vts_motion_configuration_error == "invalid_hotkey_bindings"


def test_non_object_hotkey_json_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_VTS_HOTKEY_BINDINGS_JSON", '["private"]')
    assert load_config().framework_vts_motion_configuration_error == "invalid_hotkey_bindings"


def test_non_string_hotkey_pair_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("DRC_RT7_VTS_HOTKEY_BINDINGS_JSON", '{"expression:smile":1}')
    assert load_config().framework_vts_motion_configuration_error == "invalid_hotkey_bindings"
