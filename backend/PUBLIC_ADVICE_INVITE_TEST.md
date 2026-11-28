# 公開候補アドバイス API の招待制ローカル検証

ローカル検証では PostgreSQL にトークンの SHA-256 と管理用 ID、参加者 ID、有効期限、失効日時を保持する。Bearer トークンは256ビットの乱数から発行し、平文は発行時に一度だけ表示する。個別に失効させるときは管理用 ID を使う。同じ参加者 ID で再発行すると利用枠を引き継ぐ。古いトークンを無効にする場合は、その管理用 ID で個別に失効させる。

既存の日次記録用 SQLite は単一ホスト上のローカルファイルを前提とする。日次記録と認証情報を分け、独立したワーカーがトランザクションを共有できる PostgreSQL を今回の候補とした。Redis を採用する場合は、両方の枠をまとめて確保する処理に加え、再起動時の永続化と復旧設定が必要になる。本番のストアと配置先は未決定。

## ローカル起動

ローカルの PostgreSQL に検証専用 DB を作成し、すべての検証ワーカーで同じ DSN と上限値を使う。次は `backend` で実行する PowerShell の例。DSN にパスワードが必要な場合はローカルの秘密管理から設定し、端末やリポジトリに渡さない。

```powershell
python -m pip install -r requirements.txt -r requirements-public-advice-postgres.txt
$env:DRC_PUBLIC_ADVICE_POSTGRES_DSN = 'host=127.0.0.1 port=5432 dbname=drc_advice_test user=drc_test'
$env:DRC_PUBLIC_ADVICE_TEST_PER_USER = '3'
$env:DRC_PUBLIC_ADVICE_TEST_TOTAL = '9'
$env:DRC_PUBLIC_ADVICE_TEST_MODEL = 'local-synthetic-v1'
python -m scripts.public_advice_invite init-db
python -m scripts.public_advice_invite set-monthly-budget 788
python -m scripts.public_advice_invite resume
python -m scripts.public_advice_invite issue participant-001 --ttl-hours 1
python -m uvicorn scripts.public_advice_invite:create_local_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

発行コマンドはログや画面共有を行っていない運営者用シェルで実行する。Bearer トークンを `Authorization` ヘッダーに設定し、`POST http://127.0.0.1:8000/v1/advice` に `{"mood":"normal","character_id":"gentle_mina"}` を送る。ローカル起動用アプリは差し替え済みの固定本文を返す。既存の Backend を起動した場合、公開候補 API は明示的にランタイムが接続されるまで無効。

失効は別の運営者用シェルに同じ DSN を設定し、`python -m scripts.public_advice_invite revoke <管理用のToken-ID>` を実行する。管理コマンドは HTTP API に公開されない。

## 固定応答を使った HTTPS 配置の事前確認

検証用ホストでは、上記の固定応答アプリを管理 TLS 終端の背後で起動する。検証専用 PostgreSQL と短命の招待を使う。URL にトークンを含めず、入口と監視の記録から Authorization と本文を除外する。

- 外部 HTTPS 入口は `GET /health` と `POST /v1/advice` を許可する。`/health` は稼働確認用。DB と生成処理を含む確認には検証用の招待を使う。
- HTTPS 側から旧 API・開発ルート・ドキュメントが開かず、TLS 終端を経由しない Backend への直接アクセスが閉じていることを確認する。
- `app_public` から署名済み APK を作る。ホスト名は検証先に置き換える。

  ```powershell
  flutter build apk --release -t lib/main_invite_release.dart --dart-define=DRC_INVITE_ADVICE_URL=https://example.invalid/v1/advice
  ```

- 候補と復帰用の通常版のアプリ ID、署名証明書、versionCode を確認する。上書きで戻す場合は復帰用の通常版に候補より大きい versionCode を割り当てる。候補のコミット、ターゲット、APK の SHA-256 と署名証明書の SHA-256 を記録する。
- A301OP で USB 転送なしの成功（200）、無効または失効済みトークン（401）、上限到達（429）、停止（503）、通信断を確認する。参加者別日次上限を1にすると、同じ検証参加者の2回目で上限を確認できる。停止は枠の残った有効な参加者で確認する。失敗の各ケースで端末内アドバイスが表示されることを確認する。
- 合格後は同じ候補を使って Gemini 側を検証する。固定応答の検証台帳と Gemini のマイクロドル専用台帳は分ける。

### ローカル TLS の事前検証

公開 `main` の `0ca5d3f` を基準とする固定応答入口の変更で、検証専用 PostgreSQL とローカル証明書を使った HTTPS 疎通を確認した。`/health` は200、`/docs` は404。生成は有効な招待で200、無効・失効済みの招待で401、参加者の日次上限で429、運営者停止中は503だった。関連テストは72件合格し、ローカルの Gemma トークナイザーファイルが必要な1件はスキップした。公開ホストの TLS 終端と A301OP の署名済み候補は別途検証する。

### Render での検証用設定案

固定応答入口の変更を含む Git ブランチをデプロイ対象に指定し、Auto-Deploy を無効にする。Python Web Service と検証専用 PostgreSQL は同じリージョンに置く。検証にはサービスの `https://<service>.onrender.com` を使う。 [Web Service](https://render.com/docs/web-services) · [PostgreSQL](https://render.com/docs/postgresql-creating-connecting)

| 設定 | 値 |
| --- | --- |
| Root Directory | `backend` |
| Build Command | `python -m pip install -r requirements.txt -r requirements-public-advice-postgres.txt` |
| Start Command | `python -m uvicorn scripts.public_advice_invite:create_local_app --factory --host 0.0.0.0 --port "$PORT" --no-access-log` |
| Health Check Path | `/health` |
| `DRC_PUBLIC_ADVICE_POSTGRES_DSN` | 検証 DB の Internal Database URL を秘密の環境変数に設定 |
| `DRC_PUBLIC_ADVICE_TEST_MODEL` | `local-synthetic-v1` |
| `DRC_PUBLIC_ADVICE_TEST_PER_USER` | `1` |
| `DRC_PUBLIC_ADVICE_TEST_TOTAL` | `2` |

サービスの管理シェルを使える場合は、`backend` を作業ディレクトリにして次を実行する。管理シェルを使えない場合は Windows の運営者シェルから同じ CLI を実行し、検証 DB の外部接続はその端末の送信元 IP に絞り、運営操作が終わったら閉じる。トークンは発行出力から直接 A301OP へ入力し、ビルドログや共有記録に残さない。 [無料インスタンスの制約](https://render.com/docs/free)

```text
python -m scripts.public_advice_invite init-db
python -m scripts.public_advice_invite set-monthly-budget 788
python -m scripts.public_advice_invite issue device-https-check --ttl-hours 1
python -m scripts.public_advice_invite resume
```

`GET /health` の200と、無効トークンでの `POST /v1/advice` の401を HTTPS 経由で確認してから、同じホストの `/v1/advice` を APK のビルド引数に使う。無料 Web Service を利用する場合は、休止からの起動を待ち、`/health` の200を確認してから端末試験を始める。

### A301OP での固定応答 HTTPS 検証（2026-11-28 JST）

Render に `test/invite-https` の `f846df7` を配置し、PC のブラウザで HTTPS の `/health` が `{"status":"ok"}` を返すことを確認した。Android 側では `main_invite_release.dart` をターゲットに、Render の `/v1/advice` を指定した release APK をビルドし、A301OP に上書きインストールした。

| 実機の操作 | 画面で確認した結果 |
| --- | --- |
| オンラインで有効な招待を使って生成 | 固定応答「今日は自分のペースでいこう。」を表示した。 |
| 同じ招待で再生成 | 端末内アドバイスと取得失敗の案内を表示した。参加者別日次上限1回の設定での想定動作と一致した。 |
| 機内モードで生成 | 端末内アドバイスと取得失敗の案内を表示した。 |
| オンラインに戻し、無効な招待で生成 | 端末内アドバイスと取得失敗の案内を表示した。 |
| 運営者による停止中に新規の検証用招待で生成 | 端末内アドバイスと取得失敗の案内を表示した。 |

別途、作業環境から同じ公開 HTTPS の `POST /v1/advice` に無効な Bearer トークンと合成入力を送り、HTTP 401（`authentication_required`）を確認した。Windows PowerShell から同じ公開 HTTPS API に、日次枠を使用済みの参加者向けの招待と合成入力を送り、HTTP 429 を確認した。運営者 CLI で生成を停止し、Windows PowerShell から新規の検証用招待と合成入力を送ると HTTP 503 を返した。試験後は CLI での生成再開と検証用招待の失効を確認した。429・503 の応答本文と実機リクエストの HTTP ステータスは未採取。生成時の USB 切断状態は記録していない。

候補 APK の SHA-256 は `90865A1407054FCA1ECB7CDCF92891EF1597CA867E4E2D722B4B6158E39EE5ED`。`apksigner verify --verbose --print-certs` は `Verifies` を返し、v2 署名が1件だった。署名証明書の SHA-256 は `271f75fe3b198baca94f31ae2b658c7bfc99881a2cc35c68fe89380bfecf8ce5`。

復帰試験後の A301OP の通常版画面で、招待トークン欄がなく、ミナ・元気の選択に応じた端末内アドバイスが表示された。復帰用 APK の署名検証出力と上書きインストールのログは未採取。

## Render の公開 HTTPS で Gemini を検証する

固定応答用とは別の検証専用 PostgreSQL を、Web Service と同じリージョンに用意する。現在の Render のビルド・起動設定とデプロイ済みコミットを控える。Gemini 用 DB の External URL を運営者 CLI の `DRC_PUBLIC_ADVICE_POSTGRES_DSN` に設定し、`init-db`、`set-monthly-budget 512`、`issue device-gemini-https-check --ttl-hours 1`、`resume` を行う。この予算は検証用の1回分の予約額。実機で最初に使うため、発行した招待を PC からの成功試験に使わない。

Render の同じ Web Service で、`backend` を Root Directory にして以下を設定する。固定応答へ戻す場合は控えておいた設定で再デプロイする。

| 項目 | 値 |
| --- | --- |
| Build Command | `python -m pip install -r requirements.txt -r requirements-public-advice-gemini.txt && bash scripts/prepare_gemini_tokenizer.sh` |
| Start Command | `python -m uvicorn app.public_main:app --host 0.0.0.0 --port "$PORT" --no-access-log` |
| Health Check Path | `/health` |
| `DRC_PUBLIC_ADVICE_GEMINI_ENABLED` | `1` |
| `DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN` | Gemini 検証 DB の Internal URL |
| `DRC_PUBLIC_ADVICE_GEMINI_API_KEY` | Gemini の検証用 API キー |
| `DRC_PUBLIC_ADVICE_GEMINI_DAILY_PER_USER` | `1` |
| `DRC_PUBLIC_ADVICE_GEMINI_DAILY_TOTAL` | `1` |
| `DRC_GEMINI_TOKENIZER_DIR` | `.gemini-tokenizer` |

ビルドでは固定リビジョンのトークナイザーを取得し、アプリと同じ SHA-256 検証を通す。デプロイ後は `/health` の200と、無効な招待で `POST /v1/advice` が401を返すことを確認する。503の場合は Gemini の起動設定・DB・予算・トークナイザーを確認する。

A301OP の通常版が versionCode 8 の場合は、同じ HTTPS URL を指定して招待候補を versionCode 9 でビルドし、署名を確認して上書きする。有効な招待で生成を1回行い、実機表示と検証 DB に残った1回分の予約を照合する。試験後は招待を失効し、必要なら Gemini 側を停止して固定応答設定に戻す。

### A301OP での Gemini 公開 HTTPS 検証（2026-11-28 JST）

- Render のデプロイは `5276a61`。起動時に DB 名 `drc_gemini_https_test` を明示すると起動警告が消え、ダミーの招待で HTTP 401 `authentication_required` を確認した。
- 21:34 JST 頃、A301OP の招待候補 APK（`versionCode=9`）で「ふつう・ミナ」を選び、公開 HTTPS 経由の Gemini 生成結果が画面に表示された。
- Gemini 用 DB の当月予約額は512マイクロドルで、試験1回分の予約額と一致した。
- 実際の請求額と、実機で生成結果が表示されたリクエストの HTTP ステータスは未採取。

## A301OP での招待開発ビルドの音声出力確認（2026-11-28 JST）

A301OP の招待開発ビルドで、睡眠時間の使用をオフにし、「ふつう・ミナ」で生成したアドバイスの音声出力を確認した。画面には生成済みアドバイスと「音声再生」ボタンが表示された。

同じ開発ビルドで、アドバイス生成後に自動再生されないこと、「音声再生」を押すと表示本文と一致する読み上げが流れること、再生を途中で停止できることを確認した。

## Windows の通常 FastAPI 起動で Gemini 招待制テストを有効にする

マイクロドル専用のローカル PostgreSQL データベース（例 `drc_advice_gemini_test`）を作成する。合成モデルの台帳や上記のテスト単位の予算は別の DB に置く。以下は `backend` で実行する検証用 PowerShell の例。全ワーカーに同じ DSN と回数上限を設定する。本番の回数上限と月額予算は未決定。

```powershell
python -m pip install -r requirements.txt -r requirements-public-advice-gemini.txt
$env:DRC_SKIP_BACKEND_DOTENV = '1'
$env:CONVERSATION_ENGINE = 'mock'
$env:SLEEP_PROVIDER = 'mock'
$env:DRC_PUBLIC_ADVICE_GEMINI_ENABLED = '1'
$env:DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN = 'host=127.0.0.1 port=5432 dbname=drc_advice_gemini_test user=drc_test'
$env:DRC_PUBLIC_ADVICE_GEMINI_DAILY_PER_USER = '1'
$env:DRC_PUBLIC_ADVICE_GEMINI_DAILY_TOTAL = '2'
$env:DRC_GEMINI_TOKENIZER_DIR = 'C:\path\to\reviewed-tokenizer-files'

$env:DRC_PUBLIC_ADVICE_POSTGRES_DSN = $env:DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN
python -m scripts.public_advice_invite init-db
python -m scripts.public_advice_invite set-monthly-budget 1024
python -m scripts.public_advice_invite issue participant-001 --ttl-hours 1
python -m scripts.public_advice_invite resume

$key = Read-Host 'Gemini development key' -AsSecureString
try {
    $env:DRC_PUBLIC_ADVICE_GEMINI_API_KEY = [System.Net.NetworkCredential]::new('', $key).Password
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --lifespan on --no-access-log
} finally {
    Remove-Item Env:DRC_PUBLIC_ADVICE_GEMINI_API_KEY -ErrorAction SilentlyContinue
    $key.Dispose()
}
```

`DRC_GEMINI_TOKENIZER_DIR` には、下記の SHA-256 に一致する `tokenizer.json` と `chat_template.jinja` を置く。起動時にオフラインで全9通りの入力を数える。フラグが未設定なら生成は無効。起動時にキー・DB・月次予算・回数上限・トークナイザーのいずれかを確認できない場合も `/v1/advice` は `503 advice_unavailable` を返す。初期設定を修正した場合は FastAPI を再起動する。

発行した招待トークンを `Authorization: Bearer …` に設定して `POST http://127.0.0.1:8000/v1/advice` を呼ぶ。無効なトークンは `401`、回数または予算の上限は `429`。停止・DB 障害は `503`。認証・回数・月次予算の確認と512マイクロドルの確保が完了してから Gemini へ最大1回送信する。停止と再開には同じ DSN を指定した運営者用シェルで `pause` または `resume` を使う。再起動は不要。

## 費用の予約と生成停止

- 回数は DB の UTC 日付ごとに、予算は UTC の暦月（毎月1日 00:00 から翌月1日 00:00 まで）ごとに集計する。回数と最大見込み費用は、生成前に同じ PostgreSQL トランザクションで確保する。旧版から切り替えるときはすべての旧ワーカーを停止し、`init-db` と予算設定を行ってから新版を起動する。既存のトークンと回数枠は引き継がれ、費用の集計はこの機能の有効化後の予約から始まる。
- `local-synthetic-v1` は1 UTF-8 バイトを1トークンとして数える検証用モデル。固定プロンプトと選択値を含む入力上限は128、出力上限は96。価格は100万トークン当たり、入力1,200,000、出力2,500,000のテスト用管理単位（1単位は100万分の1円相当）。1回の予約額は `ceil((128 × 1,200,000 + 96 × 2,500,000) / 1,000,000) = 394` 単位。例の月額788単位は2回分。
- 生成は1リクエストにつき1回。自動再試行とフォールバックは行わない。予算不足は `429 global_quota_exceeded`、停止・設定不足・DB 障害は `503 advice_unavailable`。拒否時は回数・費用を計上せず、確保後のタイムアウトや上流障害でも予約額は残る。
- 新規予約を止めるには、同じ DSN を設定した運営者用シェルで `python -m scripts.public_advice_invite pause` を実行する。停止状態は DB に保存され、全ワーカーに適用される。確保済みのリクエストは取り消されない。予算を設定したうえで `resume` を実行すると、新規予約を再開できる。予算変更・再開で当月の予約額はリセットされない。

## テストと利用枠

検証専用 DB にスキーマを作成できる権限で、次を実行する。

```powershell
python -m pip install -r requirements-dev.txt
$env:DRC_PUBLIC_ADVICE_TEST_POSTGRES_DSN = $env:DRC_PUBLIC_ADVICE_POSTGRES_DSN
python -m pytest -q tests/test_postgres_public_advice.py tests/test_public_advice.py
```

上記の回数・単価・予算はローカル例で、本番値は未決定。予約額で実請求の上限を検証するには、提供元・モデル、課金対象（固定指示、出力以外に課金されるトークン、タイムアウト・失敗時の扱い）、入力・出力上限の強制方法、SDK 内部の再試行を確認する。再試行やフォールバックを採用する場合は追加呼び出しごとに最大費用を先に確保する。本番前に費用の照合と停止・復帰手順、保持・削除、バックアップと復旧、DB の接続権限、HTTPS、トークン配布方法を決める。

## Gemini 3.1 Flash-Lite の費用予約候補

2026-11-21 JST 時点。Gemini Developer API の `gemini-3.1-flash-lite` の標準有料テキスト生成は、100万トークン当たり入力0.25 USD、出力1.50 USD。入力にはシステム指示が含まれ、出力単価は思考トークンにも適用される。検索、ツール、キャッシュ指定、履歴、追加候補は送らない。 [料金表](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite) · [入力トークン](https://ai.google.dev/gemini-api/docs/tokens#system-instructions)

`generateContent` の思考ガイドでは、`maxOutputTokens` は回答と内部思考を合わせた上限。API の利用量では `candidatesTokenCount` と `thoughtsTokenCount` が別々に返る。`MINIMAL` は思考を抑える設定で、思考の課金をゼロと見なさない。入力上限512、出力上限256を使うと、予約額は `ceil((512 × 250000 + 256 × 1500000) / 1000000) = 512` マイクロドル。これを候補ランタイムの予約額とした。 [generateContent の思考と出力上限](https://ai.google.dev/gemini-api/docs/generate-content/thinking#token-limits) · [利用量フィールド](https://ai.google.dev/api/generate-content#UsageMetadata)

気分×キャラクターの全9通りで、送信する本文とシステム指示を Google 公開の Gemma 4 E4B トークナイザーでローカル計測した。既存の `google-genai==1.70.0` はこのモデルをローカルトークナイザーに登録していないため、後続 SDK `v2.9.0` のモデル対応表に従い、公開ファイルを別途使用した。SDK の固定バージョンは変更していない。各欄は「両テキストの合算 / Gemma の会話テンプレートを適用したとき」のトークン数。 [SDK のモデル対応表](https://github.com/googleapis/python-genai/blob/v2.9.0/google/genai/_local_tokenizer_loader.py) · [Google 公開トークナイザーファイル](https://huggingface.co/google/gemma-4-E4B-it/tree/main)

| 気分 | `gentle_mina` | `cheerful_sora` | `cool_rei` |
| --- | ---: | ---: | ---: |
| `energetic` | 69 / 83 | 68 / 82 | 66 / 80 |
| `normal` | 69 / 83 | 68 / 82 | 66 / 80 |
| `tired` | 69 / 83 | 68 / 82 | 66 / 80 |

全9通りでローカル計測値は512以内。Gemini Developer API が実際に計上した値は下記の実通信記録に示す。再現するには、公開ファイル `tokenizer.json` と `chat_template.jinja` を置いたディレクトリを `DRC_GEMINI_TOKENIZER_DIR` に設定し、検証用 Python に `tokenizers==0.22.2` と `jinja2==3.1.6` を入れて `tests/test_postgres_public_advice.py` を実行する。使用したファイルの SHA-256 は順に `91d9cf86906f78e197021fda88214d448e5c120665d0243a8e776e046986c6bc`、`0a2c8073c878ab1da004bee933a998606537bbb62016310352c7285c3f01c5b5`。

候補は固定モデルのノンストリーミング `generateContent` を使う。SDK 1.70.0 の同期 HTTP 経路で `HttpRetryOptions(attempts=1)` を設定し、HTTP リダイレクトと自動関数呼び出しも無効にする。認証、日次回数枠、月次予算の確保後にだけ1回送る。応答の使用量が上限を超える、または打ち切りの場合は `502 upstream_failure` とし、予約額を保持する。既存の FW 経路は会話セッションを持ち、関係性を要約する追加呼び出しがあり得るため、この候補の経路には使用しない。 [固定 SDK のリトライ実装](https://github.com/googleapis/python-genai/blob/v1.70.0/google/genai/_api_client.py)

固定応答の検証には `scripts.public_advice_invite:create_local_app` を使う。通常の FastAPI 起動では上記の明示設定を行った場合に Gemini 候補ランタイムが有効になる。本番に進むには、256で打ち切られた場合も含む実際の応答と課金、本番用のマイクロドル専用台帳、公開時の単価と本番月額予算を確認する。

### Windows 検証用 Backend の実通信記録

`d2e73c9` の `POST /v1/advice` で、合成入力 `normal` / `gentle_mina` を検証した。ループバック API と Gemini はともに HTTP 200。本文は1〜240文字の検証に合格し、入力70トークン、回答31トークン、終了理由は `STOP` だった。専用台帳で512マイクロドルを送信前に予約し、応答後も保持した。

この1件の入力・回答分の費用推計は `70 × 0.25 + 31 × 1.50 = 64` マイクロドル。

続く8件の結果を保存済みの実通信記録と照合し、**気分3種 × キャラクター3人の全9通りで実通信検証完了**。全9件で Gemini と `/v1/advice` が HTTP 200 を返し、本文は1〜240文字の検証に合格した。終了理由は全件 `STOP`、上流への送信は各1回だった。

| 気分 | キャラクター | 入力トークン | 回答トークン |
| --- | --- | ---: | ---: |
| `energetic` | `gentle_mina` | 70 | 48 |
| `energetic` | `cheerful_sora` | 69 | 33 |
| `energetic` | `cool_rei` | 67 | 21 |
| `normal` | `cheerful_sora` | 69 | 36 |
| `normal` | `cool_rei` | 67 | 16 |
| `tired` | `gentle_mina` | 70 | 31 |
| `tired` | `cheerful_sora` | 69 | 36 |
| `tired` | `cool_rei` | 67 | 27 |

成功9件の入力は67〜70トークン、回答は16〜48トークンだった。入力・回答分の費用推計は今回の8件で合計509マイクロドル、成功9件で合計573マイクロドル。思考・キャッシュのトークン数と実請求額は未確認。

DRC の費用予約は各512マイクロドルで、今回の8件で合計4,096マイクロドル、成功9件で合計4,608マイクロドル。初回の Gemini HTTP 400 は別の試行として扱い、成功分の集計から除外した。

差し替え通信では、文字数の条件を満たす途中の本文と終了理由 `MAX_TOKENS` を上流の HTTP 200 で返した。既存の候補アダプターは本文を拒否し、`/v1/advice` は HTTP 502 を返した。送信試行は1回で、512マイクロドルの予約は残った。実通信での打ち切りは未確認。

### 通常起動経路での実通信確認

基準コミット `dee6f590e8d91b047dcae5e51c4ca4d068538c06` で、上記の全9通りとは別に通常起動経路を検証した。

- Windows で `app.main:app` を通常起動し、検証用 PostgreSQL と招待トークンを使って、ループバックの `POST /v1/advice` に合成入力 `normal` / `gentle_mina` を1回送信した。
- Gemini と `/v1/advice` はともに HTTP 200。本文は1〜240文字の検証に合格した。上流送信は1回で再試行はなく、終了理由は `STOP` だった。
- 送信前に512マイクロドルを予約し、応答後も保持した。入力は70トークン、回答は29トークンだった。思考・キャッシュのトークン数と実請求額は未確認。
- 検証後、FastAPI と検証用 PostgreSQL を停止した。

### Android 実機からの Gemini 実通信確認

基準コミット `49b3c646ed031d590236f86b3075ef6771dbeff5` で、A301OP の Android 検証ビルドから USB の `adb reverse` 経由で Windows の `app.main:app` に接続し、検証用 PostgreSQL と招待トークンを使った。

- 「ふつう × ミナ」で生成を1回実行した。`POST /v1/advice` の本文は `mood` と `character_id` の2項目のみだった。FastAPI と Gemini はともに HTTP 200 を返し、生成本文は1〜240文字の検証に合格して端末に表示された。
- Gemini への送信は1回で再試行はなかった。入力は70トークン、回答は47トークンで、終了理由は `STOP` だった。
- Gemini への送信前に512マイクロドルを予約し、応答後も保持した。思考・キャッシュのトークン数と実請求額は未確認。
- 検証後、FastAPI、検証用 PostgreSQL、Flutter を停止し、今回設定した USB 転送を解除した。

### Health Connect の睡眠時間を使った Gemini 実機確認

- A301OP の招待制開発ビルドで「ふつう × ミナ」を選び、「睡眠時間をアドバイスに使う」をオンにして「アドバイス生成」を1回押した。
- USB 転送経由の `POST /debug/invite/advice` で、`total_sleep_minutes` は睡眠カードの表示、Windows Backend の受信値、Gemini への送信値で一致した。
- Backend と Gemini はともに HTTP 200。Gemini への送信は1回で再試行はなく、生成本文が端末に表示された。
- 検証後、FastAPI、PostgreSQL、開発アプリを停止し、今回設定した USB 転送を解除した。

### AI アドバイス後の会話の実機確認

- A301OP の招待制開発ビルドで、睡眠時間の使用をオフにし、「ふつう × ミナ」で AI アドバイスを1回生成して本文を表示した。
- 「会話を続ける」を開いた時点で、Gemini への追加送信は0件だった。ミナと雑談を2往復し、2回目の返信が最初の話題を踏まえていた。Backend でも、最初のやり取りが2回目の生成入力に含まれることを確認した。
- 会話を終了して開き直すと、以前の履歴は表示されなかった。
- アドバイス1回と返信2回はすべて FastAPI・Gemini ともに HTTP 200。Gemini への送信は計3回で、再試行はなかった。会話返信には、送信回数を記録するための検証用 Gemini 接続を使った。
- 検証後、FastAPI、検証用 PostgreSQL、Flutter を停止し、今回設定した USB 転送を解除した。
