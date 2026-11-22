from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager, ExitStack
from hashlib import sha256
import logging
import os
from pathlib import Path

from fastapi import FastAPI

from app.services.gemini_public_advice import gemini_advice_runtime
from app.services.postgres_public_advice import PostgresAdviceGenerationControl
from app.services.public_advice import PublicAdviceRuntime


_logger = logging.getLogger(__name__)
_TOKENIZER_HASH = "91d9cf86906f78e197021fda88214d448e5c120665d0243a8e776e046986c6bc"
_TEMPLATE_HASH = "0a2c8073c878ab1da004bee933a998606537bbb62016310352c7285c3f01c5b5"


def _verified_text(path: Path, expected_hash: str) -> str:
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected_hash:
        raise ValueError("Unexpected local tokenizer artifact.")
    return data.decode("utf-8")


def load_gemini_input_counter(directory: Path) -> Callable[[str, str], int]:
    from jinja2.sandbox import SandboxedEnvironment
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_str(_verified_text(directory / "tokenizer.json", _TOKENIZER_HASH))
    template = SandboxedEnvironment().from_string(
        _verified_text(directory / "chat_template.jinja", _TEMPLATE_HASH)
    )

    def count(system: str, prompt: str) -> int:
        formatted = template.render(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            add_generation_prompt=True,
            bos_token="<bos>",
        )
        return len(tokenizer.encode(formatted, add_special_tokens=False).ids)

    return count


def _configured_runtime(stack: ExitStack) -> PublicAdviceRuntime:
    dsn = os.getenv("DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN", "").strip()
    api_key = os.getenv("DRC_PUBLIC_ADVICE_GEMINI_API_KEY", "").strip()
    tokenizer_dir = os.getenv("DRC_GEMINI_TOKENIZER_DIR", "").strip()
    per_user = int(os.getenv("DRC_PUBLIC_ADVICE_GEMINI_DAILY_PER_USER", ""))
    total = int(os.getenv("DRC_PUBLIC_ADVICE_GEMINI_DAILY_TOTAL", ""))
    if not (dsn and api_key and tokenizer_dir and per_user > 0 and total > 0):
        raise ValueError("Incomplete Gemini invite configuration.")
    if not PostgresAdviceGenerationControl(dsn).has_monthly_budget():
        raise ValueError("The invite ledger has no monthly budget.")

    return stack.enter_context(gemini_advice_runtime(
        dsn,
        per_user=per_user,
        total=total,
        api_key=api_key,
        count_input_tokens=load_gemini_input_counter(Path(tokenizer_dir)),
    ))


@asynccontextmanager
async def public_advice_lifespan(app: FastAPI) -> AsyncIterator[None]:
    with ExitStack() as stack:
        if os.getenv("DRC_PUBLIC_ADVICE_GEMINI_ENABLED") == "1":
            try:
                runtime = _configured_runtime(stack)
            except Exception:
                # SDK and database exceptions can contain secrets or configuration values.
                _logger.warning("Gemini invite advice could not be initialized.")
            else:
                app.state.public_advice_runtime = runtime
                stack.callback(delattr, app.state, "public_advice_runtime")
        yield
