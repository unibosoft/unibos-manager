# birlikteyiz

afet durumunda iletişim ve gerçek zamanlı deprem takip uygulaması

## 📱 özellikler

- ✅ gerçek zamanlı deprem verileri (5 farklı kaynak)
- ✅ interaktif harita görünümü
- ✅ magnitude bazlı renk kodlaması
- ✅ filtreleme (zaman, büyüklük, kaynak)
- ✅ offline çalışma desteği
- ✅ push bildirimleri
- ✅ karanlık tema (terminal tarzı)
- ✅ küçük harfli arayüz

## 🛠️ kurulum

### gereksinimler

- flutter sdk 3.0+
- dart 3.0+
- android studio / xcode
- unibos backend çalışır durumda

### adımlar

1. **flutter sdk kurulumu**
```bash
# macos
brew install flutter

# veya manuel kurulum
https://docs.flutter.dev/get-started/install
```

2. **projeyi klonla**
```bash
cd /Users/berkhatirli/Desktop/unibos/birlikteyiz_app
```

3. **bağımlılıkları yükle**
```bash
flutter pub get
```

4. **kod üretimi**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

5. **backend api url'ini ayarla**

`lib/services/api_service.dart` dosyasında:
```dart
static const String baseUrl = "http://localhost:8000";  // yerel test
// static const String baseUrl = "https://recaria.org";  // production
```

6. **uygulamayı çalıştır**
```bash
# android emulator
flutter run

# ios simulator
flutter run -d ios

# chrome (web)
flutter run -d chrome
```

## 📂 proje yapısı

```
lib/
├── main.dart                    # ana uygulama
├── models/
│   └── earthquake.dart          # deprem modeli
├── services/
│   └── api_service.dart         # REST API client
├── providers/
│   └── earthquake_provider.dart # riverpod state management
├── screens/
│   ├── home_screen.dart         # ana sayfa (bottom nav)
│   ├── earthquake_list_screen.dart  # deprem listesi
│   ├── earthquake_map_screen.dart   # harita görünümü
│   └── settings_screen.dart     # ayarlar
└── widgets/                     # custom widget'lar
```

## 🌐 api endpoints

backend tarafında şu endpoint'ler kullanılıyor:

```
GET /birlikteyiz/api/earthquakes/          # tüm depremler (filtreleme)
GET /birlikteyiz/api/earthquakes/stats/    # istatistikler
GET /birlikteyiz/api/earthquakes/recent/   # son depremler
GET /birlikteyiz/api/earthquakes/map_data/ # harita verisi
GET /birlikteyiz/api/earthquakes/{id}/     # tek deprem detayı
```

### query parametreleri

- `days`: zaman aralığı (1-30)
- `min_magnitude`: minimum büyüklük (2.0-5.0)
- `source`: kaynak (KANDILLI, AFAD, USGS, GFZ, IRIS)
- `city`: şehir filtresi
- `limit`: sonuç sayısı (max 500)

## 🎨 tema ve tasarım

- **renk paleti**: terminal tarzı (yeşil, siyah)
- **font**: courier prime (monospace)
- **ui kuralı**: tüm metinler küçük harf
- **magnitude renkleri**:
  - kırmızı: ≥5.0
  - turuncu: 4.0-5.0
  - sarı: 3.0-4.0
  - yeşil: <3.0

## 📱 ekran görüntüleri

### deprem listesi
- son depremler
- filtreler (zaman, büyüklük)
- istatistikler (toplam, büyük, orta, küçük)
- kaynak badge'leri

### harita görünümü
- interaktif leaflet harita
- magnitude bazlı marker'lar
- popup detaylar
- otomatik zoom

### ayarlar
- bildirim tercihleri
- tema seçimi
- hakkında bilgisi

## 🔧 geliştirme

### kod üretimi (gerektiğinde)
```bash
flutter pub run build_runner watch
```

### test
```bash
flutter test
```

### build

#### android apk
```bash
flutter build apk --release
```

#### ios ipa
```bash
flutter build ios --release
```

#### web
```bash
flutter build web
```

## 🐛 sorun giderme

### api bağlantı hatası
```dart
// android emulator için localhost:
static const String baseUrl = "http://10.0.2.2:8000";

// ios simulator için localhost:
static const String baseUrl = "http://localhost:8000";

// fiziksel cihaz için:
static const String baseUrl = "http://192.168.1.X:8000";  // mac ip'si
```

### cors hatası
backend'de `CORS_ALLOWED_ORIGINS` ayarını kontrol et:
```python
# backend/unibos_backend/settings/development.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

### model generation hatası
```bash
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

## 📦 bağımlılıklar

### ana bağımlılıklar
- `flutter_riverpod`: state management
- `dio`: HTTP client
- `retrofit`: REST API
- `flutter_map`: harita gösterimi
- `hive`: local database
- `google_fonts`: font desteği

### dev bağımlılıklar
- `build_runner`: kod üretimi
- `json_serializable`: JSON serialization
- `riverpod_generator`: provider generation

## 🚀 deployment

### play store (android)
```bash
flutter build appbundle --release
```

### app store (ios)
```bash
flutter build ipa --release
```

## 👨‍💻 geliştirici

**berk hatırlı**
bitez, bodrum, muğla, türkiye

## 📄 lisans

bu proje unibos ekosisteminin bir parçasıdır.

## 🔗 ilgili linkler

- backend API: http://localhost:8000/birlikteyiz/
- web harita: http://localhost:8000/birlikteyiz/map/
- API docs: http://localhost:8000/birlikteyiz/api/

## 📝 notlar

- backend sunucusu çalışır durumda olmalı
- android 8.0+ (API 26+) gerekli
- ios 12.0+ gerekli
- internet bağlantısı gerekli (offline mode geliştirilecek)

## 🎯 roadmap

- [x] deprem listesi
- [x] interaktif harita
- [x] filtreleme
- [ ] offline mode
- [ ] push notifications
- [ ] mesh network entegrasyonu
- [ ] afet bölgeleri
- [ ] acil durum mesajları
