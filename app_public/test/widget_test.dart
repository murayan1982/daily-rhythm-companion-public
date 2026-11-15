import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/production_app.dart';
import 'package:drc_public_app/main.dart' as public_app;

void main() {
  testWidgets('main starts the shared production application', (tester) async {
    public_app.main();
    await tester.pump();

    expect(find.byType(ProductionApp), findsOneWidget);
    expect(find.text('Daily Rhythm Companion'), findsOneWidget);
    expect(find.text('今日のリズム'), findsOneWidget);
    expect(
      find.text('気分とキャラクターを選ぶと、端末内で今日のアドバイスを表示します。選択内容は保存されません。'),
      findsOneWidget,
    );
  });
}
