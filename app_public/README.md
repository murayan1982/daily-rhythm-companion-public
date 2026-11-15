# DRC public Android app

This Android-only Flutter application starts the `ProductionApp` exported by
the local `drc_production` package. Its direct runtime dependencies are limited
to the Flutter SDK and that shared package.

## Local setup

Use Flutter 3.41.7 / Dart 3.11.5 from the repository root:

```powershell
cd app_public
flutter pub get
flutter analyze --no-pub
flutter test --no-pub
```

On a fresh checkout, provision the locally generated Gradle wrapper files with:

```powershell
flutter build apk --config-only --no-pub -t lib/main.dart
```

The configuration-only command creates `gradlew`, `gradlew.bat`, and
`gradle/wrapper/gradle-wrapper.jar`; it does not assemble an APK or AAB.

## Release boundary

The namespace, application ID, and `MainActivity` package use the formal
`io.github.murayan1982.dailyrhythmcompanion` identity. This local configuration
does not register the Android package or verify its future Google Play
availability. Normal APK/AAB assembly and verification are also outside this
setup step.

## Distribution signing setup

Keep the distribution keystore outside this repository. Maintain an encrypted
backup and a tested recovery procedure; do not commit the keystore,
`android/key.properties`, passwords, or machine-specific paths.

Create `android/key.properties` locally with these four entries. Use
placeholders only in shared documentation or examples:

```properties
storeFile=<absolute-path-to-keystore-outside-repository>
storePassword=<store-password>
keyAlias=<key-alias>
keyPassword=<key-password>
```

When `android/key.properties` exists, the release build type uses that signing
configuration. There is no fallback to the debug key. When the file is absent,
dependency resolution, analysis, and widget tests remain available, while a
distribution-signed release artifact cannot be produced.

After restoring the keystore from its encrypted backup, inspect the public
certificate of both the original and restored copies:

```powershell
keytool -list -v -keystore "<original-keystore-path>" -alias "<key-alias>"
keytool -list -v -keystore "<restored-keystore-path>" -alias "<key-alias>"
```

Compare the reported `SHA256` certificate fingerprints exactly. A matching
file checksum alone is not a substitute for this public-certificate check.
