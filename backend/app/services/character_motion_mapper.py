"""Pure deterministic lifecycle-to-character-motion mapping for RT-6b."""

from __future__ import annotations

from app.models.character_motion import (
    CharacterMotionCommand,
    CharacterMotionCommandIntent,
    CharacterMotionCue,
    CharacterMotionLifecycleFact,
    CharacterMotionMappingInput,
    CharacterMotionMappingOutcome,
    CharacterMotionPlan,
)
from app.models.realtime import RealtimeState


class CharacterMotionMapper:
    """Map DRC lifecycle facts without runtime, provider, or session execution."""

    _REALTIME_FACTS: dict[RealtimeState, CharacterMotionLifecycleFact] = {
        RealtimeState.IDLE: CharacterMotionLifecycleFact.IDLE,
        RealtimeState.LISTENING: CharacterMotionLifecycleFact.LISTENING,
        RealtimeState.TRANSCRIBING: CharacterMotionLifecycleFact.TRANSCRIBING,
        RealtimeState.THINKING: CharacterMotionLifecycleFact.THINKING,
        RealtimeState.RESPONDING: CharacterMotionLifecycleFact.RESPONDING,
        RealtimeState.SPEAKING: CharacterMotionLifecycleFact.SPEAKING,
        RealtimeState.MOTION: CharacterMotionLifecycleFact.MOTION_ACTIVE,
        RealtimeState.INTERRUPTED: CharacterMotionLifecycleFact.INTERRUPTED,
        RealtimeState.FAILED: CharacterMotionLifecycleFact.FAILED,
        RealtimeState.COMPLETED: CharacterMotionLifecycleFact.COMPLETED,
        RealtimeState.CLOSED: CharacterMotionLifecycleFact.CLOSED,
        RealtimeState.UNAVAILABLE: CharacterMotionLifecycleFact.UNAVAILABLE,
        RealtimeState.UNKNOWN: CharacterMotionLifecycleFact.UNKNOWN,
    }

    def map(self, source: CharacterMotionMappingInput) -> CharacterMotionPlan:
        """Return the exact bounded plan for one app-owned lifecycle fact."""

        if not isinstance(source, CharacterMotionMappingInput):
            raise TypeError("source must be a CharacterMotionMappingInput")

        fact = source.fact
        if fact in {
            CharacterMotionLifecycleFact.MOTION_ACTIVE,
            CharacterMotionLifecycleFact.UNKNOWN,
        }:
            return self._plan(
                source,
                outcome=CharacterMotionMappingOutcome.IGNORED,
                cue=None,
                reason_code=(
                    "recursive_motion_fact_ignored"
                    if fact is CharacterMotionLifecycleFact.MOTION_ACTIVE
                    else "unknown_fact_ignored"
                ),
                commands=[],
            )

        if fact in {
            CharacterMotionLifecycleFact.IDLE,
            CharacterMotionLifecycleFact.COMPLETED,
        }:
            return self._plan(
                source,
                cue=CharacterMotionCue.IDLE,
                reason_code="idle_restoration",
                commands=[
                    self._speaking(1, False),
                    self._reset(2),
                    self._idle(3),
                ],
            )

        if fact is CharacterMotionLifecycleFact.LISTENING:
            return self._plan(
                source,
                cue=CharacterMotionCue.IDLE,
                reason_code="listening_supportive",
                commands=[
                    self._speaking(1, False),
                    self._expression(2, "supportive"),
                ],
            )

        if fact in {
            CharacterMotionLifecycleFact.TRANSCRIBING,
            CharacterMotionLifecycleFact.THINKING,
            CharacterMotionLifecycleFact.RESPONDING,
            CharacterMotionLifecycleFact.TTS_PREPARING,
        }:
            return self._plan(
                source,
                cue=CharacterMotionCue.THINKING,
                reason_code="thinking_presentation",
                commands=[
                    self._speaking(1, False),
                    self._expression(2, "thinking"),
                ],
            )

        if fact is CharacterMotionLifecycleFact.SPEAKING:
            return self._plan(
                source,
                cue=CharacterMotionCue.SPEAKING,
                reason_code="speaking_presentation",
                commands=[
                    self._expression(1, "speaking"),
                    self._speaking(2, True),
                ],
            )

        if fact is CharacterMotionLifecycleFact.FAILED:
            return self._plan(
                source,
                cue=CharacterMotionCue.TIRED_SUPPORTIVE,
                reason_code="failure_supportive",
                commands=[
                    self._stop(1),
                    self._speaking(2, False),
                    self._expression(3, "supportive"),
                ],
            )

        if fact in {
            CharacterMotionLifecycleFact.INTERRUPTED,
            CharacterMotionLifecycleFact.CLOSED,
            CharacterMotionLifecycleFact.UNAVAILABLE,
        }:
            return self._plan(
                source,
                cue=CharacterMotionCue.IDLE,
                reason_code="terminal_stop_and_reset",
                commands=[
                    self._stop(1),
                    self._speaking(2, False),
                    self._reset(3),
                ],
            )

        raise AssertionError(f"Unhandled character-motion lifecycle fact: {fact.value}")

    def map_realtime_state(
        self,
        state: RealtimeState,
        *,
        source_event_type: str | None = None,
        session_id: str | None = None,
        turn_id: str | None = None,
        character_id: str | None = None,
    ) -> CharacterMotionPlan:
        """Map an accepted DRC RealtimeState through the same pure boundary."""

        if not isinstance(state, RealtimeState):
            raise TypeError("state must be a RealtimeState")
        return self.map(
            CharacterMotionMappingInput(
                fact=self._REALTIME_FACTS[state],
                source_event_type=source_event_type,
                session_id=session_id,
                turn_id=turn_id,
                character_id=character_id,
            )
        )

    @staticmethod
    def _plan(
        source: CharacterMotionMappingInput,
        *,
        cue: CharacterMotionCue | None,
        reason_code: str,
        commands: list[CharacterMotionCommand],
        outcome: CharacterMotionMappingOutcome = CharacterMotionMappingOutcome.MAPPED,
    ) -> CharacterMotionPlan:
        return CharacterMotionPlan(
            outcome=outcome,
            source_fact=source.fact,
            cue=cue,
            reason_code=reason_code,
            commands=commands,
            source_event_type=source.source_event_type,
            session_id=source.session_id,
            turn_id=source.turn_id,
            character_id=source.character_id,
        )

    @staticmethod
    def _expression(order: int, expression_id: str) -> CharacterMotionCommand:
        return CharacterMotionCommand(
            order=order,
            intent=CharacterMotionCommandIntent.EXPRESSION,
            expression_id=expression_id,
        )

    @staticmethod
    def _speaking(order: int, speaking: bool) -> CharacterMotionCommand:
        return CharacterMotionCommand(
            order=order,
            intent=CharacterMotionCommandIntent.SPEAKING_STATE,
            speaking=speaking,
        )

    @staticmethod
    def _idle(order: int) -> CharacterMotionCommand:
        return CharacterMotionCommand(
            order=order,
            intent=CharacterMotionCommandIntent.IDLE_MOTION,
            motion_event=CharacterMotionCue.IDLE,
        )

    @staticmethod
    def _stop(order: int) -> CharacterMotionCommand:
        return CharacterMotionCommand(
            order=order,
            intent=CharacterMotionCommandIntent.STOP_MOTION,
        )

    @staticmethod
    def _reset(order: int) -> CharacterMotionCommand:
        return CharacterMotionCommand(
            order=order,
            intent=CharacterMotionCommandIntent.RESET_EXPRESSION,
        )
