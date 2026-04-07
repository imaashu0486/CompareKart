#!/bin/bash
# CompareKart Flutter Setup Script

echo ""
echo "🚀 CompareKart Flutter Setup"
echo "============================="

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter SDK"
    echo "📖 Visit: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version)"

# Run flutter doctor
echo ""
echo "🏥 Running flutter doctor..."
flutter doctor

# Get dependencies
echo ""
echo "📥 Getting dependencies..."
flutter pub get

# Generate models (if build_runner available)
echo ""
echo "🏗️  Generating models..."
flutter pub run build_runner build --delete-conflicting-outputs

# Summary
echo ""
echo "============================="
echo "✨ Setup Complete!"
echo "============================="
echo ""
echo "To run the app:"
echo "  1. Connect device or start emulator"
echo "  2. Run: flutter run"
echo ""
echo "To build APK (release):"
echo "  flutter build apk --release"
echo ""
echo "To build App Bundle (Play Store):"
echo "  flutter build appbundle --release"
echo ""
