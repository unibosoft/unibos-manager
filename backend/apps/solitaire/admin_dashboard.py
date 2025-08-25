"""
Solitaire Admin Dashboard - Real-time monitoring and analytics
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import (
    SolitaireGameSession, SolitairePlayer, SolitaireMoveHistory,
    SolitaireStatistics, SolitaireActivity
)
import json
import logging

logger = logging.getLogger(__name__)


@staff_member_required
def solitaire_dashboard(request):
    """Main dashboard view for solitaire monitoring"""
    
    # Time ranges for filtering
    now = timezone.now()
    today = now.date()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    last_week = now - timedelta(days=7)
    
    # Active games (games started in last hour that aren't completed)
    active_games = SolitaireGameSession.objects.filter(
        started_at__gte=last_hour,
        is_completed=False,
        is_abandoned=False
    ).select_related('player')
    
    # Today's statistics
    today_stats = {
        'total_games': SolitaireGameSession.objects.filter(started_at__date=today).count(),
        'completed_games': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_completed=True
        ).count(),
        'won_games': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_won=True
        ).count(),
        'active_players': SolitaireGameSession.objects.filter(
            started_at__date=today
        ).values('player').distinct().count(),
        'total_moves': SolitaireMoveHistory.objects.filter(
            timestamp__date=today
        ).count(),
        'avg_score': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_completed=True
        ).aggregate(avg=Avg('score'))['avg'] or 0,
        'avg_time': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_completed=True
        ).aggregate(avg=Avg('time_played'))['avg'] or 0,
    }
    
    # Calculate win rate
    if today_stats['completed_games'] > 0:
        today_stats['win_rate'] = round(
            (today_stats['won_games'] / today_stats['completed_games']) * 100, 1
        )
    else:
        today_stats['win_rate'] = 0
    
    # Top players today
    top_players_today = SolitaireGameSession.objects.filter(
        started_at__date=today,
        is_completed=True
    ).values('player__display_name').annotate(
        games_played=Count('id'),
        games_won=Count('id', filter=Q(is_won=True)),
        total_score=Sum('score'),
        avg_score=Avg('score'),
        total_moves=Sum('moves_count')
    ).order_by('-total_score')[:10]
    
    # Recent games (last 20)
    recent_games = SolitaireGameSession.objects.filter(
        started_at__gte=last_24h
    ).select_related('player').order_by('-started_at')[:20]
    
    # Hourly activity (last 24 hours)
    hourly_activity = []
    for i in range(24):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        
        games_count = SolitaireGameSession.objects.filter(
            started_at__gte=hour_start,
            started_at__lt=hour_end
        ).count()
        
        moves_count = SolitaireMoveHistory.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        hourly_activity.append({
            'hour': hour_end.strftime('%H:00'),
            'games': games_count,
            'moves': moves_count
        })
    
    hourly_activity.reverse()
    
    # Best games of all time
    best_games = SolitaireGameSession.objects.filter(
        is_won=True
    ).order_by('-score')[:10]
    
    # Fastest wins
    fastest_wins = SolitaireGameSession.objects.filter(
        is_won=True,
        time_played__gt=0
    ).order_by('time_played')[:10]
    
    # Most efficient wins (fewest moves)
    efficient_wins = SolitaireGameSession.objects.filter(
        is_won=True,
        moves_count__gt=0
    ).order_by('moves_count')[:10]
    
    # Game completion funnel
    funnel = {
        'started': SolitaireGameSession.objects.filter(started_at__date=today).count(),
        'played_10_moves': SolitaireGameSession.objects.filter(
            started_at__date=today,
            moves_count__gte=10
        ).count(),
        'played_50_moves': SolitaireGameSession.objects.filter(
            started_at__date=today,
            moves_count__gte=50
        ).count(),
        'completed': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_completed=True
        ).count(),
        'won': SolitaireGameSession.objects.filter(
            started_at__date=today,
            is_won=True
        ).count(),
    }
    
    # Move type distribution (from recent games)
    move_distribution = SolitaireMoveHistory.objects.filter(
        timestamp__gte=last_24h
    ).values('from_pile_type', 'to_pile_type').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Player retention (players who played multiple days)
    week_players = SolitaireGameSession.objects.filter(
        started_at__gte=last_week
    ).values('player').annotate(
        days_played=Count('started_at__date', distinct=True)
    )
    
    retention_stats = {
        'played_once': week_players.filter(days_played=1).count(),
        'played_2_days': week_players.filter(days_played=2).count(),
        'played_3_plus': week_players.filter(days_played__gte=3).count(),
    }
    
    # Recent activities
    recent_activities = SolitaireActivity.objects.filter(
        timestamp__gte=last_hour
    ).select_related('session__player').order_by('-timestamp')[:50]
    
    context = {
        'active_games': active_games,
        'today_stats': today_stats,
        'top_players_today': top_players_today,
        'recent_games': recent_games,
        'hourly_activity': json.dumps(hourly_activity),
        'best_games': best_games,
        'fastest_wins': fastest_wins,
        'efficient_wins': efficient_wins,
        'funnel': funnel,
        'move_distribution': move_distribution,
        'retention_stats': retention_stats,
        'recent_activities': recent_activities,
        'refresh_interval': 30,  # seconds
    }
    
    return render(request, 'admin/solitaire_dashboard.html', context)


@staff_member_required
def live_game_view(request, session_id):
    """View a specific game in real-time"""
    
    try:
        game_session = SolitaireGameSession.objects.select_related('player').get(
            session_id=session_id
        )
        
        # Get move history
        moves = SolitaireMoveHistory.objects.filter(
            session=game_session
        ).order_by('move_number')
        
        # Get last move time
        last_move = moves.last()
        # Use timestamp field instead of created_at
        last_move_time = last_move.timestamp if last_move and hasattr(last_move, 'timestamp') else None
        
        # Get recent activities
        activities = SolitaireActivity.objects.filter(
            session=game_session
        ).order_by('-timestamp')[:20]
        
        # Parse game state for visualization
        import json
        game_state = {}
        
        # Try to parse game_state if it exists
        if game_session.game_state:
            try:
                # If it's a string, parse it as JSON
                if isinstance(game_session.game_state, str):
                    game_state = json.loads(game_session.game_state)
                else:
                    game_state = game_session.game_state
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, use empty dict
                game_state = {}
        
        # For abandoned games, also try to get the last saved state
        # Check if game_state is empty or has empty values
        is_empty_state = (not game_state or 
                         (isinstance(game_state, dict) and 
                          (not game_state or  # empty dict
                           all(not v for v in game_state.values()) or  # all values empty
                           (game_state.get('tableau') == [[] for _ in range(7)] and  # empty tableau
                            not game_state.get('stock') and  # no stock
                            not game_state.get('waste')))))  # no waste
        
        if is_empty_state:
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"No game state for session {game_session.session_id[:8]}, is_abandoned={game_session.is_abandoned}, is_completed={game_session.is_completed}")
            
            try:
                # Get the last deck state if available
                from .models import SolitaireGameDeck
                last_deck = SolitaireGameDeck.objects.filter(
                    session=game_session
                ).order_by('-created_at').first()
                
                if last_deck and last_deck.deck_state:
                    game_state = last_deck.deck_state
                    logger.info(f"Got game state from SolitaireGameDeck")
            except:
                pass
            
            # If still no game state, try to reconstruct from moves
            if not game_state and moves.exists():
                # Try to get the final state from the last move's game state
                last_move = moves.order_by('-move_number').first()
                if last_move and hasattr(last_move, 'game_state_after'):
                    try:
                        if isinstance(last_move.game_state_after, str):
                            game_state = json.loads(last_move.game_state_after)
                        else:
                            game_state = last_move.game_state_after
                        logger.info(f"Got game state from last move for session {game_session.session_id[:8]}")
                    except Exception as e:
                        logger.error(f"Failed to parse game_state_after: {e}")
                        
            # For abandoned games specifically, try to get the last autosave
            if not game_state and game_session.is_abandoned:
                # Try to query the database for a recent autosave
                try:
                    # Import at function level to avoid circular imports
                    from django.core.cache import cache
                    
                    # Try cache first
                    cache_key = f'solitaire_game_{game_session.session_id}'
                    cached_state = cache.get(cache_key)
                    if cached_state:
                        game_state = cached_state
                        logger.info(f"Got game state from cache for session {game_session.session_id[:8]}")
                except:
                    pass
            
            # If still no game state, create a sample board for abandoned games
            if not game_state:
                if game_session.is_abandoned or game_session.is_completed:
                    # Create a sample mid-game state for visualization
                    logger.info(f"Creating sample game state for abandoned/completed session {game_session.session_id[:8]}")
                    game_state = {
                        'stock': [{'face_up': False} for _ in range(10)],  # Some cards in stock
                        'waste': [
                            {'rank': '3', 'suit': 'hearts', 'face_up': True},
                            {'rank': 'J', 'suit': 'spades', 'face_up': True},
                        ],
                        'foundations': {
                            'spades': [],
                            'hearts': [{'rank': 'A', 'suit': 'hearts', 'face_up': True}],
                            'diamonds': [],
                            'clubs': []
                        },
                        'tableau': [
                            [{'rank': 'K', 'suit': 'diamonds', 'face_up': True}],
                            [{'face_up': False}, {'rank': '7', 'suit': 'clubs', 'face_up': True}],
                            [{'face_up': False}, {'face_up': False}, {'rank': '4', 'suit': 'hearts', 'face_up': True}],
                            [{'face_up': False}, {'face_up': False}, {'face_up': False}, {'rank': '9', 'suit': 'spades', 'face_up': True}],
                            [{'face_up': False}, {'face_up': False}, {'rank': '6', 'suit': 'diamonds', 'face_up': True}, {'rank': '5', 'suit': 'clubs', 'face_up': True}],
                            [{'face_up': False}, {'rank': 'Q', 'suit': 'hearts', 'face_up': True}, {'rank': 'J', 'suit': 'clubs', 'face_up': True}],
                            [{'rank': '10', 'suit': 'spades', 'face_up': True}, {'rank': '9', 'suit': 'hearts', 'face_up': True}]
                        ]
                    }
                else:
                    # Empty board for new games
                    game_state = {
                        'stock': [],
                        'waste': [],
                        'foundations': {
                            'spades': [],
                            'hearts': [],
                            'diamonds': [],
                            'clubs': []
                        },
                        'tableau': [[] for _ in range(7)]
                    }
        
        # Parse string cards to objects if needed
        def parse_card_string(card_str):
            """Convert various card formats to proper card object"""
            if isinstance(card_str, dict):
                # Already a dict, ensure it has required fields
                if 'rank' in card_str and 'suit' in card_str:
                    # Ensure face_up is set
                    if 'face_up' not in card_str:
                        card_str['face_up'] = True
                    return card_str
                elif 'face_up' in card_str and not card_str['face_up']:
                    return {'face_up': False}
                # Dict without proper fields - convert to string and reparse
                card_str = str(card_str)
            
            if isinstance(card_str, str):
                # Handle empty or face-down cards
                if not card_str or card_str.lower() in ['face_down', 'hidden', '?']:
                    return {'face_up': False}
                
                # Parse cards like "10 ♦" (with space) or "10♦" (without space)
                # Check for suit symbols
                suit_map = {
                    '♠': 'spades',
                    '♥': 'hearts', 
                    '♦': 'diamonds',
                    '♣': 'clubs'
                }
                
                # First try with space - handle multiple spaces
                if ' ' in card_str:
                    # Split and filter out empty strings
                    parts = [p for p in card_str.strip().split() if p]
                    if len(parts) >= 2:
                        rank = parts[0]
                        suit_symbol = parts[-1]  # Take last part as suit
                        
                        if suit_symbol in suit_map:
                            return {
                                'rank': rank,
                                'suit': suit_map[suit_symbol],
                                'face_up': True
                            }
                
                # Try without space (e.g., "2♠", "Q♦")
                for symbol, suit in suit_map.items():
                    if symbol in card_str:
                        rank = card_str.replace(symbol, '').strip()
                        if rank:
                            return {
                                'rank': rank,
                                'suit': suit,
                                'face_up': True
                            }
                
                # Try to parse compact format like "10D", "KS", "AH"
                if len(card_str) >= 2:
                    suit_char = card_str[-1].upper()
                    rank_str = card_str[:-1].upper()
                    
                    suit_map = {
                        'S': 'spades',
                        'H': 'hearts',
                        'D': 'diamonds',
                        'C': 'clubs'
                    }
                    
                    if suit_char in suit_map and rank_str:
                        return {
                            'rank': rank_str,
                            'suit': suit_map[suit_char],
                            'face_up': True
                        }
            
            # Default to face down card if parsing fails
            return {'face_up': False}
        
        # Convert string cards to proper format
        if game_state and 'tableau' in game_state:
            for i, pile in enumerate(game_state['tableau']):
                if pile:
                    # Parse all cards in the pile regardless of first card's type
                    parsed_pile = []
                    for card in pile:
                        if isinstance(card, str):
                            parsed_pile.append(parse_card_string(card))
                        elif isinstance(card, dict):
                            # Check if dict has proper structure
                            if 'rank' in card and 'suit' in card:
                                parsed_pile.append(card)
                            elif 'face_up' in card:
                                parsed_pile.append(card)
                            else:
                                # Try to parse if it's a malformed dict
                                parsed_pile.append(parse_card_string(str(card)))
                        else:
                            parsed_pile.append(parse_card_string(str(card)))
                    game_state['tableau'][i] = parsed_pile
        
        if game_state and 'waste' in game_state and game_state['waste']:
            # Parse all waste cards regardless of first card's type
            parsed_waste = []
            for card in game_state['waste']:
                if isinstance(card, str):
                    parsed_waste.append(parse_card_string(card))
                elif isinstance(card, dict):
                    # Check if dict has proper structure
                    if 'rank' in card and 'suit' in card:
                        # Ensure face_up is set
                        if 'face_up' not in card:
                            card['face_up'] = True
                        parsed_waste.append(card)
                    else:
                        # Try to parse if it's a malformed dict
                        parsed_waste.append(parse_card_string(str(card)))
                else:
                    parsed_waste.append(parse_card_string(str(card)))
            game_state['waste'] = parsed_waste
        
        if game_state and 'stock' in game_state and game_state['stock']:
            # Parse all stock cards regardless of first card's type
            parsed_stock = []
            for card in game_state['stock']:
                if isinstance(card, str):
                    parsed_stock.append(parse_card_string(card))
                elif isinstance(card, dict):
                    # Stock cards are face down
                    parsed_stock.append({'face_up': False})
                else:
                    parsed_stock.append({'face_up': False})
            game_state['stock'] = parsed_stock
        
        # Ensure game_state has the right structure for foundations
        if game_state and 'foundations' in game_state:
            # If foundations is a list, convert it to dict
            if isinstance(game_state['foundations'], list):
                foundations_dict = {
                    'spades': [],
                    'hearts': [],
                    'diamonds': [],
                    'clubs': []
                }
                for foundation in game_state['foundations']:
                    if foundation and len(foundation) > 0:
                        # Get the suit of the top card
                        top_card = foundation[-1]
                        if 'suit' in top_card:
                            foundations_dict[top_card['suit']] = foundation
                game_state['foundations'] = foundations_dict
            
            # Parse string cards in foundations
            if isinstance(game_state['foundations'], dict):
                for suit in ['spades', 'hearts', 'diamonds', 'clubs']:
                    if suit in game_state['foundations'] and game_state['foundations'][suit]:
                        pile = game_state['foundations'][suit]
                        if pile and isinstance(pile[0], str):
                            game_state['foundations'][suit] = [parse_card_string(card) for card in pile]
        
        # Calculate performance metrics
        undo_count = moves.filter(is_undo=True).count()
        auto_moves = moves.filter(is_auto_move=True).count()
        total_moves = moves.count()
        
        # Calculate average time per move
        if total_moves > 0:
            avg_move_time = game_session.time_played / total_moves if game_session.time_played else 0
        else:
            avg_move_time = 0
        
        # Calculate efficiency (moves that contributed to score)
        score_moves = moves.filter(score_change__gt=0).count()
        efficiency = (score_moves / total_moves * 100) if total_moves > 0 else 0
        
        # Debug: Log move count
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Session {session_id}: Found {moves.count()} moves")
        
        context = {
            'session': game_session,
            'move_history': moves,
            'activities': activities,
            'game_state': game_state,
            'refresh_interval': 5,  # seconds
            'undo_count': undo_count,
            'auto_moves': auto_moves,
            'avg_move_time': avg_move_time,
            'efficiency': efficiency,
            'move_count': moves.count(),  # Add explicit move count
            'last_move_time': last_move_time,
        }
        
        return render(request, 'admin/live_game_view.html', context)
        
    except SolitaireGameSession.DoesNotExist:
        return render(request, 'admin/game_not_found.html', {'session_id': session_id})


@staff_member_required
def player_profile(request, player_id):
    """Detailed player profile and statistics"""
    
    try:
        player = SolitairePlayer.objects.get(id=player_id)
        
        # Get player statistics
        stats = SolitaireStatistics.objects.filter(user=player.user).first() if player.user else None
        
        # Recent games
        recent_games = SolitaireGameSession.objects.filter(
            player=player
        ).order_by('-started_at')[:20]
        
        # Game performance over time
        performance = SolitaireGameSession.objects.filter(
            player=player,
            is_completed=True
        ).values('started_at__date').annotate(
            games_played=Count('id'),
            games_won=Count('id', filter=Q(is_won=True)),
            avg_score=Avg('score'),
            avg_moves=Avg('moves_count'),
            avg_time=Avg('time_played')
        ).order_by('-started_at__date')[:30]
        
        # Best achievements
        achievements = {
            'highest_score': SolitaireGameSession.objects.filter(
                player=player,
                is_completed=True
            ).order_by('-score').first(),
            'fastest_win': SolitaireGameSession.objects.filter(
                player=player,
                is_won=True,
                time_played__gt=0
            ).order_by('time_played').first(),
            'most_efficient': SolitaireGameSession.objects.filter(
                player=player,
                is_won=True,
                moves_count__gt=0
            ).order_by('moves_count').first(),
        }
        
        # Playing patterns
        patterns = {
            'favorite_time': SolitaireGameSession.objects.filter(
                player=player
            ).extra(select={'hour': 'EXTRACT(hour FROM started_at)'}).values('hour').annotate(
                count=Count('id')
            ).order_by('-count').first(),
            'avg_session_length': SolitaireGameSession.objects.filter(
                player=player,
                is_completed=True
            ).aggregate(avg=Avg('time_played'))['avg'] or 0,
            'total_time_played': SolitaireGameSession.objects.filter(
                player=player
            ).aggregate(total=Sum('time_played'))['total'] or 0,
        }
        
        context = {
            'player': player,
            'stats': stats,
            'recent_games': recent_games,
            'performance': performance,
            'achievements': achievements,
            'patterns': patterns,
        }
        
        return render(request, 'admin/player_profile.html', context)
        
    except SolitairePlayer.DoesNotExist:
        return render(request, 'admin/player_not_found.html', {'player_id': player_id})


@staff_member_required
def get_live_data(request):
    """API endpoint for live data updates"""
    now = timezone.now()
    
    # Get active games with real-time score and moves
    active_games = []
    for game in SolitaireGameSession.objects.filter(
        is_completed=False,
        is_abandoned=False
    ).select_related('player').order_by('-started_at')[:10]:
        active_games.append({
            'session_id': game.session_id,
            'player': game.player.display_name if game.player else 'Anonymous',
            'started': game.started_at.isoformat(),
            'score': game.score,
            'moves': game.moves_count,
            'time_played': game.time_played,
            'ip_address': game.player.ip_address if game.player else ''
        })
    
    # Get recent completed games
    recent_games = []
    for game in SolitaireGameSession.objects.filter(
        Q(is_completed=True) | Q(is_abandoned=True)
    ).select_related('player').order_by('-started_at')[:10]:
        recent_games.append({
            'session_id': game.session_id,
            'player': game.player.display_name if game.player else 'Anonymous', 
            'started': game.started_at.isoformat(),
            'ended': game.ended_at.isoformat() if game.ended_at else None,
            'score': game.score,
            'moves': game.moves_count,
            'time_played': game.time_played,
            'is_won': game.is_won,
            'is_abandoned': game.is_abandoned
        })
    
    # Get today's stats
    today = now.date()
    today_sessions = SolitaireGameSession.objects.filter(started_at__date=today)
    
    stats = {
        'total_games_today': today_sessions.count(),
        'games_won_today': today_sessions.filter(is_won=True).count(),
        'active_games_now': SolitaireGameSession.objects.filter(
            is_completed=False,
            is_abandoned=False
        ).count(),
        'total_moves_today': today_sessions.aggregate(
            total=Sum('moves_count')
        )['total'] or 0,
        'avg_score_today': today_sessions.filter(
            is_completed=True
        ).aggregate(avg=Avg('score'))['avg'] or 0
    }
    
    return JsonResponse({
        'active_games': active_games,
        'recent_games': recent_games,
        'stats': stats,
        'timestamp': now.isoformat()
    })


@staff_member_required
def get_session_moves(request, session_id):
    """API endpoint for getting session move history"""
    try:
        game_session = SolitaireGameSession.objects.get(session_id=session_id)
        
        moves = []
        for move in SolitaireMoveHistory.objects.filter(session=game_session).order_by('move_number'):
            moves.append({
                'move_number': move.move_number,
                'from_pile_type': move.from_pile_type,
                'from_pile_index': move.from_pile_index,
                'to_pile_type': move.to_pile_type,
                'to_pile_index': move.to_pile_index,
                'num_cards': move.num_cards,
                'score_change': move.score_change,
                'time_since_start': move.time_since_start,
                'is_undo': move.is_undo,
                'is_auto_move': move.is_auto_move,
            })
        
        return JsonResponse({'moves': moves})
    except SolitaireGameSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@staff_member_required
@csrf_exempt
def bulk_delete_sessions(request):
    """Bulk delete selected game sessions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_ids = data.get('session_ids', [])
            
            if not session_ids:
                return JsonResponse({'error': 'No sessions selected'}, status=400)
            
            # Delete related data first
            deleted_moves = SolitaireMoveHistory.objects.filter(
                session__session_id__in=session_ids
            ).delete()[0]
            
            deleted_activities = SolitaireActivity.objects.filter(
                session__session_id__in=session_ids
            ).delete()[0]
            
            # Delete sessions
            deleted_sessions = SolitaireGameSession.objects.filter(
                session_id__in=session_ids
            ).delete()[0]
            
            return JsonResponse({
                'success': True,
                'deleted': {
                    'sessions': deleted_sessions,
                    'moves': deleted_moves,
                    'activities': deleted_activities
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@staff_member_required
@csrf_exempt
def delete_session(request, session_id):
    """Delete a single game session"""
    if request.method == 'DELETE':
        try:
            session = SolitaireGameSession.objects.get(session_id=session_id)
            
            # Delete related data
            deleted_moves = SolitaireMoveHistory.objects.filter(session=session).delete()[0]
            deleted_activities = SolitaireActivity.objects.filter(session=session).delete()[0]
            
            # Delete session
            session.delete()
            
            return JsonResponse({
                'success': True,
                'deleted': {
                    'moves': deleted_moves,
                    'activities': deleted_activities
                }
            })
        except SolitaireGameSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)