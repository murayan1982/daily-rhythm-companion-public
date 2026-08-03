import 'package:flutter/material.dart';

import '../models/framework_vts_motion_presentation.dart';

class FrameworkVtsMotionPresentationPanel extends StatelessWidget {
  const FrameworkVtsMotionPresentationPanel({
    super.key,
    required this.configuration,
    required this.optedIn,
    required this.selectedIntent,
    required this.selectorValue,
    required this.state,
    required this.canToggleOptIn,
    required this.canApply,
    required this.canReset,
    required this.onOptInChanged,
    required this.onIntentChanged,
    required this.onSelectorChanged,
    required this.onApply,
    required this.onReset,
  });

  final String configuration;
  final bool optedIn;
  final FrameworkVtsMotionIntent selectedIntent;
  final String selectorValue;
  final FrameworkVtsMotionPresentationState? state;
  final bool canToggleOptIn;
  final bool canApply;
  final bool canReset;
  final ValueChanged<bool> onOptInChanged;
  final ValueChanged<FrameworkVtsMotionIntent?> onIntentChanged;
  final ValueChanged<String> onSelectorChanged;
  final VoidCallback onApply;
  final VoidCallback onReset;

  @override
  Widget build(BuildContext context) {
    final result = state?.result;
    final problem = state?.problem;
    final first = result?.commandResults.isEmpty == false
        ? result!.commandResults.first
        : null;
    return Column(
      key: const ValueKey('framework-vts-motion-presentation-section'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Configured VTS Motion',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'RT-7d manual-only VTube Studio boundary. It is off by default and sends one command only after explicit Apply.',
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SwitchListTile(
                key: const ValueKey('framework-vts-motion-opt-in'),
                contentPadding: EdgeInsets.zero,
                value: optedIn,
                onChanged: canToggleOptIn ? onOptInChanged : null,
                title: const Text('Enable manual configured VTS motion'),
                subtitle: const Text(
                  'Session-local and not persisted. Toggling does not call Backend, Framework, VTS, provider, or network.',
                ),
              ),
              DropdownButtonFormField<FrameworkVtsMotionIntent>(
                key: const ValueKey('framework-vts-motion-intent'),
                initialValue: selectedIntent,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Intent',
                ),
                items: FrameworkVtsMotionIntent.values
                    .map(
                      (item) => DropdownMenuItem(
                        value: item,
                        child: Text(item.wireName),
                      ),
                    )
                    .toList(growable: false),
                onChanged: optedIn ? onIntentChanged : null,
              ),
              if (optedIn && selectedIntent.requiresSelector) ...[
                const SizedBox(height: 12),
                TextFormField(
                  key: const ValueKey('framework-vts-motion-selector'),
                  initialValue: selectorValue,
                  maxLength: frameworkVtsMotionMaxIdChars,
                  onChanged: optedIn ? onSelectorChanged : null,
                  decoration: InputDecoration(
                    border: const OutlineInputBorder(),
                    labelText: '${selectedIntent.wireName} value',
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                children: [
                  ElevatedButton(
                    key: const ValueKey('framework-vts-motion-apply-button'),
                    onPressed: canApply ? onApply : null,
                    child: const Text('Apply one VTS command'),
                  ),
                  OutlinedButton(
                    key: const ValueKey('framework-vts-motion-reset-button'),
                    onPressed: canReset ? onReset : null,
                    child: const Text('Reset local state'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _row(
                'framework-vts-motion-configuration',
                'Configuration',
                configuration,
              ),
              _row(
                'framework-vts-motion-opt-in-status',
                'Opt-in',
                optedIn ? 'on' : 'off',
              ),
              _row(
                'framework-vts-motion-selected-intent',
                'Intent',
                selectedIntent.wireName,
              ),
              _row(
                'framework-vts-motion-phase',
                'Phase',
                state?.phase.name ?? 'unconfigured',
              ),
              _row(
                'framework-vts-motion-status',
                'Status',
                result?.status.wireName ?? '-',
              ),
              _row(
                'framework-vts-motion-reason-code',
                'Reason',
                result?.reasonCode ?? problem?.code ?? '-',
              ),
              _row(
                'framework-vts-motion-safe-message',
                'Safe message',
                _message(result?.safeMessage, problem?.message),
              ),
              _row(
                'framework-vts-motion-commands-requested',
                'Commands requested',
                '${result?.commandsRequested ?? 0}',
              ),
              _row(
                'framework-vts-motion-commands-applied',
                'Commands applied',
                '${result?.commandsApplied ?? 0}',
              ),
              _row(
                'framework-vts-motion-commands-completed',
                'Commands completed',
                '${result?.commandsCompleted ?? 0}',
              ),
              _row(
                'framework-vts-motion-optional-skips',
                'Optional skips',
                '${result?.optionalCommandsSkipped ?? 0}',
              ),
              _row(
                'framework-vts-motion-command-outcome',
                'Command outcome',
                first?.outcome ?? '-',
              ),
              _row(
                'framework-vts-motion-command-state',
                'Command state',
                first?.state ?? '-',
              ),
              _row(
                'framework-vts-motion-framework-import',
                'Framework import attempted',
                '${result?.frameworkImportAttempted ?? false}',
              ),
              _row(
                'framework-vts-motion-session-created',
                'Session created',
                '${result?.sessionCreated ?? false}',
              ),
              _row(
                'framework-vts-motion-session-closed',
                'Session closed',
                '${result?.sessionClosed ?? false}',
              ),
              _row(
                'framework-vts-motion-provider-attempted',
                'Provider attempted',
                '${result?.providerExecutionAttempted ?? false}',
              ),
              _row(
                'framework-vts-motion-network-attempted',
                'Network attempted',
                '${result?.networkExecutionAttempted ?? false}',
              ),
              _row(
                'framework-vts-motion-real-motion',
                'Real motion executed',
                '${result?.realMotionExecuted ?? false}',
              ),
              const SizedBox(height: 8),
              const Text(
                'Private endpoint, token, hotkey IDs, provider payloads, response JSON, raw exceptions, and private paths are never displayed.',
                key: ValueKey('framework-vts-motion-privacy-note'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  static Widget _row(String key, String label, String value) => Padding(
    key: ValueKey(key),
    padding: const EdgeInsets.only(bottom: 4),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 190,
          child: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
        Expanded(child: Text(value.trim().isEmpty ? '-' : value)),
      ],
    ),
  );

  static String _message(String? result, String? problem) {
    final first = result?.trim() ?? '';
    if (first.isNotEmpty) return first;
    final second = problem?.trim() ?? '';
    return second.isEmpty ? '-' : second;
  }
}
