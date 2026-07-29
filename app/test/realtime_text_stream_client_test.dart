import 'dart:async';
import 'dart:convert';

import 'package:app/models/realtime_text_stream.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('RealtimeTextStreamClient', () {
    test(
      'creates a session and parses incremental SSE to completion',
      () async {
        final client = _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: [
            _sseFrame(1, 'stream_started', _event(1, 'stream_started')),
            _sseFrame(
              2,
              'stream_chunk',
              _event(2, 'stream_chunk', chunkText: 'hello '),
            ),
            _sseFrame(
              3,
              'stream_chunk',
              _event(
                3,
                'stream_chunk',
                chunkText: 'world',
                outputCharCount: 11,
              ),
            ),
            _sseFrame(
              4,
              'stream_completed',
              _event(
                4,
                'stream_completed',
                terminalOutcome: 'completed',
                finalText: 'hello world',
              ),
            ),
          ],
        );
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: client,
        );

        final created = await streamClient.createSession(
          inputText: 'private input',
        );
        final events = await streamClient.streamEvents(created).toList();

        expect(client.requests[0].method, 'POST');
        expect(client.requests[0].url.path, '/realtime/text/sessions');
        expect(client.requests[1].method, 'GET');
        expect(
          client.requests[1].url.path,
          '/realtime/text/sessions/session-1/events',
        );
        expect(created.session.cancelMode, 'cooperative');
        expect(created.session.hardCancelSupported, isFalse);
        expect(events.map((event) => event.sequence), [1, 2, 3, 4]);
        expect(events[1].chunk!.text, 'hello ');
        expect(events[2].chunk!.text, 'world');
        expect(
          events.last.terminal!.outcome,
          RealtimeTextStreamTerminalOutcome.completed,
        );
        expect(events.toString(), isNot(contains('private input')));
      },
    );

    test('parses UTF-8 split across response chunks', () async {
      final frame = utf8.encode(
        _sseFrame(
          1,
          'stream_chunk',
          _event(1, 'stream_chunk', chunkText: 'hello 🙂'),
        ),
      );
      final client = _FakeSseHttpClient(
        createBody: _createResponse(),
        rawEventChunks: [
          frame.sublist(0, frame.length - 1),
          frame.sublist(frame.length - 1),
          utf8.encode(
            _sseFrame(
              2,
              'stream_completed',
              _event(
                2,
                'stream_completed',
                terminalOutcome: 'completed',
                finalText: 'hello 🙂',
              ),
            ),
          ),
        ],
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: client,
      );

      final created = await streamClient.createSession(inputText: 'input');
      final events = await streamClient.streamEvents(created).toList();

      expect(events.first.chunk!.text, 'hello 🙂');
    });

    test('parses multiple SSE frames in one response chunk', () async {
      final client = _FakeSseHttpClient(
        createBody: _createResponse(),
        eventChunks: [
          _sseFrame(1, 'stream_started', _event(1, 'stream_started')) +
              _sseFrame(
                2,
                'stream_completed',
                _event(2, 'stream_completed', terminalOutcome: 'completed'),
              ),
        ],
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: client,
      );

      final created = await streamClient.createSession(inputText: 'input');
      final events = await streamClient.streamEvents(created).toList();

      expect(events.length, 2);
      expect(
        events.last.terminal!.outcome,
        RealtimeTextStreamTerminalOutcome.completed,
      );
    });

    test(
      'parses chunk and event fields split across response chunks',
      () async {
        final frame = _sseFrame(
          1,
          'stream_chunk',
          _event(1, 'stream_chunk', chunkText: 'split'),
        );
        final client = _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: [
            frame.substring(0, 9),
            frame.substring(9),
            _sseFrame(
              2,
              'stream_completed',
              _event(
                2,
                'stream_completed',
                terminalOutcome: 'completed',
                finalText: 'split',
              ),
            ),
          ],
        );
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: client,
        );

        final created = await streamClient.createSession(inputText: 'input');
        final events = await streamClient.streamEvents(created).toList();

        expect(events.first.chunk!.text, 'split');
      },
    );

    test('parses cancelled and failed terminals', () async {
      final cancelledClient = _FakeSseHttpClient(
        createBody: _createResponse(),
        eventChunks: [
          _sseFrame(
            1,
            'stream_cancelled',
            _event(1, 'stream_cancelled', terminalOutcome: 'cancelled'),
          ),
        ],
      );
      final failedClient = _FakeSseHttpClient(
        createBody: _createResponse(),
        eventChunks: [
          _sseFrame(
            1,
            'stream_failed',
            _event(
              1,
              'stream_failed',
              terminalOutcome: 'failed',
              safeMessage: 'bounded safe error',
              publicErrorCode: 'stream_failed',
            ),
          ),
        ],
      );

      final cancelled = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: cancelledClient,
      );
      final failed = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: failedClient,
      );

      final cancelledEvents = await cancelled
          .streamEvents(await cancelled.createSession(inputText: 'input'))
          .toList();
      final failedEvents = await failed
          .streamEvents(await failed.createSession(inputText: 'input'))
          .toList();

      expect(
        cancelledEvents.single.terminal!.outcome,
        RealtimeTextStreamTerminalOutcome.cancelled,
      );
      expect(
        failedEvents.single.terminal!.outcome,
        RealtimeTextStreamTerminalOutcome.failed,
      );
      expect(failedEvents.single.terminal!.safeMessage, 'bounded safe error');
    });

    test('posts cooperative cancel path', () async {
      final client = _FakeSseHttpClient(
        createBody: _createResponse(),
        cancelBody: _cancelResponse(),
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local/',
        client: client,
      );

      final created = await streamClient.createSession(inputText: 'input');
      final cancelled = await streamClient.cancel(created);

      expect(client.requests.last.method, 'POST');
      expect(
        client.requests.last.url.path,
        '/realtime/text/sessions/session-1/cancel',
      );
      expect(cancelled.cancelMode, 'cooperative');
      expect(cancelled.hardCancelSupported, isFalse);
    });

    test('rejects cross-origin events and cancel paths', () async {
      for (final eventsPath in <String>[
        '//evil.example/events',
        'https://evil.example/events',
        'events',
        '/events#fragment',
      ]) {
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: _FakeSseHttpClient(createBody: _createResponse()),
        );
        final created = _createResponseObject(eventsPath: eventsPath);

        await expectLater(
          streamClient.streamEvents(created).toList(),
          throwsA(
            isA<RealtimeTextStreamProblemException>().having(
              (error) => error.problem.code,
              'code',
              'invalid_events_path',
            ),
          ),
        );
      }

      for (final cancelPath in <String>[
        '//evil.example/cancel',
        'https://evil.example/cancel',
      ]) {
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: _FakeSseHttpClient(createBody: _createResponse()),
        );
        final created = _createResponseObject(cancelPath: cancelPath);

        await expectLater(
          streamClient.cancel(created),
          throwsA(
            isA<RealtimeTextStreamProblemException>().having(
              (error) => error.problem.code,
              'code',
              'invalid_cancel_path',
            ),
          ),
        );
      }
    });

    test('maps stream HTTP errors without echoing input', () async {
      const inputText = 'do not echo stream error text';
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventsStatusCode: 503,
          eventChunks: [
            jsonEncode({
              'public_error_code': 'temporary_provider_outage',
              'safe_message': inputText,
              'retryable': true,
            }),
          ],
        ),
      );

      final created = await streamClient.createSession(inputText: inputText);

      await expectLater(
        streamClient.streamEvents(created).toList(),
        throwsA(
          isA<RealtimeTextStreamProblemException>()
              .having(
                (error) => error.problem.code,
                'code',
                'stream_http_error',
              )
              .having((error) => error.problem.retryable, 'retryable', true)
              .having(
                (error) => error.problem.message.contains(inputText),
                'message contains input',
                isFalse,
              ),
        ),
      );
    });

    test('handles CRLF boundary split without cutting an id-only frame', () async {
      final firstFrame =
          'id: 1\r\n'
          'event: stream_started\r\n'
          'data: ${jsonEncode(_event(1, 'stream_started'))}\r\n'
          '\r\n';
      final secondFrame =
          'id: 2\r\n'
          'event: stream_chunk\r\n'
          'data: ${jsonEncode(_event(2, 'stream_chunk', chunkText: 'ok'))}\r\n'
          '\r\n';
      final thirdFrame =
          'id: 3\r\n'
          'event: stream_completed\r\n'
          'data: ${jsonEncode(_event(3, 'stream_completed', terminalOutcome: 'completed', finalText: 'ok'))}\r\n'
          '\r\n';
      final client = _FakeSseHttpClient(
        createBody: _createResponse(),
        eventChunks: <String>[
          firstFrame + secondFrame.substring(0, secondFrame.indexOf('\n')),
          secondFrame.substring(secondFrame.indexOf('\n')) + thirdFrame,
        ],
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: client,
      );

      final events = await streamClient
          .streamEvents(await streamClient.createSession(inputText: 'input'))
          .toList();

      expect(events.map((event) => event.sequence), <int>[1, 2, 3]);
      expect(events[1].chunk!.text, 'ok');
    });

    test('rejects malformed JSON and missing sequence', () async {
      final malformed = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: ['id: 1\nevent: stream_chunk\ndata: {bad\n\n'],
        ),
      );
      final missingSequence = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: [
            'event: stream_chunk\ndata: ${jsonEncode(_event(1, 'stream_chunk'))}\n\n',
          ],
        ),
      );

      await expectLater(
        malformed
            .streamEvents(await malformed.createSession(inputText: 'input'))
            .toList(),
        throwsA(isA<RealtimeTextStreamProblemException>()),
      );
      await expectLater(
        missingSequence
            .streamEvents(
              await missingSequence.createSession(inputText: 'input'),
            )
            .toList(),
        throwsA(isA<RealtimeTextStreamProblemException>()),
      );
    });

    test(
      'rejects event payload, state, and terminal outcome mismatches',
      () async {
        final cases = <Map<String, Object?>>[
          _event(1, 'stream_started', chunkText: 'unexpected'),
          _event(1, 'stream_chunk', state: 'cancel_requested', chunkText: 'x'),
          _event(1, 'cancel_requested', state: 'streaming'),
          _event(1, 'stream_completed', terminalOutcome: 'failed'),
          _event(1, 'stream_cancelled', terminalOutcome: 'completed'),
          _event(1, 'stream_failed', terminalOutcome: 'closed'),
          _event(1, 'stream_closed', terminalOutcome: 'failed'),
          _event(1, 'stream_chunk', chunkText: 'x', terminalOutcome: 'failed'),
          _event(1, 'stream_chunk')..['turn_id'] = null,
        ];

        for (final event in cases) {
          final streamClient = RealtimeTextStreamClient(
            baseUrl: 'http://backend.local',
            client: _FakeSseHttpClient(
              createBody: _createResponse(),
              eventChunks: <String>[
                _sseFrame(1, event['event_type']! as String, event),
              ],
            ),
          );

          await expectLater(
            streamClient
                .streamEvents(
                  await streamClient.createSession(inputText: 'input'),
                )
                .toList(),
            throwsA(isA<RealtimeTextStreamProblemException>()),
          );
        }
      },
    );

    test('rejects duplicate or out-of-order sequence', () async {
      final client = _FakeSseHttpClient(
        createBody: _createResponse(),
        eventChunks: [
          _sseFrame(1, 'stream_started', _event(1, 'stream_started')),
          _sseFrame(
            1,
            'stream_chunk',
            _event(1, 'stream_chunk', chunkText: 'dup'),
          ),
        ],
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: client,
      );

      await expectLater(
        streamClient
            .streamEvents(await streamClient.createSession(inputText: 'input'))
            .toList(),
        throwsA(
          isA<RealtimeTextStreamProblemException>().having(
            (error) => error.problem.code,
            'code',
            'out_of_order_stream_event',
          ),
        ),
      );
    });

    test(
      'uses Unicode code point limits for chunks output and messages',
      () async {
        final emoji512 = List<String>.filled(512, '\u{1F642}').join();
        final emoji513 = '$emoji512\u{1F642}';
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: _FakeSseHttpClient(
            createBody: _createResponse(),
            eventChunks: <String>[
              _sseFrame(
                1,
                'stream_chunk',
                _event(1, 'stream_chunk', chunkText: emoji512),
              ),
              _sseFrame(
                2,
                'stream_completed',
                _event(
                  2,
                  'stream_completed',
                  terminalOutcome: 'completed',
                  finalText: emoji512,
                ),
              ),
            ],
          ),
        );
        final oversized = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: _FakeSseHttpClient(
            createBody: _createResponse(),
            eventChunks: <String>[
              _sseFrame(
                1,
                'stream_chunk',
                _event(1, 'stream_chunk', chunkText: emoji513),
              ),
            ],
          ),
        );
        final problem = RealtimeTextStreamProblem.fromJson(<String, Object?>{
          'code': 'safe',
          'message': List<String>.filled(241, '\u{1F642}').join(),
          'retryable': true,
        });

        final events = await streamClient
            .streamEvents(await streamClient.createSession(inputText: 'input'))
            .toList();

        expect(events.first.chunk!.text.runes.length, 512);
        expect(problem.message.runes.length, 240);
        expect(problem.message.endsWith('\u{1F642}'), isTrue);
        await expectLater(
          oversized
              .streamEvents(await oversized.createSession(inputText: 'input'))
              .toList(),
          throwsA(isA<RealtimeTextStreamProblemException>()),
        );
      },
    );

    test('rejects oversized chunk and output', () async {
      final oversizedChunk = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: [
            _sseFrame(
              1,
              'stream_chunk',
              _event(
                1,
                'stream_chunk',
                chunkText: List<String>.filled(513, 'x').join(),
              ),
            ),
          ],
        ),
      );
      final outputOverflow = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: [
            for (var index = 1; index <= 9; index += 1)
              _sseFrame(
                index,
                'stream_chunk',
                _event(
                  index,
                  'stream_chunk',
                  chunkText: List<String>.filled(512, 'x').join(),
                  outputCharCount: index * 512,
                ),
              ),
          ],
        ),
      );

      await expectLater(
        oversizedChunk
            .streamEvents(
              await oversizedChunk.createSession(inputText: 'input'),
            )
            .toList(),
        throwsA(isA<RealtimeTextStreamProblemException>()),
      );
      await expectLater(
        outputOverflow
            .streamEvents(
              await outputOverflow.createSession(inputText: 'input'),
            )
            .toList(),
        throwsA(
          isA<RealtimeTextStreamProblemException>().having(
            (error) => error.problem.code,
            'code',
            'output_limit_exceeded',
          ),
        ),
      );
    });

    test('rejects inconsistent create and terminal responses', () async {
      for (final body in <String>[
        _createResponse(accepted: false),
        _createResponse(turnSessionId: 'session-2'),
        _createResponse(activeTurnId: 'turn-2'),
      ]) {
        final streamClient = RealtimeTextStreamClient(
          baseUrl: 'http://backend.local',
          client: _FakeSseHttpClient(createBody: body),
        );

        await expectLater(
          streamClient.createSession(inputText: 'input'),
          throwsA(isA<RealtimeTextStreamProblemException>()),
        );
      }

      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: _FakeSseHttpClient(
          createBody: _createResponse(),
          eventChunks: <String>[
            _sseFrame(
              1,
              'stream_chunk',
              _event(1, 'stream_chunk', chunkText: 'hello'),
            ),
            _sseFrame(
              2,
              'stream_completed',
              _event(
                2,
                'stream_completed',
                terminalOutcome: 'completed',
                finalText: 'different',
                outputCharCount: 5,
              ),
            ),
          ],
        ),
      );

      await expectLater(
        streamClient
            .streamEvents(await streamClient.createSession(inputText: 'input'))
            .toList(),
        throwsA(
          isA<RealtimeTextStreamProblemException>().having(
            (error) => error.problem.code,
            'code',
            'mismatched_terminal_final_text',
          ),
        ),
      );
    });

    test(
      'rejects terminal final text and count mismatches for all outcomes',
      () async {
        for (final entry in <String, String>{
          'stream_cancelled': 'cancelled',
          'stream_failed': 'failed',
          'stream_closed': 'closed',
        }.entries) {
          final streamClient = RealtimeTextStreamClient(
            baseUrl: 'http://backend.local',
            client: _FakeSseHttpClient(
              createBody: _createResponse(),
              eventChunks: <String>[
                _sseFrame(
                  1,
                  'stream_chunk',
                  _event(1, 'stream_chunk', chunkText: 'hello'),
                ),
                _sseFrame(
                  2,
                  entry.key,
                  _event(
                    2,
                    entry.key,
                    terminalOutcome: entry.value,
                    finalText: 'different',
                    outputCharCount: 5,
                  ),
                ),
              ],
            ),
          );

          await expectLater(
            streamClient
                .streamEvents(
                  await streamClient.createSession(inputText: 'input'),
                )
                .toList(),
            throwsA(
              isA<RealtimeTextStreamProblemException>().having(
                (error) => error.problem.code,
                'code',
                'mismatched_terminal_final_text',
              ),
            ),
          );
        }

        for (final terminal in <Map<String, Object?>>[
          _event(
            2,
            'stream_completed',
            terminalOutcome: 'completed',
            finalText: '',
            outputCharCount: 5,
          ),
          _event(
            2,
            'stream_completed',
            terminalOutcome: 'completed',
            finalText: 'hello',
            outputCharCount: 4,
          ),
        ]) {
          final streamClient = RealtimeTextStreamClient(
            baseUrl: 'http://backend.local',
            client: _FakeSseHttpClient(
              createBody: _createResponse(),
              eventChunks: <String>[
                _sseFrame(
                  1,
                  'stream_chunk',
                  _event(1, 'stream_chunk', chunkText: 'hello'),
                ),
                _sseFrame(2, terminal['event_type']! as String, terminal),
              ],
            ),
          );

          await expectLater(
            streamClient
                .streamEvents(
                  await streamClient.createSession(inputText: 'input'),
                )
                .toList(),
            throwsA(isA<RealtimeTextStreamProblemException>()),
          );
        }
      },
    );

    test('does not echo input text from public errors', () async {
      final privateInput = 'private input must not echo';
      final client = _FakeSseHttpClient(
        createStatusCode: 500,
        createBody: jsonEncode(<String, Object?>{
          'detail': <String, Object?>{
            'code': 'backend_failed',
            'message': privateInput,
            'retryable': true,
          },
        }),
      );
      final streamClient = RealtimeTextStreamClient(
        baseUrl: 'http://backend.local',
        client: client,
      );

      try {
        await streamClient.createSession(inputText: privateInput);
        fail('createSession should fail');
      } on RealtimeTextStreamProblemException catch (error) {
        expect(error.problem.code, 'backend_failed');
        expect(error.problem.message, isNot(contains(privateInput)));
      }
    });
  });
}

RealtimeTextStreamCreateResponse _createResponseObject({
  String eventsPath = '/realtime/text/sessions/session-1/events',
  String cancelPath = '/realtime/text/sessions/session-1/cancel',
}) {
  return RealtimeTextStreamCreateResponse(
    accepted: true,
    session: const RealtimeTextStreamSession(
      sessionId: 'session-1',
      state: RealtimeTextStreamState.streaming,
      activeTurnId: 'turn-1',
      lastSequence: 1,
      isClosed: false,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
    ),
    turn: const RealtimeTextStreamTurn(
      sessionId: 'session-1',
      turnId: 'turn-1',
      state: RealtimeTextStreamState.streaming,
      chunkCount: 0,
      outputCharCount: 0,
      cancelRequested: false,
      terminalOutcome: null,
    ),
    eventsPath: eventsPath,
    cancelPath: cancelPath,
    idleTtlSeconds: 120,
    maxDurationSeconds: 60,
    maxPendingEvents: 32,
    maxEventBytes: 32768,
  );
}

String _createResponse({
  bool accepted = true,
  String eventsPath = '/realtime/text/sessions/session-1/events',
  String cancelPath = '/realtime/text/sessions/session-1/cancel',
  String sessionId = 'session-1',
  String activeTurnId = 'turn-1',
  String turnSessionId = 'session-1',
  String turnId = 'turn-1',
}) {
  return jsonEncode(<String, Object?>{
    'schema_version': 'drc.v3.realtime-text-stream-create.1',
    'accepted': accepted,
    'session': <String, Object?>{
      'schema_version': 'drc.v3.realtime-text-stream-session.1',
      'session_id': sessionId,
      'state': 'streaming',
      'active_turn_id': activeTurnId,
      'last_sequence': 1,
      'is_closed': false,
      'cancel_mode': 'cooperative',
      'hard_cancel_supported': false,
    },
    'turn': <String, Object?>{
      'schema_version': 'drc.v3.realtime-text-stream-turn.1',
      'session_id': turnSessionId,
      'turn_id': turnId,
      'state': 'streaming',
      'chunk_count': 0,
      'output_char_count': 0,
      'cancel_requested': false,
      'terminal_outcome': null,
    },
    'events_path': eventsPath,
    'cancel_path': cancelPath,
    'idle_ttl_seconds': 120,
    'max_duration_seconds': 60,
    'max_pending_events': 32,
    'max_event_bytes': 32768,
  });
}

String _cancelResponse() {
  return jsonEncode(<String, Object?>{
    'schema_version': 'drc.v3.realtime-text-stream-cancel.1',
    'accepted': true,
    'session_id': 'session-1',
    'turn_id': 'turn-1',
    'state': 'cancelled',
    'cancel_mode': 'cooperative',
    'hard_cancel_supported': false,
    'terminal': true,
    'safe_message': 'cancelled',
  });
}

Map<String, Object?> _event(
  int sequence,
  String eventType, {
  String? chunkText,
  String? terminalOutcome,
  String? finalText,
  int? outputCharCount,
  String? state,
  String safeMessage = '',
  String? publicErrorCode,
}) {
  final resolvedFinalText = finalText ?? '';
  final outputText = resolvedFinalText.isNotEmpty
      ? resolvedFinalText
      : (chunkText ?? '');
  return <String, Object?>{
    'schema_version': 'drc.v3.realtime-text-stream-event.1',
    'event_type': eventType,
    'session_id': 'session-1',
    'turn_id': 'turn-1',
    'sequence': sequence,
    'state':
        state ??
        terminalOutcome ??
        (eventType == 'cancel_requested' ? 'cancel_requested' : 'streaming'),
    'chunk': chunkText == null
        ? null
        : <String, Object?>{
            'schema_version': 'drc.v3.realtime-text-stream-chunk.1',
            'sequence': sequence,
            'text': chunkText,
            'output_char_count': outputCharCount ?? chunkText.runes.length,
          },
    'terminal': terminalOutcome == null
        ? null
        : <String, Object?>{
            'schema_version': 'drc.v3.realtime-text-stream-terminal.1',
            'sequence': sequence,
            'outcome': terminalOutcome,
            'final_text': resolvedFinalText,
            'output_char_count': outputCharCount ?? outputText.runes.length,
            'public_error_code': publicErrorCode,
            'safe_message': safeMessage,
            'retryable': terminalOutcome == 'failed',
          },
    'safe_message': safeMessage,
  };
}

String _sseFrame(int id, String eventName, Map<String, Object?> data) {
  return 'id: $id\nevent: $eventName\ndata: ${jsonEncode(data)}\n\n';
}

class _FakeSseHttpClient extends http.BaseClient {
  _FakeSseHttpClient({
    required this.createBody,
    this.cancelBody,
    this.eventChunks = const <String>[],
    this.rawEventChunks,
    this.createStatusCode = 201,
    this.eventsStatusCode = 200,
  });

  final String createBody;
  final String? cancelBody;
  final List<String> eventChunks;
  final List<List<int>>? rawEventChunks;
  final int createStatusCode;
  final int eventsStatusCode;
  final List<http.BaseRequest> requests = <http.BaseRequest>[];

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    requests.add(request);
    if (request.method == 'POST' && request.url.path.endsWith('/sessions')) {
      await request.finalize().drain<void>();
      return http.StreamedResponse(
        Stream<List<int>>.value(utf8.encode(createBody)),
        createStatusCode,
      );
    }
    if (request.method == 'POST' && request.url.path.endsWith('/cancel')) {
      await request.finalize().drain<void>();
      return http.StreamedResponse(
        Stream<List<int>>.value(utf8.encode(cancelBody ?? _cancelResponse())),
        200,
      );
    }
    if (request.method == 'GET' && request.url.path.endsWith('/events')) {
      return http.StreamedResponse(
        Stream<List<int>>.fromIterable(
          rawEventChunks ?? eventChunks.map(utf8.encode),
        ),
        eventsStatusCode,
        headers: const <String, String>{'content-type': 'text/event-stream'},
      );
    }
    return http.StreamedResponse(Stream<List<int>>.empty(), 404);
  }
}
