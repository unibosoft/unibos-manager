#!/bin/bash
# UNIBOS Version Manager
# Yeni versiyon oluşturur, mevcut durumu arşivler
# KRİTİK: CLAUDE.md anayasadaki tüm kurallara uygun çalışır
# Versiyon: Sistem versiyonunu kullanır (VERSION.json'dan okur)

# Renklendirme
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ana dizin
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Fonksiyonlar
print_header() {
    # VERSION.json'dan mevcut versiyonu oku
    local current_version=$(grep '"version"' "$BASE_DIR/src/VERSION.json" | head -1 | cut -d'"' -f4)
    echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🪐 unibos version manager ${current_version}   ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
}

check_incomplete_tasks() {
    echo -e "${YELLOW}📋 Tamamlanmamış görev kontrolü...${NC}"
    local issues_found=false
    
    # Screenshot kontrolü ve otomatik arşivleme
    local screenshot_files=$(ls *.png *.jpg *.jpeg *.PNG *.JPG *.JPEG 2>/dev/null | wc -l)
    if [ "$screenshot_files" -gt 0 ]; then
        echo -e "${YELLOW}📸 Ana dizinde $screenshot_files adet screenshot tespit edildi, arşivleniyor...${NC}"
        
        # Arşiv dizini oluştur
        CURRENT_MONTH=$(date '+%Y-%m')
        ARCHIVE_DIR="archive/media/screenshots/v401-v500"
        mkdir -p "$ARCHIVE_DIR"
        
        # Screenshot'ları arşivle
        for file in *.png *.jpg *.jpeg *.PNG *.JPG *.JPEG; do
            if [ -f "$file" ]; then
                # Dosya adından tarih bilgisini çıkar veya mevcut tarihi kullan
                if [[ "$file" == *"Screenshot"* ]]; then
                    # macOS screenshot formatı için özel işlem
                    NEW_NAME=$(echo "$file" | sed 's/Screenshot /Screenshot_/' | sed 's/ at /_/g' | sed 's/\./_/g' | sed 's/__/\./g')
                    mv "$file" "$ARCHIVE_DIR/$NEW_NAME"
                    echo -e "   ✅ Arşivlendi: $file → $NEW_NAME"
                else
                    mv "$file" "$ARCHIVE_DIR/$file"
                    echo -e "   ✅ Arşivlendi: $file → $ARCHIVE_DIR/$file"
                fi
            fi
        done
        
        echo -e "${GREEN}✅ Screenshot'lar arşivlendi${NC}"
    fi
    
    # Archive dizini kontrolü
    if [ -d "archive" ] && [ ! -d "archive/versions" ] && [ ! -d "archive/compressed" ]; then
        echo -e "${RED}❌ Düzgün yapılandırılmamış archive dizini!${NC}"
        issues_found=true
    fi
    
    # Versiyon senkronizasyon kontrolü
    if [ -f "src/VERSION.json" ] && [ -f "src/main.py" ]; then
        json_version=$(grep '"version"' src/VERSION.json | head -1 | cut -d'"' -f4)
        main_version=$(grep '"version":' src/main.py | head -1 | cut -d'"' -f4)
        if [ "$json_version" != "$main_version" ]; then
            echo -e "${RED}❌ VERSION.json ve main.py versiyonları uyuşmuyor!${NC}"
            echo -e "   VERSION.json: $json_version"
            echo -e "   main.py: $main_version"
            issues_found=true
        fi
    fi
    
    if [ "$issues_found" = true ]; then
        echo -e "${RED}❌ Çözülmesi gereken sorunlar var!${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Tüm kontroller başarılı${NC}"
        return 0
    fi
}

get_current_version() {
    # src/VERSION.json'dan oku (ana dizinde VERSION.json yok)
    if [ -f "src/VERSION.json" ]; then
        current_version=$(grep '"version"' src/VERSION.json | head -1 | cut -d'"' -f4)
        echo "$current_version"
    else
        echo "v068"  # Fallback to current version
    fi
}

cleanup_old_sql_files() {
    echo -e "${YELLOW}🧹 Eski SQL dosyaları temizleniyor...${NC}"
    
    # Ana dizindeki tüm unibos_*.sql dosyalarını tarih sırasına göre listele
    local sql_files=($(ls -t "$BASE_DIR"/unibos_v*.sql 2>/dev/null))
    local count=${#sql_files[@]}
    
    # Eğer 3'ten fazla SQL dosyası varsa, en eskileri sil
    if [ $count -gt 3 ]; then
        local files_to_delete=$((count - 3))
        echo -e "${BLUE}   → $count SQL dosyası bulundu, $files_to_delete tanesi silinecek${NC}"
        
        # En eski dosyaları sil (dizinin sonundakiler)
        for ((i=$((count-files_to_delete)); i<$count; i++)); do
            if [ -f "${sql_files[$i]}" ]; then
                echo -e "${YELLOW}   🗑️  Siliniyor: $(basename ${sql_files[$i]})${NC}"
                rm -f "${sql_files[$i]}"
            fi
        done
        echo -e "${GREEN}✅ Eski SQL dosyaları temizlendi${NC}"
    else
        echo -e "${GREEN}✅ Temizlenecek eski SQL dosyası yok (${count}/3)${NC}"
    fi
}

export_postgresql() {
    local version=$1
    local timestamp=$2
    
    echo -e "${YELLOW}🗄️ PostgreSQL veritabanı export ediliyor...${NC}"
    
    # PostgreSQL bağlantı bilgileri
    DB_NAME="unibos_db"
    DB_USER="unibos_user"
    DB_PASS="unibos_password"
    DB_HOST="localhost"
    DB_PORT="5432"
    
    # Export dosya adı - unibos_ prefix'i ile
    SQL_FILE="unibos_${version}_${timestamp}.sql"
    
    # pg_dump ile export
    PGPASSWORD=$DB_PASS pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -f "$SQL_FILE" \
        --verbose \
        --clean \
        --if-exists \
        --no-owner \
        --no-privileges \
        2>/dev/null || {
            echo -e "${YELLOW}⚠️  PostgreSQL export başarısız oldu (veritabanı çalışmıyor olabilir)${NC}"
            return 1
        }
    
    if [ -f "$SQL_FILE" ]; then
        local sql_size=$(du -sh "$SQL_FILE" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✅ PostgreSQL export tamamlandı: $SQL_FILE ($sql_size)${NC}"
        
        # Boyut kontrolü
        local sql_size_bytes=$(du -sb "$SQL_FILE" 2>/dev/null | cut -f1)
        if [ -n "$sql_size_bytes" ] && [ $sql_size_bytes -gt 10485760 ]; then  # 10MB
            echo -e "${YELLOW}⚠️  SQL export boyutu büyük ($sql_size). Boyut optimizasyonu gerekebilir.${NC}"
        fi
        
        # Eski SQL dosyalarını temizle (sadece 3 tane kalsın)
        cleanup_old_sql_files
        
        return 0
    else
        echo -e "${RED}❌ SQL export dosyası oluşturulamadı${NC}"
        return 1
    fi
}

create_backup() {
    local version=$1
    local timestamp=$2
    local backup_name="unibos_${version}_${timestamp}"
    
    echo -e "${YELLOW}📦 mevcut versiyon yedekleniyor...${NC}"
    
    # Archive dizini yoksa oluştur
    if [ ! -d "archive/versions" ]; then
        echo -e "${YELLOW}📁 archive/versions dizini oluşturuluyor...${NC}"
        mkdir -p "archive/versions"
    fi
    
    # compressed dizini artık kullanılmıyor (ZIP oluşturulmadığı için)
    
    # Açık klasör olarak yedekle (archive hariç!)
    mkdir -p "archive/versions/${backup_name}"
    
    # .archiveignore dosyasını oku ve exclude listesi oluştur
    local exclude_args=""
    if [ -f ".archiveignore" ]; then
        echo -e "${BLUE}📋 .archiveignore dosyası kullanılıyor...${NC}"
        while IFS= read -r pattern || [ -n "$pattern" ]; do
            # Boş satırları ve yorumları atla
            if [[ -n "$pattern" && ! "$pattern" =~ ^# ]]; then
                # Trim whitespace
                pattern=$(echo "$pattern" | xargs)
                if [ -n "$pattern" ]; then
                    exclude_args="$exclude_args --exclude='$pattern'"
                fi
            fi
        done < ".archiveignore"
    fi
    
    # rsync ile kopyala - .archiveignore ve varsayılan exclude'ları kullan
    eval rsync -av --exclude='archive' --exclude='.git' \
              $exclude_args \
              . "archive/versions/${backup_name}/"
    
    # ZIP oluşturma kaldırıldı - sadece açık klasör olarak arşivleniyor
    echo -e "${YELLOW}📁 Sadece klasör olarak arşivleniyor (ZIP oluşturulmuyor)...${NC}"
    
    # Kritik doğrulama: archive dizini kopyalanmış mı?
    if find "archive/versions/${backup_name}" -name "archive" -type d | grep -q "archive"; then
        echo -e "${RED}❌ HATA: Archive dizini yedeklemeye dahil edilmiş!${NC}"
        echo -e "${YELLOW}🔧 Temizleniyor...${NC}"
        find "archive/versions/${backup_name}" -name "archive" -type d -exec rm -rf {} +
    fi
    
    echo -e "${GREEN}✅ yedekleme tamamlandı: ${backup_name}${NC}"
    
    # Boyut kontrolü ve raporu - Sadece dizin boyutu
    local dir_size=$(du -sh "archive/versions/${backup_name}" 2>/dev/null | cut -f1)
    
    echo -e "${BLUE}📊 Arşiv Boyutu:${NC}"
    echo -e "   Dizin: ${dir_size:-HATA}"
    
    # Boyut anomali kontrolü - .archiveignore kullanıldığında boyutlar düşük olacak
    if [ -d "archive/versions/${backup_name}" ]; then
        local dir_size_bytes=$(du -sb "archive/versions/${backup_name}" 2>/dev/null | cut -f1)
        if [ -n "$dir_size_bytes" ]; then
            # .archiveignore kullanıldığında boyutlar daha düşük olacak
            if [ -f ".archiveignore" ]; then
                # .archiveignore varsa daha düşük limitler
                if [ $dir_size_bytes -gt 8388608 ]; then  # 8MB
                    echo -e "${RED}⚠️  UYARI: Arşiv 8MB'dan büyük! Gereksiz dosyalar dahil edilmiş olabilir!${NC}"
                    echo -e "${YELLOW}   .archiveignore dosyasını kontrol edin${NC}"
                elif [ $dir_size_bytes -lt 102400 ]; then  # 100KB
                    echo -e "${RED}⚠️  UYARI: Arşiv 100KB'dan küçük! Kritik dosyalar eksik olabilir!${NC}"
                else
                    echo -e "${GREEN}✅ Arşiv boyutu normal aralıkta (${dir_size})${NC}"
                fi
            else
                # .archiveignore yoksa eski limitler
                if [ $dir_size_bytes -gt 10485760 ]; then  # 10MB
                    echo -e "${RED}⚠️  UYARI: Arşiv 10MB'dan büyük! .archiveignore dosyası oluşturun${NC}"
                elif [ $dir_size_bytes -lt 512000 ]; then  # 500KB
                    echo -e "${RED}⚠️  UYARI: Arşiv 500KB'dan küçük! Eksik dosyalar olabilir!${NC}"
                fi
            fi
        fi
    fi
    
    # Son 3 versiyon karşılaştırması - Dizinler için
    echo -e "${BLUE}📈 Son 3 Versiyon Boyut Karşılaştırması:${NC}"
    ls -dh archive/versions/unibos_v* 2>/dev/null | tail -3 | while read dir; do
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        basename=$(basename "$dir")
        echo "   $basename: $size"
    done
}

update_version_files() {
    local new_version=$1
    local timestamp=$2
    
    echo -e "${YELLOW}📝 versiyon dosyaları güncelleniyor...${NC}"
    
    # Sadece src/VERSION.json güncelle (ana dizinde VERSION.json yok)
    # src/VERSION.json güncelle
    if [ -f "src/VERSION.json" ]; then
        sed -i '' "s/\"version\": \"v[0-9]*\"/\"version\": \"${new_version}\"/" src/VERSION.json
        sed -i '' "s/\"build_number\": \"[^\"]*\"/\"build_number\": \"${timestamp}\"/" src/VERSION.json
        sed -i '' "s/\"release_date\": \"[^\"]*\"/\"release_date\": \"$(TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S +03:00')\"/" src/VERSION.json
    fi
    
    # src/main.py güncelle - docstring ve fallback version
    if [ -f "src/main.py" ]; then
        # Docstring'deki versiyonu güncelle
        sed -i '' "s/unibos v[0-9]*/unibos ${new_version}/" src/main.py
        sed -i '' "s/Version: v[0-9]*_[0-9_]*/Version: ${new_version}_${timestamp}/" src/main.py
        
        # Fallback VERSION_INFO güncelle
        sed -i '' "s/\"version\": \"v[0-9]*\"/\"version\": \"${new_version}\"/" src/main.py
        sed -i '' "s/\"build\": \"[0-9_]*\"/\"build\": \"${timestamp}\"/" src/main.py
        sed -i '' "s/\"build_date\": \"[^\"]*\"/\"build_date\": \"$(TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S +03:00')\"/" src/main.py
        
        # Diğer v05X referanslarını güncelle
        version_num=${new_version#v}
        sed -i '' "s/v0[0-9][0-9]_[0-9_]*/${new_version}_${timestamp}/g" src/main.py
        sed -i '' "s/MODULE v0[0-9][0-9]/MODULE ${new_version}/g" src/main.py
        sed -i '' "s/SUITE v0[0-9][0-9]/SUITE ${new_version}/g" src/main.py
    fi
    
    echo -e "${GREEN}✅ versiyon dosyaları güncellendi${NC}"
}

# CHANGELOG güncelleme fonksiyonu
update_changelog() {
    local new_version=$1
    local timestamp=$2
    local date_str=$(TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S +03:00')
    
    echo -e "${YELLOW}📋 CHANGELOG güncelleniyor...${NC}"
    
    if [ -f "CHANGELOG.md" ]; then
        # Yeni versiyon başlığını ekle (ilk ## bulunmadan önce)
        local temp_file=$(mktemp)
        local version_added=false
        
        while IFS= read -r line; do
            if [[ $line == "## ["* ]] && [ "$version_added" = false ]; then
                echo "## [${new_version}] - ${date_str}" >> "$temp_file"
                echo "" >> "$temp_file"
                echo "### Eklenenler" >> "$temp_file"
                echo "- 🚀 Otomatik versiyon geçişi" >> "$temp_file"
                echo "" >> "$temp_file"
                echo "### Değiştirilenler" >> "$temp_file"
                echo "- 📝 Version manager ile güncelleme" >> "$temp_file"
                echo "" >> "$temp_file"
                version_added=true
            fi
            echo "$line" >> "$temp_file"
        done < "CHANGELOG.md"
        
        mv "$temp_file" "CHANGELOG.md"
        echo -e "${GREEN}✅ CHANGELOG güncellendi${NC}"
    else
        echo -e "${RED}❌ CHANGELOG.md bulunamadı!${NC}"
    fi
}

# Ana program
print_header
echo

# Kritik kontroller
echo -e "${YELLOW}🔍 Ön kontroller yapılıyor...${NC}"

# Tamamlanmamış görev kontrolü
if ! check_incomplete_tasks; then
    echo -e "${RED}❌ HATA: Önce yukarıdaki sorunları çözün!${NC}"
    exit 1
fi

# VERSION.json kontrolü
if [ ! -f "src/VERSION.json" ]; then
    echo -e "${RED}❌ HATA: src/VERSION.json bulunamadı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ön kontroller tamamlandı${NC}"
echo

# Mevcut versiyon
current_version=$(get_current_version)
echo -e "${BLUE}📌 mevcut versiyon: ${current_version}${NC}"

# Yeni versiyon numarasını hesapla
version_number=${current_version#v}
# 10# ile decimal olduğunu belirt (octal değil)
new_version_number=$((10#$version_number + 1))
new_version=$(printf "v%03d" $new_version_number)

echo -e "${BLUE}🆕 yeni versiyon: ${new_version}${NC}"
echo

# Onay al
echo -n "devam etmek istiyor musunuz? (e/h): "
read -n 1 -r REPLY
echo  # Yeni satır için
if [[ ! $REPLY =~ ^[Ee]$ ]]; then
    echo -e "${RED}❌ iptal edildi${NC}"
    exit 1
fi

# Otomatik push varsayılan olarak aktif
AUTO_PUSH="e"
echo -e "${BLUE}ℹ️  Otomatik push aktif${NC}"

# Timestamp - İstanbul saati ile
export TZ='Europe/Istanbul'
timestamp=$(date '+%Y%m%d_%H%M')

# Versiyon dosyalarını güncelle (ÖNCE güncelle ki arşivde yeni versiyon olsun)
update_version_files "$new_version" "$timestamp"

# Yedekleme yap (güncellenen durum yeni versiyon ile arşivlenir)
create_backup "$new_version" "$timestamp"

# CHANGELOG güncelle
update_changelog "$new_version" "$timestamp"

# PostgreSQL export - YENİ versiyonla export et, arşivlemeden SONRA
echo -e "${YELLOW}🗄️ PostgreSQL veritabanı export ediliyor...${NC}"
export_postgresql "$new_version" "$timestamp"

# README.md'deki version badge'i güncelle
if [ -f "README.md" ]; then
    echo -e "${YELLOW}📝 README.md güncelleniyor...${NC}"
    sed -i '' "s/version-v[0-9]*-blue/version-${new_version}-blue/" README.md
    echo -e "${GREEN}✅ README.md güncellendi${NC}"
fi

# CLAUDE.md'deki güncel durum güncelle
if [ -f "CLAUDE.md" ]; then
    echo -e "${YELLOW}📝 CLAUDE.md güncelleniyor...${NC}"
    # Güncel Durum başlığını bul ve versiyonu güncelle
    sed -i '' "/^- \*\*Versiyon\*\*:/s/v[0-9]*/${new_version}/" CLAUDE.md
    # Tarihi güncelle
    sed -i '' "/^- \*\*Tarih\*\*:/s/.*$/- **Tarih**: $(TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S +03:00')/" CLAUDE.md
    echo -e "${GREEN}✅ CLAUDE.md güncellendi${NC}"
fi

# Son kontroller
echo
echo -e "${BLUE}🔍 Son kontroller yapılıyor...${NC}"

# Archive kontrolü
if find archive/versions -name "archive" -type d | grep -q "archive"; then
    echo -e "${RED}❌ UYARI: Arşivlerde archive dizini bulundu!${NC}"
else
    echo -e "${GREEN}✅ Archive dizini kontrolü: Temiz${NC}"
fi

# Dizin içeriği kontrolü (ZIP yerine)
latest_version=$(ls -t archive/versions/ 2>/dev/null | head -1)
if [ -d "archive/versions/$latest_version" ]; then
    forbidden_dirs=$(find "archive/versions/$latest_version" -type d \( -name "venv" -o -name "__pycache__" -o -name "node_modules" \) 2>/dev/null | wc -l)
    if [ $forbidden_dirs -gt 0 ]; then
        echo -e "${RED}❌ UYARI: Arşivde yasak dizinler var!${NC}"
    else
        echo -e "${GREEN}✅ Arşiv içeriği kontrolü: Temiz${NC}"
    fi
fi

# Git işlemleri - OTOMATİK COMMIT VE BRANCH OLUŞTURMA
echo
echo -e "${YELLOW}📦 Git işlemleri yapılıyor...${NC}"

# Git durumunu kontrol et
if [ -d ".git" ]; then
    # Değişiklikleri ekle
    git add -A
    
    # Commit mesajı oluştur
    commit_message="${new_version}: Version update via version_manager.sh"
    
    # Commit yap
    echo -e "${YELLOW}📝 Commit yapılıyor: ${commit_message}${NC}"
    git commit -m "$commit_message" 2>/dev/null || echo -e "${YELLOW}ℹ️  Değişiklik yok veya zaten commit edilmiş${NC}"
    
    # Yeni versiyon branch'i oluştur
    echo -e "${YELLOW}🌿 ${new_version} branch'i oluşturuluyor...${NC}"
    git checkout -b "${new_version}" 2>/dev/null || {
        echo -e "${YELLOW}ℹ️  ${new_version} branch'i zaten var, güncelleniyor...${NC}"
        git checkout "${new_version}"
        git merge main --no-edit 2>/dev/null || true
    }
    
    # Main'e geri dön
    git checkout main 2>/dev/null
    
    # Otomatik push işlemleri (her zaman aktif)
    echo -e "${YELLOW}📤 Uzak repository'ye otomatik push ediliyor...${NC}"
    
    # Main branch'i push et
    echo -e "${BLUE}   → main branch push ediliyor...${NC}"
    if git push origin main 2>&1 | grep -q "Everything up-to-date\|successfully"; then
        echo -e "${GREEN}   ✅ main branch başarıyla push edildi${NC}"
    else
        git push origin main 2>/dev/null && echo -e "${GREEN}   ✅ main branch başarıyla push edildi${NC}" || echo -e "${YELLOW}   ⚠️ main branch push başarısız (internet bağlantısı yok olabilir)${NC}"
    fi
    
    # Yeni versiyon branch'ini push et
    echo -e "${BLUE}   → ${new_version} branch push ediliyor...${NC}"
    if git push origin ${new_version} 2>&1 | grep -q "Everything up-to-date\|successfully"; then
        echo -e "${GREEN}   ✅ ${new_version} branch başarıyla push edildi${NC}"
    else
        git push origin ${new_version} 2>/dev/null && echo -e "${GREEN}   ✅ ${new_version} branch başarıyla push edildi${NC}" || echo -e "${YELLOW}   ⚠️ ${new_version} branch push başarısız (internet bağlantısı yok olabilir)${NC}"
    fi
    
    echo -e "${GREEN}✅ Git işlemleri tamamlandı ve otomatik push edildi${NC}"
else
    echo -e "${YELLOW}⚠️  Git repository değil, git işlemleri atlandı${NC}"
fi

echo
echo -e "${GREEN}🎉 versiyon geçişi tamamlandı!${NC}"
echo -e "${BLUE}   eski: ${current_version}${NC}"
echo -e "${BLUE}   yeni: ${new_version}${NC}"
echo
echo -e "${YELLOW}💡 ipucu: yazılımı test etmek için:${NC}"
echo -e "   ${GREEN}./unibos.sh${NC}"
echo
echo -e "${YELLOW}📋 ÖNEMLI: CHANGELOG.md'yi manuel olarak güncelleyin!${NC}"