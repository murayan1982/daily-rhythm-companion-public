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

全9通りでローカル計測値は512以内。Gemini Developer API が計上する正確な入力トークン数は未確認。再現するには、公開ファイル `tokenizer.json` と `chat_template.jinja` を置いたディレクトリを `DRC_GEMINI_TOKENIZER_DIR` に設定し、検証用 Python に `tokenizers==0.22.2` と `jinja2==3.1.6` を入れて `tests/test_postgres_public_advice.py` を実行する。使用したファイルの SHA-256 は順に `91d9cf86906f78e197021fda88214d448e5c120665d0243a8e776e046986c6bc`、`0a2c8073c878ab1da004bee933a998606537bbb62016310352c7285c3f01c5b5`。

候補は固定モデルのノンストリーミング `generateContent` を使う。SDK 1.70.0 の同期 HTTP 経路で `HttpRetryOptions(attempts=1)` を設定し、HTTP リダイレクトと自動関数呼び出しも無効にする。認証、日次回数枠、月次予算の確保後にだけ1回送る。応答の使用量が上限を超える、または打ち切りの場合は `502 upstream_failure` とし、予約額を保持する。既存の FW 経路は会話セッションを持ち、関係性を要約する追加呼び出しがあり得るため、この候補の経路には使用しない。 [固定 SDK のリトライ実装](https://github.com/googleapis/python-genai/blob/v1.70.0/google/genai/_api_client.py)

通常の招待制起動は引き続き固定応答を使う。Gemini 候補ランタイムは既定の起動経路に接続していない。本番に進むには、同一内容9通りのサーバー計上、256で打ち切られた場合も含む実際の応答と課金、マイクロドル専用の予算台帳、公開時の単価と本番月額予算を確認する。合成モデル用の台帳は単位が異なるため共用しない。
