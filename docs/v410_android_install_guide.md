# Daily Rhythm Companion v4.1.0 Android インストール案内

> APK 公開前の案内です。Android 開発者確認・パッケージ登録と GitHub Release の公開は未完了です。APK のダウンロードリンクは Release 公開時に確定します。

## 対応条件と実機確認

- Android 7.0（API 24）以上を搭載し、ARM64（`arm64-v8a`）アプリを実行できる端末が必要です。
- 実機確認は A301OP（Android API 34、`arm64-v8a`）で行いました。この端末で新規インストール、起動、アドバイス表示、検証用 APK からの上書き更新を確認済みです。別画面サイズの実機での確認は保留です。

## 公式 APK の入手と確認

公開後に、[公式 GitHub Releases](https://github.com/murayan1982/daily-rhythm-companion-public/releases) で v4.1.0 Android Public Beta を開き、**Assets** にある下記の `.apk` を取得してください。`Source code (zip)` と `Source code (tar.gz)` はソースのアーカイブです。APK の配布元はこの公式リポジトリです。

| 項目 | 検査済み候補 |
| --- | --- |
| ファイル名 | `DRC_v4.1.0_arm64_signed_candidate.apk` |
| サイズ | 15,081,786 バイト |
| バージョン | `versionName=4.1.0` / `versionCode=6` |
| アプリ ID | `io.github.murayan1982.dailyrhythmcompanion` |
| APK の SHA-256 | `A50D6987B8E059A49FFF1FB340A7081293617DE9EE784E3304547BA17FDCE373` |
| 署名証明書の SHA-256 | `27:1F:75:FE:3B:19:8B:AC:A9:4F:31:AE:2B:65:8C:7B:FC:99:88:1A:2C:C3:5C:68:FE:89:38:0B:FE:CF:8C:E5` |

APK を開く前に、ファイルの SHA-256 を計算して Release に掲載された **APK の SHA-256** と照合してください。パソコンで確認する場合は、APK を保存したフォルダーで次のコマンドを実行します。

| OS | コマンド |
| --- | --- |
| Windows PowerShell | `Get-FileHash -Algorithm SHA256 -LiteralPath './DRC_v4.1.0_arm64_signed_candidate.apk'` |
| macOS | `shasum -a 256 DRC_v4.1.0_arm64_signed_candidate.apk` |
| Linux | `sha256sum DRC_v4.1.0_arm64_signed_candidate.apk` |

大文字と小文字の違いを除き、64 桁すべてが一致した場合に、その APK を端末で開いてください。不一致の場合はインストールを中止し、公式 Release で取得先を確認してください。署名証明書の SHA-256 は、署名者を確認するための別の値です。

## インストール

1. 端末のファイル管理アプリやブラウザのダウンロード一覧から、照合済みの APK を開きます。
2. 外部からのアプリのインストール許可を求められた場合は、Android のバージョンに応じて設定します。
   - **Android 8.0 以上**では、「不明なアプリのインストール」で、APK を開いたブラウザやファイル管理アプリに対して「この提供元のアプリを許可」をオンにします。
   - **Android 7.0／7.1** では、今回だけの許可が表示されたらそれを選びます。端末設定が必要な場合は「設定 → セキュリティ → 提供元不明のアプリ」を一時的に許可します。
3. インストール画面に表示されるアプリ名が **Daily Rhythm Companion** であることを確認し、「インストール」を選びます。完了後に起動し、気分とキャラクターを選んでアドバイスが表示されることを確認します。
4. インストールのために変更した許可は、作業後に元に戻してください。

設定名や画面は端末によって異なります。 [Android の外部配布とインストール許可](https://developer.android.com/distribute/marketing-tools/alternative-distribution?hl=ja)

## 上書き更新

インストール済みのアプリを残したまま、公式 Release から更新用 APK を取得し、SHA-256 を照合して開きます。Android が更新を提示したら「更新」を選び、完了後に起動を確認します。上書きには、インストール済みの版と同じアプリ ID・署名証明書が必要です。古い版への上書きは行わず、更新を拒否された場合は表示されたエラーを控えてサポート窓口へご連絡ください。 [Android の上書き更新条件](https://developer.android.com/google/play/app-updates)

A301OP では、同じアプリ ID・署名証明書の検証専用 `versionCode=5` から、この候補 `versionCode=6` への上書き更新を確認しました。

## アンインストールと端末上のデータ削除

- アプリを残して端末上のアプリデータを消去するには、「設定 → アプリ → Daily Rhythm Companion → ストレージとキャッシュ → ストレージを消去」を選びます。設定名は端末によって異なります。
- アプリと端末上のアプリ固有データを削除するには、「設定 → アプリ → Daily Rhythm Companion → アンインストール」を選びます。
- ダウンロードした APK や自分で撮ったスクリーンショットは、必要に応じてファイル管理アプリなどで個別に削除してください。Android のバックアップや端末間移行の挙動は、OS と端末の設定によって異なります。 [プライバシーポリシー](../PRIVACY.md)

## 問い合わせ

アプリの使い方、インストール時のエラー、プライバシーに関するご質問は、[サポート窓口（メール）](mailto:murayan1982@gmail.com)で受け付けます。データと問い合わせの取扱いは[プライバシーポリシー](../PRIVACY.md)をご覧ください。
