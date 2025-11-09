# ⚠️ VERSIYONLAMA İŞ AKIŞI - HER ZAMAN BU KURALLARI TAKİP ET

**Bu dosya ana dizinde yönlendirme amaçlıdır. Detaylı kurallar için:**
👉 [docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)

---

## 🚨 EN ÖNEMLİ KURAL

**ARŞİVLENEN = BİTMİŞ VERSİYON** (yeni versiyon değil!)

## ✅ Doğru Sıralama (v531 → v532 örneği)

```bash
# ŞU ANDA v531'desin, tüm geliştirmeler tamamlandı

1. DATABASE BACKUP oluştur
   ./tools/scripts/backup_database.sh

2. ARŞİV oluştur (v531'i arşivle - henüz v532'ye GEÇMEDİN!)
   # Script şu an YANLIŞ çalışıyor, manuel yap:
   timestamp=$(TZ='Europe/Istanbul' date +%Y%m%d_%H%M)
   rsync -av --exclude-from=.archiveignore . "archive/versions/unibos_v531_${timestamp}/"

3. GIT COMMIT (v531 final)
   git add -A
   git commit -m "v531: Description of completed work"

4. GIT TAG oluştur (v531)
   git tag v531

5. GIT BRANCH oluştur (v531)
   git checkout -b v531
   git push origin refs/heads/v531  # Full ref path kullan

6. GITHUB'A PUSH (main + tag)
   git checkout main
   git push origin main
   git push origin refs/tags/v531   # Full ref path kullan

   ⚠️ DİKKAT: main ve v531 branch'i aynı commit'te olmalı!

7. DEPLOY (v531'i rocksteady'ye gönder)
   ./tools/scripts/rocksteady_deploy.sh deploy

8. ŞİMDİ YENİ VERSİYONA GEÇ (v532)
   # v531'in VERSION.json'unu v532 yap
   # v531'in main.py'sini v532 yap
   git add -A
   git commit -m "chore: bump version to v532"
   git push origin main

9. Artık v532'desin, yeni geliştirmelere başla!
```

## ❌ YANLIŞ Workflow (Veri Kaybı Riski!)

```bash
❌ VERSION.json'u v532 yap (önce)
❌ Sonra arşivle (v532 boş olarak arşivlenir!)
❌ v531 kaybolur!
```

## 🔧 Script Sorunu

`tools/scripts/unibos_version.sh` scripti şu anda **YANLIŞ** sırayla çalışıyor:

**Mevcut (YANLIŞ):**
```
update_version_json($next_version)  ← Önce güncelle (YANLIŞ!)
create_archive($next_version)       ← Boş versiyonu arşivle (YANLIŞ!)
git_operations($next_version)
```

**Olması Gereken (DOĞRU):**
```
create_archive($current_version)    ← Önce arşivle (DOĞRU!)
git_operations($current_version)    ← Tag/branch oluştur
update_version_json($next_version)  ← Sonra güncelle (DOĞRU!)
```

## 📋 Script Düzeltmesi Gerekiyor

Script'in `quick_release()` fonksiyonu düzeltilmeli:

**Değişiklik gereken satırlar:** 634-640

```bash
# MEVCUT (YANLIŞ):
update_version_json "$next_version" "$description"
update_django_files "$next_version"
create_archive "$next_version"
git_operations "$next_version" "$description"

# OLMASI GEREKEN (DOĞRU):
current_version=$(get_current_version)  # Önce mevcut versiyonu al
create_archive "$current_version"       # Mevcut versiyonu arşivle
git_operations "$current_version" "$description"  # Mevcut versiyonu tag'le
update_version_json "$next_version" "$description"  # Sonra yeni versiyona geç
update_django_files "$next_version"
git add apps/cli/src/VERSION.json apps/web/backend/VERSION.json apps/cli/src/main.py
git commit -m "chore: bump version to v${next_version}"
git push origin main
```

## 🎯 Mantık

Düşün: Bir kitap yazıyorsun
- Kitap bitti (v531 tamamlandı) ✅
- Kitabı basıl (Arşiv oluştur) ✅
- Kütüphaneye koy (Deploy et) ✅
- **ŞİMDİ** yeni kitaba başla (v532'ye geç) ✅

Asla: Yeni kitabın adını (v532) yazıp eski kitabı (v531) basma!

## 📚 Daha Fazla Bilgi

- **Arşiv kuralları:** [docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)
- **Arşiv boyut kontrolü:** [docs/development/VERSIONING_RULES.md#expected-archive-sizes](docs/development/VERSIONING_RULES.md#expected-archive-sizes)
- **Database backup:** [docs/development/VERSIONING_RULES.md#database-backup-system](docs/development/VERSIONING_RULES.md#database-backup-system)
- **Script kullanımı:** `./tools/scripts/unibos_version.sh`
- **Deployment:** `./tools/scripts/rocksteady_deploy.sh`

---

**Son Güncelleme:** 2025-11-09
**Oluşturan:** Claude + Berk Hatırlı
**Amaç:** Versiyonlama hatalarını önlemek için ana dizinde hızlı referans
