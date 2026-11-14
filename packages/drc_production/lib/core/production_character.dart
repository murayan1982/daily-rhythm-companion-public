enum ProductionCharacter { gentleMina, cheerfulSora, coolRei }

class ProductionCharacterOption {
  const ProductionCharacterOption({
    required this.character,
    required this.characterId,
    required this.displayName,
    required this.headline,
    required this.tagline,
    required this.toneLabel,
    required this.summary,
  });

  final ProductionCharacter character;
  final String characterId;
  final String displayName;
  final String headline;
  final String tagline;
  final String toneLabel;
  final String summary;
}

const List<ProductionCharacterOption> productionCharacterOptions = [
  ProductionCharacterOption(
    character: ProductionCharacter.gentleMina,
    characterId: 'gentle_mina',
    displayName: 'ミナ',
    headline: 'やさしく整える',
    tagline: '休息に寄り添う落ち着いた相棒',
    toneLabel: '休息重視 / やさしい',
    summary: '疲れ気味の日でも、無理なく整える一言をくれるキャラクター。',
  ),
  ProductionCharacterOption(
    character: ProductionCharacter.cheerfulSora,
    characterId: 'cheerful_sora',
    displayName: 'ソラ',
    headline: '明るく背中を押す',
    tagline: '前向きな勢いをくれる相棒',
    toneLabel: '前向き / 元気',
    summary: '少し気分を上げたい日に、軽く動き出せる言葉をくれるキャラクター。',
  ),
  ProductionCharacterOption(
    character: ProductionCharacter.coolRei,
    characterId: 'cool_rei',
    displayName: 'レイ',
    headline: '短く実用的に整理する',
    tagline: '落ち着いて次の一手を出す相棒',
    toneLabel: '実用重視 / 端的',
    summary: '忙しい日でも、今できる小さな行動へ整理してくれるキャラクター。',
  ),
];

ProductionCharacterOption productionCharacterOptionFor(
  ProductionCharacter character,
) {
  return productionCharacterOptions.singleWhere(
    (option) => option.character == character,
  );
}
