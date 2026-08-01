import 'package:flutter/material.dart';

import '../models/character_motion_presentation.dart';

class CharacterMotionPresentationPanel extends StatelessWidget {
  const CharacterMotionPresentationPanel({
    super.key,
    required this.configuration,
    required this.optedIn,
    required this.selectedFact,
    required this.state,
    required this.canToggleOptIn,
    required this.canApply,
    required this.canReset,
    required this.onOptInChanged,
    required this.onFactChanged,
    required this.onApply,
    required this.onReset,
  });

  final String configuration;
  final bool optedIn;
  final CharacterMotionLifecycleFact selectedFact;
  final CharacterMotionPresentationState? state;
  final bool canToggleOptIn;
  final bool canApply;
  final bool canReset;
  final ValueChanged<bool> onOptInChanged;
  final ValueChanged<CharacterMotionLifecycleFact?> onFactChanged;
  final VoidCallback onApply;
  final VoidCallback onReset;

  @override
  Widget build(BuildContext context) {
    final presentationState = state;
    final result = presentationState?.result;
    final problem = presentationState?.problem;

    return Column(
      key: const ValueKey('character-motion-presentation-section'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Character Motion Presentation',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'RT-6 normalized mock-motion presentation. It is session-local, off by default, and applies only after an explicit action.',
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
                key: const ValueKey('character-motion-opt-in'),
                contentPadding: EdgeInsets.zero,
                value: optedIn,
                onChanged: canToggleOptIn ? onOptInChanged : null,
                title: const Text('Enable character motion presentation'),
                subtitle: const Text(
                  'Off by default and not persisted. Toggling alone does not call a transport, Backend, Framework, provider, VTS, or Live2D runtime.',
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<CharacterMotionLifecycleFact>(
                key: const ValueKey('character-motion-lifecycle-fact'),
                initialValue: selectedFact,
                isExpanded: true,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Lifecycle fact',
                ),
                items: CharacterMotionLifecycleFact.values
                    .map(
                      (fact) => DropdownMenuItem(
                        value: fact,
                        child: Text(fact.wireName),
                      ),
                    )
                    .toList(growable: false),
                onChanged: optedIn ? onFactChanged : null,
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 8,
                children: [
                  ElevatedButton(
                    key: const ValueKey('character-motion-apply-button'),
                    onPressed: canApply ? onApply : null,
                    child: const Text('Apply selected lifecycle fact'),
                  ),
                  OutlinedButton(
                    key: const ValueKey('character-motion-reset-button'),
                    onPressed: canReset ? onReset : null,
                    child: const Text('Reset presentation'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _DetailRow(
                key: const ValueKey('character-motion-configuration'),
                label: 'Configuration',
                value: configuration,
              ),
              _DetailRow(
                key: const ValueKey('character-motion-opt-in-status'),
                label: 'Opt-in',
                value: optedIn ? 'on' : 'off',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-selected-fact'),
                label: 'Selected fact',
                value: selectedFact.wireName,
              ),
              _DetailRow(
                key: const ValueKey('character-motion-phase'),
                label: 'Presentation phase',
                value: presentationState?.phase.name ?? 'unconfigured',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-execution-status'),
                label: 'Execution status',
                value: result?.status.wireName ?? '-',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-cue'),
                label: 'Cue',
                value: result?.cue?.wireName ?? '-',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-commands-requested'),
                label: 'Commands requested',
                value: '${result?.commandsRequested ?? 0}',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-commands-completed'),
                label: 'Commands completed',
                value: '${result?.commandsCompleted ?? 0}',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-event-type-count'),
                label: 'Event type count',
                value: '${result?.eventTypes.length ?? 0}',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-adapter'),
                label: 'Adapter',
                value: result?.adapter ?? 'mock',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-real-adapter-enabled'),
                label: 'Real adapter enabled',
                value: '${result?.realAdapterEnabled ?? false}',
              ),
              _DetailRow(
                key: const ValueKey(
                  'character-motion-provider-execution-attempted',
                ),
                label: 'Provider attempted',
                value: '${result?.providerExecutionAttempted ?? false}',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-network-execution'),
                label: 'Network execution',
                value: '${result?.networkExecution ?? false}',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-reason-code'),
                label: 'Reason code',
                value: result?.reasonCode ?? problem?.code ?? '-',
              ),
              _DetailRow(
                key: const ValueKey('character-motion-safe-message'),
                label: 'Safe message',
                value: _safeMessage(result?.safeMessage, problem?.message),
              ),
              const SizedBox(height: 12),
              const Text(
                'Normalized mock motion state only. The repository character image remains static. No Live2D / VTS animation is executed.',
                key: ValueKey('character-motion-static-safety-note'),
              ),
              const SizedBox(height: 4),
              const Text(
                'This panel does not display source event, session, turn, character, Framework, command, or provider identifiers; raw command results; event strings; response JSON; paths; credentials; payloads; or raw exceptions.',
                key: ValueKey('character-motion-privacy-note'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  static String _safeMessage(String? resultMessage, String? problemMessage) {
    final result = resultMessage?.trim() ?? '';
    if (result.isNotEmpty) {
      return result;
    }
    final problem = problemMessage?.trim() ?? '';
    return problem.isEmpty ? '-' : problem;
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({super.key, required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 176,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(child: Text(value.trim().isEmpty ? '-' : value)),
        ],
      ),
    );
  }
}
