from dataclasses import dataclass
from typing import Protocol, get_args

from app.models.advice import AdviceCharacterId, AdviceMood
from app.services.public_advice import AdviceGenerator


_TOKENS_PER_PRICE_UNIT = 1_000_000
_FIXED_PROMPT = "Give one short Japanese daily-rhythm tip in the selected character's voice."


@dataclass(frozen=True)
class SyntheticAdviceModel:
    name: str
    max_input_tokens: int
    max_output_tokens: int
    input_price_per_million: int
    output_price_per_million: int

    def __post_init__(self) -> None:
        values = (
            self.max_input_tokens,
            self.max_output_tokens,
            self.input_price_per_million,
            self.output_price_per_million,
        )
        if not self.name.strip() or any(type(value) is not int or value <= 0 for value in values):
            raise ValueError("A named model with positive integer prices and limits is required.")
        largest_input = max(
            _synthetic_token_count(_prompt(mood, character_id))
            for mood in get_args(AdviceMood)
            for character_id in get_args(AdviceCharacterId)
        )
        if largest_input > self.max_input_tokens:
            raise ValueError("The full synthetic prompt exceeds the input limit.")

    @property
    def maximum_cost(self) -> int:
        numerator = (
            self.max_input_tokens * self.input_price_per_million
            + self.max_output_tokens * self.output_price_per_million
        )
        return (numerator + _TOKENS_PER_PRICE_UNIT - 1) // _TOKENS_PER_PRICE_UNIT


class SyntheticAdviceProvider(Protocol):
    def __call__(
        self, *, model: str, prompt: str, max_input_tokens: int, max_output_tokens: int
    ) -> str:
        ...


def generate_synthetic_advice(
    model: SyntheticAdviceModel, provider: SyntheticAdviceProvider
) -> AdviceGenerator:
    def generate(*, mood: AdviceMood, character_id: AdviceCharacterId) -> str:
        reply = provider(
            model=model.name,
            prompt=_prompt(mood, character_id),
            max_input_tokens=model.max_input_tokens,
            max_output_tokens=model.max_output_tokens,
        )
        if not isinstance(reply, str) or _synthetic_token_count(reply) > model.max_output_tokens:
            raise ValueError("The synthetic response exceeds the model contract.")
        return reply

    return generate


def _prompt(mood: AdviceMood, character_id: AdviceCharacterId) -> str:
    return f"{_FIXED_PROMPT}\nMood: {mood}\nCharacter: {character_id}"


def _synthetic_token_count(text: str) -> int:
    # The local provider treats each UTF-8 byte as one token.
    return len(text.encode("utf-8"))


LOCAL_TEST_MODEL = SyntheticAdviceModel(
    name="local-synthetic-v1",
    max_input_tokens=128,
    max_output_tokens=96,
    input_price_per_million=1_200_000,
    output_price_per_million=2_500_000,
)
