from app.engines.base import ConversationEngine
from app.models.advice import AdviceRequest, AdviceResponse, AdviceSource
from app.models.sleep import SleepSummary
from app.models.recent_sleep_trend import RecentSleepTrend


class MockConversationEngine(ConversationEngine):
    """
    Development-only conversation engine.

    This engine returns a deterministic response without calling any external
    LLM provider or the framework. It still mirrors the production advice
    contract by reflecting normalized sleep data, mood, and character context.

    Mock responses intentionally use stable internal mood IDs and normalized
    sleep quality labels. Future UI layers may vary mood choice labels by
    character, sleep state, or date, but this engine should keep depending on
    the stable mood contract used by the advice prompt builder.
    """

    def create_advice(self, request: AdviceRequest) -> AdviceResponse:
        mood_label = self._format_mood_label(request.mood)
        message = self._build_message(request, mood_label)

        return AdviceResponse(
            message=message,
            character_name=request.character.display_name,
            source=AdviceSource(
                engine="mock",
                drc_character_id=request.character.character_id,
                drc_character_name=request.character.display_name,
            ),
        )

    def _build_message(self, request: AdviceRequest, mood_label: str) -> str:
        sleep = request.sleep
        character_name = request.character.display_name

        if not sleep.available:
            return self._build_unavailable_sleep_message(
                character_name=character_name,
                personality_type=request.character.personality_type,
                mood=request.mood,
                mood_label=mood_label,
                recent_sleep_trend=request.recent_sleep_trend,
            )

        sleep_hours = sleep.total_sleep_minutes // 60
        sleep_minutes = sleep.total_sleep_minutes % 60
        quality_label = self._format_quality_label(sleep.quality_label)
        data_prefix = "Google Healthの実データでは" if sleep.is_real_data else "睡眠サマリーでは"
        quality_sentence = (
            f"睡眠評価は「{quality_label}」です。" if quality_label else ""
        )
        advice_sentence = self._build_advice_sentence(
            sleep=sleep,
            mood=request.mood,
        )

        return (
            f"{character_name}です。"
            f"{data_prefix}、昨夜の睡眠は{sleep_hours}時間{sleep_minutes}分くらいですね。"
            f"{quality_sentence}"
            f"今の気分は「{mood_label}」として受け取りました。"
            f"{advice_sentence}"
        )

    def _build_unavailable_sleep_message(
        self,
        *,
        character_name: str,
        personality_type: str,
        mood: str,
        mood_label: str,
        recent_sleep_trend: RecentSleepTrend | None = None,
    ) -> str:
        """
        Build a character-facing message when current sleep data is unavailable.

        The mock engine must not invent sleep duration or quality here. Instead,
        it mirrors the intended app experience: the character acknowledges that
        today's sleep could not be observed and then bases the advice on mood.
        """

        opening = self._build_unavailable_sleep_opening(
            personality_type=personality_type,
        )
        trend_note = self._build_recent_sleep_trend_note(recent_sleep_trend)
        advice = self._build_unavailable_sleep_advice(
            personality_type=personality_type,
            mood=mood,
            mood_label=mood_label,
        )

        return f"{character_name}です。{opening}{trend_note}{advice}"

    def _build_recent_sleep_trend_note(
        self,
        recent_sleep_trend: RecentSleepTrend | None,
    ) -> str:
        """Build a short user-facing note from historical sleep context only."""

        if (
            recent_sleep_trend is None
            or recent_sleep_trend.label == "insufficient_data"
        ):
            return ""

        if recent_sleep_trend.label == "recently_short":
            return "最近の記録では、睡眠が短めの日が続いていそうです。"

        if recent_sleep_trend.label == "recently_good":
            return "最近の記録では、睡眠は比較的足りていそうです。"

        return "最近の記録では、睡眠リズムは大きく崩れていなさそうです。"

    def _build_unavailable_sleep_opening(self, *, personality_type: str) -> str:
        if personality_type == "cheerful":
            return "ごめん、今日は君の眠りをうまく見つけられなかったみたい。"

        if personality_type == "cool":
            return "今日は睡眠データを確認できませんでした。"

        return "ごめんね、今日は君の眠りを観測できなかったんだ。"

    def _build_unavailable_sleep_advice(
        self,
        *,
        personality_type: str,
        mood: str,
        mood_label: str,
    ) -> str:
        if personality_type == "cheerful":
            return self._build_cheerful_unavailable_advice(
                mood=mood,
                mood_label=mood_label,
            )

        if personality_type == "cool":
            return self._build_cool_unavailable_advice(
                mood=mood,
                mood_label=mood_label,
            )

        return self._build_gentle_unavailable_advice(
            mood=mood,
            mood_label=mood_label,
        )

    def _build_gentle_unavailable_advice(
        self,
        *,
        mood: str,
        mood_label: str,
    ) -> str:
        if mood == "tired":
            return (
                f"だから今の気分「{mood_label}」を中心に見ていくね。"
                "無理に予定を詰めず、まずは軽めのタスクを1つだけ選ぼう。"
            )

        if mood == "energetic":
            return (
                f"でも今の気分「{mood_label}」はちゃんと受け取れてるよ。"
                "調子の良さを活かしつつ、休憩も先に入れて進めよう。"
            )

        return (
            f"だから今の気分「{mood_label}」を中心に見ていくね。"
            "まずは普段通りのペースで、今日やることを小さく区切って始めよう。"
        )

    def _build_cheerful_unavailable_advice(
        self,
        *,
        mood: str,
        mood_label: str,
    ) -> str:
        if mood == "tired":
            return (
                f"でも今の気分「{mood_label}」はちゃんと見えてるよ。"
                "今日は省エネ作戦で、軽めのタスクから始めよう。"
            )

        if mood == "energetic":
            return (
                f"でも今の気分「{mood_label}」はちゃんと見えてるよ。"
                "調子の良さを活かしつつ、休憩も先に入れて進めよう。"
            )

        return (
            f"でも今の気分「{mood_label}」はちゃんと見えてるよ。"
            "そこから今日の作戦を立てて、まずは動きやすいことから始めよう。"
        )

    def _build_cool_unavailable_advice(
        self,
        *,
        mood: str,
        mood_label: str,
    ) -> str:
        if mood == "tired":
            return (
                f"今の気分「{mood_label}」を基準に、今日の負荷を少し下げましょう。"
                "まずは小さなタスクから始めるのが良さそうです。"
            )

        if mood == "energetic":
            return (
                f"今の気分「{mood_label}」を基準に、進める作業を1つ選びましょう。"
                "睡眠状態は断定せず、休憩も予定に入れておくのが安全です。"
            )

        return (
            f"今の気分「{mood_label}」を基準に、今日の予定を調整しましょう。"
            "まずは優先度の高いタスクを1つ選ぶのが良さそうです。"
        )

    def _build_advice_sentence(self, *, sleep: SleepSummary, mood: str) -> str:
        quality_label = sleep.quality_label or ""

        if quality_label == "short":
            return self._build_short_sleep_advice(mood)

        if quality_label == "good":
            return self._build_good_sleep_advice(mood)

        if quality_label == "fair":
            return self._build_fair_sleep_advice(mood)

        return self._build_unknown_sleep_advice(mood)

    def _build_short_sleep_advice(self, mood: str) -> str:
        if mood == "tired":
            return (
                "睡眠は短めで、気分も少し重そうなので、今日は回復優先でいきましょう。"
                "最初のタスクは小さくして、できれば予定の負荷も少し下げるのがよさそうです。"
            )

        if mood == "energetic":
            return (
                "睡眠は短めですが、今は動けそうな状態ですね。"
                "ただ、後半に疲れが出るかもしれないので、大事なことは早めに進めて、休憩も先に予定へ入れておきましょう。"
            )

        return (
            "睡眠は短めなので、今日は少し軽めの計画がよさそうです。"
            "まずは小さな作業から始めて、こまめに休憩を入れていきましょう。"
        )

    def _build_good_sleep_advice(self, mood: str) -> str:
        if mood == "tired":
            return (
                "睡眠は悪くなさそうですが、今のだるさも大事なサインとして扱いましょう。"
                "いきなり全力にせず、軽い準備運動のようなタスクから始めるのがよさそうです。"
            )

        if mood == "energetic":
            return (
                "睡眠も気分も良さそうなので、今日は大事なタスクを1つ前に進めるチャンスです。"
                "ただし予定を詰め込みすぎず、良いリズムを保つ意識でいきましょう。"
            )

        return (
            "睡眠は良さそうなので、今日は安定したペースで進められそうです。"
            "大きく広げすぎず、まずは今日の中心タスクを1つ決めるのがよさそうです。"
        )

    def _build_fair_sleep_advice(self, mood: str) -> str:
        if mood == "tired":
            return (
                "睡眠はそこそこですが、気分は少し重そうですね。"
                "今日は無理に上げようとせず、作業を小さく区切って休憩をはさむのがよさそうです。"
            )

        if mood == "energetic":
            return (
                "睡眠はまずまずで、気分は前向きですね。"
                "勢いを使いつつ、詰め込みすぎない範囲で今日の優先タスクから進めましょう。"
            )

        return (
            "睡眠も気分も大きく崩れてはいなさそうです。"
            "今日は普段通りのペースで、無理なく進められるタスクを1つ選びましょう。"
        )

    def _build_unknown_sleep_advice(self, mood: str) -> str:
        if mood == "tired":
            return (
                "睡眠評価はまだはっきりしませんが、今のだるさを優先して見ていきましょう。"
                "今日は軽めに始めて、休憩を先に入れておくのがよさそうです。"
            )

        if mood == "energetic":
            return (
                "睡眠評価はまだはっきりしませんが、今の前向きさは活かせそうです。"
                "無理に広げすぎず、まずは大事なことを1つ進めましょう。"
            )

        return (
            "睡眠評価はまだはっきりしないので、今日は様子を見ながら進めましょう。"
            "まずは取りかかりやすいタスクを1つ選ぶのがよさそうです。"
        )

    def _format_mood_label(self, mood: str) -> str:
        """Convert internal mood values into user-facing Japanese labels."""
        mood_labels = {
            "energetic": "元気",
            "normal": "ふつう",
            "tired": "だるい",
        }

        return mood_labels.get(mood, mood)

    def _format_quality_label(self, value: str | None) -> str:
        """Convert normalized sleep quality labels into Japanese labels."""
        quality_labels = {
            "good": "良好",
            "fair": "ふつう",
            "short": "短め",
            "unavailable": "未取得",
        }

        if not value:
            return ""

        return quality_labels.get(value, value)
