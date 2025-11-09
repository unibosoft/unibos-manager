# 📱 Birlikteyiz - iOS & Android Komple Kurulum Rehberi

## ✅ Öngereksinimler
- [x] Xcode kurulu (App Store)
- [x] Android Studio kurulu
- [ ] Xcode setup tamamlanacak
- [ ] Android SDK kurulacak
- [ ] Emulator'ler oluşturulacak

---

## 🍎 ADIM 1: XCODE KURULUMU (5-10 dakika)

### Terminalde şu komutları çalıştırın (şifre isteyecek):

```bash
# 1. Xcode path ayarla
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 2. License kabul
sudo xcodebuild -license accept

# 3. First launch (ilk açılış, biraz sürer)
sudo xcodebuild -runFirstLaunch

# 4. CocoaPods kur (iOS dependency manager)
sudo gem install cocoapods
pod setup

# 5. Kontrol
flutter doctor
```

**Beklenen çıktı:** `[✓] Xcode - develop for iOS and macOS`

---

## 🤖 ADIM 2: ANDROID SDK KURULUMU (10-15 dakika)

### A. Android Studio'da SDK İndir

1. **Android Studio'yu aç:**
   ```bash
   open -a "Android Studio"
   ```

2. **SDK Manager'ı aç:**
   - Welcome ekranında: **"More Actions"** > **"SDK Manager"**
   - veya: **Tools** > **SDK Manager**

3. **SDK Platforms** sekmesinde şunları seç ve indir:
   - ☑ **Android 14.0 (UpsideDownCake)** - API Level 34
   - ☑ **Android 13.0 (Tiramisu)** - API Level 33
   - ☑ **Android 12.0 (S)** - API Level 31

4. **SDK Tools** sekmesinde şunları seç (Show Package Details açık olmalı):
   - ☑ **Android SDK Build-Tools** (en son versiyonu)
   - ☑ **Android SDK Platform-Tools**
   - ☑ **Android SDK Command-line Tools (latest)**
   - ☑ **Android Emulator**
   - ☑ **Google Play services**
   - ☑ **Intel x86 Emulator Accelerator (HAXM installer)** (Mac Intel için)

5. **"Apply"** > **"OK"** > indirmeyi bekle

### B. Flutter'a SDK Path Bildir

```bash
# SDK path'i flutter'a tanıt
flutter config --android-sdk ~/Library/Android/sdk

# License'ları kabul et (hepsine 'y')
flutter doctor --android-licenses

# Kontrol
flutter doctor
```

**Beklenen çıktı:** `[✓] Android toolchain - develop for Android devices`

---

## 📱 ADIM 3: iOS SIMULATOR KURULUMU

### A. Simulator İndir (Xcode içinde)

1. **Xcode'u aç:**
   ```bash
   open -a Xcode
   ```

2. **Xcode** > **Settings** (⌘,) > **Platforms** sekmesi

3. **iOS** seç ve **GET** butonuna tıkla (~5GB indirecek)

4. Beklenen platformlar:
   - iOS 17.0 Simulator
   - iOS 16.0 Simulator (opsiyonel)

### B. Simulator'ü Test Et

```bash
# Mevcut simulator'leri listele
xcrun simctl list devices

# Simulator'ü aç
open -a Simulator

# veya
xcrun simctl boot "iPhone 15 Pro"
```

---

## 🤖 ADIM 4: ANDROID EMULATOR OLUŞTURMA

### A. Device Manager'da Emulator Oluştur

1. **Android Studio'yu aç**

2. **More Actions** > **Virtual Device Manager**
   - veya: **Tools** > **Device Manager**

3. **"Create Device"** butonuna tıkla

4. **Hardware** seçimi:
   - Category: **Phone**
   - Device: **Pixel 8 Pro** (önerilen)
   - veya: **Pixel 6**

5. **"Next"** > **System Image** seç:
   - **UpsideDownCake (API 34)** - Android 14
   - **Download** butonuna tıkla ve indir

6. **"Next"** > **AVD Name**: "Pixel_8_API_34"

7. **Advanced Settings** (opsiyonel):
   - RAM: 4096 MB
   - Internal Storage: 2048 MB

8. **"Finish"**

### B. Emulator'ü Test Et

```bash
# Emulator'leri listele
flutter emulators

# Emulator başlat
flutter emulators --launch <emulator_id>

# veya Android Studio'dan ▶ (play) butonuna tıkla
```

---

## 🚀 ADIM 5: FLUTTER APP TEST (iOS)

### A. iOS Build İçin Gerekli Ayarlar

```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app

# iOS klasörüne git
cd ios

# Pod dependencies kur
pod install

# Geri dön
cd ..
```

### B. iOS Simulator'de Çalıştır

```bash
# Simulator'ü aç
open -a Simulator

# Flutter app'i çalıştır
flutter run -d ios

# veya belirli simulator seç
flutter devices
flutter run -d "iPhone 15 Pro"
```

**Beklenen:** App iOS simulator'de açılacak!

---

## 🤖 ADIM 6: FLUTTER APP TEST (Android)

### A. Android Build İçin API URL Değişikliği

**Önemli:** Android emulator localhost'a `10.0.2.2` üzerinden erişir.

`lib/services/api_service.dart` dosyasını düzenle:

```dart
// Android emulator için:
@RestApi(baseUrl: "http://10.0.2.2:8000/birlikteyiz/api/")

// iOS simulator için:
@RestApi(baseUrl: "http://localhost:8000/birlikteyiz/api/")
```

**NOT:** Her platform için ayrı build gerekir, veya runtime'da environment check yapabilirsiniz.

### B. Android Emulator'de Çalıştır

```bash
# Emulator başlat (Android Studio'dan veya)
flutter emulators --launch Pixel_8_API_34

# 30 saniye bekle, emulator açılsın
sleep 30

# Flutter app'i çalıştır
flutter run -d android

# veya emulator id'si ile
flutter devices
flutter run -d emulator-5554
```

**Beklenen:** App Android emulator'de açılacak!

---

## 🔔 ADIM 7: PUSH NOTIFICATION TEST

### A. iOS için Notification Permission

iOS simulator'de ilk açılışta:
1. **"Allow"** notification permission'a
2. Ayarlar açılacak
3. **Notifications** > **birlikteyiz** > açık

### B. Android için Notification Permission

Android emulator'de:
1. İlk açılışta notification izni isteyecek
2. **"Allow"** deyin
3. Android 13+ için runtime permission otomatik

### C. Test: Yeni Deprem Notification

#### Backend'den Test Depremi Oluştur:

```bash
cd /Users/berkhatirli/Desktop/unibos/backend
source venv/bin/activate

python manage.py shell -c "
from apps.birlikteyiz.models import Earthquake
from django.utils import timezone
from decimal import Decimal

test_eq = Earthquake.objects.create(
    magnitude=Decimal('4.8'),
    depth=Decimal('12.5'),
    latitude=Decimal('38.4192'),
    longitude=Decimal('27.1287'),
    location='NOTIFICATION TEST - İzmir',
    city='İzmir',
    source='KANDILLI',
    occurred_at=timezone.now(),
    fetched_at=timezone.now(),
    unique_id='TEST_NOTIF_' + str(timezone.now().timestamp())
)

print(f'✅ Test depremi: M{test_eq.magnitude} - {test_eq.location}')
"
```

#### Beklenen:
1. **Backend log:** "Earthquake notification triggered"
2. **Flutter app:** 5 dakika içinde polling ile notification gelecek
3. **iOS/Android:** Notification görünecek!

---

## 📊 HER ŞEY HAZIR! SON KONTROL

```bash
flutter doctor -v
```

**Beklenen çıktı:**
```
[✓] Flutter
[✓] Android toolchain
[✓] Xcode
[✓] Chrome
[✓] Android Studio
[✓] VS Code
[✓] Connected device (4 available)
    • iPhone 15 Pro Simulator (ios)
    • Pixel 8 API 34 (android)
    • macOS (desktop)
    • Chrome (web)
```

---

## 🐛 SORUN GİDERME

### 1. "Building for iOS requires a Mac"
**Çözüm:** macOS'ta çalıştığınızdan emin olun.

### 2. "CocoaPods not installed"
```bash
sudo gem install cocoapods
cd ios && pod install
```

### 3. "Android licenses not accepted"
```bash
flutter doctor --android-licenses
# Hepsine 'y'
```

### 4. "Unable to locate Android SDK"
```bash
flutter config --android-sdk ~/Library/Android/sdk
```

### 5. Emulator başlamıyor
```bash
# Android: HAXM kur
# iOS: Xcode > Open Developer Tool > Simulator
```

### 6. Notification gelmiyor (iOS)
- Settings > Notifications > birlikteyiz > Allow
- App'i restart et

### 7. API bağlanamıyor (Android)
- `10.0.2.2:8000` kullanıyor musunuz?
- Backend 8000 portunda çalışıyor mu? `curl localhost:8000/birlikteyiz/api/earthquakes/stats/`

---

## 🎯 ÖNERİLEN TEST SIRALAMASI

1. ✅ Flutter doctor all green
2. ✅ iOS simulator açılıyor
3. ✅ Android emulator açılıyor
4. ✅ Backend Django çalışıyor (8000 port)
5. ✅ Chrome'da app çalışıyor
6. ✅ iOS'ta app açılıyor
7. ✅ Android'de app açılıyor
8. ✅ Test depremi oluştur
9. ✅ Notification geliyor!

---

## 📝 NOTLAR

- **İlk build 5-10 dakika sürebilir** (dependencies download)
- **Emulator açılması 2-3 dakika** alabilir
- **Hot reload:** iOS/Android'de `r` tuşu ile anlık değişiklik
- **Debug logs:** `flutter logs` komutu ile canlı log izle
- **API değişikliği:** Android için `10.0.2.2`, iOS için `localhost`

---

**🎊 Kurulum tamamlandığında hem iOS hem Android'de deprem takip + push notification sisteminiz hazır!**

## 💡 HIZLI TEST KOMUTU

Tüm testleri aynı anda yapmak için:

```bash
# Terminal 1: Backend
cd /Users/berkhatirli/Desktop/unibos/backend
source venv/bin/activate
python manage.py runserver

# Terminal 2: iOS
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app
flutter run -d ios

# Terminal 3: Android (iOS bittikten sonra)
flutter run -d android
```

Başarılar! 🚀
