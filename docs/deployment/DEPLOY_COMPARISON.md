# quick deploy vs full deployment karşılaştırma

**Last Updated**: 2025-11-10 (v532+ Modular Structure)

## ⚡ quick deploy (hızlı dağıtım)

### ne yapar:
1. **settings backup** - production.py ve .env yedeklenir
2. **file sync** - sadece değişen dosyalar rsync ile gönderilir
3. **settings restore** - yedeklenen ayarlar geri yüklenir
4. **gunicorn fix** - problemli gunicorn.conf.py silinir
5. **service restart** - gunicorn restart, nginx reload

### ne zaman kullanılır:
- kod güncellemeleri
- template değişiklikleri
- küçük bug fixler
- css/js güncellemeleri
- sık yapılan deploylar

### avantajları:
- **çok hızlı** (10-15 saniye)
- **güvenli** - settings korunur
- **minimal downtime** - sadece restart süresi
- **incremental** - sadece değişenler gönderilir

### yapmadiği şeyler:
- ❌ yeni paketler yüklemez
- ❌ migrations çalıştırmaz
- ❌ static files toplamaz
- ❌ venv güncellemez

---

## 📦 full deployment (tam dağıtım)

### ne yapar:
1. **settings backup** - production.py ve .env yedeklenir
2. **complete sync** - tüm proje rsync ile gönderilir
3. **settings restore** - yedeklenen ayarlar geri yüklenir
4. **gunicorn fix** - problemli config temizlenir
5. **venv check** - virtual environment kontrol/oluşturulur
6. **install deps** - requirements.txt'den paketler yüklenir
7. **run migrations** - database migrations çalıştırılır
8. **collect static** - static dosyalar toplanır
9. **service restart** - tüm servisler yeniden başlatılır

### ne zaman kullanılır:
- ilk kurulum
- yeni paket eklendi (requirements.txt değişti)
- model değişiklikleri (migrations gerekli)
- major güncellemeler
- uzun süre deploy yapılmadıysa

### avantajları:
- **komple güncelleme** - her şey güncel
- **bağımlılıklar dahil** - yeni paketler yüklenir
- **database güncel** - migrations çalışır
- **static files güncel** - css/js/images toplanır

### dezavantajları:
- **yavaş** (2-5 dakika)
- **downtime riski** - servisler restart
- **resource yoğun** - cpu/memory kullanımı

---

## 🔧 backend only

### ne yapar:
- sadece backend/ klasörünü günceller
- migrations çalıştırır
- gunicorn restart eder

### ne zaman:
- django kod değişiklikleri
- api güncellemeleri
- model değişiklikleri

---

## 💻 cli only

### ne yapar:
- sadece src/ klasörünü günceller
- script permissions ayarlar
- unibos.sh günceller

### ne zaman:
- cli menü değişiklikleri
- cli bug fixler
- backend'e dokunmayan değişiklikler

---

## 📊 özet karşılaştırma

| özellik | quick | full | backend | cli |
|---------|-------|------|---------|-----|
| süre | 10-15s | 2-5m | 30s | 15s |
| settings korunur | ✅ | ✅ | ✅ | - |
| dosya sync | ✅ | ✅ | ✅ | ✅ |
| dependencies | ❌ | ✅ | ❌ | ❌ |
| migrations | ❌ | ✅ | ✅ | ❌ |
| static files | ❌ | ✅ | ❌ | ❌ |
| service restart | ✅ | ✅ | ✅ | ❌ |
| downtime | minimal | var | minimal | yok |

---

## 🎯 önerilen kullanım

### günlük development:
```bash
quick deploy  # %90 durumlar için yeterli
```

### haftalık/major update:
```bash
full deployment  # komple güncelleme
```

### specific updates:
```bash
backend only  # django değişiklikleri
cli only      # cli değişiklikleri
```

---

## ⚠️ önemli notlar

1. **her zaman quick deploy ile başla** - çoğu zaman yeterli
2. **full deploy sadece gerektiğinde** - requirements.txt değişti, migrations var
3. **production.py asla transfer edilmez** - remote'daki korunur
4. **archive/ klasörü asla gönderilmez** - .rsyncignore ile korunur
5. **gunicorn.conf.py otomatik silinir** - permission hatalarını önler

---

## 🐛 troubleshooting

### 502 bad gateway:
```bash
# gunicorn'i kontrol et
ssh rocksteady "sudo systemctl status gunicorn"

# gunicorn.conf.py varsa sil
ssh rocksteady "rm -f ~/unibos/backend/gunicorn.conf.py"

# restart
ssh rocksteady "sudo systemctl restart gunicorn"
```

### migrations hata:
```bash
# full deploy çalıştır
full deployment
```

### static files görünmüyor:
```bash
# collectstatic gerekli
ssh rocksteady "cd ~/unibos/backend && ./venv/bin/python manage.py collectstatic --noinput"
```

## 📦 v532+ modular structure

### yeni yapı:
- **21 modül** - `modules/*/backend/` dizininde
- **her modül izole** - kendi backend/, mobile/, module.json dosyaları
- **Django settings** - `apps/web/backend/` içinde kalıyor
- **migrations** - Django tüm modül migration'larını otomatik buluyor

### deployment etkisi:
- **hiçbir değişiklik gerekmiyor** - mevcut deployment komutları çalışıyor
- **modules/ otomatik sync** - rsync tüm modülleri gönderiyor
- **static files** - tüm modüllerden toplanıyor
- **boyut artışı** - v532+ için ~40-60MB (21 modül dahil)

### ne deploy edilir:
✅ `modules/*/backend/` - tüm modül backend kodları
✅ `apps/web/backend/` - Django project settings
✅ `apps/cli/` - CLI interface
❌ `modules/*/mobile/build/` - Flutter build'ler excluded
❌ `archive/` - korunuyor

last updated: 2025-11-10