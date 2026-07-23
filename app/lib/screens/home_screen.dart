import 'package:flutter/material.dart';

import '../models/advice_response.dart';
import '../models/advice_source.dart';
import '../models/character_preset.dart';
import '../models/chat.dart';
import '../models/demo_status.dart';
import '../models/fitbit_connect_response.dart';
import '../models/fitbit_status.dart';
import '../models/google_health_connection_ux.dart';
import '../models/google_health_diagnostics.dart';
import '../models/google_health_preflight.dart';
import '../models/google_health_self_check.dart';
import '../models/sleep_provider_selection.dart';
import '../models/sleep_summary.dart';
import '../models/report_handoff_context.dart';
import '../models/voice_input_demo.dart';
import '../models/voice_output_demo.dart';
import '../models/motion_demo.dart';
import '../services/backend_api_client.dart';
import '../ui/character_asset_catalog.dart';

import 'package:url_launcher/url_launcher.dart';
import 'history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    this.apiClient = const BackendApiClient(),
  });

  final BackendApiClient apiClient;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _MoodChoiceCopy {
  const _MoodChoiceCopy({
    required this.label,
    required this.supportMessage,
    required this.adviceFocus,
  });

  final String label;
  final String supportMessage;
  final String adviceFocus;
}

const Map<String, _MoodChoiceCopy> _defaultMoodChoiceCopy = {
  'energetic': _MoodChoiceCopy(
    label: '元気',
    supportMessage: '今日は前向きに動けそう。勢いを使いすぎない提案に寄せます。',
    adviceFocus: '前向きに進める',
  ),
  'normal': _MoodChoiceCopy(
    label: 'ふつう',
    supportMessage: '今日はいつも通り。生活リズムを崩さない軽めの提案に寄せます。',
    adviceFocus: '無理なく維持する',
  ),
  'tired': _MoodChoiceCopy(
    label: 'だるい',
    supportMessage: '今日は回復優先。睡眠データが薄い場合も無理をしない提案に寄せます。',
    adviceFocus: '回復優先で整える',
  ),
};

const Map<String, Map<String, _MoodChoiceCopy>> _characterAwareMoodChoiceCopy = {
  'gentle_mina': {
    'energetic': _MoodChoiceCopy(
      label: 'いい感じ',
      supportMessage: '調子がよさそう。がんばりすぎず、いい流れを保つ提案にするね。',
      adviceFocus: 'いい流れを保つ',
    ),
    'normal': _MoodChoiceCopy(
      label: 'いつも通り',
      supportMessage: '今日は落ち着いていけそう。生活リズムを崩さない提案にするね。',
      adviceFocus: '穏やかに整える',
    ),
    'tired': _MoodChoiceCopy(
      label: 'ちょっと休みたい',
      supportMessage: '今日は回復優先で大丈夫。負担を減らす提案にするね。',
      adviceFocus: '回復を優先する',
    ),
  },
  'cheerful_sora': {
    'energetic': _MoodChoiceCopy(
      label: 'いけそう！',
      supportMessage: '今日は勢いがありそう。楽しく進めつつ、使いすぎない提案にするよ。',
      adviceFocus: '楽しく進める',
    ),
    'normal': _MoodChoiceCopy(
      label: 'ぼちぼち',
      supportMessage: 'いつもの調子でいけそう。小さく前に進める提案にするよ。',
      adviceFocus: '小さく進める',
    ),
    'tired': _MoodChoiceCopy(
      label: '省エネで',
      supportMessage: '今日は省エネでOK。元気を取り戻しやすい提案にするよ。',
      adviceFocus: '省エネで整える',
    ),
  },
  'cool_rei': {
    'energetic': _MoodChoiceCopy(
      label: '高め',
      supportMessage: '活動量を上げられる状態。優先度を絞って進める提案にします。',
      adviceFocus: '優先度を絞って進める',
    ),
    'normal': _MoodChoiceCopy(
      label: '標準',
      supportMessage: '通常運転。リズム維持を中心に提案します。',
      adviceFocus: 'リズムを維持する',
    ),
    'tired': _MoodChoiceCopy(
      label: '低め',
      supportMessage: '回復優先。今日は負荷を抑える提案にします。',
      adviceFocus: '負荷を抑える',
    ),
  },
};

class _HomeScreenState extends State<HomeScreen> {
  String _backendStatus = 'not checked yet';
  bool _isLoading = false;
  bool _isCreatingAdvice = false;
  bool _isConnectingHealthData = false;
  bool _isRefreshingDemoStatus = false;
  bool _isSubmittingVoiceInputDemo = false;
  bool _isSubmittingVoiceOutputDemo = false;
  bool _isSubmittingMotionDemo = false;
  bool _isStartingPostAdviceChat = false;
  bool _isSendingPostAdviceChatMessage = false;
  bool _postAdviceChatSkipped = false;
  bool _isRefreshingGoogleHealthChecks = false;
  bool _isRefreshingGoogleHealthConnectionUx = false;
  String? _errorMessage;
  String? _demoStatusError;
  String? _voiceInputDemoError;
  String? _voiceOutputDemoError;
  String? _motionDemoError;
  String? _postAdviceChatError;
  String? _googleHealthDebugError;
  String? _googleHealthConnectionUxError;
  String? _sleepProviderSelectionError;

  List<CharacterPreset> _characters = [];
  CharacterPreset? _selectedCharacter;
  SleepSummary? _sleepSummary;
  SleepProviderSelectionStatus? _sleepProviderSelectionStatus;
  FitbitStatus? _fitbitStatus;
  FitbitConnectResponse? _fitbitConnectResponse;
  DemoStatus? _demoStatus;
  VoiceInputDemoRequestResponse? _voiceInputDemoResponse;
  VoiceOutputDemoRequestResponse? _voiceOutputDemoResponse;
  MotionDemoRequestResponse? _motionDemoResponse;
  ChatSession? _postAdviceChatSession;
  GoogleHealthConnectionUx? _googleHealthConnectionUx;
  GoogleHealthDiagnostics? _googleHealthDiagnostics;
  GoogleHealthPreflight? _googleHealthPreflight;
  GoogleHealthSelfCheck? _googleHealthSelfCheck;

  String _selectedMood = 'normal';
  String _selectedMotionEvent = 'greeting';
  String _selectedExpressionId = 'happy';
  AdviceResponse? _adviceResponse;
  String? _healthDataConnectUrl;
  final TextEditingController _postAdviceChatMessageController =
      TextEditingController();

  @override
  void dispose() {
    _postAdviceChatMessageController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    setState(() {
      _isLoading = true;
      _backendStatus = 'checking...';
      _errorMessage = null;
    });

    try {
      final status = await widget.apiClient.fetchHealthStatus();
      final characters = await widget.apiClient.fetchCharacters();
      final sleepSummary = await widget.apiClient.fetchSleepSummary();

      SleepProviderSelectionStatus? providerSelectionStatus;
      String? providerSelectionError;
      FitbitStatus? fitbitStatus;

      try {
        providerSelectionStatus =
            await widget.apiClient.fetchSleepProviderSelectionStatus();
      } catch (error) {
        providerSelectionError = _formatUserFacingError(error);
      }

      if (providerSelectionStatus?.isFitbit == true) {
        try {
          fitbitStatus = await widget.apiClient.fetchFitbitStatus();
        } catch (error) {
          providerSelectionError ??= _formatUserFacingError(error);
        }
      }

      setState(() {
        _backendStatus = status;
        _characters = characters;
        _selectedCharacter = characters.isNotEmpty ? characters.first : null;
        _sleepSummary = sleepSummary;
        _sleepProviderSelectionStatus = providerSelectionStatus;
        _sleepProviderSelectionError = providerSelectionError;
        _fitbitStatus = fitbitStatus;
      });
    } catch (error) {
      setState(() {
        _backendStatus = 'error';
        _errorMessage = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _createAdvice() async {
    final selectedCharacter = _selectedCharacter;
    if (selectedCharacter == null) {
      setState(() {
        _errorMessage = 'キャラクターを選択してください。';
      });
      return;
    }

    final sleepSummary = _sleepSummary;
    if (sleepSummary == null) {
      setState(() {
        _errorMessage = '睡眠サマリーを読み込み中です。少し待ってからもう一度試してください。';
      });
      return;
    }

    setState(() {
      _isCreatingAdvice = true;
      _errorMessage = null;
      _adviceResponse = null;
      _postAdviceChatSession = null;
      _postAdviceChatError = null;
      _postAdviceChatSkipped = false;
      _postAdviceChatMessageController.clear();
    });

    try {
      final adviceResponse = await widget.apiClient.createAdvice(
        character: selectedCharacter,
        sleepSummary: sleepSummary,
        mood: _selectedMood,
      );

      setState(() {
        _adviceResponse = adviceResponse;
      });
    } catch (error) {
      setState(() {
        _errorMessage = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isCreatingAdvice = false;
      });
    }
  }




  Future<void> _startPostAdviceChat() async {
    final selectedCharacter = _selectedCharacter;
    final adviceResponse = _adviceResponse;

    if (selectedCharacter == null || adviceResponse == null) {
      setState(() {
        _postAdviceChatError = 'アドバイス作成後にもう一度試してください。';
      });
      return;
    }

    setState(() {
      _isStartingPostAdviceChat = true;
      _postAdviceChatError = null;
      _postAdviceChatSkipped = false;
    });

    try {
      final session = await widget.apiClient.createPostAdviceChatSession(
        character: selectedCharacter,
        adviceResponse: adviceResponse,
        mood: _selectedMood,
      );

      setState(() {
        _postAdviceChatSession = session;
      });
    } catch (error) {
      setState(() {
        _postAdviceChatError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isStartingPostAdviceChat = false;
      });
    }
  }

  void _skipPostAdviceChat() {
    setState(() {
      _postAdviceChatSkipped = true;
      _postAdviceChatError = null;
      _postAdviceChatSession = null;
      _postAdviceChatMessageController.clear();
    });
  }

  Future<void> _sendPostAdviceChatMessage() async {
    final session = _postAdviceChatSession;
    final message = _postAdviceChatMessageController.text.trim();

    if (session == null) {
      setState(() {
        _postAdviceChatError = '先に「少し話す」からチャットを開始してください。';
      });
      return;
    }

    if (message.isEmpty) {
      setState(() {
        _postAdviceChatError = '送信するメッセージを入力してください。';
      });
      return;
    }

    setState(() {
      _isSendingPostAdviceChatMessage = true;
      _postAdviceChatError = null;
    });

    try {
      final response = await widget.apiClient.sendPostAdviceChatMessage(
        sessionId: session.sessionId,
        message: message,
      );

      setState(() {
        _postAdviceChatSession = ChatSession(
          sessionId: response.sessionId,
          status: session.status,
          source: response.source,
          context: session.context,
          messages: response.messages,
        );
        _postAdviceChatMessageController.clear();
      });
    } catch (error) {
      setState(() {
        _postAdviceChatError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isSendingPostAdviceChatMessage = false;
      });
    }
  }


  Future<void> _refreshDemoStatus() async {
    setState(() {
      _isRefreshingDemoStatus = true;
      _demoStatusError = null;
    });

    try {
      final demoStatus = await widget.apiClient.fetchDemoStatus();

      setState(() {
        _demoStatus = demoStatus;
      });
    } catch (error) {
      setState(() {
        _demoStatusError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isRefreshingDemoStatus = false;
      });
    }
  }


  Future<void> _submitVoiceInputDemoRequest() async {
    setState(() {
      _isSubmittingVoiceInputDemo = true;
      _voiceInputDemoError = null;
      _voiceInputDemoResponse = null;
    });

    try {
      final response = await widget.apiClient.submitVoiceInputDemoRequest(
        clientEventId:
            'flutter-demo-button-${DateTime.now().toUtc().toIso8601String()}',
        inputMode: 'demo_button',
        textHint: 'Flutter voice input demo button tapped.',
      );

      setState(() {
        _voiceInputDemoResponse = response;
      });
    } catch (error) {
      setState(() {
        _voiceInputDemoError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isSubmittingVoiceInputDemo = false;
      });
    }
  }

  Future<void> _submitVoiceOutputDemoRequest() async {
    final selectedCharacter = _selectedCharacter;
    final textContent = _adviceResponse?.message ??
        'Flutter voice output demo text for guarded real TTS runtime check.';

    setState(() {
      _isSubmittingVoiceOutputDemo = true;
      _voiceOutputDemoError = null;
      _voiceOutputDemoResponse = null;
    });

    try {
      final response = await widget.apiClient.submitVoiceOutputDemoRequest(
        clientEventId:
            'flutter-tts-demo-button-${DateTime.now().toUtc().toIso8601String()}',
        outputMode: 'tts',
        textContent: textContent,
        characterId: selectedCharacter?.characterId,
        voiceProfileId: selectedCharacter?.characterId,
        audioFormat: 'mp3',
        utterancePurpose: 'daily_advice',
      );

      setState(() {
        _voiceOutputDemoResponse = response;
      });
    } catch (error) {
      setState(() {
        _voiceOutputDemoError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isSubmittingVoiceOutputDemo = false;
      });
    }
  }


  Future<void> _submitMotionDemoRequest() async {
    final selectedCharacter = _selectedCharacter;

    setState(() {
      _isSubmittingMotionDemo = true;
      _motionDemoError = null;
      _motionDemoResponse = null;
    });

    try {
      final response = await widget.apiClient.submitMotionDemoRequest(
        clientEventId:
            'flutter-motion-demo-${DateTime.now().toUtc().toIso8601String()}',
        motionEvent: _selectedMotionEvent,
        characterId: selectedCharacter?.characterId,
        expressionId: _selectedExpressionId,
        triggerSource: 'manual',
        requestedAdapterMode: 'simulator',
      );

      setState(() {
        _motionDemoResponse = response;
      });
    } catch (error) {
      setState(() {
        _motionDemoError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isSubmittingMotionDemo = false;
      });
    }
  }

  Future<void> _refreshGoogleHealthConnectionUx() async {
    setState(() {
      _isRefreshingGoogleHealthConnectionUx = true;
      _googleHealthConnectionUxError = null;
    });

    try {
      final connectionUx = await widget.apiClient.fetchGoogleHealthConnectionUx();

      setState(() {
        _googleHealthConnectionUx = connectionUx;
      });
    } catch (error) {
      setState(() {
        _googleHealthConnectionUxError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isRefreshingGoogleHealthConnectionUx = false;
      });
    }
  }

  Future<void> _refreshGoogleHealthChecks() async {
    setState(() {
      _isRefreshingGoogleHealthChecks = true;
      _googleHealthDebugError = null;
    });

    try {
      final diagnostics = await widget.apiClient.fetchGoogleHealthDiagnostics();
      final preflight = await widget.apiClient.fetchGoogleHealthPreflight();
      final selfCheck = await widget.apiClient.fetchGoogleHealthSelfCheck();

      setState(() {
        _googleHealthDiagnostics = diagnostics;
        _googleHealthPreflight = preflight;
        _googleHealthSelfCheck = selfCheck;
      });
    } catch (error) {
      setState(() {
        _googleHealthDebugError = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isRefreshingGoogleHealthChecks = false;
      });
    }
  }

  Future<void> _connectHealthData() async {
    setState(() {
      _isConnectingHealthData = true;
      _errorMessage = null;
      _healthDataConnectUrl = null;
      _fitbitConnectResponse = null;
    });

    try {
      final response = await widget.apiClient.fetchFitbitConnect();

      setState(() {
        _healthDataConnectUrl = response.connectUrl;
        _fitbitConnectResponse = response;
      });
    } catch (error) {
      setState(() {
        _errorMessage = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isConnectingHealthData = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _refreshDemoStatus();
    _refreshGoogleHealthConnectionUx();
    _refreshGoogleHealthChecks();
  }

  Widget _buildBackendConnectionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Backend Connection',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            if (_isLoading) ...[
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              const SizedBox(width: 8),
            ],
            Text('Backend status: $_backendStatus'),
          ],
        ),
        const SizedBox(height: 8),
        Text('API base URL: ${widget.apiClient.baseUrl}'),
        const SizedBox(height: 4),
        Text(
          widget.apiClient.smartphoneWebAccessHint,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildDailyLoopOverviewSection(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final selectedCharacter = _selectedCharacter;
    final characterLabel = selectedCharacter?.displayName ?? '未選択';
    final moodLabel = _formatMoodLabel(_selectedMood);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Today's Loop",
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'まず今日の睡眠と気分を確認して、選んだキャラクターからアドバイスを受け取ります。',
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDailyLoopStep(
                context,
                stepNumber: '1',
                title: '睡眠',
                value: _formatDailyLoopSleepStatus(),
                detail: '今日の入力コンテキスト',
              ),
              const SizedBox(height: 12),
              _buildDailyLoopStep(
                context,
                stepNumber: '2',
                title: '気分',
                value: moodLabel,
                detail: '睡眠データがない場合もアドバイスの軸になります',
              ),
              const SizedBox(height: 12),
              _buildDailyLoopStep(
                context,
                stepNumber: '3',
                title: 'キャラクター',
                value: characterLabel,
                detail: '話し方とアドバイスの雰囲気を決めます',
              ),
              const SizedBox(height: 12),
              _buildDailyLoopStep(
                context,
                stepNumber: '4',
                title: 'アドバイス',
                value: _formatDailyLoopAdviceStatus(),
                detail: '作成後は DailyRecord として履歴で確認できます',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDailyLoopStep(
    BuildContext context, {
    required String stepNumber,
    required String title,
    required String value,
    required String detail,
  }) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: colorScheme.primaryContainer,
          foregroundColor: colorScheme.onPrimaryContainer,
          child: Text(stepNumber),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Text(detail),
            ],
          ),
        ),
        const SizedBox(width: 12),
        Flexible(
          child: Align(
            alignment: Alignment.centerRight,
            child: Chip(label: Text(value)),
          ),
        ),
      ],
    );
  }


  Widget _buildDailyLoopStatusSection(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Daily Loop Status',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '読み込み・作成・エラー時も、次に何をすればいいか見えるようにします。',
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDiagnosticRow('状態', _formatDailyLoopReadinessStatus()),
              _buildDiagnosticRow('次の操作', _formatDailyLoopNextAction()),
              _buildDiagnosticRow('Backend', _backendStatus),
              _buildDiagnosticRow('Sleep', _formatDailyLoopSleepStatus()),
              _buildDiagnosticRow('Character', _formatDailyLoopCharacterStatus()),
              _buildDiagnosticRow('Advice', _formatDailyLoopAdviceStatus()),
              if (_errorMessage != null) ...[
                const SizedBox(height: 8),
                const Text(
                  '再読み込みで復旧できる場合があります。必要ならバックエンドの起動状態を確認してください。',
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  String _formatDailyLoopReadinessStatus() {
    if (_isLoading) {
      return '読み込み中';
    }

    if (_isCreatingAdvice) {
      return 'アドバイス作成中';
    }

    if (_errorMessage != null) {
      return '確認が必要です';
    }

    if (_adviceResponse != null) {
      return '履歴確認へ進めます';
    }

    if (_selectedCharacter == null) {
      return 'キャラクター未選択';
    }

    if (_sleepSummary == null) {
      return '睡眠サマリー待ち';
    }

    return '準備できています';
  }

  String _formatDailyLoopNextAction() {
    if (_isLoading) {
      return '読み込み完了を待つ';
    }

    if (_isCreatingAdvice) {
      return 'アドバイス作成完了を待つ';
    }

    if (_errorMessage != null) {
      return '内容を確認して再読み込みする';
    }

    if (_adviceResponse != null) {
      return 'DailyRecord / History で見返す';
    }

    if (_selectedCharacter == null) {
      return 'キャラクターを選ぶ';
    }

    if (_sleepSummary == null) {
      return '睡眠サマリーの読み込みを待つ';
    }

    return '今日のアドバイスを作る';
  }

  String _formatDailyLoopSleepStatus() {
    final sleepSummary = _sleepSummary;

    if (_isLoading || sleepSummary == null) {
      return '読み込み中';
    }

    if (!sleepSummary.available) {
      return '未取得';
    }

    return '${sleepSummary.formattedTotalSleep} / ${sleepSummary.displaySource}';
  }

  String _formatDailyLoopAdviceStatus() {
    if (_isCreatingAdvice) {
      return '作成中';
    }

    if (_adviceResponse != null) {
      return '作成済み';
    }

    return '未作成';
  }

  String _formatDailyLoopCharacterStatus() {
    final selectedCharacter = _selectedCharacter;

    if (_isLoading) {
      return '読み込み中';
    }

    if (selectedCharacter == null) {
      return '未選択';
    }

    return '${selectedCharacter.displayName} / ${selectedCharacter.adviceStyle}';
  }


  Widget _buildDailyLoopDemoContextSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Demo Context',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Daily loop は通常のユーザー導線として見せつつ、AI Character Framework demo としての状態もここで軽く確認します。',
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
              const Text(
                'Daily loop demo visibility',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildDiagnosticRow('Loop engine', _formatLoopDemoEngine()),
              _buildDiagnosticRow('Loop mode', _formatLoopDemoMode()),
              _buildDiagnosticRow(
                'LLM for advice',
                _formatLoopDemoCapability('llm_response'),
              ),
              _buildDiagnosticRow(
                'Voice input demo',
                _formatLoopDemoCapability('voice_input'),
              ),
              _buildDiagnosticRow(
                'Voice output demo',
                _formatLoopDemoCapability('voice_output'),
              ),
              _buildDiagnosticRow(
                'Motion demo',
                _formatLoopDemoCapability('live2d_motion'),
              ),
              const SizedBox(height: 8),
              const Text(
                '詳細な能力チェックや voice / motion request は、区切り線の下の Advanced Demo Tools で確認します。',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAdvancedDemoToolsHeading() {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Advanced Demo Tools',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 8),
        Text(
          'ここから下は開発者・デモオペレーター向けです。通常の日次ループは上の sleep / mood / character / advice flow だけで完結します。',
        ),
      ],
    );
  }

  String _formatLoopDemoEngine() {
    final demoStatus = _demoStatus;

    if (_isRefreshingDemoStatus && demoStatus == null) {
      return '読み込み中';
    }

    if (demoStatus == null) {
      return '未確認';
    }

    return demoStatus.displayEngine;
  }

  String _formatLoopDemoMode() {
    final demoStatus = _demoStatus;

    if (_isRefreshingDemoStatus && demoStatus == null) {
      return '読み込み中';
    }

    if (demoStatus == null) {
      return '未確認';
    }

    return demoStatus.displayMode;
  }

  String _formatLoopDemoCapability(String key) {
    final demoStatus = _demoStatus;

    if (_isRefreshingDemoStatus && demoStatus == null) {
      return '読み込み中';
    }

    if (demoStatus == null) {
      return '未確認';
    }

    final capability = demoStatus.capability(key);
    return '${capability.displayStatus} / ${capability.displaySource}';
  }

  _MoodChoiceCopy _resolveMoodChoiceCopy(String mood) {
    final characterId = _selectedCharacter?.characterId;
    final characterCopy = _characterAwareMoodChoiceCopy[characterId]?[mood];
    if (characterCopy != null) {
      return characterCopy;
    }

    return _defaultMoodChoiceCopy[mood] ??
        _MoodChoiceCopy(
          label: mood,
          supportMessage: '選んだ気分に合わせてアドバイスの重さを調整します。',
          adviceFocus: '気分に合わせる',
        );
  }

  String _formatMoodLabel(String mood) {
    return _resolveMoodChoiceCopy(mood).label;
  }

  String _formatMoodSupportMessage(String mood) {
    return _resolveMoodChoiceCopy(mood).supportMessage;
  }

  String _formatMoodAdviceIntent(String mood) {
    return _resolveMoodChoiceCopy(mood).adviceFocus;
  }

  String _formatAdviceReadinessSleepStatus() {
    final sleepSummary = _sleepSummary;

    if (_isLoading || sleepSummary == null) {
      return '読み込み中';
    }

    if (!sleepSummary.available) {
      return '未取得 / ${sleepSummary.displayUnavailableReason}';
    }

    return '${sleepSummary.formattedTotalSleep} / ${sleepSummary.displaySource}';
  }


  Widget _buildDemoStatusSection(BuildContext context) {
    final demoStatus = _demoStatus;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(
              child: Text(
                'Demo Status',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),
            OutlinedButton.icon(
              onPressed: _isRefreshingDemoStatus ? null : _refreshDemoStatus,
              icon: const Icon(Icons.refresh),
              label: Text(_isRefreshingDemoStatus ? 'Refreshing' : 'Refresh'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text('AI Character Framework demo capability visibility.'),
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
              if (_isRefreshingDemoStatus) ...[
                const LinearProgressIndicator(),
                const SizedBox(height: 12),
              ],
              if (_demoStatusError != null) ...[
                Text(
                  _demoStatusError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (demoStatus == null) ...[
                const Text('Demo capability status を読み込み中です。'),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('Engine', demoStatus.displayEngine),
                    _buildStatusChip('Mode', demoStatus.displayMode),
                  ],
                ),
                const SizedBox(height: 16),
                ...DemoStatus.orderedCapabilityKeys.map(
                  (key) => _buildDemoCapabilityRow(key, demoStatus.capability(key)),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDemoCapabilityRow(
    String key,
    DemoCapabilityStatus capability,
  ) {
    final label = DemoStatus.displayCapabilityName(key);
    final message = capability.message.trim();

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$label: ${capability.displayStatus} / ${capability.displaySource}',
          ),
          if (message.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(message),
            ),
        ],
      ),
    );
  }


  Widget _buildVoiceInputDemoSection(BuildContext context) {
    final response = _voiceInputDemoResponse;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Voice Input Demo',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '録音やマイク権限はまだ使わず、backend の voice input demo request contract だけを確認します。',
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
              FilledButton.icon(
                onPressed: _isSubmittingVoiceInputDemo
                    ? null
                    : _submitVoiceInputDemoRequest,
                icon: const Icon(Icons.mic_none),
                label: Text(
                  _isSubmittingVoiceInputDemo
                      ? 'Voice input demo確認中...'
                      : 'Voice input demoを試す',
                ),
              ),
              if (_isSubmittingVoiceInputDemo) ...[
                const SizedBox(height: 12),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 12),
              if (_voiceInputDemoError != null) ...[
                Text(
                  _voiceInputDemoError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (response == null) ...[
                const Text('まだ voice input demo request は送信していません。'),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('Request', response.displayAccepted),
                    _buildStatusChip('State', response.displayRequestState),
                    _buildStatusChip('Engine', response.displayEngine),
                    _buildStatusChip('Adapter', response.displayAdapterMode),
                  ],
                ),
                const SizedBox(height: 12),
                _buildDiagnosticRow(
                  'Capability',
                  '${response.capability.displayStatus} / ${response.capability.displaySource}',
                ),
                _buildDiagnosticRow('Input mode', response.displayInputMode),
                _buildDiagnosticRow('Transcript', response.displayTranscript),
                const SizedBox(height: 8),
                Text(response.message),
                if (response.checks.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Voice input checks',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.checks.map(
                    (check) => _buildDiagnosticRow(
                      check.displayName,
                      '${check.displayStatus}: ${check.message}',
                    ),
                  ),
                ],
                if (response.candidatePaths.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Candidate paths',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.candidatePaths.map(Text.new),
                ],
                if (response.publicApiCandidates.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Public API candidates',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.publicApiCandidates.map(Text.new),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceOutputDemoSection(BuildContext context) {
    final response = _voiceOutputDemoResponse;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Voice Output / TTS Demo',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '通常は backend の guarded voice output contract だけを確認します。VOICE_OUTPUT_REAL_TTS_ENABLED=1 の private operator 実行時だけ、FW public voice output boundary への中立リクエストと Web UI の音声再生確認導線を表示します。',
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
              FilledButton.icon(
                onPressed: _isSubmittingVoiceOutputDemo
                    ? null
                    : _submitVoiceOutputDemoRequest,
                icon: const Icon(Icons.volume_up_outlined),
                label: Text(
                  _isSubmittingVoiceOutputDemo
                      ? 'Voice output demo確認中...'
                      : 'Voice output demoを試す',
                ),
              ),
              if (_isSubmittingVoiceOutputDemo) ...[
                const SizedBox(height: 12),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 12),
              if (_voiceOutputDemoError != null) ...[
                Text(
                  _voiceOutputDemoError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (response == null) ...[
                const Text('まだ voice output demo request は送信していません。'),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('Request', response.displayAccepted),
                    _buildStatusChip('State', response.displayRequestState),
                    _buildStatusChip('Engine', response.displayEngine),
                    _buildStatusChip('Adapter', response.displayAdapterMode),
                    _buildStatusChip('Real TTS', response.displayRealTtsGate),
                  ],
                ),
                const SizedBox(height: 12),
                _buildDiagnosticRow(
                  'Capability',
                  '${response.capability.displayStatus} / ${response.capability.displaySource}',
                ),
                _buildDiagnosticRow('Output mode', response.displayOutputMode),
                _buildDiagnosticRow('Character', response.displayCharacterId),
                _buildDiagnosticRow('Voice profile', response.displayVoiceProfileId),
                _buildDiagnosticRow('Utterance purpose', response.displayUtterancePurpose),
                _buildDiagnosticRow(
                  'Requested audio',
                  response.displayRequestedAudioFormat,
                ),
                _buildDiagnosticRow('Generated audio', response.displayAudioFormat),
                _buildDiagnosticRow('Audio ready', response.displayAudioReady),
                _buildDiagnosticRow('Handoff kind', response.displayAudioHandoffKind),
                _buildDiagnosticRow('Has handoff', response.displayHasAudioHandoff),
                _buildDiagnosticRow('Generated state', response.displayIsGenerated),
                _buildDiagnosticRow('Audio URL', response.displayAudioUrl),
                _buildDiagnosticRow(
                  'Audio artifact ref',
                  response.displayAudioArtifactRef,
                ),
                _buildDiagnosticRow(
                  'Playback candidate',
                  _formatVoiceOutputPlaybackCandidate(response),
                ),
                _buildDiagnosticRow('Framework call', response.displayFrameworkCallState),
                _buildDiagnosticRow('Framework API', response.displayFrameworkApiName),
                _buildDiagnosticRow('Playback', response.displayAudioPlaybackStatus),
                _buildDiagnosticRow('Evidence', response.displayEvidenceStatus),
                _buildDiagnosticRow('Text', response.displayTextContent),
                const SizedBox(height: 8),
                const Text(
                  'Public UI does not print raw audio URLs or artifact refs. Use the playback button only for generated URL handoffs during a private operator evidence run.',
                ),
                if (_canOpenVoiceOutputAudioUrl(response)) ...[
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: () => _openVoiceOutputAudioUrl(response),
                    icon: const Icon(Icons.play_circle_outline),
                    label: const Text('音声を開いて再生確認する'),
                  ),
                ],
                const SizedBox(height: 8),
                Text(response.message),
                if (response.requestWarnings.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Request warnings',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.requestWarnings.map(Text.new),
                ],
                if (response.runtimeNotes.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Runtime notes',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.runtimeNotes.map(Text.new),
                ],
                if (response.checks.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Voice output checks',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.checks.map(
                    (check) => _buildDiagnosticRow(
                      check.displayName,
                      '${check.displayStatus}: ${check.message}',
                    ),
                  ),
                ],
                if (response.candidatePaths.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Voice output candidate paths',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.candidatePaths.map(Text.new),
                ],
                if (response.publicApiCandidates.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Voice output public API candidates',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.publicApiCandidates.map(Text.new),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }



  Widget _buildMotionDemoSection(BuildContext context) {
    final response = _motionDemoResponse;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Motion Demo',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Live2Dモデルは同梱せず、軽量なペラ絵/表情差分 simulator として motion request contract を確認します。',
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
              _buildLightweightAvatarPreview(context),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _buildDropdownField(
                    label: 'Motion',
                    value: _selectedMotionEvent,
                    values: const [
                      'greeting',
                      'thinking',
                      'happy',
                      'tired_supportive',
                      'speaking',
                      'idle',
                    ],
                    onChanged: (value) {
                      if (value == null) return;
                      setState(() {
                        _selectedMotionEvent = value;
                        _selectedExpressionId = _expressionForMotion(value);
                      });
                    },
                  ),
                  _buildDropdownField(
                    label: 'Expression',
                    value: _selectedExpressionId,
                    values: const [
                      'idle',
                      'happy',
                      'thinking',
                      'supportive',
                      'speaking',
                    ],
                    onChanged: (value) {
                      if (value == null) return;
                      setState(() {
                        _selectedExpressionId = value;
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed:
                    _isSubmittingMotionDemo ? null : _submitMotionDemoRequest,
                icon: const Icon(Icons.emoji_emotions_outlined),
                label: Text(
                  _isSubmittingMotionDemo
                      ? 'Motion demo確認中...'
                      : 'Motion demoを試す',
                ),
              ),
              if (_isSubmittingMotionDemo) ...[
                const SizedBox(height: 12),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 12),
              if (_motionDemoError != null) ...[
                Text(
                  _motionDemoError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (response == null) ...[
                const Text('まだ motion demo request は送信していません。'),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('Request', response.displayAccepted),
                    _buildStatusChip('State', response.displayRequestState),
                    _buildStatusChip('Engine', response.displayEngine),
                    _buildStatusChip('Adapter', response.displayAdapterMode),
                  ],
                ),
                const SizedBox(height: 12),
                _buildDiagnosticRow(
                  'Capability',
                  '${response.capability.displayStatus} / ${response.capability.displaySource}',
                ),
                _buildDiagnosticRow('Motion', response.displayMotionEvent),
                _buildDiagnosticRow('Expression', response.displayExpressionId),
                _buildDiagnosticRow('Character', response.displayCharacterId),
                _buildDiagnosticRow('Trigger', response.displayTriggerSource),
                _buildDiagnosticRow(
                  'Requested adapter',
                  response.displayRequestedAdapterMode,
                ),
                _buildDiagnosticRow(
                  'Resolved adapter',
                  response.displayResolvedAdapterMode,
                ),
                _buildDiagnosticRow('Motion sent', response.displayMotionSent),
                _buildDiagnosticRow(
                  'VTS connection',
                  response.displayVtsConnectionUsed,
                ),
                const SizedBox(height: 8),
                Text(response.message),
                if (response.requestWarnings.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Motion request warnings',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  ...response.requestWarnings.map(Text.new),
                ],
                if (response.supportedMotionEvents.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Supported motions',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(response.supportedMotionEvents.join(', ')),
                ],
                if (response.supportedExpressionIds.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'Supported expressions',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(response.supportedExpressionIds.join(', ')),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLightweightAvatarPreview(BuildContext context) {
    final characterName = _selectedCharacter?.displayName ?? 'Demo character';
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: colorScheme.surface,
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 34,
            child: Text(
              _avatarFaceForExpression(_selectedExpressionId),
              style: const TextStyle(fontSize: 28),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  characterName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text('Lightweight avatar simulator: $_selectedExpressionId'),
                Text('Motion event: $_selectedMotionEvent'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownField({
    required String label,
    required String value,
    required List<String> values,
    required ValueChanged<String?> onChanged,
  }) {
    return SizedBox(
      width: 220,
      child: DropdownButtonFormField<String>(
        initialValue: value,
        isExpanded: true,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        items: values
            .map(
              (item) => DropdownMenuItem(
                value: item,
                child: Text(
                  item.replaceAll('_', ' '),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            )
            .toList(),
        selectedItemBuilder: (context) => values
            .map(
              (item) => Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  item.replaceAll('_', ' '),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            )
            .toList(),
        onChanged: onChanged,
      ),
    );
  }

  String _expressionForMotion(String motionEvent) {
    switch (motionEvent) {
      case 'greeting':
      case 'happy':
        return 'happy';
      case 'thinking':
        return 'thinking';
      case 'tired_supportive':
        return 'supportive';
      case 'speaking':
        return 'speaking';
      case 'idle':
      default:
        return 'idle';
    }
  }

  String _avatarFaceForExpression(String expressionId) {
    switch (expressionId) {
      case 'happy':
        return '😊';
      case 'thinking':
        return '🤔';
      case 'supportive':
        return '😌';
      case 'speaking':
        return '🙂';
      case 'idle':
      default:
        return '🙂';
    }
  }

  Widget _buildSleepDataSourceSection(BuildContext context) {
    final selection = _sleepProviderSelectionStatus;
    final sleepSummary = _sleepSummary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Sleep Data Source',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'バックエンドで選ばれているproviderと、今回の睡眠データ元を分けて表示します。',
        ),
        const SizedBox(height: 12),
        Container(
          key: const Key('sleep-data-source-section'),
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_isLoading && selection == null) ...[
                const LinearProgressIndicator(),
                const SizedBox(height: 12),
                const Text('sleep provider設定を読み込み中です。'),
              ] else if (selection == null) ...[
                const Text(
                  '設定中のsleep providerを確認できませんでした。睡眠サマリーは引き続き利用できます。',
                ),
                if (_sleepProviderSelectionError != null) ...[
                  const SizedBox(height: 8),
                  Text(_sleepProviderSelectionError!),
                ],
                const SizedBox(height: 8),
                Text(
                  '今回のデータ元: ${sleepSummary?.displaySource ?? '未確認'}',
                ),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip(
                      '設定',
                      selection.displayConfiguredState,
                    ),
                    _buildStatusChip(
                      'データ種別',
                      sleepSummary?.displayDataKind ?? '読み込み中',
                    ),
                    _buildStatusChip(
                      '取得状態',
                      sleepSummary?.displayAvailability ?? '読み込み中',
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  '設定中のprovider: ${selection.configuredProviderLabel}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  '今回のデータ元: ${sleepSummary?.displaySource ?? '未確認'}',
                ),
                Text(
                  '選択方法: ${selection.displaySelectionMode}',
                ),
                const SizedBox(height: 12),
                if (!selection.configuredProviderSupported) ...[
                  const Text(
                    '未対応のprovider設定です。バックエンドのSLEEP_PROVIDERを確認してください。',
                  ),
                ] else if (selection.isGoogleHealth) ...[
                  _buildGoogleHealthUserSummary(context),
                ] else if (selection.isFitbit) ...[
                  _buildFitbitUserSummary(context),
                ] else ...[
                  const Text(
                    '外部サービスへの接続は不要です。credential不要のデモデータで日次ループを確認できます。',
                  ),
                ],
                if (selection.changeRequiresBackendRestart) ...[
                  const SizedBox(height: 12),
                  const Text(
                    'provider変更はバックエンド設定の更新と再起動後に反映されます。',
                  ),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGoogleHealthUserSummary(BuildContext context) {
    final connectionUx = _googleHealthConnectionUx;

    if (_isRefreshingGoogleHealthConnectionUx && connectionUx == null) {
      return const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LinearProgressIndicator(),
          SizedBox(height: 8),
          Text('Google Healthの接続状態を確認中です。'),
        ],
      );
    }

    if (_googleHealthConnectionUxError != null && connectionUx == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Google Healthの接続状態を確認できませんでした。'),
          const SizedBox(height: 4),
          Text(_googleHealthConnectionUxError!),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: _refreshGoogleHealthConnectionUx,
            icon: const Icon(Icons.refresh),
            label: const Text('状態を再読み込み'),
          ),
        ],
      );
    }

    if (connectionUx == null) {
      return const Text('Google Healthの接続状態を読み込み中です。');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          connectionUx.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(connectionUx.message),
        if (connectionUx.hasUserGuidance) ...[
          const SizedBox(height: 8),
          Text(connectionUx.userGuidance),
        ],
        const SizedBox(height: 8),
        Text('次の操作: ${connectionUx.nextAction}'),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: _isRefreshingGoogleHealthConnectionUx
              ? null
              : _refreshGoogleHealthConnectionUx,
          icon: const Icon(Icons.refresh),
          label: Text(
            _isRefreshingGoogleHealthConnectionUx ? '確認中...' : '状態を再読み込み',
          ),
        ),
      ],
    );
  }

  Widget _buildFitbitUserSummary(BuildContext context) {
    final fitbitStatus = _fitbitStatus;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (fitbitStatus == null) ...[
          const Text('Fitbitのローカル接続状態を確認できませんでした。'),
        ] else ...[
          Text(
            'Fitbit状態: ${fitbitStatus.displayConnectionState}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(fitbitStatus.displayMessage),
        ],
        const SizedBox(height: 8),
        const Text(
          'このproviderは旧Fitbit Web APIの移行参照です。新しい実利用経路にはGoogle Healthを使用してください。',
        ),
        const SizedBox(height: 8),
        const Text(
          '旧Fitbit OAuthの新規接続や実行受け入れは行いません。',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildHealthDataStatusSection(BuildContext context) {
    final fitbitStatus = _fitbitStatus;
    final fitbitConnectResponse = _fitbitConnectResponse;
    final sleepSummary = _sleepSummary;
    final hasRealSleepData = sleepSummary?.isRealData == true &&
        sleepSummary?.available == true;
    final connectionState = fitbitStatus == null
        ? null
        : _formatHealthDataConnectionState(
            fitbitStatus,
            hasRealSleepData: hasRealSleepData,
          );
    final provider = fitbitStatus == null
        ? null
        : _formatHealthDataProvider(
            fitbitStatus,
            sleepSummary,
            hasRealSleepData: hasRealSleepData,
          );
    final statusMessage = fitbitStatus == null
        ? null
        : _formatHealthDataStatusMessage(
            fitbitStatus,
            sleepSummary,
            hasRealSleepData: hasRealSleepData,
          );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Fitbit Operator Status',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (fitbitStatus == null)
          const Text('Fitbitのローカル状態を読み込み中です。')
        else
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
                Text('状態: $connectionState'),
                Text('Provider: $provider'),
                const SizedBox(height: 8),
                Text(statusMessage ?? ''),
                const SizedBox(height: 12),
                FilledButton.tonal(
                  onPressed:
                      _isConnectingHealthData ? null : _connectHealthData,
                  child: Text(
                    _isConnectingHealthData
                        ? '確認中...'
                        : 'Fitbit接続を確認',
                  ),
                ),
                if (_isConnectingHealthData) ...[
                  const SizedBox(height: 12),
                  const LinearProgressIndicator(),
                ],
                if (fitbitConnectResponse != null &&
                    fitbitConnectResponse.ready &&
                    fitbitConnectResponse.connectUrl != null &&
                    fitbitConnectResponse.connectUrl!.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(fitbitConnectResponse.displayMessage),
                  const SizedBox(height: 8),
                  SelectableText(fitbitConnectResponse.connectUrl!),
                  const SizedBox(height: 8),
                  OutlinedButton(
                    onPressed: _openHealthDataConnectUrl,
                    child: const Text('認証ページを開く'),
                  ),
                ],
              ],
            ),
          ),
      ],
    );
  }

  String _formatHealthDataConnectionState(
    FitbitStatus fitbitStatus, {
    required bool hasRealSleepData,
  }) {
    if (hasRealSleepData) {
      return '連携済み';
    }

    return fitbitStatus.displayConnectionState;
  }

  String _formatHealthDataProvider(
    FitbitStatus fitbitStatus,
    SleepSummary? sleepSummary, {
    required bool hasRealSleepData,
  }) {
    if (hasRealSleepData && sleepSummary != null) {
      return sleepSummary.displaySource;
    }

    return fitbitStatus.displayProvider;
  }

  String _formatHealthDataStatusMessage(
    FitbitStatus fitbitStatus,
    SleepSummary? sleepSummary, {
    required bool hasRealSleepData,
  }) {
    if (hasRealSleepData && sleepSummary != null) {
      return '実睡眠データを取得できています。';
    }

    return fitbitStatus.displayMessage;
  }




  Widget _buildGoogleHealthConnectionUxSection(BuildContext context) {
    final connectionUx = _googleHealthConnectionUx;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(
              child: Text(
                'Google Health Operator Connection Details',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),
            OutlinedButton.icon(
              onPressed: _isRefreshingGoogleHealthConnectionUx
                  ? null
                  : _refreshGoogleHealthConnectionUx,
              icon: const Icon(Icons.refresh),
              label: Text(
                _isRefreshingGoogleHealthConnectionUx
                    ? 'Refreshing'
                    : 'Refresh',
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          '開発者・オペレーター向けの詳細です。通常ユーザー向け表示は上のSleep Data Sourceに限定し、token / secret / raw commandは表示しません。',
        ),
        const SizedBox(height: 12),
        Container(
          key: const Key('google-health-operator-details'),
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_isRefreshingGoogleHealthConnectionUx) ...[
                const LinearProgressIndicator(),
                const SizedBox(height: 12),
              ],
              if (_googleHealthConnectionUxError != null) ...[
                Text(
                  _googleHealthConnectionUxError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (connectionUx == null) ...[
                const Text('Google Health接続状態を読み込み中です。'),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('状態', connectionUx.displayState),
                    _buildStatusChip('重要度', connectionUx.displaySeverity),
                    _buildStatusChip(
                      '実API',
                      connectionUx.realApiAllowed ? 'ready' : 'OFF',
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  connectionUx.title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(connectionUx.message),
                if (connectionUx.statusSummary.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('サマリー: ${connectionUx.statusSummary}'),
                ],
                if (connectionUx.hasUserGuidance) ...[
                  const SizedBox(height: 8),
                  Text('ユーザー向け: ${connectionUx.userGuidance}'),
                ],
                if (connectionUx.hasSafeGuardSummary) ...[
                  const SizedBox(height: 8),
                  Text('安全ガード: ${connectionUx.safeGuardSummary}'),
                ],
                if (connectionUx.stateStage.isNotEmpty ||
                    connectionUx.stateReason.isNotEmpty ||
                    connectionUx.hasStateDetails) ...[
                  const SizedBox(height: 12),
                  _buildConnectionStateDetailsCard(context, connectionUx),
                ],
                if (connectionUx.safeModeNote.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('安全メモ: ${connectionUx.safeModeNote}'),
                ],
                const SizedBox(height: 12),
                Text('次の操作: ${connectionUx.nextAction}'),
                if (connectionUx.hasRecoverySteps) ...[
                  const SizedBox(height: 12),
                  _buildConnectionGuidanceCard(context, connectionUx),
                ],
                if (connectionUx.hasConnectionActions) ...[
                  const SizedBox(height: 12),
                  _buildConnectionActionGroupCard(
                    context,
                    title: '接続 / 継続',
                    description: '接続開始・安全継続・設定確認に関するアクションです。',
                    actions: connectionUx.displayConnectionActions,
                  ),
                ],
                if (connectionUx.hasRetryActions) ...[
                  const SizedBox(height: 12),
                  _buildConnectionActionGroupCard(
                    context,
                    title: '再確認 / Retry',
                    description: '設定変更やOAuth完了後に状態を読み直すためのアクションです。',
                    actions: connectionUx.retryActions,
                  ),
                ],
                if (connectionUx.hasResetActions) ...[
                  const SizedBox(height: 12),
                  _buildConnectionActionGroupCard(
                    context,
                    title: 'リセット',
                    description: 'scope変更や実API検証後など、ローカル状態を戻す必要がある時だけ使います。',
                    actions: connectionUx.resetActions,
                  ),
                ],
                if (connectionUx.hasDeveloperPanel) ...[
                  const SizedBox(height: 12),
                  _buildConnectionDeveloperDetailsCard(context, connectionUx),
                ],
              ],
            ],
          ),
        ),
      ],
    );
  }


  Widget _buildConnectionStateDetailsCard(
    BuildContext context,
    GoogleHealthConnectionUx connectionUx,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '状態の理由',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          if (connectionUx.stateStage.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text('段階: ${connectionUx.stateStage}'),
          ],
          if (connectionUx.stateReason.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text('理由: ${connectionUx.stateReason}'),
          ],
          if (connectionUx.hasStateDetails) ...[
            const SizedBox(height: 8),
            for (final detail in connectionUx.stateDetails) ...[
              _buildConnectionStateDetailRow(detail),
              const SizedBox(height: 4),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildConnectionStateDetailRow(
    GoogleHealthConnectionUxStateDetail detail,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildStatusChip(detail.label, detail.value),
            _buildStatusChip('状態', detail.displayTone),
          ],
        ),
        if (detail.guidance.isNotEmpty) ...[
          const SizedBox(height: 2),
          Text('補足: ${detail.guidance}'),
        ],
      ],
    );
  }

  Widget _buildConnectionGuidanceCard(
    BuildContext context,
    GoogleHealthConnectionUx connectionUx,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '接続ガイド',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          for (var index = 0; index < connectionUx.recoverySteps.length; index++)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text('${index + 1}. ${connectionUx.recoverySteps[index]}'),
            ),
        ],
      ),
    );
  }

  Widget _buildConnectionDeveloperDetailsCard(
    BuildContext context,
    GoogleHealthConnectionUx connectionUx,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '開発者向け詳細',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          const Text(
            '通常ユーザーには不要なready状態だけをまとめます。token / secret / path / raw command は表示しません。',
          ),
          if (connectionUx.hasDeveloperSummary) ...[
            const SizedBox(height: 8),
            Text('サマリー: ${connectionUx.developerSummary}'),
          ],
          if (connectionUx.developerNote != null) ...[
            const SizedBox(height: 8),
            Text('開発メモ: ${connectionUx.developerNote}'),
          ],
          const SizedBox(height: 8),
          _buildDiagnosticRow('Provider', connectionUx.displayProvider),
          _buildDiagnosticRow(
            'Sleep provider',
            connectionUx.displaySleepProvider,
          ),
          _buildDiagnosticRow(
            'Token stored',
            _formatReady(connectionUx.tokenStored),
          ),
          _buildDiagnosticRow(
            'Reconnect recommended',
            _formatReady(connectionUx.reconnectRecommended),
          ),
          _buildDiagnosticRow(
            'Real API safety',
            connectionUx.displaySafeRealApiState,
          ),
          _buildDiagnosticRow(
            'Can start OAuth',
            _formatReady(connectionUx.canStartOauth),
          ),
          _buildDiagnosticRow(
            'Can use safe preview',
            _formatReady(connectionUx.canUseSafePreview),
          ),
          _buildDiagnosticRow(
            'Can use guarded real request',
            _formatReady(connectionUx.canUseGuardedRealRequest),
          ),
          _buildDiagnosticRow(
            'User visible details limited',
            _formatReady(connectionUx.userVisibleDetailsLimited),
          ),
          if (connectionUx.hasDeveloperDetails) ...[
            const SizedBox(height: 8),
            for (final detail in connectionUx.developerDetails) ...[
              _buildConnectionStateDetailRow(detail),
              const SizedBox(height: 4),
            ],
          ],
        ],
      ),
    );
  }


  Widget _buildConnectionActionGroupCard(
    BuildContext context, {
    required String title,
    required String description,
    required List<GoogleHealthConnectionUxAction> actions,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(description),
          const SizedBox(height: 8),
          for (final action in actions) ...[
            _buildConnectionActionCard(context, action),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }

  Widget _buildConnectionActionCard(
    BuildContext context,
    GoogleHealthConnectionUxAction action,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${action.displayActionType}: ${action.label}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(action.description),
          if (action.guidance.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text('ガイド: ${action.guidance}'),
          ],
          if (action.expectedResult.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text('結果: ${action.expectedResult}'),
          ],
          const SizedBox(height: 4),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: [
              _buildStatusChip('実行可能', _formatReady(action.enabled)),
              _buildStatusChip('安全性', action.displayRiskLevel),
              if (action.isDestructive)
                _buildStatusChip('注意', 'ローカル状態を変更'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildGoogleHealthDeveloperSection(BuildContext context) {
    final diagnostics = _googleHealthDiagnostics;
    final preflight = _googleHealthPreflight;
    final selfCheck = _googleHealthSelfCheck;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(
              child: Text(
                'Google Health Developer Check',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),
            OutlinedButton.icon(
              onPressed: _isRefreshingGoogleHealthChecks
                  ? null
                  : _refreshGoogleHealthChecks,
              icon: const Icon(Icons.refresh),
              label: Text(
                _isRefreshingGoogleHealthChecks ? 'Refreshing' : 'Refresh',
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          '実API接続前の確認用です。secret / token / raw health payload は表示しません。',
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
              if (_isRefreshingGoogleHealthChecks) ...[
                const LinearProgressIndicator(),
                const SizedBox(height: 12),
              ],
              if (_googleHealthDebugError != null) ...[
                Text(
                  _googleHealthDebugError!,
                  style: const TextStyle(color: Colors.red),
                ),
              ] else if (diagnostics == null ||
                  preflight == null ||
                  selfCheck == null) ...[
                const Text(
                  'Google Health diagnostics / preflight / self-check を読み込み中です。',
                ),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildStatusChip('Diagnostics', diagnostics.displayStatus),
                    _buildStatusChip(
                      'OAuth',
                      _formatReady(diagnostics.readyForOauth),
                    ),
                    _buildStatusChip(
                      'Sleep Provider',
                      _formatReady(diagnostics.readyForSleepProvider),
                    ),
                    _buildStatusChip(
                      'Real API',
                      _formatReady(diagnostics.readyForRealApiRequest),
                    ),
                    _buildStatusChip('Preflight', preflight.displayStatus),
                    _buildStatusChip(
                      'Self Check',
                      selfCheck.displaySourceStatus,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildDiagnosticRow('Provider', diagnostics.provider),
                _buildDiagnosticRow(
                  'Sleep provider',
                  diagnostics.config.sleepProvider,
                ),
                _buildDiagnosticRow(
                  'OAuth configured',
                  _formatReady(diagnostics.config.oauthConfigured),
                ),
                _buildDiagnosticRow(
                  'Credentials file configured',
                  _formatReady(diagnostics.config.credentialsFileConfigured),
                ),
                _buildDiagnosticRow(
                  'Credentials loaded',
                  _formatReady(diagnostics.config.credentialsLoaded),
                ),
                _buildDiagnosticRow(
                  'Redirect URI configured',
                  _formatReady(diagnostics.config.redirectUriConfigured),
                ),
                _buildDiagnosticRow(
                  'Token stored',
                  _formatReady(diagnostics.token.stored),
                ),
                _buildDiagnosticRow(
                  'Refresh token',
                  _formatReady(diagnostics.token.hasRefreshToken),
                ),
                _buildDiagnosticRow(
                  'Token refresh recommended',
                  _formatOptionalReady(diagnostics.token.refreshRecommended),
                ),
                _buildDiagnosticRow(
                  'Real token exchange enabled',
                  _formatReady(diagnostics.config.realTokenExchangeEnabled),
                ),
                _buildDiagnosticRow(
                  'Real token refresh enabled',
                  _formatReady(diagnostics.config.realTokenRefreshEnabled),
                ),
                _buildDiagnosticRow(
                  'Real API requests enabled',
                  _formatReady(diagnostics.config.realApiRequestsEnabled),
                ),
                _buildDiagnosticRow(
                  'Guard requested real API',
                  _formatReady(diagnostics.runtimeGuard.realApiRequested),
                ),
                _buildDiagnosticRow(
                  'Guard allows real API',
                  _formatReady(diagnostics.runtimeGuard.realApiAllowed),
                ),
                _buildDiagnosticRow(
                  'API base URL is placeholder',
                  _formatReady(diagnostics.runtimeGuard.apiBaseUrlPlaceholder),
                ),
                _buildDiagnosticRow(
                  'Sleep API path configured',
                  _formatReady(diagnostics.runtimeGuard.sleepApiPathConfigured),
                ),
                _buildDiagnosticRow(
                  'API timeout valid',
                  _formatReady(diagnostics.runtimeGuard.apiTimeoutValid),
                ),
                _buildDiagnosticRow(
                  'Preflight ready for OAuth',
                  _formatReady(preflight.readyForOauth),
                ),
                _buildDiagnosticRow(
                  'Preflight auth callback ready',
                  _formatReady(preflight.readyForAuthCallback),
                ),
                _buildDiagnosticRow(
                  'Preflight token refresh ready',
                  _formatReady(preflight.readyForTokenRefresh),
                ),
                _buildDiagnosticRow(
                  'Preflight real API ready',
                  _formatReady(preflight.readyForRealApiRequest),
                ),
                _buildDiagnosticRow(
                  'Credentials file exists',
                  _formatReady(preflight.credentials.credentialsFileExists),
                ),
                _buildDiagnosticRow(
                  'Client ID configured',
                  _formatReady(preflight.credentials.clientIdConfigured),
                ),
                _buildDiagnosticRow(
                  'Client secret configured',
                  _formatReady(preflight.credentials.clientSecretConfigured),
                ),
                _buildDiagnosticRow(
                  'Redirect URI registered',
                  _formatOptionalReady(
                    preflight.credentials.redirectUriRegistered,
                  ),
                ),
                _buildDiagnosticRow(
                  'OAuth scopes configured',
                  _formatReady(preflight.oauth.scopesConfigured),
                ),
                _buildDiagnosticRow(
                  'OAuth scope count',
                  preflight.oauth.scopeCount.toString(),
                ),
                _buildDiagnosticRow(
                  'OAuth URL ready',
                  _formatReady(preflight.oauth.authUrlReady),
                ),
                _buildDiagnosticRow(
                  'OAuth state ready',
                  _formatReady(preflight.oauth.stateReady),
                ),
                _buildDiagnosticRow(
                  'Preflight token stored',
                  _formatReady(preflight.token.stored),
                ),
                _buildDiagnosticRow(
                  'Preflight refresh recommended',
                  _formatOptionalReady(preflight.token.refreshRecommended),
                ),
                _buildDiagnosticRow(
                  'Preflight real API allowed',
                  _formatReady(preflight.api.realApiRequestsAllowed),
                ),
                _buildDiagnosticRow(
                  'Self-check target date',
                  selfCheck.targetDate.isEmpty ? '-' : selfCheck.targetDate,
                ),
                _buildDiagnosticRow(
                  'Self-check session token',
                  _formatOptionalReady(selfCheck.session?.tokenAvailable),
                ),
                _buildDiagnosticRow(
                  'Self-check refresh checked',
                  _formatOptionalReady(selfCheck.session?.refreshChecked),
                ),
                _buildDiagnosticRow(
                  'Self-check API requested',
                  _formatOptionalReady(selfCheck.session?.apiRequested),
                ),
                _buildDiagnosticRow(
                  'Self-check API attempted',
                  _formatOptionalReady(selfCheck.session?.api?.attempted),
                ),
                _buildDiagnosticRow(
                  'Self-check HTTP status',
                  selfCheck.session?.api?.statusCode?.toString() ?? '-',
                ),
                _buildDiagnosticRow(
                  'Real HTTP attempted',
                  _formatReady(selfCheck.realHttpAttempted),
                ),
                _buildDiagnosticRow(
                  'Safe for /sleep/summary',
                  _formatReady(selfCheck.safeToUseSleepSummary),
                ),
                const SizedBox(height: 12),
                Text('Diagnostics reason: ${diagnostics.displayReason}'),
                const SizedBox(height: 8),
                Text('Preflight reason: ${preflight.displayReason}'),
                const SizedBox(height: 8),
                Text('Self-check reason: ${selfCheck.displayReason}'),
                const SizedBox(height: 8),
                Text('Next action: ${_firstNonEmpty([
                  preflight.displayNextAction,
                  diagnostics.displayNextAction,
                  selfCheck.displayNextAction,
                ])}'),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatusChip(String label, String value) {
    return Chip(label: Text('$label: $value'));
  }

  Widget _buildDiagnosticRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Text('$label: $value'),
    );
  }

  String _formatReady(bool value) {
    return value ? 'ready' : 'not ready';
  }

  String _formatOptionalReady(bool? value) {
    if (value == null) {
      return '-';
    }
    return _formatReady(value);
  }

  String _firstNonEmpty(List<String?> values) {
    for (final value in values) {
      if (value != null && value.trim().isNotEmpty) {
        return value;
      }
    }
    return '-';
  }

  Widget _buildSleepSummarySection(BuildContext context) {
    final sleepSummary = _sleepSummary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Sleep Summary',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (sleepSummary == null)
          const Text('睡眠サマリーを読み込み中です。')
        else
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
                Row(
                  children: [
                    Expanded(child: Text('日付: ${sleepSummary.date}')),
                    Chip(label: Text(sleepSummary.displayDataKind)),
                  ],
                ),
                const SizedBox(height: 4),
                Text('データ元: ${sleepSummary.displaySource}'),
                Text('状態: ${sleepSummary.displayAvailability}'),
                const SizedBox(height: 8),
                if (sleepSummary.available) ...[
                  Text(
                    '睡眠時間: ${sleepSummary.formattedTotalSleep}',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text('睡眠時間帯: ${sleepSummary.formattedSleepWindow}'),
                  const SizedBox(height: 8),
                  Text('睡眠効率: ${sleepSummary.efficiency ?? '-'}%'),
                  Text('深い睡眠: ${sleepSummary.deepSleepMinutes ?? '-'}分'),
                  Text('REM睡眠: ${sleepSummary.remSleepMinutes ?? '-'}分'),
                  Text('覚醒時間: ${sleepSummary.awakeMinutes ?? '-'}分'),
                  if (sleepSummary.message != null &&
                      sleepSummary.message!.trim().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(sleepSummary.message!),
                  ],
                ] else ...[
                  Text(sleepSummary.displayUnavailableMessage),
                  const SizedBox(height: 8),
                  Text('理由: ${sleepSummary.displayUnavailableReason}'),
                  const SizedBox(height: 8),
                  const Text(
                    '睡眠データがない場合でも、今の気分をもとにアドバイスできます。',
                  ),
                ],
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildCharacterSection(BuildContext context) {
    final selectedCharacter = _selectedCharacter;
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Character Choice',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          "キャラクターを選ぶと、Today's Loop と作成前確認に反映されます。話し方やアドバイスの雰囲気もここで確認します。",
        ),
        const SizedBox(height: 12),
        if (_isLoading)
          const Center(child: CircularProgressIndicator())
        else if (_characters.isEmpty)
          const Text('キャラクター候補を読み込めませんでした。')
        else ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: colorScheme.surfaceContainerHighest,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '選択中のキャラクター',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                Center(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.asset(
                      CharacterAssetCatalog.imageForCharacter(
                        selectedCharacter?.characterId ?? '',
                      ),
                      key: const ValueKey<String>(
                        'selected-character-image',
                      ),
                      width: 180,
                      height: 180,
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return _buildMissingAssetPlaceholder(
                          key: const ValueKey<String>(
                            'selected-character-fallback-image',
                          ),
                          width: 180,
                          height: 180,
                        );
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                _buildDiagnosticRow(
                  'Name',
                  selectedCharacter?.displayName ?? '未選択',
                ),
                if (selectedCharacter != null) ...[
                  _buildDiagnosticRow(
                    'Personality',
                    selectedCharacter.personalityType,
                  ),
                  _buildDiagnosticRow(
                    'Speaking',
                    selectedCharacter.speakingStyle,
                  ),
                  _buildDiagnosticRow(
                    'Advice style',
                    selectedCharacter.adviceStyle,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'このキャラクターの話し方で、今日の気分と睡眠コンテキストをもとにアドバイスします。',
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          RadioGroup<CharacterPreset>(
            groupValue: selectedCharacter,
            onChanged: (value) {
              setState(() {
                _selectedCharacter = value;
              });
            },
            child: Column(
              children: [
                ..._characters.map(
                  (character) => RadioListTile<CharacterPreset>(
                    value: character,
                    title: Text(character.displayName),
                    subtitle: Text(
                      '${character.description}\n${character.adviceStyle}',
                    ),
                    isThreeLine: true,
                    secondary: SizedBox.square(
                      dimension: 56,
                      child: ClipOval(
                        child: Image.asset(
                          CharacterAssetCatalog.imageForCharacter(
                            character.characterId,
                          ),
                          key: ValueKey<String>(
                            'character-option-image-${character.characterId}',
                          ),
                          width: 56,
                          height: 56,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return _buildMissingAssetPlaceholder(
                              width: 56,
                              height: 56,
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildVisualAssetPreviewSection(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Visual Asset Preview',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'v2.0.0で受け入れ済みの背景画像とフォールバック画像を、Web UI上で確認するための表示です。',
        ),
        const SizedBox(height: 12),
        LayoutBuilder(
          builder: (context, constraints) {
            final cardWidth = constraints.maxWidth >= 720
                ? (constraints.maxWidth - 12) / 2
                : constraints.maxWidth;
            return Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _buildAssetPreviewCard(
                  context,
                  keyName: 'morning-background-preview',
                  title: 'Morning room',
                  assetPath: CharacterAssetCatalog.morningBackground,
                  width: cardWidth,
                ),
                _buildAssetPreviewCard(
                  context,
                  keyName: 'night-background-preview',
                  title: 'Night room',
                  assetPath: CharacterAssetCatalog.nightBackground,
                  width: cardWidth,
                ),
              ],
            );
          },
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: colorScheme.surfaceContainerHighest,
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final image = Image.asset(
                CharacterAssetCatalog.fallbackCharacter,
                key: const ValueKey<String>('fallback-character-preview'),
                width: 72,
                height: 72,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  return _buildMissingAssetPlaceholder(
                    width: 72,
                    height: 72,
                  );
                },
              );
              const description = Text(
                'Character fallback — キャラクター画像を解決できない場合に使う、受け入れ済みのフォールバック画像です。',
              );

              if (constraints.maxWidth < 420) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    image,
                    const SizedBox(height: 8),
                    description,
                  ],
                );
              }

              return Row(
                children: [
                  image,
                  const SizedBox(width: 12),
                  const Expanded(child: description),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildMissingAssetPlaceholder({
    Key? key,
    required double width,
    required double height,
  }) {
    return SizedBox(
      key: key,
      width: width,
      height: height,
      child: const ColoredBox(
        color: Color(0x1F808080),
        child: Center(
          child: Icon(Icons.image_not_supported_outlined),
        ),
      ),
    );
  }

  Widget _buildAssetPreviewCard(
    BuildContext context, {
    required String keyName,
    required String title,
    required String assetPath,
    required double width,
  }) {
    return SizedBox(
      width: width,
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Image.asset(
                assetPath,
                key: ValueKey<String>(keyName),
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return _buildMissingAssetPlaceholder(
                    width: double.infinity,
                    height: double.infinity,
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(
                title,
                style: Theme.of(context).textTheme.titleSmall,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMoodSection(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Mood',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '今日の気分をひとつ選びます。選択内容は Daily Loop overview とアドバイス作成前の確認に反映されます。',
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: colorScheme.surfaceContainerHighest,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '選択中: ${_formatMoodLabel(_selectedMood)}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(_formatMoodSupportMessage(_selectedMood)),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildMoodChoiceChip(
                    mood: 'energetic',
                    emoji: '☀️',
                  ),
                  _buildMoodChoiceChip(
                    mood: 'normal',
                    emoji: '🌿',
                  ),
                  _buildMoodChoiceChip(
                    mood: 'tired',
                    emoji: '😪',
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text('Advice focus: ${_formatMoodAdviceIntent(_selectedMood)}'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMoodChoiceChip({
    required String mood,
    required String emoji,
  }) {
    final copy = _resolveMoodChoiceCopy(mood);

    return ChoiceChip(
      label: Text('$emoji ${copy.label}'),
      selected: _selectedMood == mood,
      onSelected: (_) {
        setState(() {
          _selectedMood = mood;
        });
      },
    );
  }

  Widget _buildAdviceActionSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '上の内容で今日のアドバイスを作成します。作成したアドバイスはこの画面ですぐ確認でき、履歴にも DailyRecord として残ります。',
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
              const Text(
                '作成前の確認',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildDiagnosticRow('Sleep', _formatAdviceReadinessSleepStatus()),
              _buildDiagnosticRow('Mood', _formatMoodLabel(_selectedMood)),
              _buildDiagnosticRow(
                'Advice focus',
                _formatMoodAdviceIntent(_selectedMood),
              ),
              _buildDiagnosticRow(
                'Character',
                _selectedCharacter?.displayName ?? '未選択',
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        Center(
          child: ElevatedButton(
            onPressed: _isCreatingAdvice ? null : _createAdvice,
            child: Text(
              _isCreatingAdvice ? '作成中...' : '今日のアドバイスを作る',
            ),
          ),
        ),
        if (_isCreatingAdvice) ...[
          const SizedBox(height: 12),
          const LinearProgressIndicator(),
        ],
      ],
    );
  }

  Widget _buildAdviceSection(BuildContext context) {
    final adviceResponse = _adviceResponse;

    if (adviceResponse == null) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Advice',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        const Text('作成結果です。必要なら気分やキャラクターを変えて、もう一度作り直せます。'),
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
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildStatusChip('Mood', _formatMoodLabel(_selectedMood)),
                  _buildStatusChip('Character', adviceResponse.characterName),
                  _buildStatusChip('DailyRecord', '保存対象'),
                  if (adviceResponse.source?.hasReportHandoff ?? false)
                    _buildStatusChip(
                      'Report context',
                      adviceResponse.source!.displayReportHandoffLabel,
                    ),
                ],
              ),
              const SizedBox(height: 12),
              _buildAdviceContextNote(context),
              if (adviceResponse.source?.hasReportHandoff ?? false) ...[
                const SizedBox(height: 12),
                _buildReportHandoffContextCard(
                  context,
                  adviceResponse.source!.reportHandoff!,
                ),
              ],
              const SizedBox(height: 12),
              Text(_formatAdviceMessage(adviceResponse.message)),
              if (adviceResponse.source != null) ...[
                const SizedBox(height: 12),
                _buildAdviceSourceDebugCard(context, adviceResponse.source!),
              ],
            ],
          ),
        ),
      ],
    );
  }



  Widget _buildReportHandoffContextCard(
    BuildContext context,
    ReportHandoffContext reportHandoff,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Report context',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(reportHandoff.displayAdviceContextLabel),
          const SizedBox(height: 4),
          Text(reportHandoff.displaySafetyNote),
          const SizedBox(height: 8),
          _buildDiagnosticRow('記録状態', reportHandoff.displayQuality),
          _buildDiagnosticRow(
            '範囲',
            reportHandoff.displayDateRange.replaceFirst('範囲: ', ''),
          ),
          _buildDiagnosticRow(
            '保存記録',
            reportHandoff.displayRecordCoverage.replaceFirst('保存記録: ', ''),
          ),
          _buildDiagnosticRow('データ元', reportHandoff.displaySource),
          _buildDiagnosticRow('集計範囲', reportHandoff.displayScope),
          const SizedBox(height: 8),
          Text(reportHandoff.displayUserFacingSummary),
        ],
      ),
    );
  }

  Widget _buildAdviceSourceDebugCard(
    BuildContext context,
    AdviceSource source,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Advice Source',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              Chip(label: Text('Engine: ${source.displayEngine}')),
              Chip(label: Text('DRC: ${source.displayDrcCharacter}')),
              if (source.hasFrameworkMetadata) ...[
                Chip(label: Text('FW preset: ${source.displayFrameworkPreset}')),
                Chip(
                  label: Text(
                    'FW character: ${source.displayFrameworkCharacter}',
                  ),
                ),
                Chip(
                  label: Text(
                    'FW source: ${source.displayFrameworkCharacterSource}',
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }


  Widget _buildPostAdviceChatSection(BuildContext context) {
    final adviceResponse = _adviceResponse;
    final session = _postAdviceChatSession;

    if (adviceResponse == null) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Post-advice Chat',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text('少し話す？ アドバイスを見たあと、必要なら同じキャラクターと軽く雑談できます。'),
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
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ElevatedButton.icon(
                    onPressed: _isStartingPostAdviceChat || session != null
                        ? null
                        : _startPostAdviceChat,
                    icon: _isStartingPostAdviceChat
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.chat_bubble_outline),
                    label: const Text('少し話す'),
                  ),
                  OutlinedButton.icon(
                    onPressed:
                        _isStartingPostAdviceChat ? null : _skipPostAdviceChat,
                    icon: const Icon(Icons.check_circle_outline),
                    label: const Text('今日はここまで'),
                  ),
                ],
              ),
              if (_postAdviceChatSkipped) ...[
                const SizedBox(height: 12),
                const Text(
                  '今日はここまでを選びました。アドバイスはこのままDailyRecord / Historyで確認できます。',
                ),
              ],
              if (_postAdviceChatError != null) ...[
                const SizedBox(height: 12),
                Text(
                  _postAdviceChatError!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              if (session != null) ...[
                const SizedBox(height: 12),
                _buildDiagnosticRow('Chat session', session.sessionId),
                _buildDiagnosticRow('Chat source', session.source.displayLabel),
                _buildDiagnosticRow('Status', session.status),
                const SizedBox(height: 12),
                ...session.messages.map(_buildPostAdviceChatMessage),
                const SizedBox(height: 12),
                TextField(
                  controller: _postAdviceChatMessageController,
                  decoration: const InputDecoration(
                    labelText: 'メッセージ',
                    hintText: '例: もう少しゆるく過ごすには？',
                    border: OutlineInputBorder(),
                  ),
                  minLines: 1,
                  maxLines: 3,
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerLeft,
                  child: OutlinedButton.icon(
                    onPressed: _isSendingPostAdviceChatMessage
                        ? null
                        : _sendPostAdviceChatMessage,
                    icon: _isSendingPostAdviceChatMessage
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send),
                    label: const Text('送信'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPostAdviceChatMessage(ChatMessage message) {
    final isUser = message.role == 'user';
    final roleLabel = isUser ? 'あなた' : 'キャラクター';

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: isUser
            ? Colors.blue.withValues(alpha: 0.08)
            : Colors.green.withValues(alpha: 0.08),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            roleLabel,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(message.content),
        ],
      ),
    );
  }


  Widget _buildDailyRecordHandoffSection(BuildContext context) {
    final adviceResponse = _adviceResponse;

    if (adviceResponse == null) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'DailyRecord / History',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '作成したアドバイスは DailyRecord として履歴に残る前提です。あとから見返す流れまで確認できます。',
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
              const Text(
                '保存と振り返り',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildDiagnosticRow('保存ステータス', 'DailyRecord 保存対象'),
              _buildDiagnosticRow('Mood', _formatMoodLabel(_selectedMood)),
              _buildDiagnosticRow('Character', adviceResponse.characterName),
              _buildDiagnosticRow('Sleep context', _formatAdviceReadinessSleepStatus()),
              const SizedBox(height: 12),
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => HistoryScreen(
                          apiClient: widget.apiClient,
                        ),
                      ),
                    );
                  },
                  icon: const Icon(Icons.history),
                  label: const Text('履歴で確認する'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }


  Widget _buildDailyLoopCompletionSection(BuildContext context) {
    final adviceResponse = _adviceResponse;

    if (adviceResponse == null) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Daily Loop Complete',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          '今日の睡眠・気分・キャラクター・アドバイス確認まで完了しました。次は履歴で振り返れます。',
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
              const Text(
                '完了サマリー',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildDiagnosticRow('完了ステップ', '4 / 4'),
              _buildDiagnosticRow('Advice', adviceResponse.characterName),
              _buildDiagnosticRow('次のおすすめ', 'History で今日の記録を振り返る'),
              _buildDiagnosticRow('明日の入口', '睡眠と気分を確認してもう一度作る'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildErrorSection() {
    final errorMessage = _errorMessage;

    if (errorMessage == null) {
      return const SizedBox.shrink();
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Daily loop error',
            style: TextStyle(
              color: Colors.red,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            errorMessage,
            style: const TextStyle(color: Colors.red),
          ),
          const SizedBox(height: 8),
          const Text(
            '入力内容は残したまま、バックエンド情報だけ再読み込みできます。',
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: _isLoading ? null : _loadInitialData,
            icon: const Icon(Icons.refresh),
            label: const Text('Reload backend data'),
          ),
        ],
      ),
    );
  }

  String _formatAdviceMessage(String message) {
    return message
        .replaceAll('**', '')
        .replaceAll(RegExp(r'^\s*\*\s+', multiLine: true), '・');
  }

  Widget _buildAdviceContextNote(BuildContext context) {
    final sleepSummary = _sleepSummary;

    if (sleepSummary == null) {
      return const Text('睡眠サマリーを読み込み中のため、気分を中心にアドバイスしています。');
    }

    final label = _formatAdviceContextLabel(sleepSummary);
    final detail = sleepSummary.available
        ? '睡眠時間 ${sleepSummary.formattedTotalSleep}'
        : '睡眠データ未取得 / ${sleepSummary.displayUnavailableReason}';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(detail),
        ],
      ),
    );
  }


  String _formatAdviceContextLabel(SleepSummary sleepSummary) {
    if (!sleepSummary.available) {
      return '睡眠データ未取得のため気分を中心に反映';
    }

    if (sleepSummary.isRealData) {
      return '実睡眠データを反映';
    }

    return 'デモ/代替データを反映';
  }

  bool _isVoiceOutputPlaybackCandidate(
    VoiceOutputDemoRequestResponse response,
  ) {
    final handoffKind = response.audioHandoffKind.trim();
    return response.isGenerated &&
        response.audioReady &&
        response.hasAudioHandoff &&
        (handoffKind == 'url' || handoffKind == 'artifact_ref');
  }

  bool _canOpenVoiceOutputAudioUrl(VoiceOutputDemoRequestResponse response) {
    final audioUrl = response.audioUrl?.trim();
    return _isVoiceOutputPlaybackCandidate(response) &&
        response.audioHandoffKind.trim() == 'url' &&
        audioUrl != null &&
        audioUrl.isNotEmpty;
  }

  String _formatVoiceOutputPlaybackCandidate(
    VoiceOutputDemoRequestResponse response,
  ) {
    final requestState = response.displayRequestState;
    final handoffKind = response.audioHandoffKind.trim();

    if (_isVoiceOutputPlaybackCandidate(response)) {
      if (handoffKind == 'url') {
        return 'playable URL handoff (operator confirmation required)';
      }

      return 'artifact ref handoff (resolver required before browser playback)';
    }

    if (!response.isGenerated) {
      return 'non-playable (not generated: $requestState)';
    }

    if (!response.audioReady) {
      return 'non-playable (generated but audio_ready=false)';
    }

    if (!response.hasAudioHandoff) {
      return 'non-playable (missing or invalid handoff: ${response.displayAudioHandoffKind})';
    }

    return 'non-playable (unsupported handoff: ${response.displayAudioHandoffKind})';
  }

  Uri? _resolveVoiceOutputAudioUri(VoiceOutputDemoRequestResponse response) {
    if (!_canOpenVoiceOutputAudioUrl(response)) {
      return null;
    }

    final audioUrl = response.audioUrl!.trim();

    try {
      final parsedAudioUri = Uri.parse(audioUrl);
      if (parsedAudioUri.hasScheme) {
        return parsedAudioUri;
      }

      return Uri.parse(widget.apiClient.baseUrl).resolve(audioUrl);
    } on FormatException {
      return null;
    }
  }

  Future<void> _openVoiceOutputAudioUrl(
    VoiceOutputDemoRequestResponse response,
  ) async {
    final uri = _resolveVoiceOutputAudioUri(response);

    if (uri == null) {
      setState(() {
        _voiceOutputDemoError = '音声URLを開けませんでした。';
      });
      return;
    }

    try {
      final launched = await launchUrl(
        uri,
        mode: LaunchMode.externalApplication,
      );

      if (!launched) {
        setState(() {
          _voiceOutputDemoError = '音声URLを開けませんでした。';
        });
      }
    } catch (error) {
      setState(() {
        _voiceOutputDemoError = error.toString();
      });
    }
  }

  String _formatUserFacingError(Object error) {
    final message = error.toString();

    if (message.contains('Connection refused') ||
        message.contains('Failed host lookup') ||
        message.contains('SocketException')) {
      return 'バックエンドに接続できませんでした。backend が起動しているか確認してください。';
    }

    if (message.contains('TimeoutException')) {
      return 'バックエンドの応答が遅くなっています。少し待ってからもう一度試してください。';
    }

    return 'エラーが発生しました: $message';
  }

  Future<void> _openHealthDataConnectUrl() async {
    final connectUrl = _healthDataConnectUrl;

    if (connectUrl == null || connectUrl.isEmpty) {
      setState(() {
        _errorMessage = 'ヘルスデータ連携URLはまだ準備できていません。';
      });
      return;
    }

    final uri = Uri.parse(connectUrl);

    try {
      final launched = await launchUrl(
        uri,
        mode: LaunchMode.externalApplication,
      );

      if (!launched) {
        setState(() {
          _errorMessage = 'ヘルスデータ連携URLを開けませんでした。';
        });
      }
    } catch (error) {
      setState(() {
        _errorMessage = error.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Rhythm Companion'),
        actions: [
          TextButton.icon(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => HistoryScreen(apiClient: widget.apiClient),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('History'),
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Card(
            margin: const EdgeInsets.all(24),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildBackendConnectionSection(),

                    const SizedBox(height: 24),
                    _buildDailyLoopOverviewSection(context),

                    const SizedBox(height: 24),
                    _buildDailyLoopStatusSection(context),

                    const SizedBox(height: 24),
                    _buildDailyLoopDemoContextSection(context),

                    const SizedBox(height: 24),
                    _buildCharacterSection(context),

                    const SizedBox(height: 24),
                    _buildVisualAssetPreviewSection(context),

                    const SizedBox(height: 24),
                    _buildSleepDataSourceSection(context),

                    const SizedBox(height: 24),
                    _buildSleepSummarySection(context),

                    const SizedBox(height: 24),
                    _buildMoodSection(context),

                    const SizedBox(height: 24),
                    _buildAdviceActionSection(context),

                    if (_errorMessage != null) ...[
                      const SizedBox(height: 24),
                      _buildErrorSection(),
                    ],

                    if (_adviceResponse != null) ...[
                      const SizedBox(height: 24),
                      _buildAdviceSection(context),

                      const SizedBox(height: 24),
                      _buildPostAdviceChatSection(context),

                      const SizedBox(height: 24),
                      _buildDailyRecordHandoffSection(context),

                      const SizedBox(height: 24),
                      _buildDailyLoopCompletionSection(context),
                    ],

                    const SizedBox(height: 32),
                    const Divider(),

                    const SizedBox(height: 24),
                    _buildAdvancedDemoToolsHeading(),

                    const SizedBox(height: 24),
                    _buildDemoStatusSection(context),

                    const SizedBox(height: 24),
                    _buildVoiceInputDemoSection(context),

                    const SizedBox(height: 24),
                    _buildVoiceOutputDemoSection(context),
                    const SizedBox(height: 32),
                    _buildMotionDemoSection(context),

                    if (_sleepProviderSelectionStatus?.isFitbit == true) ...[
                      const SizedBox(height: 24),
                      _buildHealthDataStatusSection(context),
                    ],

                    const SizedBox(height: 24),
                    _buildGoogleHealthConnectionUxSection(context),

                    const SizedBox(height: 24),
                    _buildGoogleHealthDeveloperSection(context),

                    const SizedBox(height: 24),
                    Center(
                      child: TextButton(
                        onPressed: _isLoading ? null : _loadInitialData,
                        child: const Text('Reload backend data'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
