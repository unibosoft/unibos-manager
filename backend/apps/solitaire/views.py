"""
Solitaire game views
"""

import json
import uuid
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import (
    SolitaireSession, SolitaireMove, SolitaireStatistics,
    SolitairePlayer, SolitaireGameSession, SolitaireActivity,
    SolitaireMoveHistory
)
from .game import SolitaireGame, hash_password

logger = logging.getLogger(__name__)


def get_or_create_player(request):
    """Get or create a player record for tracking"""
    if request.user.is_authenticated:
        # For authenticated users
        player, created = SolitairePlayer.objects.get_or_create(
            user=request.user,
            defaults={
                'session_key': request.session.session_key or str(uuid.uuid4()),
                'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'display_name': request.user.username,
                'is_anonymous': False
            }
        )
    else:
        # For anonymous users
        session_key = request.session.session_key
        if not session_key:
            session_key = str(uuid.uuid4())
        
        player, created = SolitairePlayer.objects.get_or_create(
            session_key=session_key,
            defaults={
                'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'display_name': f'Guest_{session_key[:8]}',
                'is_anonymous': True
            }
        )
    
    # Update last seen
    player.last_seen = timezone.now()
    player.save(update_fields=['last_seen'])
    
    return player


@login_required
def solitaire_game(request):
    """Simplified solitaire game view - single session management"""
    
    # No need for player tracking with UUID users
    
    # Get or create active session
    session = SolitaireSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    # Also check if the corresponding GameSession exists (might have been deleted from admin)
    if session:
        game_session_exists = SolitaireGameSession.objects.filter(
            session_id=session.session_id
        ).exists()
        
        if not game_session_exists:
            # Session was deleted from admin, mark as inactive
            logger.info(f"Session {session.session_id[:8]} was deleted from admin, creating new game")
            session.is_active = False
            session.save()
            session = None
    
    if not session:
        # Get player for tracking
        player, _ = SolitairePlayer.objects.get_or_create(
            user=request.user,
            defaults={
                'session_key': request.session.session_key or str(uuid.uuid4()),
                'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'display_name': request.user.username,
                'is_anonymous': False
            }
        )
        
        # NOTE: We do NOT automatically mark old games as abandoned here
        # Games stay active until player explicitly starts a new game or wins
        
        # Create new game session
        logger.info(f"Creating new game for {request.user.username}")
        
        # Create fresh game
        game = SolitaireGame()
        game.new_game()
        game_state = game.to_dict()
        
        # Verify game state
        stock_count = len(game_state.get('stock', []))
        tableau_counts = [len(pile) for pile in game_state.get('tableau', [])]
        
        if stock_count != 24 or tableau_counts != [1, 2, 3, 4, 5, 6, 7]:
            logger.error(f"Invalid game state! Stock: {stock_count}, Tableau: {tableau_counts}")
            # Try again
            game = SolitaireGame()
            game.new_game()
            game_state = game.to_dict()
        
        # Create session
        new_session_id = str(uuid.uuid4())
        session = SolitaireSession.objects.create(
            user=request.user,
            session_id=new_session_id,
            is_active=True
        )
        session.save_game_state(game_state)
        session.save()
        
        # Create corresponding SolitaireGameSession for tracking
        SolitaireGameSession.objects.create(
            player=player,
            session_id=new_session_id,
            game_state=game_state,
            moves_count=0,
            score=0,
            time_played=0,
            is_completed=False,
            is_won=False,
            is_abandoned=False
        )
        
        logger.info(f"New session created: {session.session_id[:8]}")
        logger.info(f"Game state - Stock: {len(game_state.get('stock', []))}, Tableau: {[len(p) for p in game_state.get('tableau', [])]}")
    else:
        logger.info(f"Found existing session: {session.session_id[:8]}, moves={session.moves_count}")
    
    # Get game state
    game_state = session.get_game_state()
    
    # Log what we're sending
    logger.info(f"Sending to template - Stock: {len(game_state.get('stock', []))}, Tableau: {[len(p) for p in game_state.get('tableau', [])]}")
    
    # Prepare context
    context = {
        'session_id': session.session_id,
        'game_state': json.dumps(game_state),
        'user_id': str(request.user.id),  # UUID as string
        'is_authenticated': True
    }
    
    return render(request, 'web_ui/solitaire.html', context)


@csrf_exempt
def solitaire_api(request, action):
    """API endpoint for game actions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'No session ID'}, status=400)
        
        # Get session - works for both authenticated and anonymous users
        session = None
        if request.user.is_authenticated:
            session = SolitaireSession.objects.filter(
                session_id=session_id,
                user=request.user
            ).first()
        else:
            # For anonymous users, get session by session_id only
            session = SolitaireSession.objects.filter(
                session_id=session_id,
                user__isnull=True
            ).first()
            
        if not session:
            logger.error(f"Session not found: {session_id[:8]}")
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Load game state
        game = SolitaireGame()
        game.from_dict(session.get_game_state())
        
        result = {'success': False}
        
        if action == 'draw':
            game.draw_from_stock()
            result['success'] = True
            
        elif action == 'move':
            # Frontend handles the move logic, just save the state
            if 'game_state' in data:
                # Use the game state from frontend
                session.save_game_state(data['game_state'])
                session.moves_count = data.get('moves', session.moves_count)
                session.score = data.get('score', session.score)
                session.game_time = data.get('time', session.game_time)
                session.save()
                
                # Track move history if provided
                if 'move_details' in data:
                    move_details = data['move_details']
                    
                    # Get or create player (works for both authenticated and anonymous)
                    player = get_or_create_player(request)
                    
                    game_session = SolitaireGameSession.objects.filter(
                        player=player,
                        session_id=session_id,
                        is_completed=False
                    ).first()
                    
                    if not game_session:
                        game_session = SolitaireGameSession.objects.create(
                            player=player,
                            session_id=session_id,
                            game_state=data['game_state'],
                            moves_count=data.get('moves', 0),
                            score=data.get('score', 0),
                            time_played=data.get('time', 0)
                        )
                    else:
                        # Update existing game session with latest data
                        game_session.game_state = data['game_state']
                        game_session.moves_count = data.get('moves', 0)
                        game_session.score = data.get('score', 0)
                        game_session.time_played = data.get('time', 0)
                        game_session.save()
                    
                    # Create move history entry
                    move_number = SolitaireMoveHistory.objects.filter(session=game_session).count() + 1
                    SolitaireMoveHistory.objects.create(
                        session=game_session,
                        move_number=move_number,
                        from_pile_type=move_details.get('from_type'),
                        from_pile_index=move_details.get('from_index'),
                        to_pile_type=move_details.get('to_type'),
                        to_pile_index=move_details.get('to_index'),
                        cards=move_details.get('cards', []),
                        num_cards=len(move_details.get('cards', [])),
                        score_before=move_details.get('score_before', 0),
                        score_after=session.score,
                        score_change=session.score - move_details.get('score_before', 0),
                        time_since_start=move_details.get('time_since_start', 0),
                        time_since_last_move=move_details.get('time_since_last_move', 0),
                        is_undo=move_details.get('is_undo', False),
                        is_auto_move=move_details.get('is_auto', False)
                    )
                
                result['success'] = True
                logger.info(f"Saved game state - moves: {session.moves_count}, score: {session.score}")
            
        elif action == 'save':
            # Save current game state
            logger.info(f"SAVE ACTION: Received save request for session {session_id[:8]}")
            logger.info(f"  Current DB state - Moves: {session.moves_count}, Score: {session.score}")
            
            if 'game_state' in data:
                game_state = data['game_state']
                
                # Log what we're receiving
                logger.info(f"  Incoming state - Stock: {len(game_state.get('stock', []))}, "
                           f"Waste: {len(game_state.get('waste', []))}, "
                           f"Tableau: {[len(p) for p in game_state.get('tableau', [])]}")
                logger.info(f"  Incoming - Moves: {data.get('moves', 0)}, Score: {data.get('score', 0)}")
                
                session.save_game_state(game_state)
                session.moves_count = data.get('moves', session.moves_count)
                session.score = data.get('score', session.score)
                session.game_time = data.get('time', session.game_time)
                
                # Also handle move_details if provided (for save_with_move action from frontend)
                if 'move_details' in data:
                    move_details = data['move_details']
                    
                    # Get or create player (works for both authenticated and anonymous)
                    player = get_or_create_player(request)
                    
                    game_session = SolitaireGameSession.objects.filter(
                        player=player,
                        session_id=session_id,
                        is_completed=False
                    ).first()
                    
                    if not game_session:
                        game_session = SolitaireGameSession.objects.create(
                            player=player,
                            session_id=session_id,
                            game_state=data['game_state'],
                            moves_count=data.get('moves', 0),
                            score=data.get('score', 0),
                            time_played=data.get('time', 0)
                        )
                    else:
                        # Update existing game session with latest data
                        game_session.game_state = data['game_state']
                        game_session.moves_count = data.get('moves', 0)
                        game_session.score = data.get('score', 0)
                        game_session.time_played = data.get('time', 0)
                        game_session.save()
                    
                    # Create move history entry
                    move_number = SolitaireMoveHistory.objects.filter(session=game_session).count() + 1
                    SolitaireMoveHistory.objects.create(
                        session=game_session,
                        move_number=move_number,
                        from_pile_type=move_details.get('from_type'),
                        from_pile_index=move_details.get('from_index'),
                        to_pile_type=move_details.get('to_type'),
                        to_pile_index=move_details.get('to_index'),
                        cards=move_details.get('cards', []),
                        num_cards=len(move_details.get('cards', [])),
                        score_before=move_details.get('score_before', 0),
                        score_after=session.score,
                        score_change=session.score - move_details.get('score_before', 0),
                        time_since_start=move_details.get('time_since_start', 0),
                        time_since_last_move=move_details.get('time_since_last_move', 0),
                        is_undo=move_details.get('is_undo', False),
                        is_auto_move=move_details.get('is_auto', False)
                    )
                
                # Check if game is won
                is_won = data.get('is_won', False)
                is_completed = data.get('is_completed', False)
                
                if is_won:
                    session.is_won = True
                    session.is_active = False
                    logger.info(f"Game WON! User: {request.user.username}, Score: {session.score}, Moves: {session.moves_count}")
                
                session.save()
                
                # Log what was saved
                logger.info(f"  SAVED to DB - Moves: {session.moves_count}, Score: {session.score}")
                saved_state = session.get_game_state()
                logger.info(f"  Verification - Stock: {len(saved_state.get('stock', []))}, "
                           f"Waste: {len(saved_state.get('waste', []))}, "
                           f"Tableau: {[len(p) for p in saved_state.get('tableau', [])]}")
                
                # Also update SolitaireGameSession for admin panel tracking
                player = get_or_create_player(request)
                
                game_session = SolitaireGameSession.objects.filter(
                    player=player,
                    session_id=session_id,
                    is_completed=False
                ).first()
                
                if not game_session:
                    # Create new game session if it doesn't exist
                    game_session = SolitaireGameSession.objects.create(
                        player=player,
                        session_id=session_id,
                        game_state=data['game_state'],
                        moves_count=data.get('moves', 0),
                        score=data.get('score', 0),
                        time_played=data.get('time', 0)
                    )
                else:
                    game_session.game_state = data['game_state']
                    game_session.moves_count = data.get('moves', 0)
                    game_session.score = data.get('score', 0)
                    game_session.time_played = data.get('time', 0)
                    game_session.save()  # IMPORTANT: Save the updates to database!
                
                # Update win status
                if is_won:
                    game_session.is_won = True
                    game_session.is_completed = True
                    game_session.ended_at = timezone.now()
                    
                    # Update user statistics
                    stats, created = SolitaireStatistics.objects.get_or_create(user=request.user)
                    stats.games_won += 1
                    stats.games_played += 1
                    stats.total_score += game_session.score
                    stats.total_time_played += game_session.time_played
                    
                    if game_session.score > stats.highest_score:
                        stats.highest_score = game_session.score
                    
                    # Update win streak
                    stats.current_win_streak += 1
                    if stats.current_win_streak > stats.best_win_streak:
                        stats.best_win_streak = stats.current_win_streak
                    
                    # Check for fastest win
                    if not stats.fastest_win or game_session.time_played < stats.fastest_win:
                        stats.fastest_win = game_session.time_played
                    
                    # Check for fewest moves win
                    if not stats.fewest_moves_win or game_session.moves_count < stats.fewest_moves_win:
                        stats.fewest_moves_win = game_session.moves_count
                    
                    stats.save()
                    
                elif is_completed:
                    game_session.is_completed = True
                    game_session.ended_at = timezone.now()
                    
                    # Update statistics for loss
                    stats, created = SolitaireStatistics.objects.get_or_create(user=request.user)
                    stats.games_played += 1
                    stats.current_win_streak = 0  # Reset streak on loss
                    stats.save()
                    
                game_session.save()
                
                result['success'] = True
                result['message'] = f"Game saved successfully - moves: {session.moves_count}, score: {session.score}"
                logger.info(f"✓ Game saved - Session: {session_id[:8]}, Moves: {session.moves_count}, Score: {session.score}, Won: {is_won}")
            
        elif action == 'new_game':
            # Get player for tracking
            player, _ = SolitairePlayer.objects.get_or_create(
                user=request.user,
                defaults={
                    'session_key': request.session.session_key or str(uuid.uuid4()),
                    'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'display_name': request.user.username,
                    'is_anonymous': False
                }
            )
            
            # Mark ALL incomplete game sessions as abandoned to prevent multiple in-progress games
            incomplete_sessions = SolitaireGameSession.objects.filter(
                player=player,
                is_completed=False
            )
            
            for game_sess in incomplete_sessions:
                if not game_sess.is_won and not game_sess.is_abandoned:
                    game_sess.is_abandoned = True
                    game_sess.is_completed = True
                    game_sess.ended_at = timezone.now()
                    game_sess.save()
                    logger.info(f"Marked game session {game_sess.session_id[:8]} as abandoned due to new game")
            
            # Deactivate ALL existing active sessions for this user
            existing_sessions = SolitaireSession.objects.filter(
                user=request.user,
                is_active=True
            )
            for s in existing_sessions:
                if not s.is_won:
                    s.is_abandoned = True
                s.is_active = False
                s.save()
                logger.info(f"Deactivated session {s.session_id[:8]}")
            
            # Create new game
            game = SolitaireGame()
            game.new_game()
            new_game_state = game.to_dict()
            
            # Verify game state
            stock_count = len(new_game_state.get('stock', []))
            tableau_counts = [len(pile) for pile in new_game_state.get('tableau', [])]
            logger.info(f"New game created - Stock: {stock_count}, Tableau: {tableau_counts}")
            
            # Create new session
            new_session = SolitaireSession.objects.create(
                user=request.user,
                session_id=str(uuid.uuid4()),
                is_active=True
            )
            new_session.save_game_state(new_game_state)
            new_session.save()
            
            # Create corresponding SolitaireGameSession for tracking
            new_game_session = SolitaireGameSession.objects.create(
                player=player,
                session_id=new_session.session_id,
                game_state=new_game_state,
                moves_count=0,
                score=0,
                time_played=0,
                is_completed=False,
                is_won=False,
                is_abandoned=False
            )
            
            result['success'] = True
            result['session_id'] = new_session.session_id
            result['game_state'] = new_game_state
            
            logger.info(f"New game session created: {new_session.session_id[:8]}")
            
        elif action == 'undo':
            result['success'] = game.undo()
            if result['success']:
                session.save_game_state(game.to_dict())
                session.save()
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def solitaire_stats(request):
    """View for solitaire statistics"""
    # TODO: Implement stats view
    return JsonResponse({'stats': 'not implemented'})