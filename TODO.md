# UNIBOS Development TODO

**Version:** v2.0.2
**Updated:** 2025-12-05
**Status:** Active Development

---

## Current Sprint: Real-World Integration Testing

### In Progress
- [ ] End-to-End Authentication Flow
  - [ ] Test iOS app -> Hub login -> JWT received
  - [ ] Test Raspberry Pi -> Node registration -> Heartbeat
  - [ ] Test Web UI -> Authenticate -> Module access
  - [ ] Document API response format for clients

### Next Up
- [ ] Offline Authentication
  - [ ] Implement offline password hash in JWT
  - [ ] Add offline login cache to Flutter
  - [ ] Test offline mode on iOS app

- [ ] Node-Hub Data Sync
  - [ ] Implement sync init API
  - [ ] Implement sync pull/push API
  - [ ] Add version vector to models

---

## Backlog

### Phase 1: Identity Enhancements
- [ ] Account linking (local to hub)
- [ ] Email verification flow (already has models)
- [ ] Permission sync to nodes
- [ ] WebSocket auth notifications
- [ ] RS256 key pair generation for hub

### Phase 2: Data Sync Engine
- [ ] Version vector implementation
- [ ] Sync init/pull/push API
- [ ] Conflict detection
- [ ] Conflict resolution UI
- [ ] Offline queue management

### Phase 3: Export Control
- [ ] Kill switch toggle
- [ ] Module-level export permissions
- [ ] Export audit logging
- [ ] Export log viewer UI

### Phase 4: P2P Communication
- [ ] mDNS node discovery
- [ ] P2P WebSocket transport
- [ ] Message signing
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
1. **Integration Testing** - Verify existing APIs work end-to-end
2. **Offline Mode** - Add offline auth capability
3. **Sync Engine** - Core data flow feature
4. **P2P** - Advanced networking

---

## Related Documents
- [TODO_ARCHITECTURE.md](./TODO_ARCHITECTURE.md) - System architecture details
- [TODO_DATA_FLOW.md](./TODO_DATA_FLOW.md) - Data flow & identity specs
- [RULES.md](./RULES.md) - Development rules & conventions
