"""
Personal Inflation module views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import timedelta


class PersonalInflationDashboardView(LoginRequiredMixin, TemplateView):
    """Personal inflation dashboard view"""
    template_name = 'personal_inflation/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate some statistics (placeholder for now)
        today = timezone.now().date()
        last_month = today - timedelta(days=30)
        
        context.update({
            'module_name': 'kişisel enflasyon',
            'module_icon': '📈',
            'description': 'kişisel tüketim sepetinizi takip edin ve enflasyonunuzu hesaplayın',
            'features': [
                'kişisel sepet oluşturma',
                'ürün fiyat takibi',
                'market karşılaştırması',
                'enflasyon hesaplama',
                'harcama analizi',
                'tasarruf önerileri',
                'kategori bazlı takip',
                'aylık raporlar'
            ],
            'stats': {
                'monthly_inflation': 0.0,
                'yearly_inflation': 0.0,
                'tracked_products': 0,
                'tracked_stores': 0,
                'total_savings': 0.0,
                'price_alerts': 0
            },
            'recent_changes': [],
            'top_categories': []
        })
        return context