import 'package:drc_production/core/production_character.dart';
import 'package:flutter/material.dart';

Widget buildBundledCharacterPortrait(
  ProductionCharacterOption option,
  Widget fallback,
) {
  final verticalAlignment = switch (option.character) {
    ProductionCharacter.gentleMina => -0.42,
    ProductionCharacter.cheerfulSora => -0.32,
    ProductionCharacter.coolRei => -0.35,
  };
  return Image.asset(
    'assets/characters/${option.characterId}_demo.png',
    fit: BoxFit.cover,
    cacheWidth: 256,
    frameBuilder: (context, child, frame, _) {
      if (frame == null) return fallback;
      // Zoom around each face; the character card supplies the circular clip.
      return Transform.scale(
        scale: 1.6,
        alignment: Alignment(0, verticalAlignment),
        child: child,
      );
    },
    errorBuilder: (context, error, stackTrace) => fallback,
  );
}
