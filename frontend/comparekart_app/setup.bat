@echo off
REM CompareKart Flutter Setup Script (Windows)

echo.
echo 🚀 CompareKart Flutter Setup
echo =============================

REM Check if Flutter is installed
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Flutter is not installed. Please install Flutter SDK
    echo 📖 Visit: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('flutter --version') do set FLUTTER_VERSION=%%i
echo ✅ %FLUTTER_VERSION%

REM Run flutter doctor
echo.
echo 🏥 Running flutter doctor...
flutter doctor

REM Get dependencies
echo.
echo 📥 Getting dependencies...
flutter pub get

REM Generate models (if build_runner available)
echo.
echo 🏗️  Generating models...
flutter pub run build_runner build --delete-conflicting-outputs

REM Summary
echo.
echo =============================
echo ✨ Setup Complete!
echo =============================
echo.
echo To run the app:
echo   1. Connect device or start emulator
echo   2. Run: flutter run
echo.
echo To build APK (release):
echo   flutter build apk --release
echo.
echo To build App Bundle (Play Store):
echo   flutter build appbundle --release
echo.
pause
