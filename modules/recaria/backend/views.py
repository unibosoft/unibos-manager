"""
Recaria module views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class RecariaDashboardView(LoginRequiredMixin, TemplateView):
    """Recaria dashboard view"""
    template_name = 'recaria/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'module_name': 'recaria',
            'module_icon': '🪐',
            'description': 'ultima online inspired mmorpg system',
            'features': [
                'character creation & management',
                'guild system',
                'trading post',
                'skill progression',
                'pvp battles',
                'resource gathering',
                'crafting system',
                'world exploration'
            ],
            'stats': {
                'total_characters': 0,
                'active_guilds': 0,
                'ongoing_battles': 0,
                'trade_listings': 0
            }
        })
        return context