# 🎬 CLAUDE OTURUM PROTOKOLÜ

> **Amaç:** Her Claude oturumunun başlangıç ve bitişinde takip edilmesi gereken standart prosedürler.
> **Ref:** [RULES.md](../../RULES.md) - "HER OTURUM BAŞLANGICI" bölümü

---

## 🚀 OTURUM BAŞLANGICI (Session Start)

### Adım 1: Otomatik Taramalar (İlk 30 saniye)

Her oturum başında **MUTLAKA** bu kontrolleri yap:

#### A. Screenshot Kontrolü

```bash
# Ana dizinde screenshot var mı?
ls -la *.png Screenshot*.png 2>/dev/null

# Eğer screenshot varsa:
# 1. SCREENSHOT_MANAGEMENT.md'yi OKU
# 2. Protokolü takip et
# 3. İşlemi tamamla
```

**Neden:** Berk sıklıkla screenshot paylaşır, bunları hemen tespit edip işlemek gerekir.

#### B. Istanbul Timezone Doğrulama

```bash
# Istanbul saatini kontrol et
TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S %z'

# BEKLENEN ÇIKTI: 2025-11-09 14:30:45 +0300
# "+03:00" veya "+0300" görmeli sin!
```

**Neden:** Tüm timestamp'ler Istanbul timezone'da olmalı (Europe/Istanbul, UTC+3).

**HATA Durumu:** Eğer farklı timezone görürsen:
- ❌ Hemen DURDUR
- ⚠️ Kullanıcıya bildir: "UYARI: Timezone Istanbul değil!"
- 🔧 Düzelt ve devam et

#### C. Git Status Kontrolü

```bash
# Uncommitted değişiklikler var mı?
git status --short

# Örnek çıktı:
# M apps/web/backend/apps/documents/views.py
# ?? new_file.py
```

**Neden:** Kullanıcıya çalışma ortamının durumunu bildirmek.

**Bildirim:** Karşılamada kullanıcıya ilet:
- Clean: "Git status: Clean"
- Değişiklikler varsa: "Git status: 5 files changed, 2 untracked"

#### D. Current Version Kontrolü

```bash
# Mevcut version ne?
grep '"version"' apps/cli/src/VERSION.json | head -1

# Örnek çıktı: "version": "v531"
```

**Neden:** Hangi version üzerinde çalıştığını bilmek kritik.

---

### Adım 2: Kural Dosyalarını Oku

**SIRA ÖNEMLİ!** Her oturumda bu dosyaları oku:

1. **[RULES.md](../../RULES.md)** ← Ana yönlendirme (MUTLAKA)
2. **İlgili detay dosyası** ← Task'e göre seç
3. **Bu dosya** (CLAUDE_SESSION_PROTOCOL.md) ← Protokol hatırlatma

**Neden:** Kurallar sürekli güncellenebilir, her oturumda taze bilgi gerekir.

---

### Adım 3: Kullanıcıya Türkçe Karşılama

**Format:**

```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: [VAR: dosya adı / YOK]
⏰ Istanbul: [2025-11-09 14:30:45 +0300]
🔧 Git status: [Clean / 5 files changed]
📌 Version: [v531]

Ne üzerinde çalışmamı istersin?
```

**Örnekler:**

#### Örnek 1: Clean ortam, screenshot yok
```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: YOK
⏰ Istanbul: 2025-11-09 14:30:45 +0300
🔧 Git status: Clean
📌 Version: v531

Ne üzerinde çalışmamı istersin?
```

#### Örnek 2: Screenshot var, uncommitted changes var
```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: VAR - Screenshot_2025-11-09_14-30-45.png (işleme hazır)
⏰ Istanbul: 2025-11-09 14:30:45 +0300
🔧 Git status: 3 files changed, 1 untracked
📌 Version: v531

Screenshot'ı işleyebilirim ya da başka bir task verebilirsin. Ne yapmamı istersin?
```

---

## 🎯 OTURUM SIRASI GÖREVLER (During Session)

### 1. Screenshot İşleme (Öncelikli)

Eğer screenshot tespit edildiyse:

- **[SCREENSHOT_MANAGEMENT.md](SCREENSHOT_MANAGEMENT.md)** ← Protokolü takip et
- İşlem tamamlanana kadar diğer tasklara geçme
- İşlem sonunda kullanıcıya özet rapor ver

### 2. Kod Kalitesi Standartları

Her kod değişikliğinde:

- **[CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md)** ← Standartları kontrol et
- Istanbul timezone enforcement
- Crash prevention checks
- Django server restart kuralları

### 3. Versiyonlama İşlemleri

Versiyonlama yapılacaksa:

1. **[VERSIONING_WORKFLOW.md](VERSIONING_WORKFLOW.md)** ← Hızlı workflow
2. **[VERSIONING_RULES.md](VERSIONING_RULES.md)** ← Detaylı kurallar
3. **Script kullan:** `./tools/scripts/unibos_version.sh`

**ASLA MANUEL KOMUT KULLANMA!**

---

## 🏁 OTURUM SONU (Session End)

### Adım 1: Development Log Güncellemesi

**ZORUNLU:** Her oturum sonunda [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) güncelle!

```bash
# Script kullan
./tools/scripts/add_dev_log.sh \
  "Kategori" \
  "Başlık" \
  "Yapılan işlemler detayı" \
  "Sonuç ve notlar"
```

**Kategoriler:**
- Project Structure
- Version Management
- Feature Development
- Bug Fix
- Documentation
- Deployment
- Database
- Rules System

**Örnek:**

```bash
./tools/scripts/add_dev_log.sh \
  "Rules System" \
  "Claude session protocol eklendi" \
  "Oturum başlangıç ve bitiş protokollerini içeren CLAUDE_SESSION_PROTOCOL.md oluşturuldu. Screenshot yönetimi, timezone kontrolü, git status kontrolü ve karşılama formatı standardize edildi." \
  "Artık her oturumda Claude bu protokolü takip edecek."
```

### Adım 2: Git Status Kontrolü

```bash
# Son durum ne?
git status

# Uncommitted değişiklikler varsa:
# - Kullanıcıya bildir
# - Commit gerekip gerekmediğini sor
```

### Adım 3: Özet Rapor

Kullanıcıya oturumun özetini ver:

```
📊 Oturum Özeti:

✅ Tamamlanan:
- [Task 1]
- [Task 2]

⏸️ Devam Eden:
- [Task 3 - %60 tamamlandı]

📝 Not:
- [Önemli bilgi 1]
- [Önemli bilgi 2]

🔜 Sonraki Adım Önerisi:
- [Öneri]
```

---

## ⚠️ KRİTİK HATALAR VE ÇÖZÜMLER

### Hata 1: Timezone Yanlış

**Tespit:**
```bash
date '+%z'  # Çıktı: +0000 veya +0200 (YANLIŞ!)
```

**Çözüm:**
```bash
# Her komutta TZ belirt
TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S %z'
```

### Hata 2: Screenshot Atlandı

**Tespit:** Oturum başında screenshot kontrolü yapılmadı

**Çözüm:**
- Hemen kontrol et
- Bulunursa, derhal işleme al
- Kullanıcıya bildir: "Screenshot tespit edildi, önce onu işleyeyim mi?"

### Hata 3: Development Log Unutuldu

**Tespit:** Oturum sonunda log güncellenmedi

**Çözüm:**
- Bir sonraki oturumda ilk iş olarak güncelle
- Önceki oturum için de ekle (tarih belirterek)

### Hata 4: Manuel Komut Kullanıldı

**Tespit:** `rsync`, `git commit`, deployment manuel çalıştırıldı

**Çözüm:**
- İşlemi DURDUR
- Script kullan: `tools/scripts/` altındaki uygun script'i çalıştır
- [RULES.md](../../RULES.md) tekrar oku

---

## 📋 Quick Reference Checklist

### Session Start ✅
- [ ] Screenshot kontrolü yaptım
- [ ] Istanbul timezone doğruladım
- [ ] Git status kontrol ettim
- [ ] Current version öğrendim
- [ ] RULES.md okudum
- [ ] Türkçe karşılama yaptım

### During Session ✅
- [ ] Screenshot varsa önce onu işledim
- [ ] Kod kalitesi standartlarına uydum
- [ ] Manuel komut kullanmadım, script kullandım
- [ ] Atomik commit kuralına uydum

### Session End ✅
- [ ] DEVELOPMENT_LOG.md güncelledim
- [ ] Git status kontrol ettim
- [ ] Özet rapor verdim
- [ ] Sonraki adım önerdim

---

## 📝 Son Güncelleme

**Tarih:** 2025-11-09
**Değişiklik:** İlk oluşturma - Claude oturum protokolü standardize edildi
**Neden:** Her oturumda tutarlı prosedür izlenmesi, screenshot ve timezone kontrollerinin otomasyonu

---

**⬆️ Üst Dosya:** [RULES.md](../../RULES.md)
**📚 İlgili Dosyalar:**
- [SCREENSHOT_MANAGEMENT.md](SCREENSHOT_MANAGEMENT.md)
- [CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md)
- [VERSIONING_RULES.md](VERSIONING_RULES.md)
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)
