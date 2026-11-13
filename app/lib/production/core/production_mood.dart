enum ProductionMood { energetic, normal, tired }

class ProductionMoodOption {
  const ProductionMoodOption({
    required this.mood,
    required this.code,
    required this.emoji,
    required this.label,
    required this.supportMessage,
  });

  final ProductionMood mood;
  final String code;
  final String emoji;
  final String label;
  final String supportMessage;
}

const List<ProductionMoodOption> productionMoodOptions = [
  ProductionMoodOption(
    mood: ProductionMood.energetic,
    code: 'energetic',
    emoji: '☀️',
    label: '元気',
    supportMessage: '今日は前向きに動けそうです。',
  ),
  ProductionMoodOption(
    mood: ProductionMood.normal,
    code: 'normal',
    emoji: '🌿',
    label: 'ふつう',
    supportMessage: '今日はいつも通り過ごせそうです。',
  ),
  ProductionMoodOption(
    mood: ProductionMood.tired,
    code: 'tired',
    emoji: '😪',
    label: 'だるい',
    supportMessage: '今日は回復を優先したい状態です。',
  ),
];

ProductionMoodOption productionMoodOptionFor(ProductionMood mood) {
  return productionMoodOptions.singleWhere((option) => option.mood == mood);
}
