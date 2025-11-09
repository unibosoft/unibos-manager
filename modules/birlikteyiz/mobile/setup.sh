#!/bin/bash
# birlikteyiz flutter app setup script

echo "🚀 birlikteyiz flutter app kurulumu başlıyor..."
echo ""

# Check Flutter installation
if ! command -v flutter &> /dev/null; then
    echo "❌ flutter bulunamadı!"
    echo "flutter sdk'yı kurmak için: https://docs.flutter.dev/get-started/install"
    echo "veya homebrew ile: brew install flutter"
    exit 1
fi

echo "✅ flutter bulundu: $(flutter --version | head -1)"
echo ""

# Clean previous builds
echo "🧹 önceki build dosyaları temizleniyor..."
flutter clean

# Get dependencies
echo "📦 bağımlılıklar yükleniyor..."
flutter pub get

# Generate code
echo "⚙️  kod üretiliyor (model, api, provider)..."
flutter pub run build_runner build --delete-conflicting-outputs

# Check if Django backend is running
echo ""
echo "🔍 django backend kontrolü..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ django backend çalışıyor"
else
    echo "⚠️  django backend çalışmıyor!"
    echo "backend'i başlatmak için:"
    echo "  cd ../backend"
    echo "  source venv/bin/activate"
    echo "  python manage.py runserver"
fi

echo ""
echo "✅ kurulum tamamlandı!"
echo ""
echo "uygulamayı çalıştırmak için:"
echo "  flutter run                 # emulator/simulator"
echo "  flutter run -d chrome       # web browser"
echo "  flutter run -d macos        # macos desktop"
echo ""
echo "build almak için:"
echo "  flutter build apk           # android"
echo "  flutter build ios           # ios"
echo "  flutter build web           # web"
echo ""
