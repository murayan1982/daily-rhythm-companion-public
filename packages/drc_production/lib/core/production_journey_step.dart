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
    step: ProductionJourneyStep.moodCheckIn,
    capability: ProductionCapability.moodCheckIn,
    order: 1,
    title: '気分を選ぶ',
    description: '今日の気分を3つから選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localSelectionAvailable,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.characterSelection,
    capability: ProductionCapability.characterSelection,
    order: 2,
    title: 'キャラクターを選ぶ',
    description: '3人のキャラクターから、今の自分に合う相棒を選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localSelectionAvailable,
  ),
  ProductionJourneyItem(
    step: ProductionJourneyStep.dailyAdvice,
    capability: ProductionCapability.dailyAdvice,
    order: 3,
    title: '今日のアドバイス',
    description: '気分とキャラクターを選ぶと、端末内で今日のメッセージを表示します。選択内容は保存されません。',
    isOptional: false,
    state: ProductionJourneyStepState.localResultAvailable,
  ),
];
