# 🚀 birlikteyiz flutter app - kurulum ve çalıştırma rehberi

## ✅ başarıyla tamamlananlar

### 1. backend api (django)
- ✅ deprem verisi api'leri public yapıldı (`AllowAny` permission)
- ✅ CORS ayarları eklendi (localhost:3000 için)
- ✅ 5 farklı veri kaynağından deprem verisi çekiliyor:
  - KANDILLI (türkiye)
  - AFAD (türkiye)
  - USGS (global)
  - GFZ (avrupa)
  - IRIS (global)
- ✅ 1405+ deprem verisi mevcut
- ✅ api endpoint'leri:
  - `GET /birlikteyiz/api/earthquakes/` - tüm depremler
  - `GET /birlikteyiz/api/earthquakes/stats/` - istatistikler
  - `GET /birlikteyiz/api/earthquakes/recent/` - son depremler
  - `GET /birlikteyiz/api/earthquakes/map_data/` - harita verisi

### 2. flutter app
- ✅ dependencies kuruldu
- ✅ build_runner code generation tamamlandı
- ✅ chrome (web) üzerinde çalışıyor
- ✅ push notification service entegre edildi
- ✅ 5 dakikada bir yeni deprem kontrolü yapılıyor
- ✅ magnitude >= 3.0 olan depremler için bildirim gönderiliyor

### 3. push notifications
- ✅ local notification service oluşturuldu
- ✅ polling mekanizması (her 5 dakikada bir api'yi kontrol eder)
- ✅ magnitude bazlı önceliklendirme:
  - 🚨 >= 5.0: büyük deprem (high priority, kırmızı)
  - ⚠️ >= 4.0: orta şiddetli (high priority, turuncu)
  - 📊 >= 3.0: deprem (normal priority, sarı)
  - ℹ️ < 3.0: küçük deprem (low priority, yeşil)

---

## 🎯 uygulamayı çalıştırma

### backend (django)
```bash
cd /Users/berkhatirli/Desktop/unibos/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### flutter app (chrome/web)
```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app
flutter run -d chrome --web-port=3000
```

tarayıcınızda aç: **http://localhost:3000**

---

## 📱 android emulator kurulumu

### adım 1: android studio kurulumu
```bash
# homebrew ile kur
brew install --cask android-studio

# manuel: https://developer.android.com/studio
```

### adım 2: android sdk ve emulator kurulumu
1. android studio'yu aç
2. **more actions** > **sdk manager**
3. **sdk platforms** sekmesi:
   - ✅ android 13 (tiramisu) api 33
   - ✅ android 12 (s) api 31
4. **sdk tools** sekmesi:
   - ✅ android sdk build-tools
   - ✅ android sdk platform-tools
   - ✅ android emulator
   - ✅ google play services
5. **apply** > **ok**

### adım 3: virtual device oluşturma
1. **more actions** > **virtual device manager**
2. **create device**
3. **phone** kategori > **pixel 6** seç
4. **next** > system image: **tiramisu (android 13, api 33)** indir
5. **next** > **finish**

### adım 4: flutter ile android emulator çalıştırma
```bash
# emulator listesi
flutter emulators

# emulator başlat
flutter emulators --launch <emulator_id>

# veya android studio'dan başlat
# avd manager > play button

# flutter app'i çalıştır
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app
flutter run
# emulator otomatik seçilecek
```

### android için önemli ayarlar

#### 1. api url (android emulator için)
`lib/services/api_service.dart`:
```dart
// android emulator için localhost:
@RestApi(baseUrl: "http://10.0.2.2:8000/birlikteyiz/api/")

// fiziksel cihaz için (mac'in ip'si):
@RestApi(baseUrl: "http://192.168.1.X:8000/birlikteyiz/api/")

// web için:
@RestApi(baseUrl: "http://localhost:8000/birlikteyiz/api/")
```

#### 2. notification permissions (android)
`android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.VIBRATE"/>
```

---

## 🔔 notification sistemi nasıl çalışıyor?

### polling mekanizması
```dart
// main.dart
void main() async {
  // notification service başlat
  final notificationService = NotificationService();
  await notificationService.initialize();

  // 5 dakikada bir kontrol et
  notificationService.startPolling(
    interval: Duration(minutes: 5)
  );
}
```

### yeni deprem kontrolü
1. her 5 dakikada bir `/api/earthquakes/recent/?limit=1` endpoint'i çağrılır
2. son deprem id'si `SharedPreferences`'da saklanır
3. yeni bir deprem varsa ve magnitude >= 3.0 ise notification gösterilir
4. bildirim gösterildikten sonra yeni deprem id'si kaydedilir

### test için manuel notification
```dart
// test için manuel notification göster
final earthquake = Earthquake(/* ... */);
await notificationService.showEarthquakeNotification(earthquake);
```

---

## 🐛 sorun giderme

### 1. cors hatası
**sorun**: `DioException [connection error]`
**çözüm**: backend CORS ayarları kontrol et
```python
# backend/unibos_backend/settings/development.py
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 2. api bağlantı hatası (android)
**sorun**: localhost bağlanamıyor
**çözüm**: android için `10.0.2.2` kullan
```dart
@RestApi(baseUrl: "http://10.0.2.2:8000/birlikteyiz/api/")
```

### 3. build hataları
**çözüm**:
```bash
flutter clean
flutter pub get
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

### 4. notification çalışmıyor (android)
**çözüm**:
1. manifest'te permission'lar var mı kontrol et
2. android 13+ için runtime permission iste
3. notification channel oluşturuldu mu kontrol et

---

## 📊 veri yapısı

### earthquake model
```dart
class Earthquake {
  final int id;
  final double magnitude;
  final double depth;
  final double latitude;
  final double longitude;
  final String location;
  final String? city;
  final String source;
  final DateTime occurredAt;
}
```

### api response
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "magnitude": "4.2",
      "depth": "10.5",
      "latitude": "38.1234",
      "longitude": "27.5678",
      "location": "izmir körfezi",
      "city": "izmir",
      "source": "KANDILLI",
      "occurred_at": "2025-11-02T00:45:50Z",
      "time_ago": "5 dakika önce"
    }
  ]
}
```

---

## 🚀 production build

### android apk
```bash
flutter build apk --release
# output: build/app/outputs/flutter-apk/app-release.apk
```

### android app bundle (play store)
```bash
flutter build appbundle --release
# output: build/app/outputs/bundle/release/app-release.aab
```

### ios (macos gerekli)
```bash
flutter build ios --release
# xcode ile imzala ve yayınla
```

### web
```bash
flutter build web
# output: build/web/
```

---

## 📝 geliştirme notları

### kod yapısı
```
lib/
├── main.dart                    # ana uygulama, notification init
├── models/
│   └── earthquake.dart          # deprem modeli
├── services/
│   ├── api_service.dart         # REST API client (retrofit)
│   └── notification_service.dart # local notification + polling
├── providers/
│   └── earthquake_provider.dart # riverpod state management
├── screens/
│   ├── home_screen.dart         # bottom navigation
│   ├── earthquake_list_screen.dart
│   ├── earthquake_map_screen.dart
│   └── settings_screen.dart
└── widgets/                     # custom widget'lar
```

### state management (riverpod)
```dart
// earthquake listesi (filtreleme ile)
final earthquakesAsync = ref.watch(
  earthquakesProvider((days, minMagnitude))
);

// istatistikler
final statsAsync = ref.watch(earthquakeStatsProvider);

// harita verisi
final mapDataAsync = ref.watch(
  mapDataProvider((days, minMagnitude))
);
```

---

## ✨ gelecek geliştirmeler

- [ ] firebase cloud messaging (FCM) entegrasyonu (backend push)
- [ ] offline mode (hive database)
- [ ] deprem haritasında gerçek zamanlı güncelleme
- [ ] mesh network entegrasyonu (lora)
- [ ] acil durum mesajlaşma
- [ ] konum bazlı uyarılar
- [ ] push notification history
- [ ] widget support (android/ios)

---

## 📞 yardım

**backend logs**:
```bash
tail -f /tmp/django.log
```

**flutter logs**:
```bash
flutter logs
```

**deprem verisi güncelleme**:
```bash
cd /Users/berkhatirli/Desktop/unibos/backend
python manage.py fetch_earthquakes
```

---

**🎉 başarıyla kuruldu ve çalışıyor!**

deprem takip uygulaması artık:
- ✅ web'de çalışıyor (localhost:3000)
- ✅ 1405+ gerçek deprem verisi gösteriyor
- ✅ 5 dakikada bir yeni deprem kontrolü yapıyor
- ✅ magnitude >= 3.0 depremler için bildirim gönderiyor

android için emulator kurulumunu yukarıdaki adımları takip ederek yapabilirsiniz!
