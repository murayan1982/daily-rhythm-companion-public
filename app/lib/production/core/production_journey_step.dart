import 'production_capability.dart';

enum ProductionJourneyStep {
  sleepStatus,
  moodCheckIn,
  characterSelection,
  dailyAdvice,
  optionalTextChat,
  history,
}

enum ProductionJourneyStepState {
  planned,
  decisionPending,
  localSelectionAvailable,
  localResultAvailable,
}

class ProductionJourneyItem {
  const ProductionJourneyItem({
    required this.step,
    required this.capability,
    required this.order,
    required this.title,
    required this.description,
    required this.isOptional,
    required this.state,
  });

  final ProductionJourneyStep step;
  final ProductionCapability capability;
  final int order;
  final String title;
  final String description;
  final bool isOptional;
  final ProductionJourneyStepState state;
}

const List<ProductionJourneyItem> productionJourneyItems = [
  ProductionJourneyItem(
    step: ProductionJourneyStep.sleepStatus,
    capability: ProductionCapability.sleepHealthConnection,
    order: 1,
    title: '睡眠を確認',
    description: '睡眠の確認や健康データの連携方法を準備中です。',
    isOptional: false,
    state: ProductionJourneyStepState.decisionPending,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.moodCheckIn,
    capability: ProductionCapability.moodCheckIn,
    order: 2,
    title: '気分を記録',
    description: '今日の気分を3つから選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localSelectionAvailable,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.characterSelection,
    capability: ProductionCapability.characterSelection,
    order: 3,
    title: 'キャラクターを選択',
    description: '3人のキャラクターから、今の自分に合う相棒を選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localSelectionAvailable,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.dailyAdvice,
    capability: ProductionCapability.dailyAdvice,
    order: 4,
    title: '今日のアドバイス',
    description: '気分とキャラクターを選ぶと、端末内で今日のメッセージを表示します。選択内容は保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localResultAvailable,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.optionalTextChat,
    capability: ProductionCapability.optionalTextChat,
    order: 5,
    title: '会話を続ける',
    description: 'アドバイスのあとに、必要に応じて文字で会話を続けられるようになります。',
    isOptional: true,
    state: ProductionJourneyStepState.planned,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.history,
    capability: ProductionCapability.history,
    order: 6,
    title: '履歴を振り返る',
    description: 'これまでの記録を振り返る機能を準備しています。',
    isOptional: false,
    state: ProductionJourneyStepState.planned,
  ),
];
