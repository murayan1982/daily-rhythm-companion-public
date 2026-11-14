import 'production_character.dart';
import 'production_mood.dart';

class ProductionLocalAdvice {
  const ProductionLocalAdvice({
    required this.mood,
    required this.character,
    required this.message,
  });

  final ProductionMood mood;
  final ProductionCharacter character;
  final String message;
}

ProductionLocalAdvice productionLocalAdviceFor({
  required ProductionMood mood,
  required ProductionCharacter character,
}) {
  final message = switch ((character, mood)) {
    (ProductionCharacter.gentleMina, ProductionMood.energetic) =>
      '今日は調子がよさそうですね。無理に予定を増やさず、気持ちよいペースを保っていきましょう。',
    (ProductionCharacter.gentleMina, ProductionMood.normal) =>
      'いつもの調子を大切に、ひとつずつ進めてみましょう。少し疲れたら、早めに休憩して大丈夫です。',
    (ProductionCharacter.gentleMina, ProductionMood.tired) =>
      '今日は無理に頑張りすぎなくて大丈夫です。まずは短い休憩と、できることをひとつだけにしましょう。',
    (ProductionCharacter.cheerfulSora, ProductionMood.energetic) =>
      'いい調子ですね！今の勢いを使って、やりたいことをひとつ始めてみましょう。',
    (ProductionCharacter.cheerfulSora, ProductionMood.normal) =>
      '今日は小さく動き出せれば十分です。まずは気軽にひとつ、始めてみましょう！',
    (ProductionCharacter.cheerfulSora, ProductionMood.tired) =>
      '疲れている日は小さな一歩でOKです。水分をとって、負担の少ないことから始めましょう。',
    (ProductionCharacter.coolRei, ProductionMood.energetic) =>
      '調子は良好です。優先することを一つ決め、終えたら次へ進みましょう。',
    (ProductionCharacter.coolRei, ProductionMood.normal) =>
      '今日の優先事項を一つ決めましょう。終えたら短い休憩を入れてください。',
    (ProductionCharacter.coolRei, ProductionMood.tired) =>
      '今日はタスクを増やさない方がよいでしょう。必要なことを一つに絞り、終えたら休みましょう。',
  };

  return ProductionLocalAdvice(
    mood: mood,
    character: character,
    message: message,
  );
}
