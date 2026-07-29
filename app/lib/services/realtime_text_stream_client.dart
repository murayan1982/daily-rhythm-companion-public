import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/realtime_text_stream.dart';

class RealtimeTextStreamClient {
  RealtimeTextStreamClient({
    required String baseUrl,
    required http.Client client,
    this.maximumSseEventBytes = 32768,
  }) : _baseUri = Uri.parse(baseUrl.endsWith('/') ? baseUrl : '$baseUrl/'),
       _client = client;

  final Uri _baseUri;
  final http.Client _client;
  final int maximumSseEventBytes;

  Future<RealtimeTextStreamCreateResponse> createSession({
    required String inputText,
  }) async {
    final request =
        http.Request('POST', _baseUri.resolve('realtime/text/sessions'))
          ..headers['content-type'] = 'application/json; charset=utf-8'
          ..body = jsonEncode(<String, Object?>{'input_text': inputText});

    final response = await _client.send(request);
    final body = await utf8.decodeStream(response.stream);
    if (response.statusCode != 201) {
      throw RealtimeTextStreamProblemException(_problemFromBody(body));
    }
    try {
      final decoded = jsonDecode(body);
      return RealtimeTextStreamCreateResponse.fromJson(
        _asMap(decoded, 'invalid_create_response'),
      );
    } on RealtimeTextStreamProblemException {
      rethrow;
    } catch (_) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'invalid_create_response',
          message: 'The stream create response was invalid.',
          retryable: true,
        ),
      );
    }
  }

  Stream<RealtimeTextStreamEvent> streamEvents(
    RealtimeTextStreamCreateResponse createResponse,
  ) async* {
    final request = http.Request(
      'GET',
      _resolveSameOriginPath(createResponse.eventsPath, 'invalid_events_path'),
    );
    final response = await _client.send(request);
    if (response.statusCode != 200) {
      final body = await utf8.decodeStream(response.stream);
      throw RealtimeTextStreamProblemException(_problemFromBody(body));
    }

    var buffer = '';
    var lastSequence = 0;
    var outputCharCount = 0;
    var outputText = '';

    await for (final decodedChunk in response.stream.transform(utf8.decoder)) {
      buffer += decodedChunk;
      while (true) {
        final boundary = _findSseFrameBoundary(buffer);
        if (boundary == null) {
          if (utf8.encode(buffer).length > maximumSseEventBytes) {
            throw const RealtimeTextStreamProblemException(
              RealtimeTextStreamProblem(
                code: 'stream_event_bytes_exceeded',
                message:
                    'A text-stream event exceeded the configured byte limit.',
                retryable: false,
              ),
            );
          }
          break;
        }
        final frameText = buffer
            .substring(0, boundary.start)
            .replaceAll('\r\n', '\n')
            .replaceAll('\r', '\n');
        buffer = buffer.substring(boundary.end);
        if (frameText.trim().isEmpty) {
          continue;
        }
        if (utf8.encode(frameText).length > maximumSseEventBytes) {
          throw const RealtimeTextStreamProblemException(
            RealtimeTextStreamProblem(
              code: 'stream_event_bytes_exceeded',
              message:
                  'A text-stream event exceeded the configured byte limit.',
              retryable: false,
            ),
          );
        }
        final parsed = _parseSseFrame(frameText);
        final event = _eventFromFrame(parsed);
        _validateEvent(
          event: event,
          frame: parsed,
          createResponse: createResponse,
          expectedNextSequence: lastSequence + 1,
          outputCharCount: outputCharCount,
          outputText: outputText,
        );
        lastSequence = event.sequence;
        final chunk = event.chunk;
        if (chunk != null) {
          outputText += chunk.text;
          outputCharCount = _codePointCount(outputText);
        }
        yield event;
        if (event.isTerminal) {
          return;
        }
      }
    }

    if (buffer.trim().isNotEmpty) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'incomplete_sse_frame',
          message: 'The text-stream event frame ended before it was complete.',
          retryable: true,
        ),
      );
    }
  }

  Future<RealtimeTextStreamCancelResponse> cancel(
    RealtimeTextStreamCreateResponse createResponse,
  ) async {
    final request = http.Request(
      'POST',
      _resolveSameOriginPath(createResponse.cancelPath, 'invalid_cancel_path'),
    );
    final response = await _client.send(request);
    final body = await utf8.decodeStream(response.stream);
    if (response.statusCode != 200) {
      throw RealtimeTextStreamProblemException(_problemFromBody(body));
    }
    try {
      final decoded = jsonDecode(body);
      final cancelResponse = RealtimeTextStreamCancelResponse.fromJson(
        _asMap(decoded, 'invalid_cancel_response'),
      );
      if (cancelResponse.sessionId != createResponse.session.sessionId) {
        throw const RealtimeTextStreamProblemException(
          RealtimeTextStreamProblem(
            code: 'mismatched_cancel_session',
            message: 'The cancel response belonged to another stream session.',
            retryable: false,
          ),
        );
      }
      return cancelResponse;
    } on RealtimeTextStreamProblemException {
      rethrow;
    } catch (_) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'invalid_cancel_response',
          message: 'The stream cancel response was invalid.',
          retryable: true,
        ),
      );
    }
  }

  Uri _resolveSameOriginPath(String rawPath, String code) {
    final parsed = Uri.tryParse(rawPath);
    if (parsed == null ||
        parsed.scheme.isNotEmpty ||
        parsed.hasAuthority ||
        parsed.host.isNotEmpty ||
        rawPath.startsWith('//') ||
        !parsed.path.startsWith('/') ||
        parsed.hasFragment) {
      throw RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: code,
          message: 'The stream path was invalid.',
          retryable: true,
        ),
      );
    }
    final target = _baseUri.resolveUri(parsed);
    if (target.scheme != _baseUri.scheme ||
        target.host != _baseUri.host ||
        target.port != _baseUri.port) {
      throw RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: code,
          message: 'The stream path was invalid.',
          retryable: true,
        ),
      );
    }
    return target;
  }

  void close() {
    _client.close();
  }
}

class RealtimeTextStreamSseBoundary {
  const RealtimeTextStreamSseBoundary({required this.start, required this.end});

  final int start;
  final int end;
}

class RealtimeTextStreamSseFrame {
  const RealtimeTextStreamSseFrame({
    required this.id,
    required this.eventName,
    required this.data,
  });

  final int id;
  final String eventName;
  final String data;
}

RealtimeTextStreamSseFrame _parseSseFrame(String frameText) {
  int? id;
  String? eventName;
  final dataLines = <String>[];

  for (final line in frameText.split('\n')) {
    if (line.isEmpty || line.startsWith(':')) {
      continue;
    }
    final separator = line.indexOf(':');
    if (separator < 0) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'malformed_sse_field',
          message: 'The text-stream event frame was malformed.',
          retryable: true,
        ),
      );
    }
    final name = line.substring(0, separator);
    var value = line.substring(separator + 1);
    if (value.startsWith(' ')) {
      value = value.substring(1);
    }
    switch (name) {
      case 'id':
        id = int.tryParse(value);
        break;
      case 'event':
        eventName = value;
        break;
      case 'data':
        dataLines.add(value);
        break;
    }
  }

  if (id == null || id <= 0 || eventName == null || dataLines.isEmpty) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'malformed_sse_frame',
        message: 'The text-stream event frame was missing required fields.',
        retryable: true,
      ),
    );
  }

  return RealtimeTextStreamSseFrame(
    id: id,
    eventName: eventName,
    data: dataLines.join('\n'),
  );
}

RealtimeTextStreamEvent _eventFromFrame(RealtimeTextStreamSseFrame frame) {
  try {
    final decoded = jsonDecode(frame.data);
    return RealtimeTextStreamEvent.fromJson(
      _asMap(decoded, 'invalid_stream_event'),
    );
  } on RealtimeTextStreamProblemException {
    rethrow;
  } catch (_) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'malformed_stream_event_json',
        message: 'The text-stream event JSON was malformed.',
        retryable: true,
      ),
    );
  }
}

void _validateEvent({
  required RealtimeTextStreamEvent event,
  required RealtimeTextStreamSseFrame frame,
  required RealtimeTextStreamCreateResponse createResponse,
  required int expectedNextSequence,
  required int outputCharCount,
  required String outputText,
}) {
  if (event.sequence != frame.id) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'mismatched_sse_sequence',
        message: 'The text-stream event sequence was inconsistent.',
        retryable: true,
      ),
    );
  }
  if (event.eventType.wireName != frame.eventName) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'mismatched_sse_event_type',
        message: 'The text-stream event type was inconsistent.',
        retryable: true,
      ),
    );
  }
  if (event.sequence != expectedNextSequence) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'out_of_order_stream_event',
        message: 'The text-stream event sequence was out of order.',
        retryable: true,
      ),
    );
  }
  if (event.sessionId != createResponse.session.sessionId) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'mismatched_stream_session',
        message: 'The text-stream event belonged to another session.',
        retryable: false,
      ),
    );
  }
  final turnId = event.turnId;
  if (turnId != createResponse.turn.turnId) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'stale_stream_turn',
        message: 'The text-stream event belonged to an obsolete turn.',
        retryable: false,
      ),
    );
  }
  final chunk = event.chunk;
  if (chunk != null) {
    if (chunk.sequence != event.sequence) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_chunk_sequence',
          message: 'The text-stream chunk sequence was inconsistent.',
          retryable: true,
        ),
      );
    }
    final nextOutputCount = outputCharCount + _codePointCount(chunk.text);
    if (chunk.outputCharCount != nextOutputCount) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_chunk_output_count',
          message: 'The text-stream chunk output count was inconsistent.',
          retryable: true,
        ),
      );
    }
    if (nextOutputCount > realtimeTextStreamMaxOutputChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'output_limit_exceeded',
          message:
              'The streamed response exceeded the configured output limit.',
          retryable: true,
        ),
      );
    }
  }
  final terminal = event.terminal;
  if (terminal != null) {
    if (terminal.sequence != event.sequence) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_terminal_sequence',
          message: 'The text-stream terminal sequence was inconsistent.',
          retryable: true,
        ),
      );
    }
    final outputCount = _codePointCount(outputText);
    if (terminal.outputCharCount != outputCount) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_terminal_output_count',
          message: 'The text-stream terminal output count was inconsistent.',
          retryable: true,
        ),
      );
    }
    if (terminal.finalText != outputText) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_terminal_final_text',
          message: 'The text-stream terminal final text was inconsistent.',
          retryable: true,
        ),
      );
    }
    if (outputCount > realtimeTextStreamMaxOutputChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'output_limit_exceeded',
          message:
              'The streamed response exceeded the configured output limit.',
          retryable: true,
        ),
      );
    }
  }
}

RealtimeTextStreamSseBoundary? _findSseFrameBoundary(String buffer) {
  for (var index = 0; index < buffer.length; index += 1) {
    final unit = buffer.codeUnitAt(index);
    if (unit == 10) {
      if (index + 1 < buffer.length && buffer.codeUnitAt(index + 1) == 10) {
        return RealtimeTextStreamSseBoundary(start: index, end: index + 2);
      }
      if (index + 2 < buffer.length &&
          buffer.codeUnitAt(index + 1) == 13 &&
          buffer.codeUnitAt(index + 2) == 10) {
        return RealtimeTextStreamSseBoundary(start: index, end: index + 3);
      }
    }
    if (unit == 13) {
      if (index + 3 < buffer.length &&
          buffer.codeUnitAt(index + 1) == 10 &&
          buffer.codeUnitAt(index + 2) == 13 &&
          buffer.codeUnitAt(index + 3) == 10) {
        return RealtimeTextStreamSseBoundary(start: index, end: index + 4);
      }
      if (index + 2 < buffer.length &&
          buffer.codeUnitAt(index + 1) == 13 &&
          buffer.codeUnitAt(index + 2) == 10) {
        return RealtimeTextStreamSseBoundary(start: index, end: index + 3);
      }
    }
  }
  return null;
}

int _codePointCount(String value) => value.runes.length;

RealtimeTextStreamProblem _problemFromBody(String body) {
  try {
    final decoded = jsonDecode(body);
    final map = _asMap(decoded, 'invalid_stream_problem');
    final detail = map['detail'];
    if (detail is Map) {
      final problem = RealtimeTextStreamProblem.fromJson(
        Map<String, Object?>.from(detail),
      );
      return RealtimeTextStreamProblem(
        code: problem.code,
        message: 'The text stream request failed safely.',
        retryable: problem.retryable,
      );
    }
  } catch (_) {
    // Fall through to a bounded synthetic problem.
  }
  return const RealtimeTextStreamProblem(
    code: 'stream_http_error',
    message: 'The text stream request failed.',
    retryable: true,
  );
}

Map<String, Object?> _asMap(Object? value, String code) {
  if (value is Map) {
    return Map<String, Object?>.from(value);
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The text stream response shape was invalid.',
      retryable: true,
    ),
  );
}
