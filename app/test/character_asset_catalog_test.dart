import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/ui/character_asset_catalog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('accepted image files are included in the Flutter asset bundle', () async {
    for (final assetPath in CharacterAssetCatalog.allAssetPaths) {
      final data = await rootBundle.load(assetPath);
      expect(
        data.lengthInBytes,
        greaterThan(0),
        reason: 'Flutter asset is missing or empty: $assetPath',
      );
    }
  });

  test('known character ids resolve accepted image assets', () {
    expect(
      CharacterAssetCatalog.imageForCharacter('gentle_mina'),
      'assets/images/characters/gentle_mina_demo.png',
    );
    expect(
      CharacterAssetCatalog.imageForCharacter('cheerful_sora'),
      'assets/images/characters/cheerful_sora_demo.png',
    );
    expect(
      CharacterAssetCatalog.imageForCharacter('cool_rei'),
      'assets/images/characters/cool_rei_demo.png',
    );
  });

  test('unknown character id resolves accepted fallback asset', () {
    expect(
      CharacterAssetCatalog.imageForCharacter('unknown_character'),
      CharacterAssetCatalog.fallbackCharacter,
    );
  });
}
