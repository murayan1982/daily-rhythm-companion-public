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

The current namespace and application ID are provisional GP-2 values. GP-4
will apply the approved formal application ID, display name, version, and
distribution signing. Normal APK/AAB assembly and signing are outside this
setup step.
