"""
Messenger Module URL Configuration
"""

from django.urls import path
from .views import (
    # Encryption Keys
    KeyGenerateView,
    KeyListView,
    KeyRevokeView,
    UserPublicKeyView,
    # Conversations
    ConversationViewSet,
    # Messages
    MessageViewSet,
    AttachmentUploadView,
    # P2P
    P2PStatusView,
    P2PConnectView,
    P2PAnswerView,
    P2PDisconnectView,
    # Typing & Search
    TypingIndicatorView,
    MessageSearchView,
    MarkAllReadView,
)

app_name = 'messenger'

urlpatterns = [
    # ========== Encryption Keys ==========
    path('keys/generate/', KeyGenerateView.as_view(), name='key-generate'),
    path('keys/', KeyListView.as_view(), name='key-list'),
    path('keys/<uuid:key_id>/revoke/', KeyRevokeView.as_view(), name='key-revoke'),
    path('keys/public/<uuid:user_id>/', UserPublicKeyView.as_view(), name='user-public-key'),

    # ========== Conversations ==========
    path('conversations/', ConversationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='conversation-list'),

    path('conversations/<uuid:pk>/', ConversationViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='conversation-detail'),

    path('conversations/<uuid:pk>/participants/', ConversationViewSet.as_view({
        'post': 'add_participant'
    }), name='conversation-add-participant'),

    path('conversations/<uuid:pk>/participants/<uuid:user_id>/', ConversationViewSet.as_view({
        'delete': 'remove_participant'
    }), name='conversation-remove-participant'),

    path('conversations/<uuid:conversation_id>/read-all/', MarkAllReadView.as_view(), name='mark-all-read'),

    # ========== Messages ==========
    path('conversations/<uuid:conversation_id>/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='message-list'),

    path('conversations/<uuid:conversation_id>/messages/<uuid:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='message-detail'),

    path('conversations/<uuid:conversation_id>/messages/<uuid:pk>/read/', MessageViewSet.as_view({
        'post': 'read'
    }), name='message-read'),

    path('conversations/<uuid:conversation_id>/messages/<uuid:pk>/reactions/', MessageViewSet.as_view({
        'post': 'reactions',
        'delete': 'reactions'
    }), name='message-reactions'),

    # ========== Attachments ==========
    path('conversations/<uuid:conversation_id>/messages/<uuid:message_id>/attachments/',
         AttachmentUploadView.as_view(), name='attachment-upload'),

    # ========== P2P ==========
    path('p2p/status/', P2PStatusView.as_view(), name='p2p-status'),
    path('p2p/connect/', P2PConnectView.as_view(), name='p2p-connect'),
    path('p2p/answer/', P2PAnswerView.as_view(), name='p2p-answer'),
    path('p2p/disconnect/<uuid:session_id>/', P2PDisconnectView.as_view(), name='p2p-disconnect'),

    # ========== Typing & Search ==========
    path('typing/', TypingIndicatorView.as_view(), name='typing-indicator'),
    path('search/', MessageSearchView.as_view(), name='message-search'),
]
