import java.util.Properties

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

val keyPropertiesFile = rootProject.file("key.properties")
val keyProperties = Properties().apply {
    if (keyPropertiesFile.isFile) {
        keyPropertiesFile.inputStream().use(::load)
    }
}

fun requiredSigningProperty(name: String): String =
    checkNotNull(keyProperties.getProperty(name)) {
        "$name is required in android/key.properties"
    }

val flutterProjectDirectory = rootProject.projectDir.parentFile
val inviteReleaseTarget = flutterProjectDirectory.resolve("lib/main_invite_release.dart")
val buildsInviteRelease = providers.gradleProperty("target").orNull?.let {
    flutterProjectDirectory.resolve(it).canonicalFile == inviteReleaseTarget.canonicalFile
} ?: false

android {
    namespace = "io.github.murayan1982.dailyrhythmcompanion"
    compileSdk = 36
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        // Formal GP-4 Android identity confirmed for application on 2026-11-15.
        applicationId = "io.github.murayan1982.dailyrhythmcompanion"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = 24
        targetSdk = 36
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (keyPropertiesFile.isFile) {
            create("release") {
                storeFile = file(requiredSigningProperty("storeFile"))
                storePassword = requiredSigningProperty("storePassword")
                keyAlias = requiredSigningProperty("keyAlias")
                keyPassword = requiredSigningProperty("keyPassword")
            }
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".dev"
        }

        release {
            signingConfigs.findByName("release")?.let {
                signingConfig = it
            }
        }
    }

    // Flutter passes -t as the Gradle target property. Only this release target
    // uses the invite manifest overlay; the default release command is unchanged.
    if (buildsInviteRelease) {
        sourceSets.getByName("release").manifest.srcFile("src/inviteRelease/AndroidManifest.xml")
    }
}

flutter {
    source = "../.."
}
