"""
Solitaire Admin Configuration - Enhanced
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from .models import (
    SolitaireSession, SolitaireMove, SolitaireStatistics,
    SolitairePlayer, SolitaireGameSession, SolitaireActivity, SolitaireMoveHistory
)
import json


@admin.register(SolitairePlayer)
class SolitairePlayerAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'is_anonymous', 'total_sessions', 'last_seen', 'ip_address']
    list_filter = ['is_anonymous', 'last_seen']
    search_fields = ['display_name', 'user__username', 'ip_address']
    readonly_fields = ['session_key', 'last_seen']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class SolitaireMoveHistoryInline(admin.TabularInline):
    """Inline admin for showing move history within a game session"""
    model = SolitaireMoveHistory
    extra = 0
    fields = ['move_number', 'get_move_display', 'score_change', 'time_since_last_move', 'is_undo', 'is_auto_move']
    readonly_fields = ['move_number', 'get_move_display', 'score_change', 'time_since_last_move', 'is_undo', 'is_auto_move']
    ordering = ['-move_number']
    can_delete = False
    
    def get_move_display(self, obj):
        """Display move in a readable format"""
        from_str = f"{obj.from_pile_type}"
        if obj.from_pile_index is not None:
            from_str += f"[{obj.from_pile_index}]"
        to_str = f"{obj.to_pile_type}"
        if obj.to_pile_index is not None:
            to_str += f"[{obj.to_pile_index}]"
        
        card_display = obj.get_card_display()
        return format_html(
            '<span style="font-family: monospace;">{} → {} ({})</span>',
            from_str, to_str, card_display
        )
    get_move_display.short_description = 'Move'


@admin.register(SolitaireGameSession)  
class SolitaireGameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id_short', 'player_name', 'moves_count', 'score', 'time_played', 
                   'is_won', 'is_completed', 'started_at']
    list_filter = ['is_won', 'is_completed', 'is_abandoned', 'started_at']
    search_fields = ['session_id', 'player__display_name', 'player__user__username']
    readonly_fields = ['session_id', 'started_at', 'ended_at', 'game_state_preview', 'move_history_preview']
    date_hierarchy = 'started_at'
    inlines = [SolitaireMoveHistoryInline]  # Add move history inline
    
    def session_id_short(self, obj):
        return obj.session_id[:8] + '...'
    session_id_short.short_description = 'Session'
    
    def player_name(self, obj):
        return obj.player.display_name
    player_name.short_description = 'Player'
    
    def game_state_preview(self, obj):
        if obj.game_state:
            state = obj.game_state
            return format_html(
                '<div style="font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 5px;">'
                '<strong>Stock:</strong> {} cards<br>'
                '<strong>Waste:</strong> {} cards<br>' 
                '<strong>Moves:</strong> {}<br>'
                '<strong>Score:</strong> {}<br>'
                '<strong>Move History:</strong> {} moves recorded'
                '</div>',
                len(state.get('stock', [])),
                len(state.get('waste', [])),
                state.get('moves', 0),
                state.get('score', 0),
                len(state.get('move_history', []))
            )
        return 'No game state'
    game_state_preview.short_description = 'Game State'
    
    def move_history_preview(self, obj):
        if obj.game_state and 'move_history' in obj.game_state:
            moves = obj.game_state['move_history']
            if moves:
                html = '<div style="font-family: monospace; background: #f8f8f8; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto;">'
                for i, move in enumerate(moves[-10:], 1):  # Show last 10 moves
                    html += f"<div style='margin-bottom: 5px;'>"
                    html += f"<strong>Move {move.get('moveNumber', i)}:</strong> "
                    html += f"{move.get('type', 'unknown')} - "
                    html += f"from {move.get('from', '?')} to {move.get('to', '?')}"
                    if 'cards' in move and move['cards']:
                        html += f" ({len(move['cards'])} cards)"
                    html += "</div>"
                html += '</div>'
                if len(moves) > 10:
                    html += f'<small>Showing last 10 of {len(moves)} total moves</small>'
                return format_html(html)
        return 'No move history'
    move_history_preview.short_description = 'Move History'
    
    fieldsets = [
        ('Session Info', {
            'fields': ['player', 'session_id', 'is_completed', 'is_won', 'is_abandoned']
        }),
        ('Game Stats', {
            'fields': ['moves_count', 'score', 'time_played', 'started_at', 'ended_at']
        }),
        ('Game State', {
            'fields': ['game_state_preview', 'move_history_preview'],
            'classes': ['wide']
        }),
        ('Browser Info', {
            'fields': ['browser_info'],
            'classes': ['collapse']
        })
    ]


@admin.register(SolitaireActivity)
class SolitaireActivityAdmin(admin.ModelAdmin):
    list_display = ['session_short', 'action', 'timestamp', 'details_preview']
    list_filter = ['action', 'timestamp']
    search_fields = ['session__session_id', 'session__player__display_name']
    readonly_fields = ['timestamp', 'formatted_details']
    date_hierarchy = 'timestamp'
    
    def session_short(self, obj):
        return f"{obj.session.session_id[:8]}... ({obj.session.player.display_name})"
    session_short.short_description = 'Session'
    
    def details_preview(self, obj):
        if obj.details:
            # Show first 50 chars of details
            details_str = json.dumps(obj.details)
            if len(details_str) > 50:
                return details_str[:50] + '...'
            return details_str
        return '-'
    details_preview.short_description = 'Details'
    
    def formatted_details(self, obj):
        if obj.details:
            return format_html(
                '<pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">{}</pre>',
                json.dumps(obj.details, indent=2)
            )
        return 'No details'
    formatted_details.short_description = 'Formatted Details'


@admin.register(SolitaireSession)
class SolitaireSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'score', 'moves_count', 'is_active', 'is_won', 'last_played']
    list_filter = ['is_active', 'is_won', 'created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at', 'last_played', 'game_preview']
    
    def game_preview(self, obj):
        state = obj.get_game_state()
        if state:
            return format_html(
                '<div style="font-family: monospace; background: #f0f0f0; padding: 10px;">'
                '<strong>Stock:</strong> {} cards<br>'
                '<strong>Waste:</strong> {} cards<br>'
                '<strong>Moves:</strong> {}<br>'
                '<strong>Score:</strong> {}'
                '</div>',
                len(state.get('stock', [])),
                len(state.get('waste', [])),
                state.get('moves', 0),
                state.get('score', 0)
            )
        return 'No game state'
    game_preview.short_description = 'Game Preview'
    
    fieldsets = [
        ('Session Info', {
            'fields': ['user', 'session_id', 'is_active', 'is_won']
        }),
        ('Game State', {
            'fields': ['game_preview', 'stock_pile', 'waste_pile', 'foundation_piles', 'tableau_piles'],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': ['moves_count', 'score', 'game_time']
        }),
        ('Security', {
            'fields': ['last_minimize', 'lock_password']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'last_played']
        })
    ]


@admin.register(SolitaireMove)
class SolitaireMoveAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'move_number', 'from_pile', 'to_pile', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['session__session_id']
    readonly_fields = ['timestamp']


@admin.register(SolitaireStatistics)
class SolitaireStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'games_won', 'win_rate_display', 'highest_score', 'best_win_streak']
    search_fields = ['user__username']
    readonly_fields = ['last_updated', 'statistics_summary']
    
    def win_rate_display(self, obj):
        rate = obj.win_rate()
        if rate is not None:
            color = 'green' if rate > 50 else 'orange' if rate > 25 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color, rate
            )
        return '-'
    win_rate_display.short_description = 'Win Rate'
    
    def statistics_summary(self, obj):
        return format_html(
            '<div style="background: #f0f0f0; padding: 15px; border-radius: 5px;">'
            '<h4>Player Statistics Summary</h4>'
            '<ul style="list-style: none; padding: 0;">'
            '<li><strong>Total Games:</strong> {}</li>'
            '<li><strong>Games Won:</strong> {} ({}%)</li>'
            '<li><strong>Current Streak:</strong> {}</li>'
            '<li><strong>Best Streak:</strong> {}</li>'
            '<li><strong>Total Score:</strong> {:,}</li>'
            '<li><strong>Highest Score:</strong> {:,}</li>'
            '<li><strong>Total Time:</strong> {} hours</li>'
            '<li><strong>Fastest Win:</strong> {} seconds</li>'
            '<li><strong>Fewest Moves Win:</strong> {} moves</li>'
            '</ul>'
            '</div>',
            obj.games_played,
            obj.games_won, obj.win_rate() or 0,
            obj.current_win_streak,
            obj.best_win_streak,
            obj.total_score,
            obj.highest_score,
            round(obj.total_time_played / 3600, 1) if obj.total_time_played else 0,
            obj.fastest_win or 'N/A',
            obj.fewest_moves_win or 'N/A'
        )
    statistics_summary.short_description = 'Summary'
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Summary', {
            'fields': ['statistics_summary']
        }),
        ('Game Stats', {
            'fields': ['games_played', 'games_won', 'total_score', 'highest_score', 'total_time_played']
        }),
        ('Streaks', {
            'fields': ['current_win_streak', 'best_win_streak']
        }),
        ('Records', {
            'fields': ['fastest_win', 'fewest_moves_win']
        }),
        ('Metadata', {
            'fields': ['last_updated']
        })
    ]


@admin.register(SolitaireMoveHistory)
class SolitaireMoveHistoryAdmin(admin.ModelAdmin):
    list_display = ['get_session_display', 'move_number', 'get_move_summary', 'score_change', 'timestamp']
    list_filter = ['from_pile_type', 'to_pile_type', 'is_undo', 'is_auto_move', 'timestamp']
    search_fields = ['session__session_id', 'session__player__display_name']
    date_hierarchy = 'timestamp'
    readonly_fields = ['session', 'move_number', 'from_pile_type', 'from_pile_index', 
                      'to_pile_type', 'to_pile_index', 'cards', 'num_cards', 
                      'score_before', 'score_after', 'score_change', 'timestamp',
                      'time_since_start', 'time_since_last_move', 'is_undo', 
                      'is_auto_move', 'revealed_card']
    
    def get_session_display(self, obj):
        return f"{obj.session.player.display_name} - {obj.session.session_id[:8]}..."
    get_session_display.short_description = 'Session'
    
    def get_move_summary(self, obj):
        from_str = f"{obj.from_pile_type}"
        if obj.from_pile_index is not None:
            from_str += f"[{obj.from_pile_index}]"
        to_str = f"{obj.to_pile_type}"
        if obj.to_pile_index is not None:
            to_str += f"[{obj.to_pile_index}]"
        
        card_display = obj.get_card_display()
        
        # Add special indicators
        indicators = []
        if obj.is_undo:
            indicators.append('↩')
        if obj.is_auto_move:
            indicators.append('⚡')
        
        indicator_str = ' '.join(indicators) if indicators else ''
        
        return format_html(
            '<span style="font-family: monospace;">{} {} → {} {}</span>',
            card_display, from_str, to_str, indicator_str
        )
    get_move_summary.short_description = 'Move'


# Admin Site Customization
admin.site.site_header = "UNIBOS Solitaire Administration"
admin.site.index_title = "Solitaire Game Management"

# Add custom admin actions
from django.urls import reverse
from django.utils.safestring import mark_safe

def get_admin_actions(request):
    """Add custom actions to admin index"""
    return [
        {
            'name': 'solitaire dashboard',
            'url': reverse('solitaire:admin_dashboard'),
            'description': 'real-time game monitoring and analytics'
        }
    ]