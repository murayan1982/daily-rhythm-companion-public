import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/framework_v600_realtime_session.dart';

const Set<String> frameworkV600RealtimeInterruptScopes = {
  'current_turn',
  'llm_stream',
  'tts_queue',
  'voice_output',
  'motion',
  'all',
};

const Set<String> frameworkV600RealtimeInterruptReasons = {
  'user_barge_in',
  'user_cancel',
  'new_turn_started',
  'session_closed',
  'timeout',
  'host_app_request',
  'provider_failure',
};

class FrameworkV600RealtimeSessionClient {
  FrameworkV600RealtimeSessionClient({
    required String baseUrl,
    required http.Client client,
  }) : _baseUri = Uri.parse(baseUrl.endsWith('/') ? baseUrl : '$baseUrl/'),
       _client = client;

  static const String _prefix = 'realtime/framework-v6/provider-free/sessions';

  final Uri _baseUri;
  final http.Client _client;

  Future<FrameworkV600RealtimeOpenResult> createSession() async {
    final response = await _send('POST', _prefix);
    final body = await _boundedBody(response);
    if (response.statusCode != 201) {
      throw _problemFromBody(body);
    }
    return _parse(
      body,
      FrameworkV600RealtimeOpenResult.fromJson,
      'invalid_response',
    );
  }

  Future<FrameworkV600RealtimeTurnResult> runTurn({
    required String sessionId,
    required String inputText,
  }) async {
    _validateSessionId(sessionId);
    _validateInputText(inputText);
    final response = await _send(
      'POST',
      '$_prefix/$sessionId/turns',
      body: <String, Object?>{'input_text': inputText},
    );
    final body = await _boundedBody(response);
    if (response.statusCode != 200) {
      throw _problemFromBody(body);
    }
    return _parse(
      body,
      FrameworkV600RealtimeTurnResult.fromJson,
      'invalid_response',
    );
  }

  Future<FrameworkV600RealtimeInterruptResult> interrupt({
    required String sessionId,
    String scope = 'current_turn',
    String reason = 'host_app_request',
  }) async {
    _validateSessionId(sessionId);
    if (!frameworkV600RealtimeInterruptScopes.contains(scope)) {
      throw _localProblem(
        'invalid_interrupt_scope',
        'The interrupt request was invalid.',
      );
    }
    if (!frameworkV600RealtimeInterruptReasons.contains(reason)) {
      throw _localProblem(
        'invalid_interrupt_reason',
        'The interrupt request was invalid.',
      );
    }
    final response = await _send(
      'POST',
      '$_prefix/$sessionId/interrupt',
      body: <String, Object?>{'scope': scope, 'reason': reason},
    );
    final body = await _boundedBody(response);
    if (response.statusCode != 200) {
      throw _problemFromBody(body);
    }
    return _parse(
      body,
      FrameworkV600RealtimeInterruptResult.fromJson,
      'invalid_response',
    );
  }

  Future<FrameworkV600RealtimeDiagnosticsSnapshot> diagnostics({
    required String sessionId,
  }) async {
    _validateSessionId(sessionId);
    final response = await _send('GET', '$_prefix/$sessionId/diagnostics');
    final body = await _boundedBody(response);
    if (response.statusCode != 200) {
      throw _problemFromBody(body);
    }
    return _parse(
      body,
      FrameworkV600RealtimeDiagnosticsSnapshot.fromJson,
      'invalid_response',
    );
  }

  Future<void> closeSession({required String sessionId}) async {
    _validateSessionId(sessionId);
    final response = await _send('DELETE', '$_prefix/$sessionId');
    final body = await _boundedBody(response);
    if (response.statusCode != 204) {
      throw _problemFromBody(body);
    }
  }

  void close() {
    _client.close();
  }

  Future<http.StreamedResponse> _send(
    String method,
    String path, {
    Map<String, Object?>? body,
  }) async {
    final request = http.Request(method, _baseUri.resolve(path));
    if (body != null) {
      request.headers['content-type'] = 'application/json; charset=utf-8';
      request.body = jsonEncode(body);
    }
    try {
      return await _client.send(request);
    } catch (_) {
      throw _localProblem('request_failed', 'The request failed safely.');
    }
  }

  Future<String> _boundedBody(http.StreamedResponse response) async {
    final builder = BytesBuilder(copy: false);
    await for (final chunk in response.stream) {
      if (builder.length + chunk.length > frameworkV600RealtimeMaxBodyBytes) {
        throw _localProblem(
          'response_body_too_large',
          'The response was too large.',
        );
      }
      builder.add(chunk);
    }
    try {
      return utf8.decode(builder.takeBytes());
    } catch (_) {
      throw _localProblem('invalid_response', 'The response was invalid.');
    }
  }

  T _parse<T>(
    String body,
    T Function(Map<String, Object?> json) parser,
    String code,
  ) {
    try {
      final decoded = jsonDecode(body);
      return parser(_asMap(decoded));
    } on FrameworkV600RealtimeProblemException {
      rethrow;
    } catch (_) {
      throw _localProblem(code, 'The response was invalid.');
    }
  }

  FrameworkV600RealtimeProblemException _problemFromBody(String body) {
    try {
      final decoded = jsonDecode(body);
      final root = _asMap(decoded);
      final detail = _asMap(root['detail']);
      return FrameworkV600RealtimeProblemException(
        FrameworkV600RealtimeProblem.fromJson(detail),
      );
    } catch (_) {
      return _localProblem(
        'invalid_response',
        'The error response was invalid.',
      );
    }
  }

  Map<String, Object?> _asMap(Object? value) {
    if (value is Map<String, Object?>) {
      return value;
    }
    if (value is Map) {
      return value.map((key, value) => MapEntry(key.toString(), value));
    }
    throw _localProblem('invalid_response', 'The response was invalid.');
  }

  void _validateSessionId(String value) {
    if (!RegExp(r'^fw_session_[0-9a-f]{32}$').hasMatch(value)) {
      throw _localProblem('invalid_session_id', 'The session id was invalid.');
    }
  }

  void _validateInputText(String value) {
    if (value.isEmpty || value.trim().isEmpty) {
      throw _localProblem(
        'invalid_input_text',
        'The turn request was invalid.',
      );
    }
    if (value.runes.length > frameworkV600RealtimeMaxInputChars) {
      throw _localProblem(
        'invalid_input_text',
        'The turn request was invalid.',
      );
    }
  }

  FrameworkV600RealtimeProblemException _localProblem(
    String code,
    String message,
  ) {
    return FrameworkV600RealtimeProblemException(
      FrameworkV600RealtimeProblem(
        code: code,
        message: message,
        retryable: false,
      ),
    );
  }
}
