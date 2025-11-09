# 🚀 birlikteyiz - hızlı başlangıç

## ⚡ 5 dakikada çalıştır

### 1. flutter kurulumu (ilk kez)

```bash
# macos
brew install flutter

# doğrulama
flutter doctor
```

### 2. projeyi hazırla

```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app

# otomatik kurulum
./setup.sh

# veya manuel:
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. backend'i başlat

**başka terminal'de:**
```bash
cd /Users/berkhatirli/Desktop/unibos/backend
source venv/bin/activate
python manage.py runserver
```

### 4. uygulamayı çalıştır

```bash
# android emulator
flutter run

# ios simulator
flutter run -d ios

# chrome (web)
flutter run -d chrome

# macos desktop
flutter run -d macos
```

## 📱 platform notları

### android
- API level 26+ (Android 8.0+)
- emulator veya fiziksel cihaz
- localhost için: `http://10.0.2.2:8000`

### ios
- ios 12.0+
- xcode gerekli
- simulator veya fiziksel cihaz

### web
- chrome öneriliNode
- cors ayarları backend'de yapılmalı

## 🔧 API yapılandırma

`lib/services/api_service.dart` dosyasında:

```dart
// yerel geliştirme (mac)
static const String baseUrl = "http://localhost:8000";

// android emulator
static const String baseUrl = "http://10.0.2.2:8000";

// fiziksel cihaz (mac'in ip'si)
static const String baseUrl = "http://192.168.1.X:8000";

// production
static const String baseUrl = "https://recaria.org";
```

## 🎯 test et

1. backend çalışıyor mu? → http://localhost:8000/birlikteyiz/
2. api çalışıyor mu? → http://localhost:8000/birlikteyiz/api/earthquakes/stats/
3. deprem verisi var mı? → 1407 deprem olmalı

## 🐛 sorun mu var?

### "flutter: command not found"
```bash
# path'e ekle
export PATH="$PATH:/path/to/flutter/bin"
```

### "no devices found"
```bash
# android emulator başlat
flutter emulators
flutter emulators --launch <emulator_id>

# veya
open -a Simulator  # ios
```

### "api connection failed"
- backend çalışıyor mu kontrol et
- api url doğru mu kontrol et
- cors ayarları yapıldı mı kontrol et

### "build runner error"
```bash
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

## 📦 build alma

```bash
# android apk
flutter build apk --release

# ios ipa (macos gerekli)
flutter build ios --release

# web
flutter build web

# macos app
flutter build macos
```

## 🎨 ekranlar

✅ **deprem listesi** - son depremler, filtreler, istatistikler
✅ **harita** - interaktif harita, magnitude bazlı marker'lar
✅ **ayarlar** - bildirim tercihleri, tema, hakkında

## 🌐 api endpoint'leri

- `GET /birlikteyiz/api/earthquakes/` - deprem listesi
- `GET /birlikteyiz/api/earthquakes/stats/` - istatistikler
- `GET /birlikteyiz/api/earthquakes/recent/` - son depremler
- `GET /birlikteyiz/api/earthquakes/map_data/` - harita verisi

## 💡 ipuçları

- **hot reload**: `r` tuşuna bas
- **hot restart**: `R` tuşuna bas
- **debug toggle**: `p` tuşuna bas
- **inspector**: `i` tuşuna bas
- **quit**: `q` tuşuna bas

## 📞 yardım

detaylı bilgi için: [README.md](README.md)

---

**geliştirici:** berk hatırlı - bitez, bodrum
**proje:** unibos / birlikteyiz
**versiyon:** 1.0.0
