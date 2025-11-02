# CLAUDE_TECH.md - Teknik Özellikler ve Altyapı

> **🔧 NOT**: Bu dosya UNIBOS projesinin teknik detaylarını içerir. Ana yönetim için [CLAUDE.md](./CLAUDE.md) dosyasına bakın.

## 🎮 Ultima Online 2 Benzeri UI Geliştirme {#ultima-ui}

### Genel UI/UX Prensipler
1. **İzometrik Görünüm**: 2.5D izometrik perspektif (45° açı)
2. **Paperdoll Sistemi**: Sürükle-bırak inventory ve karakter ekipmanı
3. **Gump Pencereler**: Taşınabilir, yeniden boyutlandırılabilir UI elemanları
4. **Sağ Tık Menüler**: Contextual interaction menüleri
5. **Hotbar**: Özelleştirilebilir skill/item kısayolları

### Teknik Gereksinimler
```javascript
// Phaser.js 3.70+ yapılandırması
const gameConfig = {
    type: Phaser.WEBGL,
    width: 1024,
    height: 768,
    backgroundColor: '#000000',
    scene: [BootScene, GameScene, UIScene],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    render: {
        pixelArt: false,
        antialias: true
    }
};
```

### UI Komponentleri
1. **Ana Oyun Ekranı**
   - İzometrik harita görünümü (merkez)
   - Karakter portresi (sol üst)
   - Mini harita (sağ üst)
   - Chat penceresi (sol alt)
   - Hotbar (alt orta)

2. **Inventory Sistemi**
   - Grid tabanlı (8x10 slotlar)
   - Item stacking
   - Drag & drop
   - Item tooltips

3. **Karakter Penceresi**
   - Paperdoll (ekipman slotları)
   - Stats paneli
   - Skills listesi
   - Guild/party bilgileri

### Renk Paleti
```css
/* Ultima Online 2 tarzı renkler */
--ui-border: #8B7355;
--ui-background: #1a1a1a;
--ui-text: #FFD700;
--ui-highlight: #FF6B6B;
--health-bar: #FF0000;
--mana-bar: #0066CC;
--stamina-bar: #FFFF00;
```

### Asset Gereksinimleri
- Sprite sheets: 32x32 veya 64x64 piksel
- İzometrik tile'lar: 64x32 piksel
- UI elementleri: 9-slice sprites
- Font: Medieval/Gothic stil

## Teknoloji Stack ve Altyapı

### Backend
- **Python**: 3.8+ (3.11+ önerilir)
- **Web Framework**: 
  - Django 4.2+ (Recaria modülü için)
  - Flask 3.0+ (API endpoints için)
- **Database**:
  - PostgreSQL 15+ (required for all environments)
- **Async**: asyncio, aiohttp
- **ORM**: Django ORM, SQLAlchemy

### Frontend
- **Game Engine**: Phaser.js 3.70+
- **Map Library**: Leaflet 1.9+
- **UI Framework**: 
  - Vanilla JS (terminal UI)
  - React 18+ (web dashboard - planlanıyor)
- **CSS**: Tailwind CSS 3.3+
- **Build Tools**: Webpack 5+

### DevOps & Infrastructure
- **Container**: Docker 24+, docker-compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Reverse Proxy**: Nginx 1.24+
- **Process Manager**: Gunicorn, Supervisor

### Hardware & IoT
- **Board**: Raspberry Pi Zero 2W / Pi 4
- **LoRa**: SX1278 (RA-01/02 modules)
- **GPS**: NEO-6M/7M/8M
- **OS**: Raspberry Pi OS Lite (64-bit)
- **GPIO Library**: RPi.GPIO, pigpio

### Security & Auth
- **Encryption**: bcrypt, cryptography
- **JWT**: PyJWT
- **SSL/TLS**: Let's Encrypt, certbot
- **VPN**: WireGuard

### External APIs
- **Maps**: OpenStreetMap Nominatim
- **Currency**: TCMB XML Feed, CoinGecko API
- **Weather**: OpenWeatherMap (planlanıyor)
- **Geocoding**: Google Maps API (opsiyonel)

### Development Tools
- **Version Control**: Git, GitHub
- **Testing**: pytest, unittest, coverage
- **Linting**: flake8, black, mypy
- **Documentation**: Sphinx, MkDocs

## Proje Özel Bilgiler

### Veritabanı Stratejisi
- **All Environments**: PostgreSQL (ölçeklenebilir, güvenli)
- **Migration**: Otomatik migration scriptleri mevcut
- **Backup**: Her versiyon değişiminde otomatik yedekleme

### API Tasarım Prensipleri
- RESTful standartlarına uygun
- JWT tabanlı authentication
- Rate limiting (100 req/min default)
- Versiyonlanmış endpoints (/api/v1/)
- CORS desteği (configurable)

### Güvenlik Katmanları
1. **Authentication**: JWT + Refresh Token
2. **Authorization**: Role-based (admin, user, guest)
3. **Encryption**: AES-256 for sensitive data
4. **Network**: SSL/TLS zorunlu
5. **Input Validation**: Tüm inputlar validate edilmeli

### Performance Optimizasyonları
- Lazy loading modüller
- Redis cache desteği (opsiyonel)
- Database connection pooling
- Async/await pattern kullanımı
- Background task queue (Celery ready)

### CI/CD Pipeline (Planlanıyor)
- GitHub Actions
- Automated testing
- Code quality checks (flake8, mypy)
- Security scanning
- Automated deployment

### Monitoring & Analytics
- Prometheus metrics endpoint
- Health check endpoint (/health)
- Performance profiling hooks
- User analytics (privacy-first)

### Raspberry Pi Özel Notlar
- GPIO pin mapping dokümante edilmeli
- Power consumption optimizasyonu
- Temperature monitoring
- Automatic restart on failure
- Remote update capability

---
*Modül detayları için [CLAUDE_MODULES.md](./CLAUDE_MODULES.md) dosyasına bakın.*
*Son güncelleme: 2025-07-16 17:48:00 +03:00*