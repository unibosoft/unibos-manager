# 🍎 iOS / macOS Kurulum Rehberi - Birlikteyiz

## ⚠️ Gereksinimler

### Xcode ve Command Line Tools Kurulumu

#### 1. Xcode Kurulumu
```bash
# App Store'dan Xcode'u indirin (ücretsiz, ~15GB)
# veya
xcode-select --install  # Sadece command line tools için
```

#### 2. Xcode License Kabul
```bash
sudo xcodebuild -license accept
```

#### 3. Xcode Command Line Tools Doğrulama
```bash
xcode-select -p
# Beklenen çıktı: /Applications/Xcode.app/Contents/Developer
```

#### 4. Flutter iOS Setup
```bash
flutter doctor
# iOS toolchain sorunlarını kontrol edin

# CocoaPods kurulumu (gerekiyorsa)
sudo gem install cocoapods
pod setup
```

---

## 📱 iOS Simulator Kurulumu

### Adım 1: Xcode'u açın
```bash
open -a Xcode
```

### Adım 2: iOS Simulator İndir
1. **Xcode** > **Settings** > **Platforms**
2. **iOS** platformunu seç
3. İstediğiniz iOS versiyonunu indir (örn: iOS 17)

### Adım 3: Simulator Başlat
```bash
# Mevcut simulator'leri listele
xcrun simctl list devices

# Simulator aç
open -a Simulator

# veya Flutter ile direkt başlat
flutter run
# iOS simulator otomatik seçilecek
```

---

## 🖥️ macOS Desktop App

### Adım 1: macOS Build Etkinleştir
```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app

# macOS support ekle (ilk kez)
flutter create --platforms=macos .

# macOS build klasörünü kontrol et
ls -la macos/
```

### Adım 2: macOS Permissions Ekle

`macos/Runner/DebugProfile.entitlements` ve `macos/Runner/Release.entitlements` dosyalarına:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

### Adım 3: macOS'ta Çalıştır
```bash
flutter run -d macos

# veya production build
flutter build macos --release
```

---

## 🔔 iOS/macOS Push Notifications

### Local Notifications (Şu an aktif)
- ✅ `flutter_local_notifications` kullanıyor
- ✅ Polling mekanizması (her 5 dakika)
- ✅ Cross-platform (iOS, Android, macOS, web)

### iOS için ekstra izinler

#### 1. Info.plist güncelleme
`ios/Runner/Info.plist`:
```xml
<key>NSUserNotificationsUsageDescription</key>
<string>deprem uyarıları için bildirim izni gerekli</string>

<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>remote-notification</string>
</array>
```

#### 2. macOS için NotificationCenter izni
`macos/Runner/Info.plist`:
```xml
<key>NSUserNotificationAlertStyle</key>
<string>alert</string>
```

---

## 🚀 Çalıştırma Komutları

### iOS Simulator
```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app

# Simulator başlat
open -a Simulator

# App'i çalıştır
flutter run -d ios

# Belirli simulator seç
flutter run -d "iPhone 15 Pro"
```

### macOS Desktop
```bash
flutter run -d macos
```

### Chrome (Web)
```bash
flutter run -d chrome --web-port=3000
```

---

## 🐛 Sorun Giderme

### 1. "xcodebuild not found"
**Çözüm**:
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

### 2. "No valid code signing identity"
**Çözüm**: Xcode'da hesap ekleyin
1. Xcode > Settings > Accounts
2. Apple ID ekle
3. Personal Team seç (ücretsiz geliştirme için)

### 3. CocoaPods hataları
**Çözüm**:
```bash
cd ios
pod deintegrate
pod install
cd ..
flutter clean
flutter pub get
```

### 4. macOS build hatası
**Çözüm**:
```bash
flutter clean
cd macos
pod install
cd ..
flutter build macos
```

---

## 📊 API Endpoint Ayarları

### iOS Simulator için
```dart
// lib/services/api_service.dart
@RestApi(baseUrl: "http://localhost:8000/birlikteyiz/api/")
```

### Fiziksel iOS cihaz için
```dart
// Mac'in IP adresini kullan
@RestApi(baseUrl: "http://192.168.1.X:8000/birlikteyiz/api/")

// IP öğrenmek için:
// ifconfig | grep "inet " | grep -v 127.0.0.1
```

---

## ✅ Kurulum Kontrolü

```bash
# Flutter doctor çalıştır
flutter doctor -v

# Beklenen çıktı:
# ✓ Flutter (Channel stable)
# ✓ Xcode - develop for iOS and macOS
# ✓ Chrome - develop for the web
# ✓ VS Code (version x.x.x)
```

---

## 🎯 Sonraki Adımlar

1. **Xcode'u kur**: `xcode-select --install`
2. **iOS Simulator indir**: Xcode > Settings > Platforms
3. **macOS build test et**: `flutter run -d macos`
4. **iOS build test et**: `flutter run -d ios`
5. **Push notification test et**: Yeni deprem geldiğinde bildirim gelecek

---

## 📝 Notlar

- **macOS notification permission**: İlk çalıştırmada izin isteyecek
- **iOS notification permission**: Runtime'da izin gerekli
- **Background fetch**: iOS'ta 15 dakikada bir sınırlı (sistem kontrolünde)
- **Polling interval**: macOS/web'de istediğiniz gibi ayarlanabilir

---

**🎊 Xcode kurulduktan sonra hem iOS simulator hem macOS desktop'ta çalışabileceksiniz!**
