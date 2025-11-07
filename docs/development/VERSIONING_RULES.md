# UNIBOS Versioning & Archiving Rules

## 📋 Overview
This document defines strict rules for version management and archiving to prevent data loss, bloat, and ensure consistency.

## 🎯 Core Principles

1. **No Data Loss** - Every archive must contain all source code
2. **No Bloat** - Exclude build artifacts, logs, and temporary files
3. **Consistency** - Archive sizes should be predictable (~30-90MB range)
4. **Traceability** - Clear changelog and git history

## 📦 Archive Exclusion Rules

### ✅ ALWAYS Exclude:

#### Build Artifacts & Dependencies
- `venv/` - Python virtual environments
- `node_modules/` - Node.js dependencies
- `apps/mobile/*/build/` - Flutter build outputs (~1.5GB)
- `apps/mobile/*/.dart_tool/` - Dart tooling cache
- `apps/mobile/*/.flutter-plugins*` - Flutter plugin files
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files

#### Database & Backups
- `*.sql` - **SQL dump files (can be 50MB+ each)**
- `*.sqlite3` - SQLite database files
- `*.sqlite3.backup` - SQLite backups
- `data_db/` - Database data directories
- `data_db_backup_*` - Database backup folders

#### Logs & Temporary Files
- `*.log` - Log files
- `apps/web/backend/logs/` - Application logs
- `apps/web/backend/staticfiles/` - Collected static files
- `.DS_Store` - macOS metadata

#### Media & Documents
- `apps/web/backend/media/` - User uploaded files
- `apps/web/backend/documents/2025/` - Processed documents

#### Archives & Backups
- `archive/` - Old version archives
- `archive_backup_*` - Archive backups
- `*.zip` - Compressed archives

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
| v528+ | 30-40MB | Cleaned structure |

### 🚨 Size Anomalies to Watch:

- **< 20MB**: Likely missing code/features
- **> 100MB**: Check for build artifacts or SQL dumps
- **> 500MB**: Critical - Flutter build not excluded
- **> 1GB**: Emergency - immediate investigation needed

## 🔍 Pre-Archive Checklist

Before creating a version archive:

1. ✅ Check current working directory size: `du -sh .`
2. ✅ Verify no SQL dumps in root: `ls -lh *.sql`
3. ✅ Check Flutter build dirs: `du -sh apps/mobile/*/build`
4. ✅ Verify VERSION.json updated
5. ✅ Confirm git commits are clean
6. ✅ Test exclude patterns work

## 📝 Version Creation Process

### 1. Update VERSION.json
```bash
# Update version, build_number, release_date
# Add changelog entry
# Update description
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
**Cause**: Missing code directories (apps/cli, apps/web, apps/mobile)

**Check**:
```bash
du -sh archive/versions/unibos_vXXX_*/apps/*
# Should show:
# - apps/cli: ~3-4MB
# - apps/web: ~10-15MB
# - apps/mobile: ~7-15MB
```

### Issue 3: Duplicate Versions
**Cause**: Created v530 instead of fixing v529

**Solution**: Follow proper versioning:
1. Only increment version for NEW features
2. Fix existing version if it had archiving issues
3. Use git reset/amend for version number corrections

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

# 2. Structure check
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

1. **Always use the archiving script** - Don't manually rsync
2. **Verify before committing** - Check archive size and contents
3. **Document anomalies** - Note any unusual sizes in changelog
4. **Keep archives clean** - Delete failed/test archives
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

**Last Updated**: 2025-11-07
**Maintainer**: Berk Hatırlı
**Related**: `tools/scripts/unibos_version.sh`, `VERSION.json`
