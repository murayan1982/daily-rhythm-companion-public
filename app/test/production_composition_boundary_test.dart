import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/production/production_app.dart';
import 'package:app/production/production_home_screen.dart';

void main() {
  testWidgets('ProductionApp exposes only the minimal production shell', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ProductionApp());

    final app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.title, 'Daily Rhythm Companion');
    expect(app.debugShowCheckedModeBanner, isFalse);
    expect(find.byType(ProductionHomeScreen), findsOneWidget);
    expect(find.text('Daily Rhythm Companion'), findsNWidgets(2));
  });

  testWidgets('Production shell exposes no non-product or endpoint copy', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ProductionApp());

    for (final text in <String>[
      'developer',
      'operator',
      'demo',
      'diagnostic',
      'localhost',
      'Backend',
      'engine',
      'capability',
      'session ID',
      'technical code',
    ]) {
      expect(find.textContaining(text, findRichText: true), findsNothing);
    }
  });

  test('production entrypoint has the exact direct directive boundary', () {
    final source = File('lib/main_production.dart').readAsStringSync();
    final directives = _directives(source);

    expect(directives, <_SourceDirective>[
      const _SourceDirective('import', 'package:flutter/material.dart'),
      const _SourceDirective('import', 'production/production_app.dart'),
    ]);
  });

  test(
    'production directory recursively stays inside its directive boundary',
    () {
      final productionRoot = Directory('lib/production').absolute;
      final files =
          productionRoot
              .listSync(recursive: true)
              .whereType<File>()
              .where((file) => file.path.endsWith('.dart'))
              .toList()
            ..sort((a, b) => a.path.compareTo(b.path));

      expect(files, isNotEmpty);
      for (final file in files) {
        for (final directive in _directives(file.readAsStringSync())) {
          expect(
            _isAllowedProductionUri(
              directive.uri,
              sourcePath: file.absolute.path,
              productionRootPath: productionRoot.path,
              caseInsensitive: Platform.isWindows,
            ),
            isTrue,
            reason: '${file.path} ${directive.kind}s ${directive.uri}',
          );
        }
      }
    },
  );

  test('directive guard accepts only Flutter and contained relative URIs', () {
    const source = 'lib/production/production_app.dart';
    const root = 'lib/production';
    final accepted = <String>[
      'package:flutter/material.dart',
      'production_home_screen.dart',
      'components/example.dart',
    ];

    for (final uri in accepted) {
      expect(
        _isAllowedProductionUri(
          uri,
          sourcePath: source,
          productionRootPath: root,
          caseInsensitive: false,
        ),
        isTrue,
        reason: 'accepted URI: $uri',
      );
    }

    expect(
      _isAllowedProductionUri(
        'COMPONENTS/example.dart',
        sourcePath: source,
        productionRootPath: 'LIB/PRODUCTION',
        caseInsensitive: true,
      ),
      isTrue,
    );
  });

  test('directive guard rejects adversarial boundary escapes', () {
    const source = 'lib/production/production_app.dart';
    const root = 'lib/production';
    final rejected = <String>[
      'dart:io',
      'package:app/screens/home_screen.dart',
      '../screens/home_screen.dart',
      '../models/example.dart',
      '../operators/example.dart',
      'file:///temporary/example.dart',
      '/temporary/example.dart',
      'C:/temporary/example.dart',
      r'\\server\share\example.dart',
      '../../outside.dart',
      '../production_evil/example.dart',
      'https://example.invalid/example.dart',
      'package:flutter/../services.dart',
      'package:flutter/%2e%2e/services.dart',
      'package:flutter/material.dart?debug=true',
      'package:flutter/material.dart#fragment',
      r'package:flutter\material.dart',
      'components/%2e%2e/outside.dart',
      'components/%2Foutside.dart',
    ];

    for (final uri in rejected) {
      expect(
        _isAllowedProductionUri(
          uri,
          sourcePath: source,
          productionRootPath: root,
          caseInsensitive: false,
        ),
        isFalse,
        reason: 'rejected URI: $uri',
      );
    }

    final directives = _directives(
      "import 'dart:io';\n"
      "export '../models/example.dart';\n"
      "part '../operators/example.dart';\n"
      'part of example;\n',
    );
    expect(directives, <_SourceDirective>[
      const _SourceDirective('import', 'dart:io'),
      const _SourceDirective('export', '../models/example.dart'),
      const _SourceDirective('part', '../operators/example.dart'),
    ]);
  });

  test('directive parser captures every conditional alternative URI', () {
    final directives = _directives(
      "import 'base.dart' if (dart.library.io) '../io.dart' "
      "if (dart.library.html) 'package:app/web.dart';\n"
      "export 'base_export.dart' if (dart.library.io) '../io_export.dart';\n",
    );

    expect(directives, <_SourceDirective>[
      const _SourceDirective('import', 'base.dart'),
      const _SourceDirective('import', '../io.dart'),
      const _SourceDirective('import', 'package:app/web.dart'),
      const _SourceDirective('export', 'base_export.dart'),
      const _SourceDirective('export', '../io_export.dart'),
    ]);
  });

  test('directive parser supports comments between directive tokens', () {
    final directives = _directives(
      "import/* first */'one.dart';\n"
      "export // second\n 'two.dart';\n"
      "part/* third\n */'three.dart';\n"
      'part /* excluded */ of example;\n',
    );

    expect(directives, <_SourceDirective>[
      const _SourceDirective('import', 'one.dart'),
      const _SourceDirective('export', 'two.dart'),
      const _SourceDirective('part', 'three.dart'),
    ]);
  });

  test('directive parser ignores directive text in comments and strings', () {
    final directives = _directives(
      "// import '../comment.dart';\n"
      "/* export '../block.dart'; */\n"
      "const text = \"part '../string.dart';\";\n"
      "import 'allowed.dart';\n",
    );

    expect(directives, <_SourceDirective>[
      const _SourceDirective('import', 'allowed.dart'),
    ]);
  });

  test('directive parser fails closed for malformed directives', () {
    for (final source in <String>[
      'import;',
      "import 'unterminated.dart",
      "export 'missing_semicolon.dart'",
      "part 'valid.dart'; /* unterminated",
      "import 'base.dart' if (dart.library.io);",
    ]) {
      expect(() => _directives(source), throwsFormatException, reason: source);
    }
  });
  test('structural source exclusion is the boundary, not visual hiding', () {
    final productionSources = <File>[
      File('lib/main_production.dart'),
      ...Directory('lib/production')
          .listSync(recursive: true)
          .whereType<File>()
          .where((file) => file.path.endsWith('.dart')),
    ];
    final combined = productionSources
        .map((file) => file.readAsStringSync())
        .join('\n');
    final forbidden = <RegExp>[
      RegExp(r'\bBackendApiClient\b'),
      RegExp(r'\bHomeScreen\b'),
      RegExp(r'\bHistoryScreen\b'),
      RegExp(r'screens/'),
      RegExp(r'services/'),
      RegExp(r'operators/'),
      RegExp(r'widgets/'),
      RegExp(r'package:app/main\.dart'),
      RegExp(r'\bRT2EC\b', caseSensitive: false),
      RegExp(r'realtime', caseSensitive: false),
      RegExp(r'framework', caseSensitive: false),
      RegExp(r'developer', caseSensitive: false),
      RegExp(r'operator', caseSensitive: false),
      RegExp(r'demo', caseSensitive: false),
      RegExp(r'diagnostic', caseSensitive: false),
    ];

    for (final pattern in forbidden) {
      expect(
        pattern.hasMatch(combined),
        isFalse,
        reason: 'forbidden: $pattern',
      );
    }

    final mixedMain = File('lib/main.dart').readAsStringSync();
    expect(mixedMain, contains("import 'screens/home_screen.dart';"));
    expect(mixedMain, contains('HomeScreen('));
  });
}

List<_SourceDirective> _directives(String source) {
  final tokens = _tokenize(source);
  final directives = <_SourceDirective>[];

  for (var index = 0; index < tokens.length; index++) {
    final token = tokens[index];
    if (token.kind != _TokenKind.identifier ||
        !const <String>{'import', 'export', 'part'}.contains(token.value)) {
      continue;
    }

    final kind = token.value;
    var cursor = index + 1;
    if (kind == 'part' &&
        cursor < tokens.length &&
        tokens[cursor].kind == _TokenKind.identifier &&
        tokens[cursor].value == 'of') {
      continue;
    }
    if (cursor >= tokens.length || tokens[cursor].kind != _TokenKind.string) {
      throw FormatException('Malformed $kind directive');
    }

    final uris = <String>[tokens[cursor].value];
    cursor++;
    var terminated = false;
    while (cursor < tokens.length) {
      final current = tokens[cursor];
      if (current.kind == _TokenKind.symbol && current.value == ';') {
        terminated = true;
        break;
      }
      if (current.kind == _TokenKind.identifier && current.value == 'if') {
        cursor = _skipConditionalConfiguration(tokens, cursor + 1);
        if (cursor >= tokens.length ||
            tokens[cursor].kind != _TokenKind.string) {
          throw FormatException('Conditional $kind URI is missing');
        }
        uris.add(tokens[cursor].value);
      } else if (current.kind == _TokenKind.string) {
        throw FormatException('Unexpected string in $kind directive');
      }
      cursor++;
    }
    if (!terminated || uris.any((uri) => uri.isEmpty || uri.contains(r'$'))) {
      throw FormatException('Unterminated or invalid $kind directive');
    }

    directives.addAll(uris.map((uri) => _SourceDirective(kind, uri)));
    index = cursor;
  }
  return directives;
}

int _skipConditionalConfiguration(List<_Token> tokens, int cursor) {
  if (cursor >= tokens.length ||
      tokens[cursor].kind != _TokenKind.symbol ||
      tokens[cursor].value != '(') {
    throw const FormatException('Conditional directive is missing "("');
  }
  var depth = 0;
  for (; cursor < tokens.length; cursor++) {
    final token = tokens[cursor];
    if (token.kind == _TokenKind.symbol && token.value == '(') {
      depth++;
    } else if (token.kind == _TokenKind.symbol && token.value == ')') {
      depth--;
      if (depth == 0) {
        return cursor + 1;
      }
    } else if (token.kind == _TokenKind.symbol && token.value == ';') {
      break;
    }
  }
  throw const FormatException('Unterminated conditional directive');
}

List<_Token> _tokenize(String source) {
  final tokens = <_Token>[];
  var index = 0;
  while (index < source.length) {
    final code = source.codeUnitAt(index);
    if (_isWhitespace(code)) {
      index++;
      continue;
    }
    if (code == 0x2f && index + 1 < source.length) {
      final next = source.codeUnitAt(index + 1);
      if (next == 0x2f) {
        index += 2;
        while (index < source.length && source.codeUnitAt(index) != 0x0a) {
          index++;
        }
        continue;
      }
      if (next == 0x2a) {
        index += 2;
        var depth = 1;
        while (index < source.length && depth > 0) {
          if (index + 1 < source.length &&
              source.codeUnitAt(index) == 0x2f &&
              source.codeUnitAt(index + 1) == 0x2a) {
            depth++;
            index += 2;
          } else if (index + 1 < source.length &&
              source.codeUnitAt(index) == 0x2a &&
              source.codeUnitAt(index + 1) == 0x2f) {
            depth--;
            index += 2;
          } else {
            index++;
          }
        }
        if (depth != 0) {
          throw const FormatException('Unterminated block comment');
        }
        continue;
      }
    }
    if (_isIdentifierStart(code)) {
      final start = index++;
      while (index < source.length &&
          _isIdentifierPart(source.codeUnitAt(index))) {
        index++;
      }
      tokens.add(_Token(_TokenKind.identifier, source.substring(start, index)));
      continue;
    }
    if (code == 0x22 || code == 0x27) {
      final quote = code;
      final triple =
          index + 2 < source.length &&
          source.codeUnitAt(index + 1) == quote &&
          source.codeUnitAt(index + 2) == quote;
      index += triple ? 3 : 1;
      final value = StringBuffer();
      var terminated = false;
      while (index < source.length) {
        if (triple &&
            index + 2 < source.length &&
            source.codeUnitAt(index) == quote &&
            source.codeUnitAt(index + 1) == quote &&
            source.codeUnitAt(index + 2) == quote) {
          index += 3;
          terminated = true;
          break;
        }
        if (!triple && source.codeUnitAt(index) == quote) {
          index++;
          terminated = true;
          break;
        }
        if (source.codeUnitAt(index) == 0x5c) {
          if (index + 1 >= source.length) {
            break;
          }
          value
            ..writeCharCode(source.codeUnitAt(index))
            ..writeCharCode(source.codeUnitAt(index + 1));
          index += 2;
          continue;
        }
        value.writeCharCode(source.codeUnitAt(index++));
      }
      if (!terminated) {
        throw const FormatException('Unterminated string literal');
      }
      tokens.add(_Token(_TokenKind.string, value.toString()));
      continue;
    }
    tokens.add(_Token(_TokenKind.symbol, source[index]));
    index++;
  }
  return tokens;
}

bool _isWhitespace(int code) =>
    code == 0x20 || code == 0x09 || code == 0x0a || code == 0x0d;

bool _isIdentifierStart(int code) =>
    code == 0x5f ||
    code == 0x24 ||
    (code >= 0x41 && code <= 0x5a) ||
    (code >= 0x61 && code <= 0x7a);

bool _isIdentifierPart(int code) =>
    _isIdentifierStart(code) || (code >= 0x30 && code <= 0x39);

bool _isAllowedProductionUri(
  String directiveUri, {
  required String sourcePath,
  required String productionRootPath,
  required bool caseInsensitive,
}) {
  if (directiveUri.isEmpty ||
      directiveUri.contains(r'\') ||
      RegExp(r'%(?:2e|2f|5c)', caseSensitive: false).hasMatch(directiveUri)) {
    return false;
  }
  final parsed = Uri.tryParse(directiveUri);
  if (parsed == null ||
      parsed.hasAuthority ||
      parsed.hasQuery ||
      parsed.hasFragment ||
      parsed.path.isEmpty) {
    return false;
  }

  final uriSegments = _safeUriSegments(parsed);
  if (uriSegments == null) {
    return false;
  }
  if (parsed.scheme.isNotEmpty) {
    return parsed.scheme == 'package' &&
        uriSegments.length >= 2 &&
        uriSegments.first == 'flutter';
  }
  if (directiveUri.startsWith('/') ||
      directiveUri.startsWith('//') ||
      RegExp(r'^[A-Za-z]:').hasMatch(directiveUri)) {
    return false;
  }

  final sourceSegments = _normalizePath(sourcePath);
  final rootSegments = _normalizePath(productionRootPath);
  if (sourceSegments == null ||
      rootSegments == null ||
      sourceSegments.isEmpty) {
    return false;
  }
  final targetSegments = _resolvePathSegments(
    sourceSegments.sublist(0, sourceSegments.length - 1),
    uriSegments,
  );
  if (targetSegments == null || targetSegments.length < rootSegments.length) {
    return false;
  }
  for (var index = 0; index < rootSegments.length; index++) {
    final target = targetSegments[index];
    final root = rootSegments[index];
    if (caseInsensitive
        ? target.toLowerCase() != root.toLowerCase()
        : target != root) {
      return false;
    }
  }
  return true;
}

List<String>? _safeUriSegments(Uri uri) {
  final result = <String>[];
  for (final original in uri.pathSegments) {
    var segment = original;
    try {
      for (var pass = 0; pass < 2; pass++) {
        final decoded = Uri.decodeComponent(segment);
        if (decoded == segment) {
          break;
        }
        segment = decoded;
      }
    } on FormatException {
      return null;
    }
    if (segment.isEmpty ||
        segment == '.' ||
        segment == '..' ||
        segment.contains('/') ||
        segment.contains(r'\')) {
      return null;
    }
    result.add(segment);
  }
  return result;
}

List<String>? _normalizePath(String path) {
  final normalized = path.replaceAll(r'\', '/');
  final driveMatch = RegExp(r'^([A-Za-z]:)/').firstMatch(normalized);
  final base = driveMatch == null ? <String>[] : <String>[driveMatch.group(1)!];
  final remainder = driveMatch == null
      ? normalized
      : normalized.substring(driveMatch.end);
  return _resolvePathSegments(base, remainder.split('/'));
}

List<String>? _resolvePathSegments(
  List<String> base,
  Iterable<String> additions,
) {
  final result = List<String>.of(base);
  for (final segment in additions) {
    if (segment.isEmpty || segment == '.') {
      continue;
    }
    if (segment == '..') {
      if (result.isEmpty) {
        return null;
      }
      result.removeLast();
      continue;
    }
    result.add(segment);
  }
  return result;
}

enum _TokenKind { identifier, string, symbol }

class _Token {
  const _Token(this.kind, this.value);

  final _TokenKind kind;
  final String value;
}

class _SourceDirective {
  const _SourceDirective(this.kind, this.uri);

  final String kind;
  final String uri;

  @override
  bool operator ==(Object other) {
    return other is _SourceDirective && other.kind == kind && other.uri == uri;
  }

  @override
  int get hashCode => Object.hash(kind, uri);

  @override
  String toString() => '$kind $uri';
}
