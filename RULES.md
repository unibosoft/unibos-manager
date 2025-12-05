# 🎯 UNIBOS KURALLAR - CLAUDE İÇİN YÖNLENDME DOSYASI

> **⚠️ KRİTİK:** Bu dosya ana dizindedir, Claude her oturumda MUTLAKA görecektir.
> **AMAÇ:** Claude'u doğru kural dosyalarına yönlendirmek, detay vermek DEĞİL!
> **VERSİYON:** v2.0.0 (5-Profile Architecture)

---

## 🚨 EN ÖNEMLİ 3 KURAL

### 1️⃣ HİÇBİR ZAMAN MANUEL İŞLEM YAPMA
```
❌ ASLA ASLA ASLA:
   • Manuel rsync komutları
   • Manuel ssh deployment komutları
   • Manuel git commit/tag/branch komutları
   • Manuel deployment işlemleri
   • Manuel arşiv oluşturma
   • Manuel version bump işlemleri
   • Manuel pip install veya dependency kurulumu (remote'da)
   • Manuel service restart komutları
   • Manuel dev→prod sync veya git push komutları

✅ HER ZAMAN HER ZAMAN HER ZAMAN:
   • unibos-dev TUI → versions → 📦 quick release (versiyonlama için)
   • ReleasePipeline sınıfı (core/profiles/dev/release_pipeline.py)
   • ./tools/scripts/backup_database.sh (database backup için)
   • ./core/deployment/rocksteady_deploy.sh (deployment için)
   • unibos-dev git push-all (tüm repolara push için)
   • unibos-dev git push-all --repos dev,hub,manager,node,worker

⚠️ BU KURAL İHLAL EDİLEMEZ - HİÇBİR İSTİSNA YOK!
⚠️ DEPLOYMENT MUTLAKA ./core/deployment/rocksteady_deploy.sh İLE YAPILMALI!
```

### 2️⃣ HER OTURUMDA KURALLARI OKU
```
1. İlk iş: RULES.md (bu dosya)
2. İkinci iş: İlgili detay dosyası
3. Son iş: Script'i çalıştır
```

### 3️⃣ DEĞIŞIKLIKLER ATOMIK OLMALI
```
Kural değişti → Script + Dokümantasyon birlikte güncelle
Script değişti → Kurallar + Dokümantasyon birlikte güncelle
TODO güncellendi → İlgili code/docs birlikte commit et
```

### 4️⃣ ANA DİZİN HEP DÜZENLİ OLMALI
```
✅ Ana dizinde SADECE:
   • README.md, RULES.md, TODO.md
   • VERSION.json
   • .gitignore, .rsyncignore, .archiveignore
   • setup.py, pyproject.toml (packaging)
   • core/, modules/, data/, docs/, tools/ (dizinler)

❌ Ana dizinde ASLA:
   • Eski TODO/ROADMAP dosyaları
   • Geçici notlar, planlar
   • Backup dosyaları
   • Test dosyaları

→ Tüm eski planlama dosyaları: archive/planning/
→ Tamamlanan TODO'lar: archive/planning/completed/
```

### 5️⃣ DOKÜMANTASYON KURALI
```
✅ YAP:
   • Mevcut dökümanları her zaman güncel tut
   • Değişiklik yaptığında ilgili dökümanı güncelle
   • TODO.md'yi sürekli güncel tut
   • RULES.md'yi yeni kurallarla güncelle

❌ YAPMA:
   • Yeni dokümantasyon dosyası oluşturma
   • Gereksiz README dosyaları yaratma
   • Aynı bilgiyi birden fazla yerde tekrarlama
   • Dökümantasyonu erteleme (değişiklikle birlikte güncelle!)

⚠️ TEK İSTİSNA: Kullanıcı açıkça yeni döküman isterse
```

---

## 🎬 HER OTURUM BAŞLANGICI - ZORUNLU CHECKLIST

**⚠️ MUTLAKA YAP:** Claude, her yeni oturuma başlarken bu checklist'i takip et!

### 1️⃣ Otomatik Kontroller (İlk 30 saniye)

```bash
# A. Screenshot kontrolü
ls -la *.png Screenshot*.png 2>/dev/null
# → VARSA: SCREENSHOT_MANAGEMENT.md oku ve işle
# → YOKSA: Devam et

# B. Istanbul timezone doğrulama
TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S %z'
# → "+03:00" görmeli sin - YOKSA HATA!

# C. Git status
git status --short
# → Uncommitted changes varsa: Not et, kullanıcıya bildir

# D. Current version
python3 -c "from core.version import __version__, __build__; print(f'v{__version__}+{__build__}')"
```

### 2️⃣ Detaylı Protokol (Oku ve Uygula)

- **[docs/development/CLAUDE_SESSION_PROTOCOL.md](docs/development/CLAUDE_SESSION_PROTOCOL.md)** ← Oturum protokolü (MUTLAKA OKU!)
- **[docs/development/SCREENSHOT_MANAGEMENT.md](docs/development/SCREENSHOT_MANAGEMENT.md)** ← SS varsa işle
- **[docs/development/CODE_QUALITY_STANDARDS.md](docs/development/CODE_QUALITY_STANDARDS.md)** ← Kod standartları

### 3️⃣ Kullanıcıya Karşılama (Türkçe)

```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: [VAR: dosya adı / YOK]
⏰ Istanbul: [YYYY-MM-DD HH:MM:SS +03:00]
🔧 Git status: [Clean / X files changed]
📌 Version: [v2.0.0+BUILD_TIMESTAMP]

Ne üzerinde çalışmamı istersin?
```

---

## 📂 KURAL DOSYALARI - BURAYA GIT!

### Versiyonlama Yapacaksan:
1. **[docs/development/VERSIONING_WORKFLOW.md](docs/development/VERSIONING_WORKFLOW.md)** ← Hızlı workflow özeti
2. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← Detaylı kurallar
3. **TUI:** `unibos-dev` → versions → 📦 quick release
4. **Pipeline:** `core/profiles/dev/release_pipeline.py`

### Arşivleme Yapacaksan:
1. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← "Archive Exclusion Rules" bölümü
2. **[.archiveignore](.archiveignore)** ← Hariç tutulan dosyalar
3. **Pipeline:** `ReleasePipeline._step_create_archive()` metodu
4. **Konum:** `archive/versions/unibos_v{VERSION}_b{BUILD}/`

### Database Backup Yapacaksan:
1. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← "Database Backup System" bölümü
2. **Script:** `./tools/scripts/backup_database.sh`
3. **Verify:** `./tools/scripts/verify_database_backup.sh`

### Deployment Yapacaksan:
1. **[core/deployment/README.md](core/deployment/README.md)** ← Deployment guide
2. **Script:** `./core/deployment/rocksteady_deploy.sh`
3. **⚠️ MUTLAKA:** Pre-flight checks yapılır, manuel komut yasak!

### Multi-Repo Workflow Yapacaksan:
1. **5 Repo Mimarisi:**
   - `unibos-dev` - Tam geliştirme ortamı
   - `unibos-hub` - Hub server (Identity Provider, Registry)
   - `unibos-manager` - Uzak yönetim araçları
   - `unibos` (node) - Local node uygulaması
   - `unibos-worker` - Background task processing
2. **CLI Commands:**
   - `unibos-dev git setup --force` - Git remotes kurulumu
   - `unibos-dev git push-all --repos all` - Tüm repolara push
   - `unibos-dev git push-all --repos dev,hub` - Seçili repolara push
3. **⚠️ KRİTİK:**
   - Her repo için ayrı .gitignore.{profile} template'i var
   - Push sırasında otomatik olarak doğru template aktive edilir
   - ASLA manuel git push kullanma, her zaman push-all komutunu kullan!

---

## 🔗 DOSYA HİYERARŞİSİ

```
RULES.md (bu dosya - YÖNLENDME)
    ↓
core/
    ├── version.py (versiyon bilgisi: __version__, __build__)
    ├── profiles/dev/
    │   ├── tui.py (Dev TUI - versions menüsü)
    │   └── release_pipeline.py (ReleasePipeline sınıfı)
    └── clients/cli/framework/ui/
        └── splash.py (MERKEZI splash modülü)
    ↓
docs/development/
    ├── VERSIONING_WORKFLOW.md (hızlı referans)
    ├── VERSIONING_RULES.md (DETAYLI KURALLAR - BURAYA GIT!)
    ├── DEVELOPMENT_LOG.md
    └── [diğer dokümanlar]
    ↓
tools/scripts/
    ├── backup_database.sh
    └── verify_database_backup.sh
core/deployment/
    ├── rocksteady_deploy.sh (production deployment)
    └── README.md (deployment guide)
```

---

## ✅ HER İŞLEM ÖNCESİ CHECKLIST

### Versiyonlama Yapacaksan:
- [ ] `RULES.md` okudum (bu dosya)
- [ ] `VERSIONING_WORKFLOW.md` okudum (hızlı workflow)
- [ ] `docs/development/VERSIONING_RULES.md` okudum (detaylı kurallar)
- [ ] TUI veya ReleasePipeline kullanacağım (manuel komut YOK!)

### Script Değiştireceksen:
- [ ] Hangi kuralın etkilendiğini tespit ettim
- [ ] İlgili kural dosyasını okudum
- [ ] Atomik commit yapacağım (script + kurallar birlikte)

### Kural Değiştireceksen:
- [ ] Hangi script'lerin etkileneceğini tespit ettim
- [ ] Tüm seviyeler güncellenecek (RULES.md, VERSIONING_WORKFLOW.md, VERSIONING_RULES.md)
- [ ] Atomik commit yapacağım (kurallar + scriptler birlikte)

---

## 🔄 RECURSIVE SELF-VALIDATION SYSTEM

### Kendini Koruyan Kurallar Prensibi

**Amaç**: Kuralların zamanla bozulmasını önlemek, her değişiklikte tutarlılığı sağlamak.

### Validation Matrix

| Değişiklik Yapılan | Kontrol Edilmesi Gerekenler | Güncellenmesi Gerekenler |
|-------------------|---------------------------|------------------------|
| **RULES.md** | VERSIONING_WORKFLOW.md, VERSIONING_RULES.md, CLAUDE_SESSION_PROTOCOL.md | Script header comment'leri, CLAUDE.md index |
| **TODO.md** | Tamamlanan tasklar archive'e taşınmalı | İlgili code/docs birlikte commit |
| **unibos_version.sh** | VERSIONING_RULES.md workflow bölümü | Script header, kural dökümanları |
| **VERSIONING_RULES.md** | unibos_version.sh, backup_database.sh | VERSIONING_WORKFLOW.md örnekleri |
| **.archiveignore** | .gitignore tutarlılığı | VERSIONING_RULES.md exclusion listesi |
| **.rsyncignore** | .archiveignore tutarlılığı | core/deployment/README.md exclusion listesi |
| **rocksteady_deploy.sh** | core/deployment/README.md, .rsyncignore | RULES.md deployment bölümü |
| **CLAUDE_SESSION_PROTOCOL.md** | SCREENSHOT_MANAGEMENT.md, CODE_QUALITY_STANDARDS.md | RULES.md checklist, CLAUDE.md index |
| **SCREENSHOT_MANAGEMENT.md** | CLAUDE_SESSION_PROTOCOL.md | .archiveignore screenshot path'leri |
| **CODE_QUALITY_STANDARDS.md** | CLAUDE_SESSION_PROTOCOL.md | Kod değişikliklerinde uyumluluk |
| **.gitignore.{profile}** | git.py, release_pipeline.py | 5-repo push templates |
| **core/profiles/dev/commands/git.py** | .gitignore templates | Push-all command, repo config |

### Atomik Commit Kuralı

```bash
# ❌ YANLIŞ: Sadece script değişti
git add tools/scripts/unibos_version.sh
git commit -m "Updated versioning script"

# ✅ DOĞRU: Script + İlgili kurallar + Dökümanlar birlikte
git add tools/scripts/unibos_version.sh
git add docs/development/VERSIONING_RULES.md
git add VERSIONING_WORKFLOW.md
git commit -m "refactor(versioning): update workflow order

- Updated unibos_version.sh to archive before version bump
- Updated VERSIONING_RULES.md with correct workflow
- Updated VERSIONING_WORKFLOW.md examples

Refs: #recursive-validation"
```

### Self-Check Süreci

Her değişiklik sonrası kendine şu soruları sor:

1. **Kural değişti mi?**
   - Etkilenen script'ler tespit edildi mi?
   - Script header'ları güncellendi mi?
   - İlgili dökümanlar senkronize edildi mi?

2. **Script değişti mi?**
   - Script header'daki rule referansları doğru mu?
   - İlgili kural dosyaları güncellendi mi?
   - Workflow örnekleri hala geçerli mi?

3. **Değişiklik atomik mi?**
   - Tüm ilgili dosyalar aynı commit'te mi?
   - Commit mesajı ne değiştiğini açıklıyor mu?
   - Cross-reference'lar bozulmadı mı?

### Gelecek: Otomatik Validation

```bash
# TODO: tools/scripts/validate_rules.sh oluşturulacak
# Bu script otomatik olarak:
# 1. Kural dosyalarının varlığını kontrol eder
# 2. Çapraz referansları doğrular
# 3. Script header'larındaki rule linklerini validate eder
# 4. Tutarsızlıkları rapor eder
```

---

## 📝 Son Güncelleme

**Tarih:** 2025-12-05
**Versiyon:** v2.0.0+20251205150933 (5-Profile Architecture)
**Neden:** v2.0.0 major release - 5-profile architecture migration

**Değişiklikler:**
- ✅ 5-Profile Architecture: dev, hub, manager, node, worker
- ✅ 5-Repo System: unibos-dev, unibos-hub, unibos-manager, unibos, unibos-worker
- ✅ Worker profile with real Celery integration
- ✅ Profile renames: server→hub, prod→node
- ✅ Git push-all command updated for 5 repos
- ✅ .gitignore templates for each repo (.gitignore.{profile})
- ✅ Deploy system updated (HubDeployer)
- ✅ Release pipeline updated for 5-repo push
- ✅ VERSION.json display sync fix
- ✅ Mobile SDK excluded from archives

**Bir Önceki Güncelleme:** 2025-12-02 - v1.0.0 stable release
**Sonraki Gözden Geçirme:** Her major script veya kural değişikliğinde

---

## 📌 VERSİYONLAMA KURALLARI (2025-12-05)

### Semantic Versioning + Timestamp Build
```
FORMAT: MAJOR.MINOR.PATCH+BUILD_TIMESTAMP
ÖRNEK:  v2.0.0+20251205150933

MAJOR (X.0.0): Breaking changes
  ↳ CLI komut yapısı değişti
  ↳ API incompatible
  ↳ Database schema major change

MINOR (0.X.0): Yeni özellikler (geriye uyumlu)
  ↳ Yeni CLI komutları
  ↳ Yeni modüller
  ↳ Geriye uyumlu özellikler

PATCH (0.0.X): Bug fixler
  ↳ Hata düzeltmeleri
  ↳ Küçük iyileştirmeler
  ↳ Dokümantasyon güncellemeleri

BUILD (YYYYMMDDHHmmss): Her release'de otomatik güncellenir
  ↳ Timestamp formatı: 20251202003028 (2 Aralık 2025, 00:30:28)
```

### Version Dosyası
```python
# core/version.py
__version__ = "2.0.0"           # Semantic version
__version_info__ = (2, 0, 0)    # Tuple format
__build__ = "20251205150933"    # Timestamp build

# Fonksiyonlar:
get_version()           # "2.0.0"
get_build()             # "20251205150933"
get_full_version()      # Dict with all info
get_short_version_string()  # "v2.0.0"
parse_build_timestamp() # Parse build to date/time
```

### Version Değiştirme Prosedürü (TUI)
```
1. unibos-dev komutu ile TUI'yi aç
2. "versions" menüsüne git
3. "📦 quick release" seç
4. Release tipini seç:
   - build: Sadece yeni timestamp (versiyon aynı)
   - patch: 1.0.0 → 1.0.1
   - minor: 1.0.0 → 1.1.0
   - major: 1.0.0 → 2.0.0
5. Pipeline otomatik çalışır:
   - Version güncellenir
   - Arşiv oluşturulur
   - Git commit + tag
   - 5 repo'ya push (dev, hub, manager, node, worker)
6. TUI otomatik restart olur
```

### Release Pipeline
```python
# core/profiles/dev/release_pipeline.py
from core.profiles.dev.release_pipeline import ReleasePipeline

pipeline = ReleasePipeline()
result = pipeline.run(
    release_type='minor',      # build, patch, minor, major
    message='feat: new feature',
    repos=['dev', 'hub', 'manager', 'node', 'worker']
)
```

### Arşiv Yapısı
```
archive/versions/
  ├── old_pattern_v001_v533/     # Pre-1.0 arşivi (v0.1.0 - v0.533.0)
  ├── unibos_v1.0.0_b20251202000650/
  ├── unibos_v1.1.x_b.../
  └── unibos_v2.0.0_b20251205150933/

# Arşiv isimlendirme: unibos_v{VERSION}_b{BUILD}
# Örnek: unibos_v2.0.0_b20251205150933
```

### Version Branch Stratejisi (IMMUTABLE SNAPSHOT)
```
⚠️ ÖNEMLİ: Version branch'ler RELEASE SNAPSHOT'ıdır!

KURAL: Version branch = O release anındaki kod (değişmez)
       main branch = Her zaman en güncel kod

ÖRNEK:
  v2.0.0+build.20251205150933  →  Release anındaki commit (frozen)
  main                          →  En son commit'ler (active)

NEDEN?
  ✅ Reproduceability: "v2.0.0 ne içeriyordu?" sorusuna kesin cevap
  ✅ Hotfix: v2.0.0'dan branch alıp v2.0.1 yapılabilir
  ✅ Archive ile uyum: archive/versions/ aynı mantık
  ✅ Git tag'lerle tutarlı (immutable)

PUSH AKIŞI:
  unibos-dev git push-all                  # Sadece main push
  unibos-dev git push-all --with-version   # main + version branch (as-is)

❌ YAPILMAMASI GEREKEN:
  Version branch'i main ile merge etme!
  Version branch release snapshot'ı olarak kalmalı.
```

### Detaylı Döküman
- `CHANGELOG.md` - Version history (otomatik güncellenir)
- `core/version.py` - Version metadata & functions
- `core/profiles/dev/release_pipeline.py` - Release automation
- `core/profiles/dev/changelog_manager.py` - Changelog generator

---

## 📋 CHANGELOG YÖNETİMİ (Conventional Commits)

### Commit Mesajı Formatı
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Commit Tipleri
| Tip | Açıklama | Emoji | Version Etkisi |
|-----|----------|-------|----------------|
| `feat` | Yeni özellik | ✨ | MINOR bump |
| `fix` | Bug fix | 🐛 | PATCH bump |
| `docs` | Dokümantasyon | 📝 | - |
| `style` | Kod stili (formatting) | 💄 | - |
| `refactor` | Kod refactoring | ♻️ | - |
| `perf` | Performans iyileştirme | ⚡ | - |
| `test` | Test ekleme/güncelleme | ✅ | - |
| `build` | Build sistemi/dependencies | 📦 | - |
| `ci` | CI/CD konfigürasyonu | 👷 | - |
| `chore` | Bakım işleri | 🔧 | - |

### Breaking Changes (MAJOR bump)
```bash
# Seçenek 1: Ünlem işareti
feat!: redesign CLI argument structure

# Seçenek 2: Footer'da belirt
feat(api): change response format

BREAKING CHANGE: API response artık array yerine object döner
```

### Örnekler
```bash
# Yeni özellik
feat(tui): add dark mode support

# Bug fix
fix(pipeline): resolve archive duplication issue

# Scope olmadan
docs: update README with new examples

# Breaking change
feat!: redesign module loading system

# Detaylı commit
feat(changelog): add automatic changelog generation

Conventional Commits formatını parse ederek otomatik
CHANGELOG.md oluşturur.

- ChangelogManager sınıfı eklendi
- ReleasePipeline entegrasyonu yapıldı
- Keep a Changelog formatı kullanılıyor
```

### Otomatik CHANGELOG Güncellemesi
```
1. Release sırasında (📦 quick release)
2. Son tag'den bu yana tüm commit'ler parse edilir
3. Conventional Commits formatındakiler kategorize edilir
4. CHANGELOG.md otomatik güncellenir
5. [Unreleased] bölümü yeni version'a dönüşür
```

### Dosya Yapısı
```
CHANGELOG.md
├── [Unreleased]          # Henüz release edilmemiş değişiklikler
├── [2.0.0] - 2025-12-05  # En son release (5-profile architecture)
│   ├── Added             # feat commits
│   ├── Changed           # refactor, style commits
│   ├── Fixed             # fix commits
│   └── ...
└── [1.x.x] - 2025-12-0x  # Önceki releases
```

---

**Not:** Detaylı kurallar, örnekler, validation checklist'ler vb. için yukarıdaki linkleri takip et. Bu dosya sadece yönlendirme amaçlıdır.
