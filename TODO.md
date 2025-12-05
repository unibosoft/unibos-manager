# UNIBOS Development TODO

**Version:** v2.0.2
**Updated:** 2025-12-05
**Status:** Active Development

---

## Current Sprint: Hub Auth & Node Registry

### In Progress
- [ ] Hub Auth API Implementation
  - [ ] JWT token generation (RS256)
  - [ ] `/api/v1/auth/login/` endpoint
  - [ ] `/api/v1/auth/register/` endpoint
  - [ ] `/api/v1/auth/refresh/` endpoint
  - [ ] `/api/v1/auth/logout/` endpoint
  - [ ] Offline password hash generation

### Next Up
- [ ] Node Registry API
  - [ ] `/api/v1/nodes/register/` endpoint
  - [ ] `/api/v1/nodes/heartbeat/` endpoint
  - [ ] `/api/v1/nodes/list/` endpoint
  - [ ] Hub public key distribution

- [ ] Mobile Auth Integration (Flutter)
  - [ ] AuthService hub login
  - [ ] Token secure storage
  - [ ] Offline login cache
  - [ ] Auto token refresh

---

## Backlog

### Phase 1: Identity & Auth
- [ ] Account linking (local to hub)
- [ ] Email verification flow
- [ ] Password reset flow
- [ ] Permission sync to nodes
- [ ] WebSocket auth notifications

### Phase 2: Data Sync
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

### Phase 5: Client Integration
- [ ] Web UI auth flow
- [ ] iOS app hub connection
- [ ] Raspberry Pi node setup
- [ ] Cross-device sync

---

## Completed

### v2.0.2 (2025-12-05)
- [x] Celery worker service implementation
- [x] Celery beat scheduler service
- [x] Systemd service files (web, worker, beat)
- [x] Deploy pipeline for all 3 services
- [x] health_check, cleanup_temp_files, aggregate_metrics tasks
- [x] Redis connection verified on hub
- [x] Worker functionality tested

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

## Notes

### Priority Order
1. **Hub Auth** - All clients need this first
2. **Node Registry** - Raspberry Pi's need to register
3. **Mobile Auth** - iOS app integration
4. **Sync Engine** - Data flow between hub/node

### Real-World Test Scenarios
1. iOS app -> Hub login -> Get JWT
2. Raspberry Pi -> Register as node -> Receive public key
3. Web UI -> Authenticate -> Access modules
4. Offline mode -> Cached credentials -> Local auth

---

## Related Documents
- [TODO_ARCHITECTURE.md](./TODO_ARCHITECTURE.md) - System architecture details
- [TODO_DATA_FLOW.md](./TODO_DATA_FLOW.md) - Data flow & identity specs
- [RULES.md](./RULES.md) - Development rules & conventions
