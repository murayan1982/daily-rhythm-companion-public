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
