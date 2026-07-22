class CharacterAssetCatalog {
  const CharacterAssetCatalog._();

  static const String fallbackCharacter =
      'assets/images/placeholders/character_fallback.png';
  static const String morningBackground =
      'assets/images/backgrounds/morning_room_soft.png';
  static const String nightBackground =
      'assets/images/backgrounds/night_room_calm.png';

  static const Map<String, String> characterImages = <String, String>{
    'gentle_mina': 'assets/images/characters/gentle_mina_demo.png',
    'cheerful_sora': 'assets/images/characters/cheerful_sora_demo.png',
    'cool_rei': 'assets/images/characters/cool_rei_demo.png',
  };

  static const List<String> allAssetPaths = <String>[
    'assets/images/characters/gentle_mina_demo.png',
    'assets/images/characters/cheerful_sora_demo.png',
    'assets/images/characters/cool_rei_demo.png',
    morningBackground,
    nightBackground,
    fallbackCharacter,
  ];

  static String imageForCharacter(String characterId) {
    return characterImages[characterId] ?? fallbackCharacter;
  }
}
