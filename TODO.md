# UNIBOS Development TODO

**Version:** v2.0.2
**Updated:** 2025-12-05
**Status:** Active Development

---

## Current Sprint: P2P & Mobile Integration

### Completed This Sprint - Flutter Sync Client
- [x] Flutter Sync Client Integration
  - [x] Sync endpoints added to endpoints.dart
  - [x] SyncService with full sync flow
  - [x] SyncModels (SyncSession, SyncRecord, SyncConflict)
  - [x] OfflineQueue for offline operations
  - [x] SyncStateNotifier for state management
  - [x] SyncScreen UI with status, pending changes
  - [x] ConflictResolutionScreen with visual diff

### Next Up
- [ ] iOS/Android Testing
  - [ ] Test sync on iOS Simulator
  - [ ] Test sync on Android Emulator
  - [ ] Test offline queue persistence

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

### Phase 1: Identity Enhancements
- [ ] Account linking (local to hub)
- [ ] Email verification flow (already has models)
- [ ] Permission sync to nodes
- [ ] WebSocket auth notifications
- [ ] RS256 key pair generation for hub

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

### Phase 5: Multi-Platform Testing
- [ ] iOS Simulator testing
- [ ] Android Emulator testing
- [ ] Raspberry Pi deployment
- [ ] Cross-device sync verification

---

## Completed

### v2.0.2 (2025-12-05) - Current
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
6. **Flutter Sync Client** - Mobile sync integration (NEXT)

---

## Related Documents
- [TODO_ARCHITECTURE.md](./TODO_ARCHITECTURE.md) - System architecture details
- [TODO_DATA_FLOW.md](./TODO_DATA_FLOW.md) - Data flow & identity specs
- [RULES.md](./RULES.md) - Development rules & conventions
