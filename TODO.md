# UNIBOS Development TODO

**Version:** v2.1.4
**Updated:** 2025-12-06
**Status:** Active Development

---

## Current Sprint: Messenger Module Development

### Phase 6: Messenger Module ✅ COMPLETE
> **Security-First Encrypted Messaging with P2P Support**

#### 6.1 Backend Models & Database ✅
- [x] `Conversation` model - Group/direct chat support
  - [x] UUID primary key
  - [x] conversation_type (direct, group, channel)
  - [x] created_by, created_at
  - [x] is_encrypted flag
  - [x] p2p_enabled flag, transport_mode
- [x] `Participant` model - Conversation membership
  - [x] user, conversation FK
  - [x] role (owner, admin, member)
  - [x] joined_at, left_at
  - [x] notification_muted settings
  - [x] encrypted_group_key for E2E encryption
- [x] `Message` model - Core message entity
  - [x] UUID primary key
  - [x] conversation FK
  - [x] sender FK
  - [x] encrypted_content, content_nonce
  - [x] message_type (text, image, file, audio, video, system)
  - [x] reply_to (self FK for threads)
  - [x] delivered_at, read_by_count
  - [x] is_edited, edited_at
  - [x] signature, sender_key_id
- [x] `MessageAttachment` model - File attachments
  - [x] message FK
  - [x] file_url, file_type, file_size, file_name
  - [x] encrypted_key, nonce (for E2E)
  - [x] thumbnail_url (for images)
- [x] `MessageReaction` model - Emoji reactions
- [x] `MessageReadReceipt` model - Per-user read tracking
- [x] `UserEncryptionKey` model - E2E key management
  - [x] user FK
  - [x] public_key, signing_public_key
  - [x] key_id, device_id
  - [x] is_primary, is_revoked, revoked_at

#### 6.2 Security & Encryption ✅
- [x] End-to-End Encryption (E2E)
  - [x] X25519 key exchange (Curve25519)
  - [x] AES-256-GCM message encryption
  - [x] Ed25519 message signing
  - [x] Perfect Forward Secrecy (PFS) with session keys
  - [x] Double Ratchet Algorithm (Signal Protocol)
- [x] Key Management
  - [x] User key pair generation (server-side with cryptography library)
  - [x] Key rotation mechanism (revoke + generate new)
  - [x] Device key linking (device_id, device_name)
  - [x] Primary key designation
- [x] Message Security
  - [x] Message signing (Ed25519)
  - [x] Replay attack prevention (nonce)
  - [x] Message expiration (expires_at field)
  - [x] client_message_id for deduplication

#### 6.3 Transport Modes (User Selectable) ✅
- [x] **Hub Relay Mode** (Default)
  - [x] Messages routed through Hub server
  - [x] Offline message queuing
  - [x] Cross-network delivery
  - [x] Full encryption maintained
- [x] **P2P Direct Mode**
  - [x] Direct WebSocket between peers
  - [x] mDNS peer discovery integration
  - [x] Fallback to Hub if P2P fails
  - [x] Lower latency, no server storage
- [x] **Hybrid Mode**
  - [x] P2P when available, Hub fallback
  - [x] Automatic mode switching
  - [x] User-selectable per conversation

#### 6.4 REST API Endpoints ✅
- [x] Conversations
  - [x] `POST /api/v1/messenger/conversations/` - Create conversation
  - [x] `GET /api/v1/messenger/conversations/` - List conversations
  - [x] `GET /api/v1/messenger/conversations/{id}/` - Get conversation details
  - [x] `PATCH /api/v1/messenger/conversations/{id}/` - Update conversation
  - [x] `DELETE /api/v1/messenger/conversations/{id}/` - Delete/leave
  - [x] `POST /api/v1/messenger/conversations/{id}/participants/` - Add participants
  - [x] `DELETE /api/v1/messenger/conversations/{id}/participants/{user_id}/` - Remove
  - [x] `POST /api/v1/messenger/conversations/{id}/read-all/` - Mark all read
- [x] Messages
  - [x] `POST /api/v1/messenger/conversations/{id}/messages/` - Send message
  - [x] `GET /api/v1/messenger/conversations/{id}/messages/` - Get messages (paginated)
  - [x] `PATCH /api/v1/messenger/messages/{id}/` - Edit message
  - [x] `DELETE /api/v1/messenger/messages/{id}/` - Delete message
  - [x] `POST /api/v1/messenger/messages/{id}/read/` - Mark as read
  - [x] `POST /api/v1/messenger/messages/{id}/reactions/` - Add reaction
  - [x] `DELETE /api/v1/messenger/messages/{id}/reactions/` - Remove reaction
- [x] Encryption Keys
  - [x] `POST /api/v1/messenger/keys/generate/` - Generate key pair
  - [x] `GET /api/v1/messenger/keys/` - Get my keys
  - [x] `GET /api/v1/messenger/keys/public/{user_id}/` - Get user's public keys
  - [x] `POST /api/v1/messenger/keys/{id}/revoke/` - Revoke key
- [x] P2P Control
  - [x] `GET /api/v1/messenger/p2p/status/` - P2P connection status
  - [x] `POST /api/v1/messenger/p2p/connect/` - Initiate P2P
  - [x] `POST /api/v1/messenger/p2p/answer/` - Answer P2P
  - [x] `POST /api/v1/messenger/p2p/disconnect/{session_id}/` - Close P2P
- [x] Typing & Search
  - [x] `POST /api/v1/messenger/typing/` - Send typing indicator
  - [x] `POST /api/v1/messenger/search/` - Search messages

#### 6.5 WebSocket Endpoints ✅
- [x] `/ws/messenger/` - Main messaging WebSocket (MessengerConsumer)
  - [x] `message.new` - New message received
  - [x] `message.edited` - Message edited
  - [x] `message.deleted` - Message deleted
  - [x] `message.read` - Read receipt
  - [x] `typing.start` / `typing.stop` - Typing indicators
  - [x] `participant.joined` / `participant.left` - Membership changes
  - [x] `p2p.offer` / `p2p.answer` / `p2p.ice` - P2P signaling

#### 6.6 Flutter Mobile Client ✅
- [x] Core Services
  - [x] `MessengerService` - Full API client (messenger_service.dart)
  - [x] Data Models (messenger_models.dart)
    - [x] Conversation, Participant, Message, MessageReaction
    - [x] MessageReadReceipt, MessageAttachment
    - [x] UserEncryptionKey, P2PSession
- [x] State Management (Riverpod)
  - [x] `conversationsProvider` - Conversation list state
  - [x] `messagesProvider` - Message state per conversation
  - [x] `encryptionKeysProvider` - Key management
  - [x] `p2pStatusProvider` - P2P connection status
  - [x] `typingStateProvider` - Typing indicators
- [x] UI Screens
  - [x] `ConversationListScreen` - Chat list with transport mode
  - [x] `ChatScreen` - Message view & input
  - [x] `NewConversationScreen` - Create direct/group chat
  - [x] `ConversationSettingsScreen` - Chat settings, encryption, participants
- [x] UI Components
  - [x] `ConversationTile` - Conversation list item
  - [x] `MessageBubble` - Message display with reactions
  - [x] `MessageInput` - Text input with send
  - [x] `TypingIndicator` - Animated typing dots

#### 6.7 Web UI Interface ✅
- [x] Terminal-style chat interface (UNIBOS theme)
- [x] Conversation sidebar with unread count
- [x] Message area with timestamps
- [x] Input area with command support
- [x] P2P/Hub mode toggle and status
- [x] Encryption status display (🔒 indicator)
- [x] Added to main sidebar navigation

#### 6.8 Testing & Security Audit ✅ COMPLETE
- [x] Unit tests for encryption (43 tests)
  - [x] Key generation (X25519, Ed25519)
  - [x] Key derivation (HKDF)
  - [x] Message encryption/decryption (AES-256-GCM)
  - [x] Signature verification (Ed25519)
  - [x] Group encryption
  - [x] File encryption
  - [x] Replay attack prevention
  - [x] Serialization roundtrip
- [x] Integration tests for messaging flow
  - [x] Conversation creation (direct, group)
  - [x] Message sending/receiving
  - [x] Read receipts
  - [x] Reactions
  - [x] Participant management
  - [x] Encryption key management
- [x] P2P connection tests
  - [x] Session lifecycle
  - [x] Connection state transitions
  - [x] Session statistics
  - [x] Transport mode switching
- [x] Message delivery reliability tests
  - [x] Delivery queue management
  - [x] Retry logic with exponential backoff
  - [x] Message expiration
  - [x] Deduplication
- [x] Security penetration testing ✅
  - [x] Cryptographic security tests (18 tests)
  - [x] Input validation tests (4 tests)
  - [x] Timing attack resistance tests
  - [x] Key management security tests (3 tests)
  - [x] SECURITY_AUDIT.md report generated

---

## Previous Sprint: P2P & Mobile Integration

### Completed This Sprint - Flutter Sync Client
- [x] Flutter Sync Client Integration
  - [x] Sync endpoints added to endpoints.dart
  - [x] SyncService with full sync flow
  - [x] SyncModels (SyncSession, SyncRecord, SyncConflict)
  - [x] OfflineQueue for offline operations
  - [x] SyncStateNotifier for state management
  - [x] SyncScreen UI with status, pending changes
  - [x] ConflictResolutionScreen with visual diff

### Completed - Multi-Platform Testing (2025-12-05)
- [x] iOS/Android Testing
  - [x] Test sync on iOS Simulator (iPhone 16e, iOS 26.0)
  - [x] Test sync on Android Emulator (API 36, Android 16)
  - [x] Test offline queue persistence (SharedPreferences)
  - [x] Hub login flow verified on both platforms
  - [x] JWT token exchange working

### Completed This Sprint (2025-12-05)
- [x] P2P Node Communication
  - [x] mDNS discovery (Zeroconf)
  - [x] WebSocket transport
  - [x] Message signing (HMAC)
  - [x] Django Channels integration
  - [x] Avahi compatibility
  - [x] Dual-path routing (direct + hub relay)
- [x] P2P API Endpoints
  - [x] `/api/v1/p2p/status/` - Service status
  - [x] `/api/v1/p2p/start/` - Start service
  - [x] `/api/v1/p2p/stop/` - Stop service
  - [x] `/api/v1/p2p/peers/` - List peers
- [x] P2P Deployed to nodes
  - [x] unicorn-main - P2P working
  - [x] unicorn-station - P2P working
  - [x] birlikteyiz-000000003 - P2P working
- [x] P2P Testing
  - [x] mDNS peer discovery verified
  - [x] WebSocket connections established
  - [x] Peer authentication working
- [x] WiFi Direct P2P
  - [x] Configure wlan0 on Pi nodes (rfkill, hostapd, dnsmasq)
  - [x] unicorn-main AP mode (SSID: UNIBOS-P2P, IP: 10.42.0.1)
  - [x] unicorn-station client mode (IP: 10.42.0.67)
  - [x] P2P API accessible via WiFi Direct (no router needed)
- [x] End-to-End Authentication Flow
  - [x] Hub Auth API tested (register, login, refresh)
  - [x] Node Auth API tested (local JWT generation)
  - [x] Node heartbeat tested (Hub receives metrics)
  - [x] Authentication migrations created & deployed
  - [x] timezone.utc bug fixed in views.py

---

## Backlog

### Phase 1: Identity Enhancements ✅ COMPLETE
- [x] Account linking (local to hub)
  - [x] AccountLink model with verification flow
  - [x] `/api/v1/auth/link/init/` - Initialize linking
  - [x] `/api/v1/auth/link/verify/` - Verify with code
  - [x] `/api/v1/auth/link/status/` - Get/revoke link
- [x] Email verification flow
  - [x] EmailVerificationToken model
  - [x] `/api/v1/auth/email/verify/request/`
  - [x] `/api/v1/auth/email/verify/confirm/`
- [x] Permission sync to nodes
  - [x] PermissionSyncSerializer
  - [x] `/api/v1/auth/permissions/sync/`
  - [x] AccountLink stores synced_permissions/roles
- [x] WebSocket auth notifications
  - [x] AuthNotificationConsumer
  - [x] Session created/revoked notifications
  - [x] Security alert notifications
  - [x] Account link status change notifications
  - [x] `/ws/auth/notifications/` endpoint
- [x] RS256 key pair generation for hub
  - [x] HubKeyPair model with RSA generation
  - [x] `/api/v1/auth/keys/` - List keys
  - [x] `/api/v1/auth/keys/create/` - Create key pair
  - [x] `/api/v1/auth/keys/primary/` - Get primary key

### Phase 2: Data Sync Engine ✅ COMPLETE
- [x] Version vector implementation
- [x] Sync init/pull/push API
- [x] Conflict detection
- [x] Conflict resolution UI
- [x] Offline queue management

### Phase 3: Export Control ✅ COMPLETE
- [x] Kill switch toggle
- [x] Module-level export permissions
- [x] Export audit logging
- [x] Export log viewer UI

### Phase 4: P2P Communication ✅ COMPLETE
- [x] mDNS node discovery (Zeroconf)
- [x] P2P WebSocket transport
- [x] Message signing (HMAC)
- [x] WiFi Direct (AP mode + client mode)
- [ ] LoRa integration (optional)

### Phase 5: Multi-Platform Testing ✅ COMPLETE
- [x] iOS Simulator testing
- [x] Android Emulator testing
- [x] Raspberry Pi deployment (3 nodes active)
- [x] Cross-device sync verification

---

## Completed

### v2.1.4 (2025-12-06) - Current
- [x] User Registration Flow
  - [x] Web UI register page (terminal-style design)
  - [x] Flutter RegisterScreen with password strength
  - [x] Password validation synced across backend/web/mobile
  - [x] Backend validation error display in Flutter
  - [x] Email verification on registration
  - [x] Web verify-email page
  - [x] Login ↔ Register navigation links
- [x] Password policy: min 8 chars, upper+lower, digit, special char
- [x] recaria.org Mail Server Management
  - [x] `mail_service.py` - SSH-based Postfix/Dovecot provisioning
  - [x] Mailbox CRUD (create, delete, password reset)
  - [x] Forwarding and auto-responder configuration
  - [x] Usage statistics from mail server
  - [x] `sync_mailboxes` management command
  - [x] Web UI in Administration > Recaria Mail
  - [x] Server status display in mailbox detail
  - [x] MAIL_USE_SSH config setting
  - [x] Local mode support (SSH-free for same-machine deployments)
  - [x] OpenDKIM setup for DKIM email signing
  - [x] DNS configuration guide (SPF, DKIM, DMARC)
  - [x] Enhanced admin UI with real-time server status
  - [x] Statistics dashboard and quick actions

### v2.0.2 (2025-12-05)
- [x] Celery worker service implementation
- [x] Celery beat scheduler service
- [x] Systemd service files (web, worker, beat)
- [x] Deploy pipeline for all 3 services
- [x] health_check, cleanup_temp_files, aggregate_metrics tasks
- [x] Redis connection verified on hub
- [x] Worker functionality tested
- [x] TODO documentation consolidation
- [x] Raspberry Pi node deployment (3 nodes)
  - [x] unicorn-main (Pi 5, 8GB) - Installed & registered with Hub
  - [x] unicorn-station (Pi 4, 8GB) - Installed & registered with Hub
  - [x] birlikteyiz-000000003 (Pi Zero 2W, 416MB) - Installed & registered with Hub
- [x] Install script v2.0.2 (tools/install/install.sh)
  - [x] SSH clone support with HTTPS fallback
  - [x] Node UUID generation
  - [x] Hub connection (recaria.org)
  - [x] Celery worker and beat services for nodes
  - [x] DB password fix (CREATE/ALTER pattern)
- [x] node.py settings fixes
  - [x] LOG_DIR path correction
  - [x] REDIS_URL detection fix
- [x] GitHub deploy key setup for unibos (node) repo
- [x] RULES.md documentation policy rule added
- [x] Authentication migrations (0001_initial.py)
  - [x] LoginAttempt, UserSession, RefreshTokenBlacklist models
  - [x] PasswordResetToken, TwoFactorAuth models
  - [x] Deployed to Hub and all nodes
- [x] Bug fix: timezone.utc -> dt_timezone.utc in views.py
- [x] Offline Authentication Implementation
  - [x] `offline_hash` added to JWT login response (serializers.py)
  - [x] `UserOfflineCache` model for caching Hub credentials on Nodes
  - [x] `OfflineLoginView` for Node-only authentication
  - [x] `/api/v1/auth/login/offline/` endpoint
  - [x] Migration `0002_userofflinecache.py` deployed to Hub and all nodes
  - [x] Tested: Hub login returns offline_hash
  - [x] Tested: Node offline login with cached credentials works
  - [x] Tested: Wrong password returns "Invalid credentials"
- [x] Sync Engine Implementation
  - [x] `SyncSession` model for tracking sync operations
  - [x] `SyncRecord` model for individual record changes
  - [x] `SyncConflict` model for conflict detection
  - [x] `OfflineOperation` model for offline queue
  - [x] `VersionVector` model for version tracking
  - [x] `SyncableModelMixin` for syncable models
  - [x] `/api/v1/sync/init/` - Initialize sync session
  - [x] `/api/v1/sync/pull/` - Pull changes from Hub
  - [x] `/api/v1/sync/push/` - Push changes to Hub
  - [x] `/api/v1/sync/complete/` - Complete sync session
  - [x] `/api/v1/sync/status/` - Get sync status
  - [x] `/api/v1/sync/conflicts/` - Manage conflicts
  - [x] `/api/v1/sync/offline/` - Manage offline operations
  - [x] Migration deployed to Hub and all nodes
  - [x] Tested: sync init, push, complete all working
- [x] Data Export Control Implementation
  - [x] `DataExportSettings` model - master kill switch & module permissions
  - [x] `DataExportLog` model - audit logging
  - [x] `DataExportControlMiddleware` - request interception
  - [x] `/api/v1/sync/export/settings/` - Get/update export settings
  - [x] `/api/v1/sync/export/kill-switch/` - Toggle master kill switch
  - [x] `/api/v1/sync/export/module-permission/` - Set module permissions
  - [x] `/api/v1/sync/export/check/` - Check if export allowed
  - [x] `/api/v1/sync/export/logs/` - View export logs
  - [x] `/api/v1/sync/export/stats/` - Export statistics
  - [x] Emergency bypass for critical data (birlikteyiz.earthquake_alerts)
  - [x] Migration `0002_export_control.py` deployed to Hub and all nodes
  - [x] Tested: kill switch blocks exports, emergency bypass works
- [x] Integration tests passed
  - [x] Hub register: ✅ JWT tokens returned
  - [x] Hub login: ✅ JWT + user info returned
  - [x] Node login: ✅ Local JWT returned
  - [x] Node heartbeat: ✅ Hub acknowledged
  - [x] Node discovery: ✅ 6 nodes listed
- [x] Hub Auth API (full implementation exists)
  - [x] `/api/v1/auth/login/` - JWT login with rate limiting
  - [x] `/api/v1/auth/register/` - User registration
  - [x] `/api/v1/auth/refresh/` - Token refresh
  - [x] `/api/v1/auth/logout/` - Logout with token blacklist
  - [x] `/api/v1/auth/change-password/` - Password change
  - [x] `/api/v1/auth/reset-password/` - Password reset flow
  - [x] `/api/v1/auth/2fa/setup/` - 2FA setup
  - [x] `/api/v1/auth/2fa/verify/` - 2FA verification
  - [x] Session management (list, revoke)
- [x] Node Registry API (full implementation exists)
  - [x] `/api/v1/nodes/register/` - Node registration
  - [x] `/api/v1/nodes/{id}/heartbeat/` - Heartbeat with metrics
  - [x] `/api/v1/nodes/discover/` - Node discovery
  - [x] `/api/v1/nodes/summary/` - Network summary
  - [x] `/api/v1/nodes/{id}/metrics/` - Node metrics history
  - [x] `/api/v1/nodes/{id}/events/` - Node events
  - [x] `/api/v1/nodes/{id}/maintenance/` - Maintenance toggle
- [x] Flutter Auth Service (full implementation exists)
  - [x] `AuthService` - Login, register, logout
  - [x] `TokenStorage` - Secure storage with Keychain/EncryptedPrefs
  - [x] `AuthProvider` - Riverpod state management
  - [x] `ApiClient` - HTTP client with interceptors
- [x] Flutter Sync Client
  - [x] `SyncService` - Full sync flow (init, push, pull, complete)
  - [x] `SyncModels` - SyncSession, SyncRecord, SyncConflict, etc.
  - [x] `OfflineQueue` - Offline operations with retry logic
  - [x] `SyncScreen` - Status display, pending changes, sync button
  - [x] `ConflictResolutionScreen` - Visual diff with resolution strategies

### v2.0.1 (2025-12-05)
- [x] 5-profile architecture (dev, hub, manager, node, worker)
- [x] 5-repo system (unibos-dev, unibos-hub, unibos-manager, unibos, unibos-worker)
- [x] HubDeployer class
- [x] Deploy key authentication for repos
- [x] Version branch strategy (immutable snapshots)
- [x] Push-all workflow via TUI CLI

### v2.0.0 (2025-12-04)
- [x] Architecture refactor (server -> hub, prod -> node)
- [x] Profile-based settings system
- [x] CLI tools per profile (unibos-dev, unibos-hub, etc.)
- [x] Module registry system
- [x] TUI menu system

---

## API Summary

### Hub Endpoints (recaria.org)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/login/` | POST | No | Get JWT tokens |
| `/api/v1/auth/register/` | POST | No | Register new user |
| `/api/v1/auth/refresh/` | POST | No | Refresh access token |
| `/api/v1/auth/logout/` | POST | Yes | Logout (blacklist token) |
| `/api/v1/nodes/register/` | POST | No | Register node |
| `/api/v1/nodes/{id}/heartbeat/` | POST | No | Send heartbeat |
| `/api/v1/nodes/discover/` | GET | No | Find online nodes |
| `/api/v1/auth/login/offline/` | POST | No | Offline login (Node only) |
| `/api/v1/sync/init/` | POST | No | Initialize sync session |
| `/api/v1/sync/push/` | POST | No | Push changes to Hub |
| `/api/v1/sync/pull/` | POST | No | Pull changes from Hub |
| `/api/v1/sync/status/` | GET | No | Get sync status |
| `/api/v1/sync/export/settings/` | GET/PUT | No | Export settings |
| `/api/v1/sync/export/kill-switch/` | POST | No | Toggle kill switch |
| `/api/v1/sync/export/check/` | POST | No | Check export permission |

### Real-World Test Commands
```bash
# Test login
curl -X POST https://recaria.org/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Test node discovery
curl https://recaria.org/api/v1/nodes/discover/

# Test node registration
curl -X POST https://recaria.org/api/v1/nodes/register/ \
  -H "Content-Type: application/json" \
  -d '{"hostname":"my-pi","platform":"raspberry-pi","node_type":"edge"}'
```

---

## Notes

### Key Findings (2025-12-05)
- Auth API already fully implemented with 2FA, sessions, rate limiting
- Node Registry already fully implemented with metrics, events
- Flutter client already has auth service with secure storage
- **Focus should shift to integration testing, not new implementations**

### Priority Order (Updated)
1. ~~**Integration Testing** - Verify existing APIs work end-to-end~~ ✅
2. ~~**Offline Mode** - Add offline auth capability~~ ✅
3. ~~**Sync Engine** - Core data flow feature~~ ✅
4. ~~**Data Export Control** - Kill switch, module permissions~~ ✅
5. ~~**P2P** - Advanced networking~~ ✅
6. ~~**Flutter Sync Client** - Mobile sync integration~~ ✅
7. ~~**Messenger Module** - E2E encrypted messaging~~ ✅
8. ~~**Messenger Testing** - Unit/integration tests~~ ✅
9. ~~**Security Penetration Testing** - Internal audit~~ ✅
10. **Production Deployment** - Final checklist & documentation (NEXT)
11. **External Security Audit** - Third-party review (OPTIONAL)

---

## Technical Debt

### TD-1: Dynamic Module Loading Fallback (Priority: LOW)
- [ ] `get_dynamic_modules()` in `core/clients/web/unibos_backend/settings/base.py` always falls back to hardcoded 14-module list
- [ ] Module `.enabled` marker files are effectively ignored
- [ ] Fix: Make registry the primary source, remove hardcoded fallback or make it configurable

### TD-2: Empty Placeholder Directories (Priority: LOW)
- [ ] `core/base/platform/offline/` - empty
- [ ] `core/base/platform/orchestration/` - empty
- [ ] `core/base/platform/routing/` - empty
- [ ] `core/base/p2p/` - empty
- [ ] `core/base/services/` - empty
- [ ] `core/base/sync/` - empty
- [ ] Decision: Remove if not planned, or add stub implementations

### TD-3: CI/CD Pipeline (Priority: MEDIUM)
- [ ] No GitHub Actions or equivalent CI/CD configuration exists
- [ ] Add workflow to run messenger test suite (141 tests) on push
- [ ] Add linting and type checking steps
- [ ] Add deployment automation trigger

### TD-4: Test Coverage Outside Messenger (Priority: MEDIUM)
- [ ] 13 business modules have no test coverage
- [ ] System apps (authentication, users, admin, sync, p2p, nodes) lack tests
- [ ] No `conftest.py` or `pytest.ini` at project root
- [ ] Add tests incrementally with new features

### TD-5: Credential Management (Priority: HIGH)
- [ ] `rocksteady.config.json` contains production SECRET_KEY and DB password in git
- [ ] Move sensitive values to `.env` file on server
- [ ] Add `rocksteady.config.json` to `.gitignore` (keep a `.example` template)
- [ ] Rotate production SECRET_KEY after migration

---

## Related Documents
- [TODO_ARCHITECTURE.md](./TODO_ARCHITECTURE.md) - System architecture details
- [TODO_DATA_FLOW.md](./TODO_DATA_FLOW.md) - Data flow & identity specs
- [RULES.md](./RULES.md) - Development rules & conventions
