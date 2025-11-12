#!/usr/bin/env python3
import os
import sys
import django

# Django setup
sys.path.append('/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ['SECRET_KEY'] = 'django-insecure-unibos-import-temp-key-2025'
os.environ['DATABASE_URL'] = 'postgresql://unibos_user:unibos_password@localhost:5432/unibos_db'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth.models import User
from core.models.base import UserProfile

# berkhatirli kullanıcısını oluştur/güncelle
username = 'berkhatirli'
password = 'Unib0s_Str0ng_2025!'
email = 'berk@berkinatolyesi.com'

try:
    user = User.objects.get(username=username)
    print(f"✅ {username} kullanıcısı zaten mevcut, güncelleniyor...")
    user.email = email
    user.first_name = 'Berk'
    user.last_name = 'Hatırlı'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f"✅ Güncellendi!")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Berk',
        last_name='Hatırlı'
    )
    print(f"✅ {username} süper kullanıcısı oluşturuldu!")

# Telefon numarası ekle
profile, created = UserProfile.objects.get_or_create(
    user=user,
    defaults={'phone_number': '5323672225'}
)

print("\n" + "="*50)
print("🔐 berkhatirli kullanıcı bilgileri:")
print(f"  Kullanıcı adı: {username}")
print(f"  Şifre: {password}")
print(f"  Email: {email}")
print(f"  Telefon: 5323672225")
print(f"  Süper kullanıcı: Evet")
print("="*50)
print("✨ berkhatirli kullanıcısı hazır!")
