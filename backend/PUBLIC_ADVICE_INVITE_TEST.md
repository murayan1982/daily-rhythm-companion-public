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
python -m scripts.public_advice_invite init-db
python -m scripts.public_advice_invite issue participant-001 --ttl-hours 1
python -m uvicorn scripts.public_advice_invite:create_local_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

発行コマンドはログや画面共有を行っていない運営者用シェルで実行する。Bearer トークンを `Authorization` ヘッダーに設定し、`POST http://127.0.0.1:8000/v1/advice` に `{"mood":"normal","character_id":"gentle_mina"}` を送る。ローカル起動用アプリは差し替え済みの固定本文を返す。既存の Backend を起動した場合、公開候補 API は明示的にランタイムが接続されるまで無効。

失効は別の運営者用シェルに同じ DSN を設定し、`python -m scripts.public_advice_invite revoke <管理用のToken-ID>` を実行する。管理コマンドは HTTP API に公開されない。

## テストと利用枠

検証専用 DB にスキーマを作成できる権限で、次を実行する。

```powershell
python -m pip install -r requirements-dev.txt
$env:DRC_PUBLIC_ADVICE_TEST_POSTGRES_DSN = $env:DRC_PUBLIC_ADVICE_POSTGRES_DSN
python -m pytest -q tests/test_postgres_public_advice.py tests/test_public_advice.py
```

利用者別と全体の枠を呼び出し前に1トランザクションで確保する。DB 時計の UTC 日付で集計し、生成試行が失敗しても計上は残る。上記の1人3回・全体9回はローカル例で、本番値は未決定。認証や枠の確保で DB エラーが発生すると、API は `503 advice_unavailable` を返す。

本番の費用上限を設定する際は、提供元とモデル、課金単位、入力・出力上限、タイムアウトや失敗でも課金される条件を確定する。再試行・フォールバックに別の上流呼び出しを許可する場合は、その呼び出しの最大費用も毎回先に確保する。DB に共有予算を設ける場合は日次と月次の上限を原子的に引き当て、残額不足、計上不能、運営者の停止操作で新規生成を止める。保持・削除、バックアップと復旧、DB の接続権限、HTTPS、トークン配布方法も本番前に決める。
