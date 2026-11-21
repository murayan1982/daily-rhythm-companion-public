from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import get_args

import httpx

from app.models.advice import AdviceCharacterId, AdviceMood
from app.services.advice_cost import maximum_token_cost
from app.services.character_service import CharacterService
from app.services.postgres_public_advice import PostgresAdviceInvites, PostgresDailyAdviceQuota
from app.services.public_advice import PublicAdviceRuntime


GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_SDK_VERSION = "1.70.0"
MAX_INPUT_TOKENS = 512
MAX_OUTPUT_TOKENS = 256
MAXIMUM_COST_MICRODOLLARS = maximum_token_cost(MAX_INPUT_TOKENS, MAX_OUTPUT_TOKENS, 250_000, 1_500_000)
SYSTEM_INSTRUCTION = (
    "You are a daily-rhythm companion. Give one short, practical tip in Japanese. "
    "Use the selected character's style. Avoid medical claims and do not invent personal records."
)
_CHARACTERS = {preset.character_id: preset for preset in CharacterService().list_presets()}


def advice_prompt(mood: AdviceMood, character_id: AdviceCharacterId) -> str:
    character = _CHARACTERS[character_id]
    return (
        f"Mood: {mood}. Character: {character_id} ({character.display_name}).\n"
        f"Tone: {character.personality_type}, {character.speaking_style}; "
        f"advice style: {character.advice_style}.\n"
        "Write just the advice."
    )


@contextmanager
def gemini_advice_runtime(
    dsn: str, *, per_user: int, total: int, api_key: str,
    count_input_tokens: Callable[[str, str], int],
    transport: httpx.BaseTransport | None = None,
) -> Iterator[PublicAdviceRuntime]:
    """Candidate runtime for a dedicated microdollar ledger and verified offline input counter."""
    from google import genai
    from google.genai import types

    if genai.__version__ != GEMINI_SDK_VERSION or not api_key.strip():
        raise ValueError("Gemini advice requires the verified SDK version and explicit credentials.")
    prompts = {
        (mood, character): advice_prompt(mood, character)
        for mood in get_args(AdviceMood)
        for character in get_args(AdviceCharacterId)
    }
    for prompt in prompts.values():
        size = count_input_tokens(SYSTEM_INSTRUCTION, prompt)
        if type(size) is not int or not 0 < size <= MAX_INPUT_TOKENS:
            raise ValueError("Gemini advice input token count is outside the reviewed limit.")

    config = types.GenerateContentConfig(
        system_instruction=types.Content(parts=[types.Part(text=SYSTEM_INSTRUCTION)]),
        candidate_count=1,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL", include_thoughts=False),
        service_tier="standard",
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    with httpx.Client(transport=transport, follow_redirects=False, trust_env=False) as http:
        options = types.HttpOptions(
            base_url="https://generativelanguage.googleapis.com",
            api_version="v1beta",
            timeout=10_000,
            retry_options=types.HttpRetryOptions(attempts=1),
            httpx_client=http,
        )
        with genai.Client(vertexai=False, api_key=api_key, http_options=options) as client:
            def generate(*, mood: AdviceMood, character_id: AdviceCharacterId) -> str:
                reply = client.models.generate_content(
                    model=GEMINI_MODEL, contents=prompts[mood, character_id], config=config
                )
                usage = reply.usage_metadata
                if (
                    usage is None
                    or usage.prompt_token_count is None
                    or usage.candidates_token_count is None
                    or not 0 < usage.prompt_token_count <= MAX_INPUT_TOKENS
                    or not 0 < usage.candidates_token_count + (usage.thoughts_token_count or 0)
                    <= MAX_OUTPUT_TOKENS
                    or usage.tool_use_prompt_token_count
                    or len(reply.candidates or []) != 1
                    or reply.candidates[0].finish_reason != types.FinishReason.STOP
                ):
                    raise ValueError("Gemini advice did not satisfy the reviewed response limits.")
                return reply.text or ""

            yield PublicAdviceRuntime(
                authenticate=PostgresAdviceInvites(dsn).authenticate,
                quota=PostgresDailyAdviceQuota(
                    dsn, per_user=per_user, total=total, maximum_cost=MAXIMUM_COST_MICRODOLLARS
                ),
                generate=generate,
            )
