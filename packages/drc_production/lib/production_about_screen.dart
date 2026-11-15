import 'package:flutter/material.dart';

class ProductionAboutScreen extends StatelessWidget {
  const ProductionAboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('アプリについて')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      'Daily Rhythm Companion',
                      style: theme.textTheme.headlineSmall,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'このベータ版では、気分とキャラクターを選ぶと、'
                    '端末内で今日のアドバイスを表示します。',
                  ),
                  const SizedBox(height: 12),
                  const Text('選択内容は保存されません。'),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
