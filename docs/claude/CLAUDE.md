# 📚 CLAUDE Documentation Index for UNIBOS

> **Note**: This is an index file. All detailed rules have been reorganized into a hierarchical system for better maintainability.

---

## 🎯 Rule System Hierarchy

UNIBOS uses a hierarchical rule system that prevents rules from degrading over time:

```
RULES.md (Ana dizin - Yönlendirme)
    ↓
docs/development/
    ├── VERSIONING_WORKFLOW.md (Hızlı referans)
    ├── VERSIONING_RULES.md (Detaylı kurallar)
    ├── DEVELOPMENT_LOG.md (Geliştirme kaydı)
    └── [diğer dokümanlar]
    ↓
tools/scripts/
    ├── unibos_version.sh (Versiyonlama master script)
    ├── backup_database.sh
    ├── verify_database_backup.sh
    └── rocksteady_deploy.sh
```

---

## 🚨 START HERE - FIRST STEPS

### Her Oturumda İlk İşlem:

1. **[RULES.md](../../RULES.md)** ← Ana yönlendirme dosyası (ANA DİZİNDE!)
2. **İlgili detay dosyasına git** (aşağıdaki linklerden)
3. **Script'i çalıştır** (manuel komut YOK!)

---

## 📂 Detaylı Kural Dosyaları

### Versiyonlama ve Deployment:
- **[VERSIONING_WORKFLOW.md](../development/VERSIONING_WORKFLOW.md)** - Hızlı workflow özeti
- **[VERSIONING_RULES.md](../development/VERSIONING_RULES.md)** - Detaylı versiyonlama kuralları
  - Versiyonlama workflow
  - Archive exclusion kuralları
  - Database backup sistemi
  - Deployment kuralları
  - Recursive self-validation

### Geliştirme ve Loglama:
- **[DEVELOPMENT_LOG.md](../development/DEVELOPMENT_LOG.md)** - Tüm geliştirme aktiviteleri
  - Log formatı ve kategorileri
  - Her oturum sonrası güncellenmeli
  - Script: `./tools/scripts/add_dev_log.sh`

### Claude Oturum Protokolleri:
- **[CLAUDE_SESSION_PROTOCOL.md](../development/CLAUDE_SESSION_PROTOCOL.md)** - Oturum başlangıç ve bitiş prosedürleri
  - Screenshot kontrolü
  - Istanbul timezone doğrulama
  - Git status kontrolü
  - Türkçe karşılama formatı
  - Development log güncelleme zorunluluğu

- **[SCREENSHOT_MANAGEMENT.md](../development/SCREENSHOT_MANAGEMENT.md)** - Screenshot tespit ve arşivleme
  - Otomatik tespit protokolü
  - İşleme workflow
  - Arşivleme kuralları (Istanbul timezone ile)
  - archive/media/screenshots/ yönetimi

- **[CODE_QUALITY_STANDARDS.md](../development/CODE_QUALITY_STANDARDS.md)** - Kod kalitesi ve güvenlik
  - Istanbul timezone enforcement (KRİTİK!)
  - Crash prevention (null checks, try-except)
  - Django best practices
  - Security checklist (SQL injection, XSS, CSRF)
  - Server restart kuralları

### Arşivlenen Eski Sistem (v525):
- **[Old CLAUDE_* files](../archive/claude_old_system_v525/)** - Deprecated, sadece referans için
  - CLAUDE_RULES.md (36KB - artık kullanılmıyor)
  - CLAUDE_CORE.md
  - CLAUDE_INSTRUCTIONS.md
  - CLAUDE_MANAGEMENT.md
  - CLAUDE_MODULES.md
  - CLAUDE_SUGGESTIONS.md
  - CLAUDE_TECH.md
  - CLAUDE_VERSION.md
  - CLAUDE_ARCHIVE.md

---

## 🔄 Recursive Self-Validation

Yeni kural sistemi **kendini koruyan** bir yapıya sahip:

### Validation Matrix
| Değişiklik Yapılan | Kontrol Edilmesi Gerekenler | Güncellenmesi Gerekenler |
|-------------------|---------------------------|------------------------|
| **RULES.md** | VERSIONING_WORKFLOW.md, VERSIONING_RULES.md | Script header comment'leri |
| **unibos_version.sh** | VERSIONING_RULES.md workflow bölümü | Script header, kural dökümanları |
| **VERSIONING_RULES.md** | unibos_version.sh, backup_database.sh | VERSIONING_WORKFLOW.md örnekleri |

### Atomik Commit Kuralı
Kural değişti → Script + Dokümantasyon birlikte commit edilmeli!

Detaylar için: **[RULES.md](../../RULES.md) - Recursive Self-Validation bölümü**

---

## 🛠️ Scriptler

Tüm scriptler `tools/scripts/` altında:

- `unibos_version.sh` - Versiyonlama master script
- `backup_database.sh` - Database backup
- `verify_database_backup.sh` - Backup doğrulama
- `rocksteady_deploy.sh` - Production deployment
- `add_dev_log.sh` - Development log helper

**Kural**: Manuel işlem YOK, her zaman script kullan!

---

## 📋 Hızlı Başvuru

### Versiyonlama Yapacaksan:
```bash
./tools/scripts/unibos_version.sh
# Options menüsünden seç:
# 1. Full cycle (archive + bump + commit + push)
# 2. Archive only
# 3. Version bump only
# 4. Git operations only
# 5. Database backup
```

### Database Backup Yapacaksan:
```bash
./tools/scripts/backup_database.sh
```

### Deployment Yapacaksan:
```bash
./tools/scripts/rocksteady_deploy.sh deploy
```

---

## 🔗 Proje Yapısı

### Monorepo Structure (v528+):
```
apps/
  ├── cli/src/           # CLI source code
  ├── web/backend/       # Django backend
  └── mobile/birlikteyiz/ # Flutter mobile app
docs/
  ├── architecture/      # System design docs
  ├── development/       # Development rules & logs
  ├── features/          # Feature documentation
  ├── deployment/        # Deployment guides
  ├── claude/            # Claude-specific docs (bu dosya)
  └── archive/           # Archived documentation
tools/
  └── scripts/           # All automation scripts
archive/
  ├── versions/          # Version archives
  └── database_backups/  # Database backups (son 3)
```

---

## ⚠️ KRİTİK HATIRLATMALAR

1. **HİÇBİR ZAMAN MANUEL İŞLEM YAPMA**
   - ❌ rsync, git commit, deployment manuel komutları
   - ✅ Script'leri kullan (tools/scripts/)

2. **HER OTURUMDA KURALLARI OKU**
   - İlk iş: RULES.md
   - İkinci iş: İlgili detay dosyası
   - Son iş: Script'i çalıştır

3. **DEĞİŞİKLİKLER ATOMİK OLMALI**
   - Kural değişti → Script + Dokümantasyon birlikte güncelle
   - Script değişti → Kurallar + Dokümantasyon birlikte güncelle

---

## 📝 Son Güncelleme

**Tarih:** 2025-11-09
**Değişiklik:** Claude oturum protokolleri eklendi - session start/end, screenshot, kod kalitesi
**Eklenenler:**
- ✅ CLAUDE_SESSION_PROTOCOL.md (oturum başlangıç ve bitiş prosedürleri)
- ✅ SCREENSHOT_MANAGEMENT.md (screenshot tespit, işleme, arşivleme)
- ✅ CODE_QUALITY_STANDARDS.md (timezone, crash prevention, Django best practices)
- ✅ RULES.md'ye oturum başlangıç checklist eklendi
- ✅ Validation matrix genişletildi

**Eski Sistem:** v525 CLAUDE_* dosyaları `docs/archive/claude_old_system_v525/` altında arşivlendi.
**Aktif Sistem:** RULES.md → [VERSIONING_WORKFLOW.md, CLAUDE_SESSION_PROTOCOL.md] → Detaylı protokoller

---

**🎯 Sonraki Adım:** [RULES.md](../../RULES.md) dosyasını oku!