#!/usr/bin/env python
"""Check real crypto prices in database"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from modules.currencies.backend.models import CryptoExchangeRate
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count
import pytz

# Son 10 dakikadaki veriler
recent = CryptoExchangeRate.objects.filter(
    timestamp__gte=timezone.now() - timedelta(minutes=10)
).order_by('-timestamp')

print(f'Son 10 dakikada {recent.count()} kripto fiyat verisi alındı:\n')
print('=' * 70)

for rate in recent[:15]:
    currency = '₺' if 'TRY' in rate.symbol else '$'
    print(f'{rate.exchange:<12} {rate.symbol:<10} {currency}{rate.last_price:>12,.2f} ({rate.timestamp.strftime("%H:%M:%S")})')

print('\n' + '=' * 70)
print('FİYAT ÖZETİ:')
print('=' * 70)

# Özet
for symbol in ['BTC/USDT', 'ETH/USDT', 'AVAX/USDT', 'BTC/TRY', 'ETH/TRY', 'AVAX/TRY']:
    stats = CryptoExchangeRate.objects.filter(symbol=symbol).aggregate(
        avg=Avg('last_price'),
        max=Max('last_price'),
        min=Min('last_price'),
        count=Count('id')
    )
    if stats['avg']:
        currency = '₺' if 'TRY' in symbol else '$'
        print(f'{symbol:<10} Ort={currency}{stats["avg"]:>12,.2f}  Min={currency}{stats["min"]:>12,.2f}  Max={currency}{stats["max"]:>12,.2f}  ({stats["count"]} kayıt)')