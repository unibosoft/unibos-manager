# UNIBOS Raspberry Pi / Edge Node Geliştirme Planı

**Oluşturma Tarihi:** 2025-12-03
**Son Güncelleme:** 2025-12-03
**Durum:** IN PROGRESS
**İlgili Versiyon:** v1.1.0+

---

## Özet

Bu doküman, UNIBOS'un Raspberry Pi ve diğer edge cihazlarda çalışması için yapılması gereken geliştirmeleri detaylandırır. Amaç:

1. **Tek satır kurulum** (`curl | bash`)
2. **Zero-config keşif** (mDNS ile otomatik bulma)
3. **Local-first mimari** (hassas veriler yerel kalır)
4. **Akıllı fallback** (Raspberry offline → Rocksteady'e düş)

---

## Tamamlanan Adımlar

### 1. Node Registry (v1.1.0) ✅
- [x] `core/system/nodes/` Django app
- [x] Models: Node, NodeCapability, NodeMetric, NodeEvent
- [x] API: register, heartbeat, discover
- [x] Celery tasks: heartbeat monitoring, cleanup
- [x] Release v1.1.0 ve Rocksteady deploy

### 2. install.sh Script ✅
- [x] `tools/install/install.sh` oluşturuldu
- [x] Platform detection (Pi Zero 2W, Pi 4, Pi 5)
- [x] Otomatik bağımlılık kurulumu
- [x] PostgreSQL + Redis setup
- [x] mDNS (Avahi) yapılandırması
- [x] Systemd service template
- [x] Node auto-registration

---

## Devam Eden Adımlar

### 3. Edge Settings Dosyası
- [ ] `core/clients/web/unibos_backend/settings/edge.py` oluştur
  ```python
  # Edge-specific settings
  # - Lightweight configuration
  # - Local-only database
  # - Reduced logging
  # - Pi Zero optimizations
  ```

### 4. Module Enablement System
- [ ] Edge node'da sadece seçili modüllerin aktif olması
- [ ] `data/config/enabled_modules.json`
- [ ] Pi Zero 2W için minimal modül seti (sadece WIMM)
- [ ] Pi 4/5 için tam modül desteği

### 5. Client-Side Discovery (Web UI)
- [ ] JavaScript mDNS discovery (WebSocket üzerinden?)
- [ ] Known hosts cache (localStorage)
- [ ] Connection manager (primary/fallback)
- [ ] Node selector UI

---

## Yapılacaklar (Sıralı)

### Faz 1: Temel Kurulum (Öncelik: YÜKSEK)

#### 1.1 Edge Settings
```
Dosya: core/clients/web/unibos_backend/settings/edge.py
İçerik:
- DEBUG = False
- Minimal INSTALLED_APPS
- SQLite fallback (PostgreSQL yoksa)
- Düşük memory cache
- Disk-based session (Redis yoksa)
```

#### 1.2 install.sh İyileştirmeleri
```
- [ ] SQLite fallback (PostgreSQL kurulamazsa)
- [ ] Offline kurulum desteği (tar.gz'den)
- [ ] Kurulum sırasında progress bar
- [ ] Uninstall script
- [ ] Update script
```

#### 1.3 Test Script'i
```
Dosya: tools/install/test_install.sh
- [ ] Docker container'da test
- [ ] Her Pi modeli için CI/CD
- [ ] Performans benchmark'ları
```

### Faz 2: mDNS & Discovery (Öncelik: YÜKSEK)

#### 2.1 Zeroconf Python Module
```
Dosya: core/base/discovery/mdns.py
- [ ] ServiceBrowser (node keşfi)
- [ ] ServiceInfo (node bilgisi yayını)
- [ ] Callback handlers
- [ ] CLI: unibos network scan
```

#### 2.2 Web UI Discovery
```
Dosya: core/system/web_ui/static/js/discovery.js
- [ ] WebSocket üzerinden backend'e mDNS sorgusu
- [ ] localStorage'da known hosts
- [ ] Auto-connect logic
- [ ] Manual node selection
```

#### 2.3 Discovery API
```
Endpoint: /api/v1/discovery/
- [ ] GET /scan - Yerel ağda node ara
- [ ] GET /known - Bilinen node listesi
- [ ] POST /connect - Node'a bağlan
```

### Faz 3: Local-First Sync (Öncelik: ORTA)

#### 3.1 Sync Engine Base
```
Dosya: core/base/sync/engine.py
- [ ] SyncDirection enum (UP, DOWN, BIDIRECTIONAL, NONE)
- [ ] SyncPolicy per model
- [ ] Conflict resolution
- [ ] Offline queue
```

#### 3.2 Module Sync Policies
```
WIMM:          NONE (asla sync)
Documents:     NONE (asla sync)
CCTV:          NONE (asla sync)
Currencies:    DOWN (sadece fiyat al)
Birlikteyiz:   DOWN (sadece deprem verisi al)
Recaria:       BIDIRECTIONAL (multiplayer)
```

#### 3.3 Selective Field Encryption
```
Dosya: core/base/encryption/fields.py
- [ ] EncryptedCharField
- [ ] EncryptedTextField
- [ ] EncryptedJSONField
- [ ] Key derivation from master password
```

### Faz 4: Remote Access (Öncelik: ORTA)

#### 4.1 Tailscale Integration
```
Dosya: tools/install/setup_tailscale.sh
- [ ] Otomatik Tailscale kurulumu
- [ ] MagicDNS yapılandırması
- [ ] Firewall rules
```

#### 4.2 WireGuard Alternative
```
Dosya: tools/install/setup_wireguard.sh
- [ ] WireGuard server on Raspberry
- [ ] QR code generation for mobile
- [ ] Auto-reconnect
```

### Faz 5: Performance Optimization (Öncelik: DÜŞÜK)

#### 5.1 Pi Zero 2W Optimizations
```
- [ ] Single worker mode
- [ ] SQLite instead of PostgreSQL
- [ ] Disabled Celery (sync tasks)
- [ ] Reduced static files
- [ ] Memory-mapped cache
```

#### 5.2 Pi 4/5 Full Mode
```
- [ ] Multi-worker ASGI
- [ ] PostgreSQL with connection pooling
- [ ] Redis cluster support
- [ ] WebSocket scaling
```

---

## Dosya Yapısı (Hedef)

```
unibos-dev/
├── tools/
│   └── install/
│       ├── install.sh              ✅ OLUŞTURULDU
│       ├── uninstall.sh            [ ] YAPILACAK
│       ├── update.sh               [ ] YAPILACAK
│       ├── test_install.sh         [ ] YAPILACAK
│       ├── setup_tailscale.sh      [ ] YAPILACAK
│       └── setup_wireguard.sh      [ ] YAPILACAK
│
├── core/
│   ├── base/
│   │   ├── discovery/
│   │   │   ├── __init__.py         [ ] YAPILACAK
│   │   │   └── mdns.py             [ ] YAPILACAK
│   │   ├── sync/
│   │   │   ├── __init__.py         [ ] YAPILACAK
│   │   │   ├── engine.py           [ ] YAPILACAK
│   │   │   └── policies.py         [ ] YAPILACAK
│   │   └── encryption/
│   │       ├── __init__.py         [ ] YAPILACAK
│   │       └── fields.py           [ ] YAPILACAK
│   │
│   └── clients/
│       └── web/
│           └── unibos_backend/
│               └── settings/
│                   └── edge.py     [ ] YAPILACAK
│
└── TODO_RASPBERRY.md               ✅ BU DOSYA
```

---

## Test Senaryoları

### Senaryo 1: Temiz Kurulum (Pi 4)
```bash
# Raspberry Pi 4 üzerinde
curl -sSL https://unibos.recaria.org/install.sh | bash

# Beklenen:
# - 5-10 dakika kurulum
# - Tüm modüller aktif
# - mDNS yayını başlar
# - Central'a kayıt olur
```

### Senaryo 2: Minimal Kurulum (Pi Zero 2W)
```bash
# Raspberry Pi Zero 2W üzerinde
curl -sSL https://unibos.recaria.org/install.sh | bash

# Beklenen:
# - 10-15 dakika kurulum
# - Sadece WIMM aktif
# - SQLite kullanılır
# - Celery devre dışı
```

### Senaryo 3: Mac Browser → Raspberry
```
1. Mac'te browser aç
2. http://raspberry.local:8000 adresine git
3. WIMM modülüne eriş
4. Veri ekle/düzenle
5. Verinin Rocksteady'e GİTMEDİĞİNİ doğrula
```

### Senaryo 4: Raspberry Offline → Fallback
```
1. Raspberry'yi kapat
2. Mac browser'da sayfayı yenile
3. Otomatik olarak Rocksteady'e düşmeli
4. Sadece public modüller erişilebilir olmalı
5. WIMM verileri erişilemez (çünkü yerel)
```

### Senaryo 5: Dış Erişim (Tailscale)
```
1. Evde Raspberry çalışıyor
2. Dışarıda (4G) telefon/laptop'tan
3. Tailscale VPN ile bağlan
4. http://raspberry.tailnet:8000 erişimi
5. WIMM dahil tüm yerel verilere güvenli erişim
```

---

## Performans Hedefleri

| Metrik | Pi Zero 2W | Pi 4 (4GB) | Pi 5 (8GB) |
|--------|------------|------------|------------|
| Kurulum süresi | < 15 dk | < 10 dk | < 8 dk |
| Boot → Ready | < 60 sn | < 30 sn | < 20 sn |
| Memory (idle) | < 200 MB | < 400 MB | < 500 MB |
| API latency (p95) | < 500 ms | < 200 ms | < 100 ms |
| Concurrent users | 1-2 | 5-10 | 10-20 |

---

## Güvenlik Kontrol Listesi

- [ ] Database credentials şifreli (`data/config/db.env`)
- [ ] SECRET_KEY rastgele ve güvenli
- [ ] PostgreSQL sadece localhost'tan erişilebilir
- [ ] Redis password korumalı (production)
- [ ] Firewall rules (sadece 8000 portu açık)
- [ ] HTTPS (self-signed veya Let's Encrypt)
- [ ] Rate limiting aktif
- [ ] CORS sadece bilinen origins
- [ ] JWT token expiry
- [ ] Sensitive fields encrypted

---

## Notlar

### mDNS Avahi vs Zeroconf Kararı
**Seçim: HİBRİT**
- Avahi: Sistem seviyesinde temel advertisement (boot'ta hemen başlar)
- Zeroconf: Python'da gelişmiş discovery (dinamik, programatik)

### Database Encryption Kararı
**Seçim: APPLICATION-LEVEL (Faz 1), TDE (Faz 2)**
- Hızlı başlangıç için Django encrypted fields
- Sonra PostgreSQL TDE eklenebilir

### Desteklenen Platformlar
- Raspberry Pi Zero 2W (512MB) - Minimal
- Raspberry Pi 4 (2GB, 4GB, 8GB) - Önerilen
- Raspberry Pi 5 (4GB, 8GB) - Tam performans
- Ubuntu/Debian Linux - Generic support

---

## İlgili Dosyalar

- `TODO.md` - Ana geliştirme roadmap
- `RULES.md` - Proje kuralları
- `tools/install/install.sh` - Kurulum script'i
- `core/system/nodes/` - Node Registry modülü

---

## Sonraki Adımlar (Bu Oturum)

1. [x] install.sh oluştur
2. [ ] edge.py settings dosyası oluştur
3. [ ] install.sh'i executable yap ve test et
4. [ ] Raspberry Pi'de gerçek test

---

**Son Güncelleme:** 2025-12-03 17:30 UTC+3
**Güncelleyen:** Claude + Berk
