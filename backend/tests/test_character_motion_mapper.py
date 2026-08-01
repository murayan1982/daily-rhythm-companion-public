from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.character_motion import (
    CHARACTER_MOTION_MAX_COMMANDS,
    CharacterMotionCommand,
    CharacterMotionCommandIntent,
    CharacterMotionCue,
    CharacterMotionLifecycleFact,
    CharacterMotionMappingInput,
    CharacterMotionMappingOutcome,
    CharacterMotionPlan,
)
from app.models.realtime import RealtimeState
from app.services.character_motion_mapper import CharacterMotionMapper


@pytest.fixture
def mapper() -> CharacterMotionMapper:
    return CharacterMotionMapper()


def _command_shape(plan: CharacterMotionPlan) -> list[tuple[str, str | None, str | None, bool | None]]:
    return [
        (
            command.intent.value,
            command.expression_id,
            command.motion_event.value if command.motion_event else None,
            command.speaking,
        )
        for command in plan.commands
    ]


@pytest.mark.parametrize(
    ("fact", "cue", "reason", "commands"),
    [
        (
            CharacterMotionLifecycleFact.IDLE,
            CharacterMotionCue.IDLE,
            "idle_restoration",
            [
                ("speaking_state", None, None, False),
                ("reset_expression", None, None, None),
                ("idle_motion", None, "idle", None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.LISTENING,
            CharacterMotionCue.IDLE,
            "listening_supportive",
            [
                ("speaking_state", None, None, False),
                ("expression", "supportive", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.TRANSCRIBING,
            CharacterMotionCue.THINKING,
            "thinking_presentation",
            [
                ("speaking_state", None, None, False),
                ("expression", "thinking", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.THINKING,
            CharacterMotionCue.THINKING,
            "thinking_presentation",
            [
                ("speaking_state", None, None, False),
                ("expression", "thinking", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.RESPONDING,
            CharacterMotionCue.THINKING,
            "thinking_presentation",
            [
                ("speaking_state", None, None, False),
                ("expression", "thinking", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.TTS_PREPARING,
            CharacterMotionCue.THINKING,
            "thinking_presentation",
            [
                ("speaking_state", None, None, False),
                ("expression", "thinking", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.SPEAKING,
            CharacterMotionCue.SPEAKING,
            "speaking_presentation",
            [
                ("expression", "speaking", None, None),
                ("speaking_state", None, None, True),
            ],
        ),
        (
            CharacterMotionLifecycleFact.INTERRUPTED,
            CharacterMotionCue.IDLE,
            "terminal_stop_and_reset",
            [
                ("stop_motion", None, None, None),
                ("speaking_state", None, None, False),
                ("reset_expression", None, None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.COMPLETED,
            CharacterMotionCue.IDLE,
            "idle_restoration",
            [
                ("speaking_state", None, None, False),
                ("reset_expression", None, None, None),
                ("idle_motion", None, "idle", None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.FAILED,
            CharacterMotionCue.TIRED_SUPPORTIVE,
            "failure_supportive",
            [
                ("stop_motion", None, None, None),
                ("speaking_state", None, None, False),
                ("expression", "supportive", None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.CLOSED,
            CharacterMotionCue.IDLE,
            "terminal_stop_and_reset",
            [
                ("stop_motion", None, None, None),
                ("speaking_state", None, None, False),
                ("reset_expression", None, None, None),
            ],
        ),
        (
            CharacterMotionLifecycleFact.UNAVAILABLE,
            CharacterMotionCue.IDLE,
            "terminal_stop_and_reset",
            [
                ("stop_motion", None, None, None),
                ("speaking_state", None, None, False),
                ("reset_expression", None, None, None),
            ],
        ),
    ],
)
def test_exact_lifecycle_mapping(
    mapper: CharacterMotionMapper,
    fact: CharacterMotionLifecycleFact,
    cue: CharacterMotionCue,
    reason: str,
    commands: list[tuple[str, str | None, str | None, bool | None]],
) -> None:
    plan = mapper.map(CharacterMotionMappingInput(fact=fact))

    assert plan.outcome is CharacterMotionMappingOutcome.MAPPED
    assert plan.source_fact is fact
    assert plan.cue is cue
    assert plan.reason_code == reason
    assert [command.order for command in plan.commands] == list(
        range(1, len(plan.commands) + 1)
    )
    assert _command_shape(plan) == commands
    assert len(plan.commands) <= CHARACTER_MOTION_MAX_COMMANDS


@pytest.mark.parametrize(
    ("fact", "reason"),
    [
        (
            CharacterMotionLifecycleFact.MOTION_ACTIVE,
            "recursive_motion_fact_ignored",
        ),
        (CharacterMotionLifecycleFact.UNKNOWN, "unknown_fact_ignored"),
    ],
)
def test_recursive_and_unknown_facts_fail_closed(
    mapper: CharacterMotionMapper,
    fact: CharacterMotionLifecycleFact,
    reason: str,
) -> None:
    plan = mapper.map(CharacterMotionMappingInput(fact=fact))

    assert plan.outcome is CharacterMotionMappingOutcome.IGNORED
    assert plan.reason_code == reason
    assert plan.cue is None
    assert plan.commands == []


@pytest.mark.parametrize(
    ("state", "fact"),
    [
        (RealtimeState.IDLE, CharacterMotionLifecycleFact.IDLE),
        (RealtimeState.LISTENING, CharacterMotionLifecycleFact.LISTENING),
        (RealtimeState.TRANSCRIBING, CharacterMotionLifecycleFact.TRANSCRIBING),
        (RealtimeState.THINKING, CharacterMotionLifecycleFact.THINKING),
        (RealtimeState.RESPONDING, CharacterMotionLifecycleFact.RESPONDING),
        (RealtimeState.SPEAKING, CharacterMotionLifecycleFact.SPEAKING),
        (RealtimeState.MOTION, CharacterMotionLifecycleFact.MOTION_ACTIVE),
        (RealtimeState.INTERRUPTED, CharacterMotionLifecycleFact.INTERRUPTED),
        (RealtimeState.FAILED, CharacterMotionLifecycleFact.FAILED),
        (RealtimeState.COMPLETED, CharacterMotionLifecycleFact.COMPLETED),
        (RealtimeState.CLOSED, CharacterMotionLifecycleFact.CLOSED),
        (RealtimeState.UNAVAILABLE, CharacterMotionLifecycleFact.UNAVAILABLE),
        (RealtimeState.UNKNOWN, CharacterMotionLifecycleFact.UNKNOWN),
    ],
)
def test_realtime_state_mapping_is_complete(
    mapper: CharacterMotionMapper,
    state: RealtimeState,
    fact: CharacterMotionLifecycleFact,
) -> None:
    plan = mapper.map_realtime_state(state)

    assert plan.source_fact is fact


def test_mapping_is_deterministic_and_preserves_safe_ids(
    mapper: CharacterMotionMapper,
) -> None:
    source = CharacterMotionMappingInput(
        fact=CharacterMotionLifecycleFact.THINKING,
        source_event_type="text_chat_started",
        session_id="session-1",
        turn_id="turn-1",
        character_id="gentle_mina",
    )

    first = mapper.map(source)
    second = mapper.map(source)

    assert first == second
    assert first.source_event_type == "text_chat_started"
    assert first.session_id == "session-1"
    assert first.turn_id == "turn-1"
    assert first.character_id == "gentle_mina"


def test_only_speaking_fact_sets_speaking_true(
    mapper: CharacterMotionMapper,
) -> None:
    true_facts = []
    for fact in CharacterMotionLifecycleFact:
        plan = mapper.map(CharacterMotionMappingInput(fact=fact))
        if any(command.speaking is True for command in plan.commands):
            true_facts.append(fact)

    assert true_facts == [CharacterMotionLifecycleFact.SPEAKING]


@pytest.mark.parametrize(
    "fact",
    [
        CharacterMotionLifecycleFact.INTERRUPTED,
        CharacterMotionLifecycleFact.FAILED,
        CharacterMotionLifecycleFact.CLOSED,
        CharacterMotionLifecycleFact.UNAVAILABLE,
    ],
)
def test_stop_first_for_interrupted_and_terminal_failures(
    mapper: CharacterMotionMapper,
    fact: CharacterMotionLifecycleFact,
) -> None:
    plan = mapper.map(CharacterMotionMappingInput(fact=fact))

    assert plan.commands[0].intent is CharacterMotionCommandIntent.STOP_MOTION


def test_models_reject_arbitrary_metadata_and_oversized_ids() -> None:
    with pytest.raises(ValidationError):
        CharacterMotionMappingInput(
            fact=CharacterMotionLifecycleFact.IDLE,
            private_metadata={"token": "not-allowed"},  # type: ignore[call-arg]
        )
    with pytest.raises(ValidationError):
        CharacterMotionMappingInput(
            fact=CharacterMotionLifecycleFact.IDLE,
            session_id="x" * 129,
        )


def test_command_and_plan_models_reject_ambiguous_or_unbounded_shapes() -> None:
    with pytest.raises(ValidationError, match="expression command"):
        CharacterMotionCommand(
            order=1,
            intent=CharacterMotionCommandIntent.EXPRESSION,
        )
    with pytest.raises(ValidationError, match="contiguous"):
        CharacterMotionPlan(
            outcome=CharacterMotionMappingOutcome.MAPPED,
            source_fact=CharacterMotionLifecycleFact.IDLE,
            cue=CharacterMotionCue.IDLE,
            reason_code="bad_order",
            commands=[
                CharacterMotionCommand(
                    order=2,
                    intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
                )
            ],
        )
    with pytest.raises(ValidationError):
        CharacterMotionPlan(
            outcome=CharacterMotionMappingOutcome.MAPPED,
            source_fact=CharacterMotionLifecycleFact.IDLE,
            cue=CharacterMotionCue.IDLE,
            reason_code="too_many",
            commands=[
                CharacterMotionCommand(
                    order=1,
                    intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
                ),
                CharacterMotionCommand(
                    order=2,
                    intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
                ),
                CharacterMotionCommand(
                    order=3,
                    intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
                ),
                CharacterMotionCommand(
                    order=3,
                    intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
                ),
            ],
        )


def test_mapper_rejects_wrong_input_types() -> None:
    mapper = CharacterMotionMapper()

    with pytest.raises(TypeError, match="CharacterMotionMappingInput"):
        mapper.map(CharacterMotionLifecycleFact.IDLE)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="RealtimeState"):
        mapper.map_realtime_state("idle")  # type: ignore[arg-type]


def test_rt6b_source_has_no_framework_import() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    for relative in (
        "app/models/character_motion.py",
        "app/services/character_motion_mapper.py",
    ):
        tree = ast.parse((backend_root / relative).read_text(encoding="utf-8"))
        imported_modules = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ] + [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        assert not any(
            module == "framework" or module.startswith("framework.")
            for module in imported_modules
        )

    mapper = CharacterMotionMapper()
    plan = mapper.map(
        CharacterMotionMappingInput(fact=CharacterMotionLifecycleFact.IDLE)
    )
    assert plan.outcome is CharacterMotionMappingOutcome.MAPPED
