"""
Receipt Processing Views with Gamification
Modern UI with step-by-step workflow and real-time processing
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import json
import base64
import uuid
import logging
from decimal import Decimal
from typing import Dict, List, Optional

from core.system.web_ui.backend.views import BaseUIView

from .models import Document, ParsedReceipt, ReceiptItem
from .gamification_models import (
    UserProfile, Achievement, PointTransaction, Challenge, 
    UserChallenge, Leaderboard, ValidationFeedback, LearningModel,
    POINT_REWARDS, ACHIEVEMENT_DEFINITIONS
)
from .ocr_service import OCRProcessor
from .ollama_service import OllamaService, IntelligentAgent

logger = logging.getLogger('documents.receipt_processing')


class ReceiptProcessingView:
    """Main view class for receipt processing with gamification"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.ollama_service = OllamaService()
        self.intelligent_agent = IntelligentAgent(self.ollama_service)


def receipt_dashboard(request):
    """Main dashboard for receipt processing with gamification"""
    
    # Get base context from BaseUIView
    from core.system.web_ui.backend.views import BaseUIView
    base_view = BaseUIView()
    base_view.request = request  # Set request attribute
    base_context = base_view.get_context_data()
    
    # In emergency mode, use admin user if not authenticated
    if not request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            request.user = User.objects.get(username='admin')
        except User.DoesNotExist:
            # Create a dummy user if admin doesn't exist
            request.user = User.objects.create_user(username='guest', password='guest123')
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if created:
        # First time user - show tutorial
        profile.tutorial_completed = False
        profile.save()
    
    # Update streak
    profile.update_streak()
    
    # Get user stats
    stats = {
        'total_points': profile.total_points,
        'current_level': profile.current_level,
        'experience_points': profile.experience_points,
        'next_level_points': profile.get_next_level_requirement(),
        'receipts_processed': profile.receipts_processed,
        'accuracy_score': profile.accuracy_score,
        'streak_days': profile.streak_days,
        'level_progress': (profile.experience_points / profile.get_next_level_requirement()) * 100
    }
    
    # Get recent achievements
    recent_achievements = Achievement.objects.filter(
        user=request.user
    ).order_by('-unlocked_at')[:5]
    
    # Get active challenges
    active_challenges = UserChallenge.objects.filter(
        user=request.user,
        completed=False,
        challenge__is_active=True,
        challenge__end_date__gte=timezone.now()
    ).select_related('challenge')[:3]
    
    # Get leaderboard
    weekly_leaders = UserProfile.objects.filter(
        last_activity_date__gte=timezone.now().date() - timedelta(days=7)
    ).order_by('-total_points')[:10]
    
    # Get recent receipts
    recent_receipts = Document.objects.filter(
        user=request.user,
        document_type='receipt',
        is_deleted=False
    ).order_by('-uploaded_at')[:5]
    
    # Calculate daily progress and check for bonuses
    today = timezone.now().date()
    today_points = PointTransaction.objects.filter(
        user=request.user,
        created_at__date=today
    ).aggregate(total=Sum('points'))['total'] or 0
    
    # Check daily bonus (10 receipts)
    today_receipts = Document.objects.filter(
        user=request.user,
        document_type='receipt',
        uploaded_at__date=today
    ).count()
    
    if today_receipts == 10 and not PointTransaction.objects.filter(
        user=request.user,
        reason__contains='Daily bonus',
        created_at__date=today
    ).exists():
        profile.add_points(POINT_REWARDS['daily_bonus_10'], '🥕 Daily bonus: 10 receipts!')
        messages.success(request, '🥕 You earned 50 bonus carrots for processing 10 receipts today!')
    
    # Check weekly bonus (50 receipts)
    week_start = today - timedelta(days=today.weekday())
    week_receipts = Document.objects.filter(
        user=request.user,
        document_type='receipt',
        uploaded_at__date__gte=week_start
    ).count()
    
    if week_receipts >= 50 and not PointTransaction.objects.filter(
        user=request.user,
        reason__contains='Weekly bonus',
        created_at__date__gte=week_start
    ).exists():
        profile.add_points(POINT_REWARDS['weekly_bonus_50'], '🥕 Weekly bonus: 50 receipts!')
        messages.success(request, '🥕 Amazing! You earned 200 bonus carrots for 50 receipts this week!')
    
    # Check monthly bonus (100 receipts)
    month_start = today.replace(day=1)
    month_receipts = Document.objects.filter(
        user=request.user,
        document_type='receipt',
        uploaded_at__date__gte=month_start
    ).count()
    
    if month_receipts >= 100 and not PointTransaction.objects.filter(
        user=request.user,
        reason__contains='Monthly bonus',
        created_at__date__gte=month_start
    ).exists():
        profile.add_points(POINT_REWARDS['monthly_bonus_100'], '🥕 Monthly bonus: 100 receipts!')
        messages.success(request, '🥕 Incredible! You earned 500 bonus carrots for 100 receipts this month!')
    
    # Merge with base context to include modules and tools for sidebar
    context = {
        **base_context,  # Include modules, tools, etc. for sidebar
        'profile': profile,
        'stats': stats,
        'recent_achievements': recent_achievements,
        'active_challenges': active_challenges,
        'weekly_leaders': weekly_leaders,
        'recent_receipts': recent_receipts,
        'today_points': today_points,
        'today_receipts': today_receipts,
        'week_receipts': week_receipts,
        'month_receipts': month_receipts,
        'show_tutorial': not profile.tutorial_completed,
        'page_title': 'Receipt Hub - Earn Carrots 🥕',
        'current_module': 'documents'  # Highlight documents module in sidebar
    }
    
    return render(request, 'documents/receipt_dashboard.html', context)


def upload_receipt(request):
    """Step-by-step receipt upload workflow"""
    
    if request.method == 'POST':
        try:
            # Get uploaded file
            receipt_file = request.FILES.get('receipt')
            if not receipt_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            # Create document instance
            document = Document.objects.create(
                user=request.user,
                document_type='receipt',
                original_filename=receipt_file.name,
                file_path=receipt_file,
                processing_status='processing'
            )
            
            # Award carrots for upload
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            profile.add_points(POINT_REWARDS['receipt_upload'], '🥕 Receipt uploaded')
            
            # Start OCR processing
            ocr_result = process_receipt_ocr(document)
            
            if ocr_result['success']:
                # Award carrots for successful OCR
                profile.add_points(POINT_REWARDS['receipt_ocr_complete'], '🥕 OCR completed')
                
                # Check if complete extraction was successful
                parsed_data = ocr_result.get('parsed_data', {})
                if parsed_data.get('store_name') and parsed_data.get('total_amount'):
                    profile.add_points(POINT_REWARDS['complete_extraction'], '🥕 Complete data extraction')
                
                profile.receipts_processed += 1
                profile.save()
                
                # Update challenges
                update_user_challenges(request.user, 'receipts_processed')
                
                # Return processing result
                return JsonResponse({
                    'success': True,
                    'document_id': str(document.id),
                    'ocr_text': ocr_result.get('ocr_text', ''),
                    'parsed_data': ocr_result.get('parsed_data', {}),
                    'confidence': ocr_result.get('confidence', 0),
                    'carrots_earned': POINT_REWARDS['receipt_upload'] + POINT_REWARDS['receipt_ocr_complete'],
                    'message': 'Receipt uploaded successfully! Earn more carrots by validating the data.',
                    'redirect_url': f'/documents/receipt/validate/{document.id}/'
                })
            else:
                document.processing_status = 'failed'
                document.save()
                
                return JsonResponse({
                    'success': False,
                    'error': ocr_result.get('error', 'OCR processing failed'),
                    'document_id': str(document.id),
                    'redirect_url': f'/documents/receipt/manual/{document.id}/'
                })
                
        except Exception as e:
            logger.error(f"Receipt upload error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show upload form
    context = {
        'page_title': 'Upload Receipt',
        'step': 1,
        'total_steps': 4
    }
    
    return render(request, 'documents/receipt_upload.html', context)


def validate_receipt(request, document_id):
    """Interactive receipt validation with gamification"""
    
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if request.method == 'POST':
        try:
            corrections = json.loads(request.body)
            
            # Process corrections
            validation_results = process_receipt_corrections(document, corrections, request.user)
            
            # Award carrots based on detailed validation actions
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            carrots_earned = 0
            detailed_rewards = []
            
            for field, correction in corrections.items():
                if correction.get('corrected'):
                    # User corrected an error
                    if field == 'store_name':
                        carrots = POINT_REWARDS['error_correction']
                        detailed_rewards.append(('🥕 Store name correction', carrots))
                    elif field == 'date':
                        carrots = POINT_REWARDS['error_correction']
                        detailed_rewards.append(('🥕 Date correction', carrots))
                    elif field == 'total_amount':
                        carrots = POINT_REWARDS['error_correction']
                        detailed_rewards.append(('🥕 Total amount correction', carrots))
                    elif 'product' in field.lower():
                        carrots = POINT_REWARDS['error_correction']
                        detailed_rewards.append(('🥕 Product correction', carrots))
                    else:
                        carrots = POINT_REWARDS['field_correction']
                        detailed_rewards.append(('🥕 Field correction', carrots))
                    carrots_earned += carrots
                    
                elif correction.get('added'):
                    # User added missing information
                    carrots = POINT_REWARDS['missing_info_addition']
                    detailed_rewards.append(('🥕 Missing info added', carrots))
                    carrots_earned += carrots
                    
                else:
                    # User validated existing data
                    if field == 'store_name':
                        carrots = POINT_REWARDS['store_name_validation']
                        detailed_rewards.append(('🥕 Store name validation', carrots))
                    elif field == 'date':
                        carrots = POINT_REWARDS['date_validation']
                        detailed_rewards.append(('🥕 Date validation', carrots))
                    elif field == 'total_amount':
                        carrots = POINT_REWARDS['total_amount_validation']
                        detailed_rewards.append(('🥕 Total amount validation', carrots))
                    elif 'product' in field.lower():
                        carrots = POINT_REWARDS['product_validation']
                        detailed_rewards.append(('🥕 Product validation', carrots))
                    else:
                        carrots = POINT_REWARDS['field_validation']
                        detailed_rewards.append(('🥕 Field validation', carrots))
                    carrots_earned += carrots
            
            # Add all carrots with detailed description
            for description, carrots in detailed_rewards:
                profile.add_points(carrots, description)
            profile.receipts_validated += 1
            
            # Update accuracy score
            if validation_results.get('accuracy'):
                profile.accuracy_score = (profile.accuracy_score * 0.9 + validation_results['accuracy'] * 0.1)
            
            profile.save()
            
            # Check for achievements
            check_achievements(request.user, 'validation', validation_results)
            
            # Check for streak bonuses
            if validation_results.get('accuracy', 0) == 100:
                # Perfect receipt!
                profile.add_points(POINT_REWARDS['perfect_receipt'], '🥕 Perfect receipt bonus!')
                carrots_earned += POINT_REWARDS['perfect_receipt']
                
                # Check for streak
                profile.perfect_streak = getattr(profile, 'perfect_streak', 0) + 1
                if profile.perfect_streak == 5:
                    profile.add_points(POINT_REWARDS['streak_5'], '🥕 5 perfect receipts streak!')
                    carrots_earned += POINT_REWARDS['streak_5']
                elif profile.perfect_streak == 10:
                    profile.add_points(POINT_REWARDS['streak_10'], '🥕 10 perfect receipts streak!')
                    carrots_earned += POINT_REWARDS['streak_10']
            else:
                # Reset streak if not perfect
                profile.perfect_streak = 0
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'carrots_earned': carrots_earned,
                'detailed_rewards': detailed_rewards,
                'accuracy': validation_results.get('accuracy', 0),
                'is_perfect': validation_results.get('accuracy', 0) == 100,
                'redirect_url': f'/documents/receipt/complete/{document.id}/'
            })
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show validation interface
    parsed_receipt = None
    if hasattr(document, 'parsed_receipt'):
        parsed_receipt = document.parsed_receipt
    
    # Get Ollama analysis if available
    ollama_analysis = {}
    if document.ocr_text and len(document.ocr_text) > 50:
        try:
            processor = ReceiptProcessingView()
            ollama_analysis = processor.intelligent_agent.extract_fields(
                document.ocr_text, 
                'receipt'
            )
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
    
    context = {
        'document': document,
        'parsed_receipt': parsed_receipt,
        'ollama_analysis': ollama_analysis,
        'page_title': 'Validate Receipt',
        'step': 2,
        'total_steps': 4,
        'carrot_rewards': {
            'store_validation': POINT_REWARDS['store_name_validation'],
            'date_validation': POINT_REWARDS['date_validation'],
            'amount_validation': POINT_REWARDS['total_amount_validation'],
            'product_validation': POINT_REWARDS['product_validation'],
            'error_correction': POINT_REWARDS['error_correction'],
            'missing_info': POINT_REWARDS['missing_info_addition'],
            'perfect_bonus': POINT_REWARDS['perfect_receipt']
        }
    }
    
    return render(request, 'documents/receipt_validate.html', context)


def complete_receipt(request, document_id):
    """Receipt processing completion with rewards"""
    
    document = get_object_or_404(Document, id=document_id, user=request.user)
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    # Calculate total points earned
    points_breakdown = PointTransaction.objects.filter(
        user=request.user,
        related_document_id=document.id
    ).aggregate(total=Sum('points'))
    
    total_points = points_breakdown['total'] or 0
    
    # Check for perfect receipt achievement
    if document.ocr_confidence and document.ocr_confidence > 95:
        Achievement.objects.get_or_create(
            user=request.user,
            achievement_type='special',
            name='Perfect Receipt',
            defaults={
                'description': 'Processed a receipt with 95%+ accuracy',
                'points_awarded': POINT_REWARDS['perfect_receipt'],
                'icon': 'star',
                'rarity': 'epic'
            }
        )
        profile.add_points(POINT_REWARDS['perfect_receipt'], 'Perfect receipt bonus')
    
    # Get cross-module integrations
    integrations = get_cross_module_integrations(document)
    
    context = {
        'document': document,
        'total_points': total_points,
        'profile': profile,
        'integrations': integrations,
        'page_title': 'Receipt Complete',
        'step': 4,
        'total_steps': 4
    }
    
    return render(request, 'documents/receipt_complete.html', context)


def leaderboard(request):
    """Display gamification leaderboard"""
    
    # Get base context from BaseUIView for sidebar
    from core.system.web_ui.backend.views import BaseUIView
    base_view = BaseUIView()
    base_view.request = request
    base_context = base_view.get_context_data()
    
    # Handle guest user - use berkhatirli for now since all docs belong to them
    if not request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            # Try berkhatirli first since documents belong to this user
            request.user = User.objects.get(username='berkhatirli')
        except User.DoesNotExist:
            try:
                request.user = User.objects.get(username='admin')
            except User.DoesNotExist:
                request.user = User.objects.create_user(username='guest', password='guest123')
    
    period = request.GET.get('period', 'weekly')
    
    # Get leaderboard data
    if period == 'daily':
        start_date = timezone.now().date()
        leaders = Leaderboard.objects.filter(
            period_type='daily',
            period_start=start_date
        ).order_by('rank')[:50]
    elif period == 'monthly':
        start_date = timezone.now().date().replace(day=1)
        leaders = Leaderboard.objects.filter(
            period_type='monthly',
            period_start=start_date
        ).order_by('rank')[:50]
    else:  # weekly
        start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())
        leaders = Leaderboard.objects.filter(
            period_type='weekly',
            period_start=start_date
        ).order_by('rank')[:50]
    
    # Get user's rank
    user_rank = None
    try:
        user_entry = Leaderboard.objects.get(
            user=request.user,
            period_type=period.lower(),
            period_start=start_date
        )
        user_rank = user_entry.rank
    except Leaderboard.DoesNotExist:
        pass
    
    context = {
        **base_context,  # Include sidebar data
        'leaders': leaders,
        'period': period,
        'user_rank': user_rank,
        'page_title': f'{period.title()} leaderboard',
        'current_module': 'documents'
    }
    
    return render(request, 'documents/leaderboard.html', context)


def achievements(request):
    """Display user achievements and badges"""
    
    # Get base context from BaseUIView for sidebar
    from core.system.web_ui.backend.views import BaseUIView
    base_view = BaseUIView()
    base_view.request = request
    base_context = base_view.get_context_data()
    
    # Handle guest user - use berkhatirli for now since all docs belong to them
    if not request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            # Try berkhatirli first since documents belong to this user
            request.user = User.objects.get(username='berkhatirli')
        except User.DoesNotExist:
            try:
                request.user = User.objects.get(username='admin')
            except User.DoesNotExist:
                request.user = User.objects.create_user(username='guest', password='guest123')
    
    # Get all user achievements
    user_achievements = Achievement.objects.filter(
        user=request.user
    ).order_by('-unlocked_at')
    
    # Get all possible achievements
    all_achievements = []
    for key, definition in ACHIEVEMENT_DEFINITIONS.items():
        achieved = user_achievements.filter(name=definition['name']).first()
        all_achievements.append({
            'name': definition['name'],
            'description': definition['description'],
            'points': definition['points'],
            'icon': definition['icon'],
            'rarity': definition['rarity'],
            'achieved': achieved is not None,
            'unlocked_at': achieved.unlocked_at if achieved else None
        })
    
    # Sort by achieved status and rarity
    rarity_order = {'common': 0, 'rare': 1, 'epic': 2, 'legendary': 3}
    all_achievements.sort(
        key=lambda x: (not x['achieved'], -rarity_order.get(x['rarity'], 0))
    )
    
    context = {
        **base_context,  # Include sidebar data
        'achievements': all_achievements,
        'unlocked_count': len(user_achievements),
        'total_achievements': len(ACHIEVEMENT_DEFINITIONS),
        'completion_percentage': (len(user_achievements) / len(ACHIEVEMENT_DEFINITIONS)) * 100 if ACHIEVEMENT_DEFINITIONS else 0,
        'page_title': 'achievements',
        'current_module': 'documents'
    }
    
    return render(request, 'documents/achievements.html', context)


def challenges(request):
    """Display and manage user challenges"""
    
    # Get base context from BaseUIView for sidebar
    from core.system.web_ui.backend.views import BaseUIView
    base_view = BaseUIView()
    base_view.request = request
    base_context = base_view.get_context_data()
    
    # Handle guest user - use berkhatirli for now since all docs belong to them
    if not request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            # Try berkhatirli first since documents belong to this user
            request.user = User.objects.get(username='berkhatirli')
        except User.DoesNotExist:
            try:
                request.user = User.objects.get(username='admin')
            except User.DoesNotExist:
                request.user = User.objects.create_user(username='guest', password='guest123')
    
    # Get active challenges
    active_challenges = Challenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('end_date')
    
    # Get user's challenge progress
    user_challenges = UserChallenge.objects.filter(
        user=request.user
    ).select_related('challenge')
    
    # Create challenge status list
    challenge_list = []
    for challenge in active_challenges:
        user_challenge = user_challenges.filter(challenge=challenge).first()
        
        if user_challenge:
            progress = (user_challenge.current_progress / challenge.target_count) * 100
            status = 'completed' if user_challenge.completed else 'in_progress'
        else:
            progress = 0
            status = 'not_started'
        
        challenge_list.append({
            'challenge': challenge,
            'user_challenge': user_challenge,
            'progress': min(progress, 100),
            'status': status,
            'time_remaining': (challenge.end_date - timezone.now()).days
        })
    
    context = {
        **base_context,  # Include sidebar data
        'challenges': challenge_list,
        'completed_today': user_challenges.filter(
            completed=True,
            completed_at__date=timezone.now().date()
        ).count(),
        'active_challenges': challenge_list,
        'page_title': 'challenges',
        'current_module': 'documents'
    }
    
    return render(request, 'documents/challenges.html', context)


@csrf_exempt
def rescan_ocr(request, document_id):
    """Rescan OCR for a document with detailed logging"""
    if request.method == 'POST':
        try:
            import time
            start_time = time.time()
            
            document = Document.objects.get(id=document_id)
            logger.info(f"Starting OCR rescan for document {document_id}")
            
            # Store old text info
            old_text_length = len(document.ocr_text) if document.ocr_text else 0
            old_confidence = document.ocr_confidence or 0
            
            # Use OCR processor to rescan
            from modules.documents.backend.ocr_service import OCRProcessor
            ocr_processor = OCRProcessor()
            
            if document.file_path:
                logger.info(f"Processing file: {document.file_path.name}")
                
                # Try gentle enhancement first
                result = ocr_processor.process_document(
                    document.file_path.path,
                    document_type='receipt',
                    force_ocr=True,  # Force rescan
                    force_enhance=True  # Apply gentle enhancement preprocessing
                )
                
                # If result is worse, try without enhancement
                if result.get('success') and len(result.get('ocr_text', '')) < old_text_length * 0.8:
                    logger.info("Enhanced OCR produced less text, trying without enhancement...")
                    result = ocr_processor.process_document(
                        document.file_path.path,
                        document_type='receipt',
                        force_ocr=True,
                        force_enhance=False  # No enhancement
                    )
                
                processing_time = time.time() - start_time
                
                if result['success']:
                    document.ocr_text = result.get('ocr_text', '')
                    document.ocr_confidence = result.get('confidence', 0)
                    document.ocr_processed_at = timezone.now()
                    document.save()
                    
                    logger.info(f"OCR rescan successful: {len(document.ocr_text)} chars, {document.ocr_confidence}% confidence, {processing_time:.2f}s")
                    
                    return JsonResponse({
                        'success': True,
                        'ocr_text': document.ocr_text,
                        'confidence': document.ocr_confidence,
                        'old_length': old_text_length,
                        'new_length': len(document.ocr_text),
                        'old_confidence': old_confidence,
                        'method': result.get('ocr_method', 'tesseract'),
                        'processing_time': f"{processing_time:.2f}s",
                        'improvement': len(document.ocr_text) - old_text_length
                    })
                else:
                    error_msg = result.get('error', 'OCR processing failed')
                    logger.error(f"OCR rescan failed: {error_msg}")
                    
                    return JsonResponse({
                        'success': False,
                        'error': error_msg,
                        'details': result.get('details', {}),
                        'processing_time': f"{processing_time:.2f}s"
                    })
            
            return JsonResponse({'success': False, 'error': 'No file available for OCR'})
            
        except Document.DoesNotExist:
            logger.error(f"Document {document_id} not found")
            return JsonResponse({'success': False, 'error': 'Document not found'}, status=404)
        except Exception as e:
            logger.error(f"OCR rescan error: {e}", exc_info=True)
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'error_type': type(e).__name__
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_ocr(request, document_id):
    """Update OCR text for a document"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ocr_text = data.get('ocr_text', '')
            
            document = Document.objects.get(id=document_id)
            document.ocr_text = ocr_text
            document.save()
            
            return JsonResponse({'success': True})
            
        except Document.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Document not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def ai_extract_fields(request):
    """Extract fields from OCR text using Ollama/Llama with detailed logging and OSM enrichment"""
    if request.method == 'POST':
        try:
            import time
            start_time = time.time()
            
            data = json.loads(request.body)
            ocr_text = data.get('ocr_text', '')
            receipt_id = data.get('receipt_id')
            
            logger.info(f"AI extraction started for receipt {receipt_id}, OCR length: {len(ocr_text)}")
            
            if not ocr_text or len(ocr_text) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'OCR text too short or empty',
                    'ocr_length': len(ocr_text)
                }, status=400)
            
            # Try to use Ollama for extraction
            ollama_error = None
            ai_fields = None
            
            try:
                import requests
                
                logger.info("Attempting Ollama/Llama extraction...")
                
                # Prepare prompt for Llama
                prompt = f"""Aşağıdaki fiş metninden bu alanları çıkar ve JSON formatında döndür:
                - store_name: Mağaza adı
                - date: Tarih (YYYY-MM-DD formatında)
                - time: Saat (HH:MM formatında)
                - receipt_number: Fiş numarası
                - total_amount: Toplam tutar (sadece sayı)
                - subtotal: Ara toplam (sadece sayı)
                - tax_amount: KDV tutarı (sadece sayı)
                - payment_method: Ödeme yöntemi (cash/card)
                - card_last_four: Kart son 4 hanesi
                - store_address: Mağaza adresi
                - store_phone: Mağaza telefonu
                - cashier: Kasiyer adı
                - pos_terminal: POS terminal numarası
                - item_count: Ürün sayısı
                
                Fiş metni:
                {ocr_text[:1500]}...
                
                Sadece JSON döndür, başka bir şey yazma."""
                
                # Call Ollama API
                response = requests.post('http://localhost:11434/api/generate', 
                    json={
                        'model': 'llama3.2',
                        'prompt': prompt,
                        'stream': False,
                        'format': 'json'
                    },
                    timeout=30
                )
                
                logger.info(f"Ollama response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    llm_response = result.get('response', '{}')
                    
                    # Try to parse JSON from response
                    import re
                    json_match = re.search(r'\{[^}]+\}', llm_response)
                    if json_match:
                        fields = json.loads(json_match.group())
                    else:
                        fields = json.loads(llm_response)
                    
                    # Clean up fields
                    cleaned_fields = {}
                    for key, value in fields.items():
                        if value and value != 'null' and value != 'None':
                            cleaned_fields[key] = value
                    
                    if cleaned_fields:
                        processing_time = time.time() - start_time
                        logger.info(f"AI extracted {len(cleaned_fields)} fields in {processing_time:.2f}s")
                        
                        return JsonResponse({
                            'success': True,
                            'fields': cleaned_fields,
                            'method': 'ollama_llama3.2',
                            'field_count': len(cleaned_fields),
                            'processing_time': f"{processing_time:.2f}s",
                            'model_info': {
                                'model': 'llama3.2',
                                'response_time': result.get('total_duration', 0) / 1e9 if 'total_duration' in result else 'N/A'
                            }
                        })
                    else:
                        ollama_error = "AI returned empty fields"
                else:
                    ollama_error = f"Ollama returned status {response.status_code}"
                    logger.error(ollama_error)
                    
            except requests.exceptions.ConnectionError as e:
                ollama_error = "Cannot connect to Ollama (is it running? Try: ollama serve)"
                logger.warning(f"Ollama connection error: {e}")
            except requests.exceptions.Timeout:
                ollama_error = "Ollama request timed out after 30 seconds"
                logger.warning(ollama_error)
            except Exception as e:
                ollama_error = f"Ollama error: {str(e)}"
                logger.warning(f"Ollama extraction failed: {e}")
            
            # Fallback to pattern matching
            logger.info("Falling back to pattern matching...")
            import re
            
            patterns = {
                'store_name': r'^([A-ZÇĞİÖŞÜ\s]+)',
                'date': r'(\d{2}[./-]\d{2}[./-]\d{4})',
                'time': r'(\d{2}:\d{2})',
                'receipt_number': r'FİŞ\s*NO\s*:\s*(\d+)',
                'total_amount': r'TOPLAM\s*:?\s*([\d,]+\.?\d*)',
                'subtotal': r'ARA\s*TOPLAM\s*:?\s*([\d,]+\.?\d*)',
                'tax_amount': r'KDV\s*%?\d*\s*:?\s*([\d,]+\.?\d*)',
                'payment_method': r'(NAKİT|KREDİ KARTI|KREDI)',
                'store_address': r'(?:ADRES|ADR)[:\s]*([^\n]+)',
                'store_phone': r'(?:TEL|TELEFON)[:\s]*([\d\s-]+)',
                'cashier': r'(?:KASİYER|KASIYER)[:\s]*(\w+)',
                'pos_terminal': r'(?:TERMINAL|TERMİNAL)[:\s]*(\w+)',
                'card_last_four': r'KART\s*NO\s*:?\s*[X*]+(\d{4})'
            }
            
            extracted_fields = {}
            pattern_matches = []
            
            for field, pattern in patterns.items():
                match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean monetary values
                    if field in ['total_amount', 'subtotal', 'tax_amount']:
                        value = value.replace(',', '.')
                        # Extract just the number
                        num_match = re.search(r'[\d.]+', value)
                        if num_match:
                            value = num_match.group()
                    # Convert date format
                    elif field == 'date' and '.' in value:
                        parts = value.split('.')
                        if len(parts) == 3:
                            value = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                    # Normalize payment method
                    elif field == 'payment_method':
                        if 'NAKİT' in value.upper():
                            value = 'cash'
                        else:
                            value = 'card'
                    
                    extracted_fields[field] = value
                    pattern_matches.append(field)
            
            processing_time = time.time() - start_time
            logger.info(f"Pattern matching found {len(extracted_fields)} fields: {pattern_matches}")
            
            # Try to enrich with OpenStreetMap data
            osm_data = {}
            if extracted_fields.get('store_name'):
                from core.osm_service import osm_service
                
                # Use the new OSM service
                location_hint = extracted_fields.get('store_address', '')
                osm_result = osm_service.search_business(
                    name=extracted_fields['store_name'],
                    location_hint=location_hint
                )
                
                if osm_result:
                    osm_data = osm_result
                    logger.info(f"OSM enrichment found: {osm_data.get('display_name', '')}")
                    
                    # Merge OSM data with extracted fields
                    if osm_data.get('phone') and not extracted_fields.get('store_phone'):
                        extracted_fields['store_phone'] = osm_data['phone']
                    if osm_data.get('formatted_address') and not extracted_fields.get('store_address'):
                        extracted_fields['store_address'] = osm_data['formatted_address']
                    if osm_data.get('website'):
                        extracted_fields['store_website'] = osm_data['website']
                    if osm_data.get('opening_hours'):
                        extracted_fields['store_hours'] = osm_data['opening_hours']
                    if osm_data.get('payment_methods'):
                        extracted_fields['payment_methods'] = ', '.join(osm_data['payment_methods'])
            
            if extracted_fields:
                return JsonResponse({
                    'success': True,
                    'fields': extracted_fields,
                    'method': 'pattern_matching',
                    'fallback': True,
                    'field_count': len(extracted_fields),
                    'matched_fields': pattern_matches,
                    'ollama_error': ollama_error,
                    'osm_enrichment': osm_data,
                    'processing_time': f"{processing_time:.2f}s"
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No fields could be extracted from OCR text',
                    'method': 'none',
                    'ollama_error': ollama_error,
                    'ocr_sample': ocr_text[:200] if ocr_text else 'Empty',
                    'processing_time': f"{processing_time:.2f}s"
                }, status=404)
                
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def search_nearby_business(request):
    """Search for nearby businesses using OpenStreetMap"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            store_name = data.get('store_name', '')
            location_hint = data.get('location_hint', '')
            
            if not store_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Store name is required'
                }, status=400)
            
            logger.info(f"🔍 Searching nearby businesses for: {store_name}")
            
            # Use enhanced OSM service with fallbacks
            from core.osm_service_enhanced import EnhancedOSMService, KNOWN_CHAINS
            osm_service = EnhancedOSMService()
            
            # Check if it's a known chain first
            store_upper = store_name.upper()
            if store_upper in KNOWN_CHAINS:
                logger.info(f"✅ Found in known chains database: {store_upper}")
                chain_info = KNOWN_CHAINS[store_upper]
                # Create a synthetic result
                businesses = [{
                    'display_name': f"{store_name} - {location_hint or 'Turkey'}",
                    'brand': chain_info.get('brand'),
                    'type': chain_info.get('type'),
                    'amenity': chain_info.get('amenity'),
                    'website': chain_info.get('website'),
                    'note': chain_info.get('note', 'Known Turkish business chain'),
                    'source': 'known_chains'
                }]
            
            # Try multi-strategy search
            result = osm_service.search_business_multi_strategy(
                name=store_name,
                location_hint=location_hint,
                country='tr'
            )
            
            if result:
                businesses.append({
                    'name': result.get('display_name', store_name).split(',')[0],
                    'formatted_address': result.get('formatted_address', ''),
                    'address': result.get('address', {}),
                    'phone': result.get('phone', ''),
                    'website': result.get('website', ''),
                    'lat': result.get('lat', 0),
                    'lon': result.get('lon', 0),
                    'distance': 0,  # Exact match
                    'osm_id': result.get('osm_id'),
                    'confidence': 1.0
                })
            
            # If we have coordinates, search for nearby similar businesses
            if result and result.get('lat') and result.get('lon'):
                nearby = osm_service.find_nearby(
                    lat=result['lat'],
                    lon=result['lon'],
                    amenity='restaurant',  # Generic search
                    radius=2000  # 2km radius
                )
                
                for place in nearby[:9]:  # Limit to 9 more (total 10)
                    if place.get('display_name', '').lower() != result.get('display_name', '').lower():
                        businesses.append({
                            'name': place.get('display_name', '').split(',')[0],
                            'formatted_address': place.get('display_name', ''),
                            'phone': place.get('extratags', {}).get('phone', ''),
                            'website': place.get('extratags', {}).get('website', ''),
                            'lat': float(place.get('lat', 0)),
                            'lon': float(place.get('lon', 0)),
                            'distance': place.get('distance', 0),
                            'osm_id': place.get('osm_id'),
                            'confidence': 0.5
                        })
            else:
                # No exact match found, try fuzzy search
                # Search with variations
                variations = [
                    store_name,
                    store_name.lower(),
                    store_name.upper(),
                    store_name.replace('İ', 'I'),
                    store_name.replace('I', 'İ'),
                ]
                
                for variant in variations[:3]:
                    result = osm_service.search_business(
                        name=variant,
                        location_hint=location_hint,
                        country='tr'
                    )
                    if result:
                        businesses.append({
                            'name': result.get('display_name', store_name).split(',')[0],
                            'formatted_address': result.get('formatted_address', ''),
                            'address': result.get('address', {}),
                            'phone': result.get('phone', ''),
                            'website': result.get('website', ''),
                            'lat': result.get('lat', 0),
                            'lon': result.get('lon', 0),
                            'distance': 0,
                            'osm_id': result.get('osm_id'),
                            'confidence': 0.7
                        })
                        break
            
            if businesses:
                logger.info(f"✅ Found {len(businesses)} businesses")
                return JsonResponse({
                    'success': True,
                    'businesses': businesses,
                    'count': len(businesses)
                })
            else:
                logger.warning(f"No businesses found for: {store_name}")
                return JsonResponse({
                    'success': False,
                    'businesses': [],
                    'message': 'No businesses found. Try a different search term.'
                })
                
        except Exception as e:
            logger.error(f"Business search error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def document_validation(request):
    """Document validation with type detection and sharing capabilities"""
    
    # Get base context from BaseUIView for sidebar
    from core.system.web_ui.backend.views import BaseUIView
    from .document_models import DocumentType, DocumentShare, DEFAULT_DOCUMENT_TYPES
    
    base_view = BaseUIView()
    base_view.request = request
    base_context = base_view.get_context_data()
    
    # Initialize document types if not exists
    if DocumentType.objects.count() == 0:
        for dt_data in DEFAULT_DOCUMENT_TYPES:
            DocumentType.objects.create(**dt_data)
    
    # Handle guest user - use berkhatirli for now since all docs belong to them
    if not request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            # Try berkhatirli first since documents belong to this user
            request.user = User.objects.get(username='berkhatirli')
        except User.DoesNotExist:
            try:
                request.user = User.objects.get(username='admin')
            except User.DoesNotExist:
                request.user = User.objects.create_user(username='guest', password='guest123')
    
    # Get user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        # Get ALL receipts for validation
        # For admin/guest users, show all receipts (don't exclude own)
        # For regular users, exclude their own receipts
        pending_validations_query = Document.objects.filter(
            document_type='receipt',
            is_deleted=False
        ).exclude(
            processing_status='failed'
        )
        
        # Only exclude user's own receipts if they're not admin/guest
        if request.user.username not in ['admin', 'guest', 'berkhatirli']:
            pending_validations_query = pending_validations_query.exclude(user=request.user)
        
        pending_validations = pending_validations_query.select_related('parsed_receipt').order_by('-uploaded_at')[:50]
        
        # Process receipts to add display data
        for receipt in pending_validations:
            # Try to get store name and amount from ParsedReceipt
            if hasattr(receipt, 'parsed_receipt') and receipt.parsed_receipt:
                receipt.store_name = receipt.parsed_receipt.store_name or 'unknown store'
                receipt.total_amount = receipt.parsed_receipt.total_amount or 0
            else:
                receipt.store_name = 'unknown store'
                receipt.total_amount = 0
        
        # Get current receipt to validate - check for receipt_id parameter
        receipt_id = request.GET.get('receipt_id')
        if receipt_id:
            try:
                current_receipt = Document.objects.get(id=receipt_id, document_type='receipt')
            except Document.DoesNotExist:
                current_receipt = pending_validations.first() if pending_validations else None
        else:
            current_receipt = pending_validations.first() if pending_validations else None
        
        # Ensure current receipt has OCR text for display
        if current_receipt:
            if not current_receipt.ocr_text and current_receipt.file_path:
                # Try to extract OCR text if missing
                from modules.documents.backend.ocr_service import OCRProcessor
                try:
                    ocr_processor = OCRProcessor()
                    ocr_result = ocr_processor.process_document(
                        current_receipt.file_path.path,
                        document_type='receipt'
                    )
                    if ocr_result['success']:
                        current_receipt.ocr_text = ocr_result.get('ocr_text', '')
                        current_receipt.ocr_confidence = ocr_result.get('confidence', 0)
                        current_receipt.save()
                except Exception as e:
                    logger.error(f"Failed to extract OCR for receipt {current_receipt.id}: {e}")
        
        # Calculate potential carrots
        potential_carrots = POINT_REWARDS['community_validation']
        if profile.accuracy_score >= 90:
            potential_carrots *= 2  # Expert multiplier
        
        # User stats
        stats = {
            'validations_today': ValidationFeedback.objects.filter(
                user=request.user,
                created_at__date=timezone.now().date()
            ).count(),
            'total_validations': ValidationFeedback.objects.filter(user=request.user).count(),
            'accuracy': int(profile.accuracy_score),
            'carrots_earned_today': PointTransaction.objects.filter(
                user=request.user,
                created_at__date=timezone.now().date(),
                transaction_type='earned'
            ).aggregate(total=Sum('points'))['total'] or 0,
            'rank': UserProfile.objects.filter(total_points__gt=profile.total_points).count() + 1,
            'is_expert': profile.accuracy_score >= 90
        }
        
        context = {
            **base_context,  # Include sidebar data
            'profile': profile,
            'pending_validations': pending_validations,
            'current_receipt': current_receipt,
            'potential_carrots': potential_carrots,
            'stats': stats,
            'page_title': 'document validation',
            'current_module': 'documents',
            'total_pending': len(pending_validations) if pending_validations else 0
        }
        
        return render(request, 'documents/document_validation.html', context)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            feedback_id = data.get('feedback_id')
            vote = data.get('vote')  # 'up' or 'down'
            
            feedback = get_object_or_404(ValidationFeedback, id=feedback_id)
            
            if vote == 'up':
                feedback.votes_up += 1
            else:
                feedback.votes_down += 1
            
            feedback.save()
            
            # Award carrots for community validation
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            profile.add_points(POINT_REWARDS['community_validation'], '🥕 Community validation')
            
            # Check if validation is accurate (matches majority)
            if feedback.votes_up > feedback.votes_down + 3:
                profile.add_points(POINT_REWARDS['accurate_validation'], '🥕 Accurate validation bonus')
                
                # Check for expert validator status
                total_validations = ValidationFeedback.objects.filter(
                    user=request.user,
                    votes_up__gt=F('votes_down') + 3
                ).count()
                
                if total_validations >= 50:
                    # Expert validator - double carrots!
                    bonus_carrots = POINT_REWARDS['community_validation']
                    profile.add_points(bonus_carrots, '🥕 Expert validator x2 bonus')
            
            # Update learning model
            if feedback.votes_up > feedback.votes_down + 5:
                update_learning_model(feedback)
            
            return JsonResponse({
                'success': True,
                'votes_up': feedback.votes_up,
                'votes_down': feedback.votes_down,
                'carrots_earned': POINT_REWARDS['community_validation'],
                'message': '🥕 Thanks for helping the community!'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show items for validation
    pending_validations = ValidationFeedback.objects.filter(
        is_correct__isnull=True
    ).exclude(user=request.user).order_by('?')[:10]
    
    context = {
        'validations': pending_validations,
        'page_title': 'Community Validation'
    }
    
    return render(request, 'documents/document_validation.html', context)


# Helper functions

def process_receipt_ocr(document):
    """Process receipt with OCR and Ollama"""
    try:
        processor = ReceiptProcessingView()
        
        # Run OCR
        ocr_result = processor.ocr_processor.process_document(
            document.file_path.path,
            document_type='receipt',
            document_instance=document
        )
        
        if ocr_result['success']:
            # Update document
            document.ocr_text = ocr_result['ocr_text']
            document.ocr_confidence = ocr_result['confidence']
            document.ocr_processed_at = timezone.now()
            document.processing_status = 'completed'
            
            # Try Ollama enhancement if available
            if processor.ollama_service.available and ocr_result['ocr_text']:
                try:
                    ollama_result = processor.ollama_service.analyze_receipt(
                        ocr_result['ocr_text']
                    )
                    
                    if not ollama_result.get('error'):
                        document.ai_parsed_data = ollama_result
                        document.ai_processed = True
                        document.ai_provider = 'ollama'
                        document.ai_confidence = ollama_result.get('validation', {}).get('confidence', 0)
                        document.ai_processed_at = timezone.now()
                except Exception as e:
                    logger.error(f"Ollama processing failed: {e}")
            
            document.save()
            
            return {
                'success': True,
                'ocr_text': ocr_result['ocr_text'],
                'parsed_data': ocr_result.get('parsed_data', {}),
                'confidence': ocr_result['confidence']
            }
    
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        return {'success': False, 'error': str(e)}


def process_receipt_corrections(document, corrections, user):
    """Process user corrections and update learning models"""
    try:
        # Save corrections as feedback
        for field_name, correction_data in corrections.items():
            ValidationFeedback.objects.create(
                user=user,
                document_id=document.id,
                field_name=field_name,
                original_value=correction_data.get('original', ''),
                corrected_value=correction_data.get('corrected', ''),
                confidence_score=correction_data.get('confidence', 0),
                points_awarded=POINT_REWARDS['field_correction'] if correction_data.get('corrected') else POINT_REWARDS['field_validation']
            )
        
        # Update parsed receipt if exists
        if hasattr(document, 'parsed_receipt'):
            receipt = document.parsed_receipt
            
            for field, data in corrections.items():
                if data.get('corrected'):
                    # Update the field
                    if hasattr(receipt, field):
                        setattr(receipt, field, data['corrected'])
            
            receipt.save()
        
        # Learn from corrections
        if document.ai_parsed_data:
            processor = ReceiptProcessingView()
            processor.intelligent_agent.learn_from_feedback(
                document.ai_parsed_data,
                corrections,
                document.ocr_text,
                document.parsed_receipt.store_name if hasattr(document, 'parsed_receipt') else None
            )
        
        # Calculate accuracy
        total_fields = len(corrections)
        corrected_fields = sum(1 for c in corrections.values() if c.get('corrected'))
        accuracy = ((total_fields - corrected_fields) / total_fields) * 100 if total_fields > 0 else 100
        
        return {
            'success': True,
            'accuracy': accuracy,
            'fields_corrected': corrected_fields,
            'total_fields': total_fields
        }
        
    except Exception as e:
        logger.error(f"Error processing corrections: {e}")
        return {'success': False, 'error': str(e)}


def update_user_challenges(user, challenge_type, increment=1):
    """Update user challenge progress"""
    active_challenges = UserChallenge.objects.filter(
        user=user,
        completed=False,
        challenge__is_active=True,
        challenge__target_type=challenge_type,
        challenge__end_date__gte=timezone.now()
    )
    
    for user_challenge in active_challenges:
        user_challenge.update_progress(increment)


def check_achievements(user, action_type, data):
    """Check and award achievements based on user actions"""
    profile = UserProfile.objects.get_or_create(user=user)[0]
    
    # First receipt
    if action_type == 'upload' and profile.receipts_processed == 1:
        Achievement.objects.get_or_create(
            user=user,
            achievement_type='first_receipt',
            name='First Steps',
            defaults=ACHIEVEMENT_DEFINITIONS['first_receipt']
        )
    
    # Accuracy master
    if action_type == 'validation' and data.get('accuracy', 0) >= 95:
        if profile.receipts_validated >= 50:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='accuracy_master',
                name='Accuracy Master',
                defaults=ACHIEVEMENT_DEFINITIONS['accuracy_95']
            )
    
    # Speed demon
    today_count = Document.objects.filter(
        user=user,
        document_type='receipt',
        uploaded_at__date=timezone.now().date()
    ).count()
    
    if today_count >= 10:
        Achievement.objects.get_or_create(
            user=user,
            achievement_type='speed_demon',
            name='Speed Demon',
            defaults=ACHIEVEMENT_DEFINITIONS['speed_demon_10']
        )



def update_learning_model(feedback):
    """Update learning model based on validated feedback"""
    try:
        # Find or create learning pattern
        pattern, created = LearningModel.objects.get_or_create(
            pattern_type='field_location',
            pattern_value=feedback.field_name,
            defaults={
                'confidence_score': 50.0,
                'sample_text': feedback.corrected_value
            }
        )
        
        # Update confidence
        pattern.update_confidence(success=feedback.votes_up > feedback.votes_down)
        
        logger.info(f"Updated learning model for {feedback.field_name}")
        
    except Exception as e:
        logger.error(f"Error updating learning model: {e}")


def get_cross_module_integrations(document):
    """Get integration options with other UNIBOS modules"""
    integrations = []
    
    if hasattr(document, 'parsed_receipt'):
        receipt = document.parsed_receipt
        
        # WIMM integration
        if receipt.total_amount:
            integrations.append({
                'module': 'WIMM',
                'action': 'Add as expense',
                'data': {
                    'amount': float(receipt.total_amount),
                    'date': receipt.transaction_date,
                    'vendor': receipt.store_name
                }
            })
        
        # Kişisel Enflasyon integration
        if receipt.items.exists():
            integrations.append({
                'module': 'Kişisel Enflasyon',
                'action': 'Track prices',
                'data': {
                    'items': receipt.items.count(),
                    'store': receipt.store_name
                }
            })
        
        # WIMS integration
        integrations.append({
            'module': 'WIMS',
            'action': 'Update inventory',
            'data': {
                'items': receipt.items.count()
            }
        })
    
    return integrations


def api_receipt_status(request, document_id):
    """API endpoint for receipt processing status"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    response_data = {
        'status': document.processing_status,
        'ocr_complete': document.ocr_processed_at is not None,
        'ai_complete': document.ai_processed,
        'confidence': document.ocr_confidence or 0
    }
    
    if document.processing_status == 'completed':
        response_data['redirect_url'] = f'/documents/receipt/validate/{document.id}/'
    elif document.processing_status == 'failed':
        response_data['redirect_url'] = f'/documents/receipt/manual/{document.id}/'
    
    return JsonResponse(response_data)


def api_user_stats(request):
    """API endpoint for user gamification stats"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    stats = {
        'total_points': profile.total_points,
        'current_level': profile.current_level,
        'experience_points': profile.experience_points,
        'next_level_requirement': profile.get_next_level_requirement(),
        'level_progress': (profile.experience_points / profile.get_next_level_requirement()) * 100,
        'receipts_processed': profile.receipts_processed,
        'accuracy_score': profile.accuracy_score,
        'streak_days': profile.streak_days,
        'rank': profile.weekly_rank
    }
    
    return JsonResponse(stats)


@csrf_exempt
def get_receipt_detail(request, receipt_id):
    """API endpoint to get receipt details for AJAX loading in community validation"""
    try:
        receipt = get_object_or_404(Document, id=receipt_id, document_type='receipt')
        
        # Ensure OCR text is available
        if not receipt.ocr_text and receipt.file_path:
            from modules.documents.backend.ocr_service import OCRProcessor
            try:
                ocr_processor = OCRProcessor()
                ocr_result = ocr_processor.process_document(
                    receipt.file_path.path,
                    document_type='receipt'
                )
                if ocr_result['success']:
                    receipt.ocr_text = ocr_result.get('ocr_text', '')
                    receipt.ocr_confidence = ocr_result.get('confidence', 0)
                    receipt.save()
            except Exception as e:
                logger.error(f"Failed to extract OCR: {e}")
        
        # Get parsed data if available
        parsed_data = {}
        if hasattr(receipt, 'parsed_receipt') and receipt.parsed_receipt:
            parsed = receipt.parsed_receipt
            parsed_data = {
                'store_name': parsed.store_name or '',
                'transaction_date': parsed.transaction_date.isoformat() if parsed.transaction_date else '',
                'total_amount': str(parsed.total_amount) if parsed.total_amount else '',
                'tax_amount': str(parsed.tax_amount) if parsed.tax_amount else '',
                'receipt_number': parsed.receipt_number or ''
            }
        
        # Build response data
        response_data = {
            'success': True,
            'receipt': {
                'id': str(receipt.id),
                'ocr_text': receipt.ocr_text or 'Processing...',
                'ocr_confidence': receipt.ocr_confidence,
                'thumbnail_url': receipt.thumbnail_path.url if receipt.thumbnail_path else None,
                'file_url': receipt.file_path.url if receipt.file_path else None,
                'original_filename': receipt.original_filename,
                'uploaded_at': receipt.uploaded_at.isoformat(),
                'parsed_data': parsed_data
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting receipt detail: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def crop_image(request, document_id):
    """Crop receipt image based on coordinates"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        document = get_object_or_404(Document, id=document_id)
        data = json.loads(request.body)
        
        # Import PIL for image processing
        from PIL import Image
        import io
        from django.core.files.base import ContentFile
        
        # Open the original image
        img = Image.open(document.file_path.path)
        
        # Calculate actual crop coordinates
        width, height = img.size
        x = int(data['x'] * width)
        y = int(data['y'] * height)
        crop_width = int(data['width'] * width)
        crop_height = int(data['height'] * height)
        
        # Perform the crop
        cropped = img.crop((x, y, x + crop_width, y + crop_height))
        
        # Save cropped image
        output = io.BytesIO()
        cropped.save(output, format='PNG', quality=95)
        output.seek(0)
        
        # Save as new file (keeping original as backup)
        filename = f'cropped_{document.original_filename}'
        document.file_path.save(filename, ContentFile(output.read()), save=True)
        
        # Regenerate thumbnail
        from modules.documents.backend.utils import ThumbnailGenerator
        thumb_gen = ThumbnailGenerator()
        thumb_gen.generate_thumbnail(document)
        
        return JsonResponse({
            'success': True,
            'cropped_url': document.file_path.url
        })
        
    except Exception as e:
        logger.error(f"Error cropping image: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def optimize_for_ocr(request, document_id):
    """Optimize image for better OCR results"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        document = get_object_or_404(Document, id=document_id)
        
        from PIL import Image, ImageEnhance, ImageFilter
        import io
        from django.core.files.base import ContentFile
        
        # Open image
        img = Image.open(document.file_path.path)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Apply slight denoise
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        # Save optimized image
        output = io.BytesIO()
        img.save(output, format='PNG', quality=95)
        output.seek(0)
        
        # Save optimized version
        filename = f'ocr_optimized_{document.original_filename}'
        document.file_path.save(filename, ContentFile(output.read()), save=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Image optimized for OCR'
        })
        
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
def reset_image(request, document_id):
    """Reset image to original version"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Check if we have an original backup
        import os
        original_path = document.file_path.path.replace('cropped_', '').replace('ocr_optimized_', '')
        
        if os.path.exists(original_path):
            # Restore from original
            from shutil import copy2
            copy2(original_path, document.file_path.path)
            
            return JsonResponse({
                'success': True,
                'original_url': document.file_path.url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Original image not found'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error resetting image: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)