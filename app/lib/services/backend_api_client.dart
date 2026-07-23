import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/advice_response.dart';
import '../models/character_preset.dart';
import '../models/chat.dart';
import '../models/fitbit_connect_response.dart';
import '../models/fitbit_status.dart';
import '../models/google_health_connection_ux.dart';
import '../models/google_health_diagnostics.dart';
import '../models/google_health_preflight.dart';
import '../models/google_health_self_check.dart';
import '../models/sleep_summary.dart';
import '../models/sleep_provider_selection.dart';
import '../models/daily_record.dart';
import '../models/recent_sleep_trend.dart';
import '../models/weekly_sleep_summary.dart';
import '../models/rhythm_report.dart';
import '../models/demo_status.dart';
import '../models/voice_input_demo.dart';
import '../models/voice_output_demo.dart';
import '../models/motion_demo.dart';

class BackendApiClient {
  static const String defaultBaseUrl = String.fromEnvironment(
    'DRC_BACKEND_API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  const BackendApiClient({this.baseUrl = defaultBaseUrl});

  final String baseUrl;

  bool get usesLocalhostBackend =>
      baseUrl.contains('127.0.0.1') || baseUrl.contains('localhost');

  String get smartphoneWebAccessHint {
    if (usesLocalhostBackend) {
      return 'スマホWeb実演では --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000 を指定してください。';
    }

    return 'スマホWeb実演向けのbackend API URLが指定されています。';
  }

  static String formatHealthStatus(Map<String, dynamic> body) {
    final status = body['status']?.toString().trim() ?? 'unknown';
    final version = body['version']?.toString().trim() ?? '';

    if (version.isEmpty) {
      return status;
    }

    return '$status / API v$version';
  }

  Future<String> fetchHealthStatus() async {
    final uri = Uri.parse('$baseUrl/health');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Health API failed: HTTP ${response.statusCode}');
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return formatHealthStatus(body);
  }

  Future<DemoStatus> fetchDemoStatus() async {
    final uri = Uri.parse('$baseUrl/demo/status');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Demo status API failed: HTTP ${response.statusCode}');
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return DemoStatus.fromJson(body);
  }

  Future<List<CharacterPreset>> fetchCharacters() async {
    final uri = Uri.parse('$baseUrl/characters');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Characters API failed: HTTP ${response.statusCode}');
    }

    final body = jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;

    return body
        .map((item) => CharacterPreset.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<SleepSummary> fetchSleepSummary() async {
    final uri = Uri.parse('$baseUrl/sleep/summary');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Sleep summary API failed: HTTP ${response.statusCode}');
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return SleepSummary.fromJson(body);
  }

  Future<SleepProviderSelectionStatus>
      fetchSleepProviderSelectionStatus() async {
    final uri = Uri.parse('$baseUrl/sleep/providers');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Sleep provider status API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return SleepProviderSelectionStatus.fromJson(body);
  }

  Future<List<DailyRecord>> fetchDailyRecords({int limit = 30}) async {
    final uri = Uri.parse('$baseUrl/daily-records?limit=$limit');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Daily records API failed: HTTP ${response.statusCode}');
    }

    final body = jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;

    return body
        .map((item) => DailyRecord.fromJson(item as Map<String, dynamic>))
        .toList();
  }


  Future<RecentSleepTrend> fetchRecentSleepTrend({
    String? referenceDate,
    int days = 7,
  }) async {
    final queryParameters = <String, String>{'days': days.toString()};
    final normalizedReferenceDate = referenceDate?.trim();

    if (normalizedReferenceDate != null && normalizedReferenceDate.isNotEmpty) {
      queryParameters['reference_date'] = normalizedReferenceDate;
    }

    final uri = Uri.parse(
      '$baseUrl/daily-records/recent-sleep-trend',
    ).replace(queryParameters: queryParameters);
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Recent sleep trend API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return RecentSleepTrend.fromJson(body);
  }


  Future<WeeklySleepSummary> fetchWeeklySleepSummary({
    String? referenceDate,
    int days = 7,
  }) async {
    final queryParameters = <String, String>{'days': days.toString()};
    final normalizedReferenceDate = referenceDate?.trim();

    if (normalizedReferenceDate != null && normalizedReferenceDate.isNotEmpty) {
      queryParameters['reference_date'] = normalizedReferenceDate;
    }

    final uri = Uri.parse(
      '$baseUrl/daily-records/weekly-summary',
    ).replace(queryParameters: queryParameters);
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Weekly sleep summary API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return WeeklySleepSummary.fromJson(body);
  }



  Future<RhythmReport> fetchRhythmReport({
    String period = 'weekly',
    String? referenceDate,
  }) async {
    final queryParameters = <String, String>{'period': period};
    final normalizedReferenceDate = referenceDate?.trim();

    if (normalizedReferenceDate != null && normalizedReferenceDate.isNotEmpty) {
      queryParameters['reference_date'] = normalizedReferenceDate;
    }

    final uri = Uri.parse(
      '$baseUrl/daily-records/rhythm-report',
    ).replace(queryParameters: queryParameters);
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Rhythm report API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return RhythmReport.fromJson(body);
  }

  Future<FitbitStatus> fetchFitbitStatus() async {
    final uri = Uri.parse('$baseUrl/fitbit/status');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Health data status API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return FitbitStatus.fromJson(body);
  }

  Future<FitbitConnectResponse> fetchFitbitConnect() async {
    final uri = Uri.parse('$baseUrl/fitbit/connect');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Health data connect API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return FitbitConnectResponse.fromJson(body);
  }


  Future<GoogleHealthConnectionUx> fetchGoogleHealthConnectionUx() async {
    final uri = Uri.parse('$baseUrl/google-health/connection-ux');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Google Health connection UX API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return GoogleHealthConnectionUx.fromJson(body);
  }

  Future<GoogleHealthDiagnostics> fetchGoogleHealthDiagnostics() async {
    final uri = Uri.parse('$baseUrl/google-health/diagnostics');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Google Health diagnostics API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return GoogleHealthDiagnostics.fromJson(body);
  }

  Future<GoogleHealthSelfCheck> fetchGoogleHealthSelfCheck() async {
    final uri = Uri.parse('$baseUrl/google-health/self-check');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Google Health self-check API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return GoogleHealthSelfCheck.fromJson(body);
  }


  Future<GoogleHealthPreflight> fetchGoogleHealthPreflight() async {
    final uri = Uri.parse('$baseUrl/google-health/preflight');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception(
        'Google Health preflight API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return GoogleHealthPreflight.fromJson(body);
  }


  Future<VoiceInputDemoRequestResponse> submitVoiceInputDemoRequest({
    required String clientEventId,
    String inputMode = 'demo_button',
    String? textHint,
  }) async {
    final uri = Uri.parse('$baseUrl/demo/voice-input');
    final requestBody = {
      'client_event_id': clientEventId,
      'input_mode': inputMode,
      'text_hint': textHint,
      'audio_reference': null,
      'audio_format': null,
      'sample_rate_hz': null,
      'duration_ms': null,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Voice input demo request API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return VoiceInputDemoRequestResponse.fromJson(body);
  }

  Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest({
    required String clientEventId,
    String outputMode = 'tts',
    String? textContent,
    String? characterId,
    String? voiceProfileId,
    String? audioFormat,
    String utterancePurpose = 'daily_advice',
  }) async {
    final uri = Uri.parse('$baseUrl/demo/voice-output');
    final requestBody = {
      'client_event_id': clientEventId,
      'output_mode': outputMode,
      'text_content': textContent,
      'character_id': characterId,
      'voice_profile_id': voiceProfileId,
      'audio_format': audioFormat,
      'utterance_purpose': utterancePurpose,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Voice output demo request API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return VoiceOutputDemoRequestResponse.fromJson(body);
  }


  Future<MotionDemoRequestResponse> submitMotionDemoRequest({
    required String clientEventId,
    String motionEvent = 'idle',
    String? characterId,
    String? expressionId,
    String triggerSource = 'manual',
    String requestedAdapterMode = 'simulator',
  }) async {
    final uri = Uri.parse('$baseUrl/demo/motion');
    final requestBody = {
      'client_event_id': clientEventId,
      'motion_event': motionEvent,
      'character_id': characterId,
      'expression_id': expressionId,
      'trigger_source': triggerSource,
      'requested_adapter_mode': requestedAdapterMode,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Motion demo request API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return MotionDemoRequestResponse.fromJson(body);
  }


  Future<ChatSession> createPostAdviceChatSession({
    required CharacterPreset character,
    required AdviceResponse adviceResponse,
    required String mood,
    String? initialUserMessage,
  }) async {
    final uri = Uri.parse('$baseUrl/chat/sessions');
    final requestBody = {
      'context': {
        'character': character.toAdviceJson(),
        'advice_message': adviceResponse.message,
        'mood': mood,
        'advice_basis': null,
        'advice_source': adviceResponse.source?.toJson(),
        'report_handoff': adviceResponse.source?.reportHandoff?.toJson(),
        'daily_record_id': null,
      },
      'initial_user_message': initialUserMessage,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Post-advice chat session API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return ChatSession.fromJson(body);
  }

  Future<ChatMessageResponse> sendPostAdviceChatMessage({
    required String sessionId,
    required String message,
  }) async {
    final uri = Uri.parse('$baseUrl/chat/sessions/$sessionId/messages');
    final requestBody = {'message': message};

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Post-advice chat message API failed: HTTP ${response.statusCode}',
      );
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return ChatMessageResponse.fromJson(body);
  }

  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    final uri = Uri.parse('$baseUrl/advice');

    final requestBody = {
      'character': character.toAdviceJson(),
      'sleep': sleepSummary.toAdviceJson(),
      'mood': mood,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode != 200) {
      throw Exception('Advice API failed: HTTP ${response.statusCode}');
    }

    final body =
        jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;

    return AdviceResponse.fromJson(body);
  }
}
