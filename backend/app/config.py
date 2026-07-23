from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


GOOGLE_HEALTH_SLEEP_READONLY_SCOPE = (
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly"
)
GOOGLE_HEALTH_DEFAULT_OAUTH_SCOPES = (GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,)
GOOGLE_HEALTH_API_BASE_URL = "https://health.googleapis.com/v4"
GOOGLE_HEALTH_SLEEP_API_PATH = "/users/me/dataTypes/sleep/dataPoints"


@dataclass(frozen=True)
class AppConfig:
    """
    Backend application configuration.

    This config intentionally stays small for now. Environment-backed settings
    can be expanded as wearable provider, LLM, and framework integration are
    added.
    """

    conversation_engine: str = "mock"
    framework_project_root: str | None = None
    framework_preset: str = "text_chat"
    framework_character: str = "default"
    framework_adapter_mode: str = "local_import"
    framework_text_chat_smoke_enabled: bool = False
    framework_text_chat_preflight_enabled: bool = False
    framework_text_chat_session_preflight_enabled: bool = False
    framework_text_chat_live_message_enabled: bool = False
    post_advice_chat_ttl_seconds: int = 1800
    post_advice_chat_max_sessions: int = 100
    voice_input_demo_enabled: bool = False
    voice_input_adapter_mode: str = "disabled"
    voice_output_demo_enabled: bool = False
    voice_output_adapter_mode: str = "disabled"
    voice_output_real_tts_enabled: bool = False
    voice_output_utterance_purpose: str = "demo"
    voice_output_artifact_ttl_seconds: int = 86400
    voice_output_artifact_max_count: int = 100
    motion_demo_enabled: bool = False
    motion_adapter_mode: str = "disabled"
    gemini_api_key: str | None = None
    xai_api_key: str | None = None
    sleep_provider: str = "mock"

    # Legacy Fitbit Web API settings.
    # This route is kept as a temporary migration reference and is not the
    # planned public integration path.
    fitbit_client_id: str | None = None
    fitbit_client_secret: str | None = None
    fitbit_redirect_uri: str | None = None
    fitbit_dev_save_dummy_token: bool = False
    fitbit_oauth_state_ttl_seconds: int = 600
    fitbit_enable_real_token_exchange: bool = False

    # Google Health / new wearable OAuth readiness settings.
    google_health_credentials_file: str | None = None
    google_health_expected_client_id: str | None = None
    google_health_redirect_uri: str | None = None
    google_health_oauth_scopes: tuple[str, ...] = GOOGLE_HEALTH_DEFAULT_OAUTH_SCOPES
    google_health_required_sleep_scope: str | None = GOOGLE_HEALTH_SLEEP_READONLY_SCOPE
    google_health_enable_real_token_exchange: bool = False
    google_health_enable_real_token_refresh: bool = False
    google_health_enable_real_api_requests: bool = False
    google_health_real_endpoint_verified: bool = False
    google_health_real_api_opt_in: bool = False
    google_health_api_base_url: str = GOOGLE_HEALTH_API_BASE_URL
    google_health_sleep_api_path: str = GOOGLE_HEALTH_SLEEP_API_PATH
    google_health_exercise_api_path: str = "/users/me/dataTypes/exercise/dataPoints"
    google_health_sleep_filter_query_param: str = "filter"
    google_health_api_timeout_seconds: float = 10.0

    # Local v0.23 manual confirmations for 403 permission_denied retests.
    # These are operator-confirmed checklist flags only; they do not enable
    # real API requests by themselves.
    google_health_cloud_api_enabled_confirmed: bool = False
    google_health_oauth_consent_sleep_scope_confirmed: bool = False
    google_health_oauth_test_user_confirmed: bool = False
    google_health_endpoint_query_confirmed: bool = False
    google_health_data_access_scope_confirmed: bool = False
    google_health_oauth_publishing_status_testing_confirmed: bool = False
    google_health_oauth_user_type_external_confirmed: bool = False
    google_health_test_user_email_confirmed: bool = False
    # Legacy v0.23 Day5 draft flag. Kept for backward-compatible diagnostics,
    # but no longer blocks readiness because the official setup page points to
    # Data Access / Audience checks rather than a separate allowlist flag.
    google_health_access_approval_confirmed: bool = False


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value or None


def _env_flag(name: str, default: str = "0") -> bool:
    """Return True when an environment flag is explicitly enabled."""

    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _env_csv_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Load a comma/space separated environment value as a tuple."""

    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    normalized = value.replace(",", " ")
    parts = tuple(part.strip() for part in normalized.split() if part.strip())
    return parts


def _env_positive_int(name: str, default: int) -> int:
    """Load a positive integer environment value with a bounded safe fallback."""

    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    try:
        parsed = int(value.strip())
    except ValueError:
        return default

    return parsed if parsed > 0 else default


def _env_float(name: str, default: float) -> float:
    """Load a float environment value, falling back to a safe default."""

    value = os.getenv(name)
    if value is None or not value.strip():
        return default

    try:
        return float(value.strip())
    except ValueError:
        return default


def _load_backend_dotenv() -> None:
    """
    Load backend/.env when it exists.

    The release package includes .env.example. Users can copy it to .env
    and configure local development without setting environment variables
    globally.
    """

    if _env_flag("DRC_SKIP_BACKEND_DOTENV"):
        return

    backend_root = Path(__file__).resolve().parents[1]
    dotenv_path = backend_root / ".env"

    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)


def load_config() -> AppConfig:
    """Load backend configuration from environment variables."""
    _load_backend_dotenv()

    return AppConfig(
        conversation_engine=os.getenv("CONVERSATION_ENGINE", "mock").lower(),
        framework_project_root=_empty_to_none(
            os.getenv("FRAMEWORK_PROJECT_ROOT") or os.getenv("FRAMEWORK_ROOT")
        ),
        framework_preset=os.getenv("FRAMEWORK_PRESET", "text_chat").strip()
        or "text_chat",
        framework_character=os.getenv("FRAMEWORK_CHARACTER", "default").strip()
        or "default",
        framework_adapter_mode=os.getenv(
            "FRAMEWORK_ADAPTER_MODE",
            "local_import",
        ).lower(),
        framework_text_chat_smoke_enabled=_env_flag(
            "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE"
        ),
        framework_text_chat_preflight_enabled=_env_flag(
            "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT"
        ),
        framework_text_chat_session_preflight_enabled=_env_flag(
            "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT"
        ),
        framework_text_chat_live_message_enabled=_env_flag(
            "DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE"
        ),
        post_advice_chat_ttl_seconds=_env_positive_int(
            "POST_ADVICE_CHAT_TTL_SECONDS",
            1800,
        ),
        post_advice_chat_max_sessions=_env_positive_int(
            "POST_ADVICE_CHAT_MAX_SESSIONS",
            100,
        ),
        voice_input_demo_enabled=_env_flag("VOICE_INPUT_DEMO_ENABLED"),
        voice_input_adapter_mode=os.getenv(
            "VOICE_INPUT_ADAPTER_MODE",
            "disabled",
        ).strip().lower() or "disabled",
        voice_output_demo_enabled=_env_flag("VOICE_OUTPUT_DEMO_ENABLED"),
        voice_output_adapter_mode=os.getenv(
            "VOICE_OUTPUT_ADAPTER_MODE",
            "disabled",
        ).strip().lower() or "disabled",
        voice_output_real_tts_enabled=_env_flag("VOICE_OUTPUT_REAL_TTS_ENABLED"),
        voice_output_utterance_purpose=os.getenv(
            "VOICE_OUTPUT_UTTERANCE_PURPOSE",
            "demo",
        ).strip() or "demo",
        voice_output_artifact_ttl_seconds=_env_positive_int(
            "VOICE_OUTPUT_ARTIFACT_TTL_SECONDS",
            86400,
        ),
        voice_output_artifact_max_count=_env_positive_int(
            "VOICE_OUTPUT_ARTIFACT_MAX_COUNT",
            100,
        ),
        motion_demo_enabled=_env_flag("MOTION_DEMO_ENABLED"),
        motion_adapter_mode=os.getenv(
            "MOTION_DEMO_ADAPTER_MODE",
            os.getenv("MOTION_ADAPTER_MODE", "disabled"),
        ).strip().lower() or "disabled",
        gemini_api_key=_empty_to_none(os.getenv("GEMINI_API_KEY")),
        xai_api_key=_empty_to_none(os.getenv("XAI_API_KEY")),
        sleep_provider=os.getenv("SLEEP_PROVIDER", "mock").lower(),
        fitbit_client_id=_empty_to_none(os.getenv("FITBIT_CLIENT_ID")),
        fitbit_client_secret=_empty_to_none(os.getenv("FITBIT_CLIENT_SECRET")),
        fitbit_redirect_uri=_empty_to_none(os.getenv("FITBIT_REDIRECT_URI")),
        fitbit_dev_save_dummy_token=_env_flag("FITBIT_DEV_SAVE_DUMMY_TOKEN"),
        fitbit_oauth_state_ttl_seconds=int(
            os.getenv("FITBIT_OAUTH_STATE_TTL_SECONDS", "600")
        ),
        fitbit_enable_real_token_exchange=_env_flag(
            "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE"
        ),
        google_health_credentials_file=_empty_to_none(
            os.getenv("GOOGLE_HEALTH_CREDENTIALS_FILE")
        ),
        google_health_expected_client_id=_empty_to_none(
            os.getenv("GOOGLE_HEALTH_EXPECTED_CLIENT_ID")
        ),
        google_health_redirect_uri=_empty_to_none(
            os.getenv("GOOGLE_HEALTH_REDIRECT_URI")
        ),
        google_health_oauth_scopes=_env_csv_tuple(
            "GOOGLE_HEALTH_OAUTH_SCOPES",
            GOOGLE_HEALTH_DEFAULT_OAUTH_SCOPES,
        ),
        google_health_required_sleep_scope=(
            _empty_to_none(os.getenv("GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE"))
            or GOOGLE_HEALTH_SLEEP_READONLY_SCOPE
        ),
        google_health_enable_real_token_exchange=_env_flag(
            "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE"
        ),
        google_health_enable_real_token_refresh=_env_flag(
            "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH"
        ),
        google_health_enable_real_api_requests=_env_flag(
            "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS"
        ),
        google_health_real_endpoint_verified=_env_flag(
            "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED"
        ),
        google_health_real_api_opt_in=_env_flag(
            "GOOGLE_HEALTH_REAL_API_OPT_IN"
        ),
        google_health_api_base_url=os.getenv(
            "GOOGLE_HEALTH_API_BASE_URL",
            GOOGLE_HEALTH_API_BASE_URL,
        ).rstrip("/"),
        google_health_sleep_api_path=os.getenv(
            "GOOGLE_HEALTH_SLEEP_API_PATH",
            GOOGLE_HEALTH_SLEEP_API_PATH,
        ).strip() or GOOGLE_HEALTH_SLEEP_API_PATH,
        google_health_exercise_api_path=os.getenv(
            "GOOGLE_HEALTH_EXERCISE_API_PATH",
            "/users/me/dataTypes/exercise/dataPoints",
        ).strip() or "/users/me/dataTypes/exercise/dataPoints",
        google_health_sleep_filter_query_param=os.getenv(
            "GOOGLE_HEALTH_SLEEP_FILTER_QUERY_PARAM",
            "filter",
        ).strip() or "filter",
        google_health_api_timeout_seconds=_env_float(
            "GOOGLE_HEALTH_API_TIMEOUT_SECONDS",
            10.0,
        ),
        google_health_cloud_api_enabled_confirmed=_env_flag(
            "GOOGLE_HEALTH_CLOUD_API_ENABLED_CONFIRMED"
        ),
        google_health_oauth_consent_sleep_scope_confirmed=_env_flag(
            "GOOGLE_HEALTH_OAUTH_CONSENT_SLEEP_SCOPE_CONFIRMED"
        ),
        google_health_oauth_test_user_confirmed=_env_flag(
            "GOOGLE_HEALTH_OAUTH_TEST_USER_CONFIRMED"
        ),
        google_health_endpoint_query_confirmed=_env_flag(
            "GOOGLE_HEALTH_ENDPOINT_QUERY_CONFIRMED"
        ),
        google_health_data_access_scope_confirmed=_env_flag(
            "GOOGLE_HEALTH_DATA_ACCESS_SCOPE_CONFIRMED"
        ),
        google_health_oauth_publishing_status_testing_confirmed=_env_flag(
            "GOOGLE_HEALTH_OAUTH_PUBLISHING_STATUS_TESTING_CONFIRMED"
        ),
        google_health_oauth_user_type_external_confirmed=_env_flag(
            "GOOGLE_HEALTH_OAUTH_USER_TYPE_EXTERNAL_CONFIRMED"
        ),
        google_health_test_user_email_confirmed=_env_flag(
            "GOOGLE_HEALTH_TEST_USER_EMAIL_CONFIRMED"
        ),
        google_health_access_approval_confirmed=_env_flag(
            "GOOGLE_HEALTH_ACCESS_APPROVAL_CONFIRMED"
        ),
    )