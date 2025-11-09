"""
Document Sharing Views
"""

import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Document
from .document_models import DocumentShare, DocumentType
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_exempt
@login_required
def share_document(request, document_id):
    """Share a document with another user or group"""
    
    document = get_object_or_404(Document, id=document_id)
    
    # Check if user has permission to share
    if document.user != request.user:
        existing_share = DocumentShare.objects.filter(
            document=document,
            shared_with=request.user,
            permission__in=['edit', 'admin']
        ).first()
        
        if not existing_share or not existing_share.can_reshare:
            return HttpResponseForbidden("You don't have permission to share this document")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            share_type = data.get('share_type', 'user')
            permission = data.get('permission', 'view')
            can_reshare = data.get('can_reshare', False)
            expires_days = data.get('expires_days', None)
            notes = data.get('notes', '')
            
            # Calculate expiration
            expires_at = None
            if expires_days:
                expires_at = timezone.now() + timezone.timedelta(days=int(expires_days))
            
            if share_type == 'user':
                # Share with individual user
                username = data.get('username')
                if not username:
                    return JsonResponse({'success': False, 'error': 'Username required'}, status=400)
                
                try:
                    target_user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
                
                # Check if already shared
                existing = DocumentShare.objects.filter(
                    document=document,
                    shared_with=target_user
                ).first()
                
                if existing:
                    # Update existing share
                    existing.permission = permission
                    existing.can_reshare = can_reshare
                    existing.expires_at = expires_at
                    existing.notes = notes
                    existing.revoked_at = None  # Un-revoke if previously revoked
                    existing.save()
                    share = existing
                else:
                    # Create new share
                    share = DocumentShare.objects.create(
                        document=document,
                        share_type='user',
                        shared_by=request.user,
                        shared_with=target_user,
                        permission=permission,
                        can_reshare=can_reshare,
                        expires_at=expires_at,
                        notes=notes
                    )
                
                logger.info(f"Document {document_id} shared with user {username} by {request.user.username}")
                
            elif share_type == 'group':
                # Share with group
                group_name = data.get('group_name')
                if not group_name:
                    return JsonResponse({'success': False, 'error': 'Group name required'}, status=400)
                
                # Check if already shared with group
                existing = DocumentShare.objects.filter(
                    document=document,
                    shared_with_group=group_name
                ).first()
                
                if existing:
                    existing.permission = permission
                    existing.can_reshare = can_reshare
                    existing.expires_at = expires_at
                    existing.notes = notes
                    existing.revoked_at = None
                    existing.save()
                    share = existing
                else:
                    share = DocumentShare.objects.create(
                        document=document,
                        share_type='group',
                        shared_by=request.user,
                        shared_with_group=group_name,
                        permission=permission,
                        can_reshare=can_reshare,
                        expires_at=expires_at,
                        notes=notes
                    )
                
                logger.info(f"Document {document_id} shared with group {group_name} by {request.user.username}")
                
            elif share_type == 'public':
                # Create public link
                share_link = str(uuid.uuid4())[:8]  # Short link
                
                share = DocumentShare.objects.create(
                    document=document,
                    share_type='public',
                    shared_by=request.user,
                    share_link=share_link,
                    permission=permission,
                    can_reshare=False,  # Public links can't reshare
                    expires_at=expires_at,
                    notes=notes
                )
                
                logger.info(f"Public link created for document {document_id} by {request.user.username}")
            
            else:
                return JsonResponse({'success': False, 'error': 'Invalid share type'}, status=400)
            
            return JsonResponse({
                'success': True,
                'share_id': str(share.id),
                'share_link': share.share_link if share.share_link else None,
                'message': 'Document shared successfully'
            })
            
        except Exception as e:
            logger.error(f"Error sharing document: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # GET request - show sharing UI
    existing_shares = DocumentShare.objects.filter(
        document=document,
        revoked_at__isnull=True
    ).select_related('shared_with')
    
    context = {
        'document': document,
        'existing_shares': existing_shares,
        'users': User.objects.exclude(id=request.user.id).order_by('username'),
        'permission_choices': DocumentShare.PERMISSION_CHOICES,
    }
    
    return render(request, 'documents/share_document.html', context)


@login_required
def view_shared_document(request, share_id):
    """View a shared document"""
    
    share = get_object_or_404(DocumentShare, id=share_id)
    
    # Check if share is valid
    if not share.is_valid():
        return HttpResponseForbidden("This share link has expired or been revoked")
    
    # Check permissions
    if share.share_type == 'user' and share.shared_with != request.user:
        return HttpResponseForbidden("You don't have permission to view this document")
    
    # Record access
    share.record_access()
    
    # Get document
    document = share.document
    
    # Check if user can edit
    can_edit = share.permission in ['edit', 'admin']
    can_comment = share.permission in ['comment', 'edit', 'admin']
    
    context = {
        'document': document,
        'share': share,
        'can_edit': can_edit,
        'can_comment': can_comment,
        'is_shared': True,
    }
    
    return render(request, 'documents/view_document.html', context)


@login_required
def my_shared_documents(request):
    """View documents shared with the current user"""
    
    # Get all valid shares for this user
    user_shares = DocumentShare.objects.filter(
        shared_with=request.user,
        revoked_at__isnull=True
    ).select_related('document', 'shared_by')
    
    # Filter out expired shares
    valid_shares = [s for s in user_shares if s.is_valid()]
    
    # Group shares
    group_shares = []
    if request.user.groups.exists():
        group_names = request.user.groups.values_list('name', flat=True)
        group_shares = DocumentShare.objects.filter(
            shared_with_group__in=group_names,
            revoked_at__isnull=True
        ).select_related('document', 'shared_by')
        
        group_shares = [s for s in group_shares if s.is_valid()]
    
    context = {
        'user_shares': valid_shares,
        'group_shares': group_shares,
        'total_shares': len(valid_shares) + len(group_shares),
    }
    
    return render(request, 'documents/my_shared_documents.html', context)


@csrf_exempt
@login_required
def revoke_share(request, share_id):
    """Revoke a document share"""
    
    share = get_object_or_404(DocumentShare, id=share_id)
    
    # Check if user has permission to revoke
    if share.shared_by != request.user and share.document.user != request.user:
        return HttpResponseForbidden("You don't have permission to revoke this share")
    
    if request.method == 'POST':
        share.revoked_at = timezone.now()
        share.save()
        
        logger.info(f"Share {share_id} revoked by {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Share revoked successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def public_document_view(request, share_link):
    """View a document via public link (no login required)"""
    
    share = get_object_or_404(DocumentShare, share_link=share_link, share_type='public')
    
    # Check if share is valid
    if not share.is_valid():
        return HttpResponseForbidden("This share link has expired or been revoked")
    
    # Record access
    share.record_access()
    
    # Get document
    document = share.document
    
    context = {
        'document': document,
        'share': share,
        'can_edit': False,  # Public links are view-only
        'can_comment': False,
        'is_public': True,
    }
    
    return render(request, 'documents/public_document_view.html', context)