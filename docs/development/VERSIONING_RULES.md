# UNIBOS Versioning & Archiving Rules

## 📋 Overview
This document defines strict rules for version management and archiving to prevent data loss, bloat, and ensure consistency.

## 🎯 Core Principles

1. **No Data Loss** - Every archive must contain all source code
2. **No Bloat** - Exclude build artifacts, logs, and temporary files
3. **Consistency** - Archive sizes should be predictable (~30-90MB range)
4. **Traceability** - Clear changelog and git history
5. **One Archive Per Version** - Each version must have exactly ONE current archive directory

## 📦 Archive Exclusion Rules

### ✅ ALWAYS Exclude:

#### Build Artifacts & Dependencies
- `venv/` - Python virtual environments
- `node_modules/` - Node.js dependencies
- `modules/*/mobile/build/` - Flutter build outputs (~1.5GB)
- `modules/*/mobile/.dart_tool/` - Dart tooling cache
- `modules/*/mobile/.flutter-plugins*` - Flutter plugin files
- `apps/mobile/*/build/` - Legacy Flutter builds (if any)
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `modules/*/backend/staticfiles/` - Collected static files per module

#### Database & Backups
- `*.sql` - **SQL dump files (can be 50MB+ each) - STORED SEPARATELY**
- `*.sqlite3` - SQLite database files
- `*.sqlite3.backup` - SQLite backups
- `data_db/` - Database data directories
- `data_db_backup_*` - Database backup folders
- `archive/database/` - **Managed separately (database backups, old_backups)**
- `archive/database_backups/` - **Legacy location (migrated to archive/database/backups/)**

#### Logs & Temporary Files
- `*.log` - Log files
- `apps/web/backend/logs/` - Application logs
- `apps/web/backend/staticfiles/` - Collected static files
- `modules/*/backend/logs/` - Module-specific logs
- `.DS_Store` - macOS metadata

#### Media & Documents
- `apps/web/backend/media/` - Legacy user uploaded files
- `apps/web/backend/documents/2025/` - Legacy processed documents
- `modules/*/backend/media/` - Module-specific media files
- `modules/*/backend/uploads/` - Module-specific uploads
- `data/runtime/media/` - Universal Data Directory media (excluded from archives)

#### Archives & Backups
- `archive/` - Historical data (versions/, database/, code/, data/, development/, documentation/)
- `archive_backup_*` - Archive backups
- `*.zip` - Compressed archives

**Note**: Only `archive/versions/` is fully excluded. Other archive categories (`database/`, `code/`, etc.) are organizational and should be managed separately.

#### Development Files
- `.git/` - Git repository (use git for history)
- `.env.local` - Local environment config
- `quarantine/` - Quarantined code
- `berk_claude_file_pool_DONT_DELETE/` - Development pool

## 📊 Expected Archive Sizes

| Version Range | Expected Size | Notes |
|---------------|---------------|-------|
| v510-v525 | 30-70MB | Early monorepo |
| v526-v527 | 80-90MB | Full features + docs |
| v528-v531 | 30-40MB | Cleaned structure |
| v532+ | 40-60MB | **Modular structure (21 modules)** |

**v532+ Note**: Modular structure with `modules/*/backend/` adds slight size increase but provides better organization.

### 🚨 Size Anomalies to Watch:

- **< 20MB**: Likely missing code/features
- **> 100MB**: Check for build artifacts or SQL dumps
- **> 500MB**: Critical - Flutter build not excluded
- **> 1GB**: Emergency - immediate investigation needed

## 🔍 Pre-Archive Checklist

Before creating a version archive:

1. ✅ Check current working directory size: `du -sh .`
2. ✅ Verify no SQL dumps in root: `ls -lh *.sql`
3. ✅ Check Flutter build dirs (v532+): `du -sh modules/*/mobile/build`
4. ✅ Check Flutter build dirs (legacy): `du -sh apps/mobile/*/build`
5. ✅ Verify VERSION.json updated
6. ✅ Confirm git commits are clean
7. ✅ Test exclude patterns work

## ⚠️ KRİTİK: VERSİYONLAMA SIRALAMA KURALI

**EN ÖNEMLİ KURAL - ASLA UNUTULMASIN!**

### Doğru Workflow (MUTLAKA BU SIRAYLA):

```
MEVCUT VERSİYON (örn. v531):
  1. Tüm geliştirmeler tamamlandı ✅
  2. → DATABASE BACKUP oluştur
  3. → ARŞİV oluştur (mevcut v531'i arşivle)
  4. → GIT COMMIT (v531 final) - main branch'te
  5. → GIT TAG oluştur (v531)
  6. → GIT BRANCH oluştur (v531) - main'den branch al
  7. → GITHUB'A PUSH
      • refs/heads/v531 (branch)
      • main (branch)
      • refs/tags/v531 (tag)
      ⚠️ KRİTİK: main ve v531 branch'i aynı commit'te olmalı!
      ⚠️ UYARI: Bu adımdan sonra deployment yapılana kadar ASLA yeni commit yapma!
  8. → DEPLOY (rocksteady'ye v531 gönder)
      ⚠️ Deploy BAŞARISIZ olursa hemen durdur, deployment fix'le, tekrar dene
      ✅ Deploy başarılı olduktan SONRA bir sonraki adıma geç
  9. → ŞİMDİ YENİ VERSİYONA GEÇ (v532)
      - VERSION.json'u v532 yap
      - Git commit: "chore: bump version to v532"
      - Git push origin main
      ⚠️ Bu adım MUTLAKA deployment sonrasında olmalı!
  10. → Artık v532'desin, yeni geliştirmelere başla!
```

### ❌ YANLIŞ Workflow (Veri Kaybı Riski!):

```
❌ VERSION.json'u v532 yap
❌ Sonra arşivle (v532 boş olarak arşivlenir!)
❌ Sonra commit et
❌ v531 kaybolur!
```

### ❌ YANLIŞ Workflow 2 (Tag/Branch Yanlış Commit'e Point Eder!):

```
❌ Git tag ve branch oluştur
❌ Push yap
❌ SONRA deployment integration commit'i yap
❌ SONRA version bump commit'i yap
❌ Sonuç: Tag v531 eski commit'te, yeni değişiklikler eksik!
```

**Neden Yanlış?**
- Git tag ve branch oluşturulduğu anda mevcut HEAD commit'ine point eder
- Eğer sonradan yeni commit yapılırsa, tag ve branch ESKİ commit'te kalır
- Yeni commit'ler tag/branch'te olmaz ama main'de olur
- GitHub'da tag kodları ile main kodları farklı olur!

**Doğrusu:**
- Tag ve branch oluşturmadan ÖNCE tüm commit'ler yapılmalı
- Tag ve branch SONUNCU (final) commit'e point etmeli
- Tag/branch push'undan SONRA version bump commit'i yapılmalı (yeni versiyona geçiş için)

### 📌 Önemli Notlar:

1. **Arşivlenen = Bitmiş versiyon** (v531 tamamlandı → v531'i arşivle)
2. **Tag = Bitmiş commit** (v531 commit'i → v531 tag'i)
3. **Branch = Her versiyon için ayrı** (hem tag hem branch olmalı)
4. **Main ve vXXX branch = İdentical** (aynı commit'te olmalı)
5. **Deploy = Arşivlenen versiyon** (v531 arşivlendi → v531 deploy edilir)
6. **Yeni versiyon = Boş başlangıç** (v532 = temiz sayfa)
7. **Push stratejisi = Full ref path** (refs/heads/vXXX ve refs/tags/vXXX kullan)

### 🎯 Mantık:

- Bir kitap yazıyorsun
- Kitap bitti → Basıl (Arşiv)
- Baskı yapıldı → Kütüphaneye konulsun (Deploy)
- ŞİMDİ yeni kitaba başla (v532)
- Eski kitabı (v531) basarken yeni kitabın adını (v532) yazma!

## 📝 Version Creation Process

### 1. Update VERSION.json
```bash
# CURRENT version için güncelle (örn. v531)
# Yeni versiyona (v532) geçme, önce v531'i tamamla!
```

### 2. Git Commits
```bash
git add <changed files>
git commit -m "feat/fix/chore: descriptive message"
```

### 3. Create Archive
```bash
# Use unibos_version.sh script - it has proper excludes
./tools/scripts/unibos_version.sh
# Select option 1 (Quick Release) or 3 (Manual Version)
```

### 4. Verify Archive
```bash
# Check size is reasonable
du -sh archive/versions/unibos_v*_*/ | tail -5

# Check contents
ls -la archive/versions/unibos_vXXX_*/
```

### 5. Git Push
```bash
git push
```

### 6. Deploy to Production
```bash
# ❌ YANLIŞ: Manuel deployment
ssh rocksteady "cd /var/www/unibos && git pull && sudo systemctl restart gunicorn"

# ✅ DOĞRU: Script ile deployment
./tools/scripts/unibos_version.sh
# Select option 6 (Deploy to Production)

# Veya doğrudan:
./tools/scripts/rocksteady_deploy.sh deploy
```

**Deployment Script Özellikleri:**
- SSH bağlantısı kontrolü
- Kod senkronizasyonu (rsync ile)
- Dependency kurulumu (pip install)
- Database migration
- Gunicorn/Nginx servis restart
- Health check (HTTP 200 doğrulama)
- Rollback desteği (hata durumunda)

**Önemli Notlar:**
1. Deploy işlemi SADECE git push sonrasında yapılmalı
2. Production'da her zaman tagged versiyon olmalı (v531, v532 gibi)
3. Health check başarısız olursa deployment iptal edilir
4. SSH key authentication gereklidir (password-less login)

## 🐛 Common Issues & Solutions

### Issue 1: Archive Too Large (>100MB)
**Cause**: SQL dumps or Flutter build artifacts included

**Solution**:
```bash
# Find large files
find archive/versions/unibos_vXXX_*/ -type f -size +10M

# Delete problem archive
rm -rf archive/versions/unibos_vXXX_*/

# Recreate with proper excludes
# (Script should auto-exclude, but verify)
```

### Issue 2: Archive Too Small (<20MB)
**Cause**: Missing code directories (modules/, apps/)

**Check (v532+)**:
```bash
du -sh archive/versions/unibos_vXXX_*/modules
du -sh archive/versions/unibos_vXXX_*/apps/*
# Should show:
# - modules/: ~25-35MB (21 modules)
# - apps/web: ~8-10MB (Django project settings)
# - apps/cli: ~3-4MB (CLI tools)
# - apps/mobile: ~5-8MB (Flutter app structure, no build/)
```

**Check (v528-v531 - Old Structure)**:
```bash
du -sh archive/versions/unibos_vXXX_*/apps/*
# Should show:
# - apps/cli: ~3-4MB
# - apps/web: ~10-15MB
# - apps/mobile: ~7-15MB
```

### Issue 3: Duplicate Archives for Same Version
**Cause**: Multiple archive attempts created multiple directories for the same version

**Rule**: **HER VERSİYON İÇİN SADECE 1 ADET GÜNCEL ARŞİV DİZİNİ OLMALI!**

**Solution**:
1. Keep ONLY the latest and complete archive for each version
2. Delete older/failed/incomplete archives of the same version
3. Example: For v531, keep only `unibos_v531_20251109_1403`, delete all others
4. Verify archive completeness before deleting older ones:
   ```bash
   # Check size and structure
   du -sh archive/versions/unibos_v531_*/
   ls -la archive/versions/unibos_v531_*/apps/

   # Keep the latest, delete older ones
   rm -rf archive/versions/unibos_v531_20251109_1255
   rm -rf archive/versions/unibos_v531_20251109_1300
   ```

**Prevention**: Use the versioning script which handles this automatically

## 📜 Changelog Requirements

Each version MUST have:

1. **Version number** (vXXX)
2. **Date** (YYYY-MM-DD HH:MM)
3. **Description** (1-2 sentences)
4. **Changes list**:
   - Feature: New functionality
   - UI/UX: Interface improvements
   - Fix: Bug fixes
   - Enhancement: Improvements to existing features
   - Chore: Maintenance tasks

## 🔐 Archive Integrity Verification

After creating archive, run these checks:

```bash
# 1. Size check
ARCHIVE="archive/versions/unibos_vXXX_YYYYMMDD_HHMM"
SIZE=$(du -sh "$ARCHIVE" | cut -f1)
echo "Archive size: $SIZE"

# 2. Structure check (v532+)
echo "Main directories:"
ls -d "$ARCHIVE"/modules
ls -d "$ARCHIVE"/apps/*

# 2. Structure check (v528-v531 - Old Structure)
echo "Main directories:"
ls -d "$ARCHIVE"/apps/*

# 3. No SQL dumps
echo "SQL dumps (should be empty):"
find "$ARCHIVE" -name "*.sql" -type f

# 4. No Flutter build
echo "Flutter builds (should be empty):"
find "$ARCHIVE" -path "*/build/*" -type d
```

## 🎓 Best Practices

1. **❌ NEVER USE MANUAL COMMANDS** - ALWAYS use `./tools/scripts/unibos_version.sh`
   - ❌ NEVER: `rsync -av --exclude-from=...`
   - ❌ NEVER: `git commit -m "vXXX: ..."`
   - ❌ NEVER: `git tag vXXX`
   - ❌ NEVER: `git branch vXXX`
   - ✅ ALWAYS: `./tools/scripts/unibos_version.sh` (handles ALL of the above)

2. **Verify before committing** - Check archive size and contents
3. **Document anomalies** - Note any unusual sizes in changelog
4. **Keep archives clean** - Delete failed/test archives (max 1 archive per version)
5. **Monitor size trends** - Watch for gradual bloat

## 🚨 Emergency Recovery

If archive is corrupted or has data loss:

1. **Don't panic** - Git has all code
2. **Check git** - `git log --stat` shows what changed
3. **Recreate archive** - Delete bad archive, use script
4. **Compare with previous** - Use `diff -r` to verify
5. **Document incident** - Add note to DEVELOPMENT_LOG.md

## 📞 When to Ask for Help

Contact maintainer if:
- Archive size is >150MB and can't find cause
- Archive size is <15MB and all dirs present
- Multiple consecutive archives show size anomalies
- Unsure if code/data is missing

---

**Last Updated**: 2025-11-10 (Phase 2 Modular Migration Complete)
**Maintainer**: Berk Hatırlı
**Related**: `tools/scripts/unibos_version.sh`, `VERSION.json`, `ROADMAP.md`

## 📦 Archive Structure (v532+)

After Phase 2 migration and archive reorganization, the archive directory now has a logical category structure:

```
archive/ [4.7GB total]
├── versions/              ⭐ 3.6GB - 355 version snapshots (CRITICAL - NEVER MODIFY)
├── database/              382MB - Database backups and old backups
│   ├── backups/          (Current SQL backups)
│   └── old_backups/      (Historical backups)
├── code/                  71MB - Legacy code and prototypes
│   ├── legacy/           (Phase 1 attempts, quarantine, prototypes)
│   └── projects/         (Old project implementations)
├── development/           340KB - SDK, deployment scripts, old scripts
│   ├── sdk/
│   ├── deployment/
│   └── scripts/
├── data/                  250MB - Logs, old media, reports
│   ├── logs/
│   ├── old_media/
│   └── reports/
└── documentation/         232KB - Historical documentation
    └── historical_docs/
```

**Key Changes (v532)**:
- Database backups: `archive/database_backups/` → `archive/database/backups/`
- Archive organized into logical categories for better maintainability
- All legacy code preserved with zero data loss
- Version snapshots remain unchanged and protected

## 💾 Database Backup System

### Separation of Concerns

**IMPORTANT**: Database backups are stored SEPARATELY from version archives.

- **Version Archives**: Source code only (~30-90MB)
- **Database Backups**: SQL dumps in `archive/database_backups/` (10-50MB each)

### Automatic Backup Process

When creating a new version, the system:

1. **Creates database backup** - `./tools/scripts/backup_database.sh`
2. **Stores in** - `archive/database/backups/unibos_vXXX_TIMESTAMP.sql` (v532+) or `archive/database_backups/` (legacy)
3. **Keeps last 3** - Automatically deletes older backups
4. **Creates version archive** - Source code only (no SQL)

**Note (v532+)**: Database backups moved from `archive/database_backups/` to `archive/database/backups/` as part of archive reorganization.

### Manual Backup

```bash
# Create backup manually
./tools/scripts/backup_database.sh

# Verify backups
./tools/scripts/verify_database_backup.sh
```

### Backup Retention Policy

- **Keep**: Last 3 database backups (~30-150MB total)
- **Automatic cleanup**: Older backups deleted automatically
- **Not in git**: `archive/database/` is in `.gitignore`
  - Legacy: `archive/database_backups/` also in `.gitignore`
- **Not in archives**: SQL files excluded from version archives
- **Location**: `archive/database/backups/` (v532+)

### Database Restore

To restore from a backup:

```bash
cd apps/web/backend

# Restore specific backup (v532+)
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
  python manage.py loaddata ../../archive/database/backups/unibos_vXXX_TIMESTAMP.sql

# Or use the latest backup (v532+)
LATEST=$(ls -t ../../archive/database/backups/*.sql | head -1)
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
  python manage.py loaddata "$LATEST"

# Legacy path (v528-v531)
LATEST=$(ls -t ../../archive/database_backups/*.sql | head -1)
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
  python manage.py loaddata "$LATEST"
```

### Backup Verification Checklist

Before creating a new version:

1. ✅ Run backup: `./tools/scripts/backup_database.sh`
2. ✅ Verify backup: `./tools/scripts/verify_database_backup.sh`
3. ✅ Check backup size (should be 10-50MB)
4. ✅ Confirm 3 backups max in directory
5. ✅ Proceed with version creation

### Troubleshooting

**Backup too large (>100MB)**
- May include unnecessary data
- Check if media/documents are in dump
- Use `--exclude` flags if needed

**Backup empty or very small (<1MB)**
- Database may be empty
- Check Django settings
- Verify database connection

**Restore fails**
- Check Django settings match
- Verify JSON format is valid
- Ensure database is empty or use `--clear`

### Integration with Version Script

The versioning script (`unibos_version.sh`) automatically:
1. Creates database backup before archiving
2. Stores it separately in `archive/database/backups/` (v532+)
3. Excludes SQL files from version archive
4. Maintains backup rotation (last 3)
5. Archive directory organized: `database/`, `code/`, `data/`, `development/`, `documentation/`, `versions/`

This ensures:
- ✅ Database state preserved for each version
- ✅ Version archives remain small
- ✅ Easy rollback capability
- ✅ No git repository bloat

