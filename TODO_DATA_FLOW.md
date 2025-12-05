# UNIBOS Data Flow & Identity System

**Version:** v2.0.2
**Created:** 2025-12-05
**Updated:** 2025-12-05
**Status:** Phase 4 Complete - Export Control & Sync Engine Implemented
**Priority:** HIGH - Core Data & Auth Infrastructure
**Depends On:** TODO_ARCHITECTURE.md

---

## Quick Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Database Models | ✅ Complete | Auth migrations deployed |
| Phase 2: Hub Auth API | ✅ Complete | JWT tested end-to-end |
| Phase 2.5: Offline Auth | ✅ Complete | offline_hash, UserOfflineCache, OfflineLoginView |
| Phase 3: Data Export Control | ✅ Complete | Kill switch, module permissions, audit logging |
| Phase 4: Sync Engine | ✅ Complete | SyncSession, SyncRecord, VersionVector, OfflineOperation |
| Phase 5: P2P Communication | 🔄 Next | mDNS, WebSocket transport, message signing |
| Phase 6: Mobile Integration | 🔄 In Progress | Flutter auth exists, sync client pending |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Federated Identity System](#2-federated-identity-system)
3. [Authentication Flows](#3-authentication-flows)
4. [Data Flow Architecture](#4-data-flow-architecture)
5. [Data Export Control](#5-data-export-control)
6. [Sync Engine](#6-sync-engine)
7. [Conflict Resolution](#7-conflict-resolution)
8. [Offline & Local-First](#8-offline--local-first)
9. [Node-to-Node Communication](#9-node-to-node-communication)
10. [Privacy & Security](#10-privacy--security)
11. [Database Models](#11-database-models)
12. [API Specifications](#12-api-specifications)
13. [Mobile Integration](#13-mobile-integration)
14. [Implementation Phases](#14-implementation-phases)

---

## 1. Executive Summary

### Vision

UNIBOS, kullanici verilerinin tamamen kullanici kontrolunde oldugu, merkeze bagimsiz calisabilen, ancak merkezi ozelliklerden de faydalanabilen bir veri akisi mimarisi hedefliyor.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Local User ID | Email (required) | Hub hesabina hazirlik |
| Hub Linking | Email verification | Otomatik ve guvenli |
| Data Export | Kill switch + granular | Maksimum kullanici kontrolu |
| Node/Pi Ownership | Setup'ta belirlenir | Tek yetkili kaynak |
| Hub Account | Optional + incentivized | Ozgurluk + tesvik dengesi |
| Node Communication | P2P (LoRa, WiFi, Internet) | Hub bagimsiz calisma |
| Multi-Hub | Geo-distributed | Latency, redundancy |

### Core Principles

```
1. LOCAL-FIRST      : Kullanici hub hesabi olmadan sistemi tam kullanabilir
2. PRIVACY-FOCUSED  : Veri cikisi tamamen kullanici kontrolunde
3. ORGANIC MESH     : Node'lar hub olmadan birbirleriyle haberlesebilir
4. GRACEFUL DEGRADE : Internet kesilse bile sistem calisir
5. RETROACTIVE SYNC : Onceden olusturulan veriler sonradan hub'a aktarilabilir
```

---

## 2. Federated Identity System

### 2.1 Identity Architecture

```
+------------------------------------------------------------------+
|                    FEDERATED IDENTITY MODEL                        |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                    HUB (Identity Provider)                  |  |
|  |                                                            |  |
|  |  User Master Record:                                       |  |
|  |  +------------------------------------------------------+  |  |
|  |  | global_uuid    : 550e8400-e29b-41d4-a716-...         |  |  |
|  |  | email          : berk@example.com                     |  |  |
|  |  | password_hash  : bcrypt$12$...                        |  |  |
|  |  | organization   : org-uuid-123                         |  |  |
|  |  | linked_nodes   : [pi-001, mac-home, ...]             |  |  |
|  |  | permissions    : {admin: true, modules: [...]}       |  |  |
|  |  | created_at     : 2025-01-01T00:00:00Z                |  |  |
|  |  +------------------------------------------------------+  |  |
|  |                                                            |  |
|  |  Capabilities:                                             |  |
|  |  - JWT issuer (RS256)                                     |  |
|  |  - Password management                                    |  |
|  |  - Permission management                                  |  |
|  |  - Node registry                                          |  |
|  |  - Cross-node auth                                        |  |
|  +------------------------------------------------------------+  |
|                              |                                    |
|                              v Token                              |
|  +------------------------------------------------------------+  |
|  |                    NODE (Token Verifier)                    |  |
|  |                                                            |  |
|  |  User Local Cache:                                         |  |
|  |  +------------------------------------------------------+  |  |
|  |  | global_uuid      : 550e8400-e29b-41d4-a716-...       |  |  |
|  |  | local_user_id    : 1 (Django FK)                     |  |  |
|  |  | email            : berk@example.com                   |  |  |
|  |  | offline_password : bcrypt$12$... (for offline auth)  |  |  |
|  |  | permissions      : {cached from hub}                 |  |  |
|  |  | cached_at        : 2025-12-04T22:30:00Z              |  |  |
|  |  | cache_valid_until: 2025-12-11T22:30:00Z              |  |  |
|  |  +------------------------------------------------------+  |  |
|  |                                                            |  |
|  |  Capabilities:                                             |  |
|  |  - JWT verifier (RS256 public key)                        |  |
|  |  - Local JWT issuer (offline mode)                        |  |
|  |  - Offline password verification                          |  |
|  |  - Permission caching                                     |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 2.2 User Types

| Type | Hub Account | Local Account | Description |
|------|-------------|---------------|-------------|
| **Hub User** | Yes | Cached | Full hub features, cross-device |
| **Local User** | No | Yes | Node-only, can link later |
| **Guest User** | Optional | Temporary | Limited access, expires |

### 2.3 JWT Token Structure

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "berk@example.com",
  "name": "Berk Hatirli",

  "iss": "hub.unibos.recaria.org",
  "aud": ["*"],

  "iat": 1733347200,
  "exp": 1733433600,

  "org": {
    "id": "org-uuid-123",
    "name": "Hatirli Family",
    "type": "family",
    "role": "owner"
  },

  "permissions": {
    "is_admin": true,
    "modules": {
      "currencies": ["read", "write"],
      "cctv": ["read", "write", "admin"],
      "birlikteyiz": ["read", "write"],
      "documents": ["read", "write", "delete"]
    },
    "nodes": {
      "pi-001": ["full_access"],
      "pi-002": ["read_only"],
      "*": ["basic"]
    }
  },

  "offline_hash": "bcrypt:$2b$12$..."
}
```

---

## 3. Authentication Flows

### 3.1 Flow 1: Online Login (Hub Auth)

```
+----------+     +----------+     +----------+     +----------+
|  Client  |     |   Node   |     |   Hub    |     | Database |
+----+-----+     +----+-----+     +----+-----+     +----+-----+
     |                |                |                |
     | 1. Login (email, password)      |                |
     |-------------------------------->|                |
     |                |                |                |
     |                |                | 2. Verify      |
     |                |                |--------------->|
     |                |                |                |
     |                |                | 3. User Data   |
     |                |                |<---------------|
     |                |                |                |
     | 4. JWT Token + Refresh          |                |
     |<--------------------------------|                |
     |                |                |                |
     | 5. Connect to Node (with JWT)   |                |
     |--------------->|                |                |
     |                |                |                |
     |                | 6. Verify JWT signature         |
     |                |    (using hub public key)       |
     |                |                |                |
     |                | 7. Cache user locally           |
     |                |                |                |
     | 8. Access Granted               |                |
     |<---------------|                |                |
```

### 3.2 Flow 2: Local-Only Login (No Hub Account)

```
+----------+     +----------+
|  Client  |     |   Node   |
+----+-----+     +----+-----+
     |                |
     | 1. Login (email, password)
     |--------------->|
     |                |
     |                | 2. Check local user DB
     |                |    - Find user by email
     |                |    - Verify bcrypt hash
     |                |
     |                | 3. Generate local JWT
     |                |    (signed with node key)
     |                |
     | 4. Local JWT   |
     |<---------------|
     |                |
     | 5. Full local access
     |    (hub features disabled)
```

### 3.3 Flow 3: Offline Login (Cached Hub User)

```
+----------+     +----------+
|  Client  |     |   Node   |
+----+-----+     +----+-----+
     |                |
     | 1. Login (email, password)
     |--------------->|
     |                |
     |                | 2. Try hub -> UNREACHABLE
     |                |
     |                | 3. Check local cache:
     |                |    - Find cached user
     |                |    - Verify offline_password
     |                |    - Check cache validity
     |                |
     |                | 4. Generate offline JWT
     |                |    (marked: offline_session=true)
     |                |
     | 5. Offline JWT |
     |<---------------|
     |                |
     | 6. Access with cached permissions
     |    (will sync when online)
```

### 3.4 Flow 4: Local User Linking to Hub

```
+----------+     +----------+     +----------+
|  Client  |     |   Node   |     |   Hub    |
+----+-----+     +----+-----+     +----+-----+
     |                |                |
     | 1. "Create Hub Account" button  |
     |--------------->|                |
     |                |                |
     |                | 2. Forward request
     |                |    (email, password, local_uuid)
     |                |--------------->|
     |                |                |
     |                |                | 3. Check email:
     |                |                |    EXISTS? -> Verify & link
     |                |                |    NEW? -> Create account
     |                |                |
     |                | 4. Global UUID + Token
     |                |<---------------|
     |                |                |
     |                | 5. Update local user:
     |                |    Map local_id -> global_uuid
     |                |
     | 6. "Account linked!"            |
     |<---------------|                |
     |                |                |
     | 7. Optionally migrate local data
     |    (based on user's export settings)
```

---

## 4. Data Flow Architecture

### 4.1 Data Categories

```
+------------------------------------------------------------------+
|                    DATA CLASSIFICATION                            |
|                                                                   |
|  CATEGORY 1: INCOMING (External -> Node)                         |
|  +------------------------------------------------------------+  |
|  | - Exchange rates (Currencies API)                          |  |
|  | - Earthquake alerts (EMSC WebSocket)                       |  |
|  | - Weather data                                             |  |
|  | - Software updates                                         |  |
|  | Direction: ALWAYS IN                                       |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  CATEGORY 2: LOCAL-ONLY (Never leaves node)                      |
|  +------------------------------------------------------------+  |
|  | - CCTV video recordings                                    |  |
|  | - Media files (movies, music)                              |  |
|  | - Local cache/temp files                                   |  |
|  | - Session data                                             |  |
|  | Direction: NEVER OUT (hardware boundary)                   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  CATEGORY 3: NODE-SHAREABLE (Node <-> Node)                      |
|  +------------------------------------------------------------+  |
|  | - Emergency alerts (broadcast)                             |  |
|  | - Shared documents (explicit share)                        |  |
|  | - Family calendar events                                   |  |
|  | - Presence/status information                              |  |
|  | Direction: P2P (user-controlled)                           |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  CATEGORY 4: HUB-SYNCABLE (Node <-> Hub)                         |
|  +------------------------------------------------------------+  |
|  | - User profiles                                            |  |
|  | - Portfolio data (optional)                                |  |
|  | - Document metadata (optional)                             |  |
|  | - Settings/preferences                                     |  |
|  | Direction: BIDIRECTIONAL (user opt-in)                     |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  CATEGORY 5: SENSITIVE (Extra protection)                        |
|  +------------------------------------------------------------+  |
|  | - Financial transactions (WIMM)                            |  |
|  | - Personal health data                                     |  |
|  | - Location history                                         |  |
|  | - Private documents                                        |  |
|  | Direction: ENCRYPTED + USER-CONTROLLED                     |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 4.2 Data Flow Diagram

```
                        INTERNET
                           |
           +---------------+---------------+
           |                               |
   +-------v-------+               +-------v-------+
   |      HUB      |               |      HUB      |
   |   (Primary)   |<------------->|   (Standby)   |
   +-------+-------+   Replication +---------------+
           |
           | CATEGORY 4 (Opt-in)
           |
   +-------v------------------------------------------+
   |              LOCAL NETWORK (LAN)                  |
   |                                                   |
   |  +----------+    CATEGORY 3    +----------+      |
   |  |  Pi-001  |<--------------->|  Pi-002  |      |
   |  | (Owner)  |    P2P Mesh     | (Family) |      |
   |  +----+-----+                 +----+-----+      |
   |       |                            |            |
   |       |         LoRa Mesh          |            |
   |       +----------------------------+            |
   |                    |                            |
   |            +-------v-------+                    |
   |            |    Pi-003     |                    |
   |            | (No Internet) |                    |
   |            +---------------+                    |
   +--------------------------------------------------+
           |
           | CATEGORY 1 (Always)
           v
      [External APIs]
```

---

## 5. Data Export Control

### 5.1 Master Kill Switch

```
+------------------------------------------------------------------+
|                 DATA EXPORT CONTROL PANEL                         |
|                                                                   |
|  ================================================================ |
|  MASTER KILL SWITCH                                    [OFF]     |
|  ---------------------------------------------------------------- |
|  Tum dis sunucu baglantilari devre disi                          |
|  (Acik oldugunda HICBIR veri disari cikmaz)                      |
|  ================================================================ |
|                                                                   |
|  When ENABLED (ON):                                               |
|  - All outgoing API calls BLOCKED                                |
|  - All sync operations PAUSED                                    |
|  - All hub auth DISABLED (local-only mode)                       |
|  - LoRa/Local mesh STILL WORKS (configurable)                    |
|                                                                   |
|  Emergency Override:                                              |
|  - Birlikteyiz earthquake alerts ALWAYS receive                  |
|  - Can be configured to allow emergency P2P                      |
|                                                                   |
+------------------------------------------------------------------+
```

### 5.2 Module-Level Export Controls

```
+------------------------------------------------------------------+
|                MODULE EXPORT SETTINGS                             |
|                                                                   |
|  CURRENCIES                                                       |
|  +------------------------------------------------------------+  |
|  | [v] Doviz kurlari (API'den al)           <- GELEN veri     |  |
|  | [ ] Portfolyo verileri                   <- CIKAN veri     |  |
|  | [ ] Islem gecmisi                        <- CIKAN veri     |  |
|  | [ ] Favori paralar                       <- CIKAN veri     |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  DOCUMENTS                                                        |
|  +------------------------------------------------------------+  |
|  | [ ] Tum belgeler                                           |  |
|  | [ ] Sadece "shared" isaretli                               |  |
|  | [ ] Metadata only (dosya icerigi haric)                    |  |
|  | [ ] OCR sonuclari                                          |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  WIMM (Where Is My Money)                                        |
|  +------------------------------------------------------------+  |
|  | [ ] Hesap bakiyeleri                     <- HASSAS         |  |
|  | [ ] Islem gecmisi                        <- HASSAS         |  |
|  | [ ] Butce hedefleri                                        |  |
|  | [ ] Kategoriler ve etiketler                               |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  WIMS (Where Is My Stuff)                                        |
|  +------------------------------------------------------------+  |
|  | [ ] Envanter listesi                                       |  |
|  | [ ] Konum bilgileri                                        |  |
|  | [ ] Fotograflar                          ! BUYUK VERI      |  |
|  | [ ] Degerler ve fiyatlar                 <- HASSAS         |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  BIRLIKTEYIZ                                                     |
|  +------------------------------------------------------------+  |
|  | [v] Deprem uyarilari (al)                <- KRITIK/GELEN   |  |
|  | [ ] Konum gecmisi                        <- HASSAS         |  |
|  | [ ] Acil durum kontaklari                                  |  |
|  | [v] Anonim deprem raporu gonder          <- TOPLULUK       |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  CCTV                                                            |
|  +------------------------------------------------------------+  |
|  | [X] Video kayitlari                      ASLA CIKMAZ       |  |
|  | [ ] Event metadata (hareket algilama)                      |  |
|  | [ ] Kamera durumu                                          |  |
|  | [ ] Thumbnail'ler                        ! BUYUK VERI      |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  MOVIES / MUSIC                                                  |
|  +------------------------------------------------------------+  |
|  | [X] Media dosyalari                      ASLA CIKMAZ       |  |
|  | [ ] Izleme/dinleme gecmisi (metadata)                      |  |
|  | [ ] Puanlamalar ve yorumlar                                |  |
|  | [ ] Playlist'ler                                           |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  PERSONAL INFLATION                                              |
|  +------------------------------------------------------------+  |
|  | [ ] Fiyat kayitlari                                        |  |
|  | [ ] Kisisel enflasyon hesaplamalari                        |  |
|  | [v] Anonim fiyat verisi paylas           <- TOPLULUK       |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 5.3 Export Control Logic

```python
class DataExportMiddleware:
    """Middleware to enforce export controls"""

    def process_request(self, request):
        # Skip for incoming data
        if self.is_incoming_data(request):
            return None

        # Check kill switch
        settings = DataExportSettings.get_for_node()
        if settings.master_kill_switch:
            if not self.is_emergency_data(request):
                self.log_blocked(request, 'kill_switch')
                raise ExportBlocked("Master kill switch is enabled")

        # Check module-specific settings
        module = self.get_module(request)
        data_type = self.get_data_type(request)

        if not settings.can_export(module, data_type):
            self.log_blocked(request, 'module_setting')
            raise ExportBlocked(f"Export disabled for {module}.{data_type}")

        # Log successful export
        self.log_export(request)
        return None
```

---

## 6. Sync Engine

### 6.1 Sync Overview

```
+------------------------------------------------------------------+
|                    SYNC ENGINE ARCHITECTURE                        |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                     NODE                                    |  |
|  |                                                            |  |
|  |  +------------------+    +------------------+              |  |
|  |  |  Sync Queue      |    |  Sync Engine     |              |  |
|  |  |------------------|    |------------------|              |  |
|  |  | - Pending ops    |<-->| - Diff calc      |              |  |
|  |  | - Retry queue    |    | - Conflict res   |              |  |
|  |  | - Priority sort  |    | - Apply changes  |              |  |
|  |  +------------------+    +--------+---------+              |  |
|  |                                   |                        |  |
|  +-----------------------------------|------------------------+  |
|                                      |                           |
|                                      v                           |
|  +------------------------------------------------------------+  |
|  |                      HUB                                    |  |
|  |                                                            |  |
|  |  +------------------+    +------------------+              |  |
|  |  |  Sync Registry   |    |  Sync Processor  |              |  |
|  |  |------------------|    |------------------|              |  |
|  |  | - Node states    |<-->| - Version track  |              |  |
|  |  | - Last sync      |    | - Merge logic    |              |  |
|  |  | - Pending pushes |    | - Notify nodes   |              |  |
|  |  +------------------+    +------------------+              |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 6.2 Sync Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Push** | Node -> Hub | User changes data locally |
| **Pull** | Hub -> Node | User logs in on new device |
| **Full Sync** | Bidirectional | Initial setup, recovery |
| **Selective** | Specific modules | User preference |
| **Conflict** | Manual resolution | Same record changed on multiple nodes |

### 6.3 Sync Process

```
+------------------------------------------------------------------+
|                    SYNC PROCESS FLOW                               |
|                                                                   |
|  1. INITIATE                                                       |
|  +------------------------------------------------------------+  |
|  | - Node requests sync                                       |  |
|  | - Hub verifies node identity                               |  |
|  | - Exchange version vectors                                 |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  2. DIFF CALCULATION                                               |
|  +------------------------------------------------------------+  |
|  | - Compare version vectors                                  |  |
|  | - Identify changed records                                 |  |
|  | - Calculate minimal changeset                              |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  3. CONFLICT DETECTION                                             |
|  +------------------------------------------------------------+  |
|  | - Check for same-record changes                            |  |
|  | - Apply auto-resolution rules                              |  |
|  | - Queue manual conflicts                                   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  4. DATA TRANSFER                                                  |
|  +------------------------------------------------------------+  |
|  | - Compress payload                                         |  |
|  | - Encrypt sensitive fields                                 |  |
|  | - Transfer in batches                                      |  |
|  | - Verify checksums                                         |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  5. APPLY CHANGES                                                  |
|  +------------------------------------------------------------+  |
|  | - Transaction wrapper                                      |  |
|  | - Apply in dependency order                                |  |
|  | - Update version vectors                                   |  |
|  | - Notify success/failure                                   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 7. Conflict Resolution

### 7.1 Conflict Scenarios

```
+------------------------------------------------------------------+
|                    CONFLICT SCENARIOS                              |
|                                                                   |
|  Scenario 1: Same Record, Different Nodes                         |
|  +------------------------------------------------------------+  |
|  | Node A: Updates record at 10:00                            |  |
|  | Node B: Updates same record at 10:05                       |  |
|  | Both sync to hub                                           |  |
|  | -> CONFLICT: Which version wins?                           |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Scenario 2: Same Email, Multiple Nodes                           |
|  +------------------------------------------------------------+  |
|  | Pi-001: berk@mail.com local user, 100 records              |  |
|  | Pi-002: berk@mail.com local user, 200 records              |  |
|  | User links both to same hub account                        |  |
|  | -> CONFLICT: Merge or keep separate?                       |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Scenario 3: Offline Edits                                        |
|  +------------------------------------------------------------+  |
|  | Node offline for 1 week                                    |  |
|  | User makes 50 edits offline                                |  |
|  | Hub has 30 edits from other nodes                          |  |
|  | Node comes back online                                     |  |
|  | -> CONFLICT: Reconcile all changes                         |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 7.2 Resolution Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `NEWER_WINS` | Last modified wins | General data |
| `OLDER_WINS` | First created wins | Financial records |
| `LARGER_WINS` | More complete wins | Document merges |
| `MANUAL` | User decides | Important conflicts |
| `MERGE_FIELDS` | Combine non-conflicting | Partial updates |
| `KEEP_BOTH` | Create duplicate | Can't auto-resolve |

### 7.3 Auto-Resolution Rules

```python
CONFLICT_RULES = {
    "currencies.Portfolio": {
        "strategy": "MERGE_FIELDS",
        "id_field": "currency_code",
        "merge_fields": ["amount", "notes"],
        "newer_wins": ["last_updated"],
        "sum_fields": ["total_bought", "total_sold"],
    },

    "documents.Document": {
        "strategy": "KEEP_BOTH",
        "id_field": "checksum",
        "duplicate_suffix": "_conflict_{timestamp}",
    },

    "wimm.Transaction": {
        "strategy": "OLDER_WINS",
        "id_field": "transaction_id",
        "reason": "First entry is authoritative for financial records",
    },

    "birlikteyiz.EmergencyContact": {
        "strategy": "MERGE_FIELDS",
        "id_field": "phone_number",
        "merge_fields": ["name", "relationship", "notes"],
    },
}
```

### 7.4 Same-Email Merge Flow

```
+------------------------------------------------------------------+
|              EMAIL CONFLICT RESOLUTION UI                          |
|                                                                   |
|  "Multiple devices found with your email"                         |
|                                                                   |
|  +------------------------------------------------------------+  |
|  | Pi-001 (Living Room)                                       |  |
|  | - 100 records                                              |  |
|  | - Last active: 2 days ago                                  |  |
|  | [Verify with local password]                               |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  +------------------------------------------------------------+  |
|  | Pi-002 (Bedroom)                                           |  |
|  | - 200 records                                              |  |
|  | - Last active: 1 hour ago                                  |  |
|  | [Verify with local password]                               |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  After verification, choose:                                       |
|                                                                   |
|  ( ) Merge all data (recommended)                                  |
|      -> Combined: 300 records, conflicts auto-resolved            |
|                                                                   |
|  ( ) Keep Pi-001 as primary, import from Pi-002                   |
|      -> Pi-001 preserved, Pi-002 additions imported              |
|                                                                   |
|  ( ) Keep separate (multi-identity)                                |
|      -> Each node keeps own data, hub shows aggregated           |
|                                                                   |
|  [Cancel]                                        [Continue]       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 8. Offline & Local-First

### 8.1 Offline Capabilities Matrix

| Feature | Online | Offline | Notes |
|---------|--------|---------|-------|
| Local login | Yes | Yes | Cached credentials |
| Hub login | Yes | No | Requires internet |
| Module access | Full | Full | All local data |
| Currency rates | Live | Cached | Last known rates |
| Earthquake alerts | Live | Local only | LoRa relay works |
| Document OCR | Yes | Yes | Local processing |
| Node-to-node sync | Yes | Yes (LAN) | WiFi/LoRa |
| Hub sync | Yes | Queued | Syncs when online |
| User management | Yes | Limited | Can't verify hub |
| Backup | Yes | Yes | Local only |

### 8.2 Offline Queue

```python
class OfflineOperation(models.Model):
    """Operations queued for when connectivity returns"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey('nodes.Node', on_delete=models.CASCADE)

    # Operation details
    operation_type = models.CharField(max_length=50)
    # Types: "hub_sync", "hub_auth", "node_sync", "api_call"

    module = models.CharField(max_length=50, blank=True)
    payload = models.JSONField()

    # Priority (1 = highest)
    priority = models.IntegerField(default=5)
    PRIORITY_CRITICAL = 1      # Auth, emergency
    PRIORITY_HIGH = 2          # User-initiated sync
    PRIORITY_NORMAL = 5        # Background sync
    PRIORITY_LOW = 8           # Analytics
    PRIORITY_BACKGROUND = 10   # Updates

    # Status
    status = models.CharField(max_length=20, default='pending')
    # Status: "pending", "processing", "completed", "failed", "cancelled"

    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=5)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True)
    last_attempt = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ['priority', 'created_at']
```

### 8.3 Cache Validity Rules

```python
CACHE_VALIDITY = {
    # Auth caches
    "user_permissions": timedelta(days=7),
    "offline_password": timedelta(days=30),
    "jwt_public_key": timedelta(days=90),

    # Data caches
    "currency_rates": timedelta(hours=1),
    "earthquake_history": timedelta(hours=24),
    "node_registry": timedelta(minutes=5),

    # Never expire (manual invalidation only)
    "local_user_data": None,
    "local_documents": None,
}
```

---

## 9. Node-to-Node Communication

### 9.1 Discovery Mechanisms

#### mDNS (Local Network)

```python
# Service advertisement
SERVICE_TYPE = "_unibos._tcp.local."
SERVICE_NAME = "pi-001._unibos._tcp.local."

# TXT Records
{
    "uuid": "550e8400-e29b-41d4-...",
    "type": "node",
    "version": "1.2.0",
    "modules": "currencies,birlikteyiz,cctv",
    "owner_hash": "sha256:abc123...",  # Privacy
    "capabilities": "websocket,api,lora"
}
```

#### LoRa Beacon

```python
# LoRa discovery packet (max 255 bytes)
{
    "t": "DISC",              # Type: Discovery
    "id": "550e8400",         # Short UUID (8 chars)
    "n": "pi-001",            # Node name
    "c": ["cur", "bir"],      # Modules (abbreviated)
    "rssi": -65,              # Signal strength
    "hop": 0                  # Hop count (mesh)
}
```

### 9.2 P2P Message Protocol

```json
{
  "v": 1,
  "id": "msg-uuid-123",
  "type": "DATA",
  "from": "pi-001-uuid",
  "to": "pi-002-uuid",
  "timestamp": 1733347200,
  "ttl": 3,
  "payload": {
    "module": "birlikteyiz",
    "action": "earthquake_alert",
    "data": {...}
  },
  "signature": "base64..."
}
```

### 9.3 Message Types

| Type | Code | Description |
|------|------|-------------|
| DISCOVERY | `DISC` | Node announcement |
| PING | `PING` | Heartbeat |
| PONG | `PONG` | Heartbeat response |
| AUTH | `AUTH` | Authentication request |
| DATA | `DATA` | Data transfer |
| SYNC | `SYNC` | Sync request |
| EVENT | `EVNT` | Real-time event |
| ACK | `ACK` | Acknowledgment |

### 9.4 Mesh Relay

```
+------------------------------------------------------------------+
|                    MESH DATA RELAY                                |
|                                                                   |
|  Scenario: Pi-003 has no internet, needs earthquake data         |
|                                                                   |
|     INTERNET                                                      |
|        |                                                          |
|  +-----v-----+         WiFi          +----------+                |
|  |  Pi-001   |<--------------------->|  Pi-002  |                |
|  | (Gateway) |                       |          |                |
|  +-----+-----+                       +----+-----+                |
|        |                                  |                       |
|        |              LoRa                |                       |
|        +----------------------------------+                       |
|                       |                                           |
|               +-------v-------+                                   |
|               |    Pi-003     |                                   |
|               | (No Internet) |                                   |
|               +---------------+                                   |
|                                                                   |
|  Flow:                                                            |
|  1. EMSC -> Pi-001: Earthquake alert via WebSocket               |
|  2. Pi-001 -> Pi-002: Relay via WiFi                             |
|  3. Pi-001 -> Pi-003: Relay via LoRa                             |
|  4. Pi-002 -> Pi-003: Redundant relay via LoRa                   |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 10. Privacy & Security

### 10.1 Token Security Layers

```
+------------------------------------------------------------------+
|                    TOKEN SECURITY                                  |
|                                                                   |
|  Layer 1: Transport                                                |
|  +------------------------------------------------------------+  |
|  | - HTTPS everywhere (TLS 1.3)                               |  |
|  | - Certificate pinning (mobile)                             |  |
|  | - HSTS headers                                             |  |
|  | - Local: mTLS optional for node-to-node                    |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Layer 2: Token Signing                                           |
|  +------------------------------------------------------------+  |
|  | - RS256 algorithm (asymmetric)                             |  |
|  | - Hub holds private key                                    |  |
|  | - Nodes have public key (verify only)                      |  |
|  | - Key rotation every 90 days                               |  |
|  | - Local tokens: Ed25519 (per-node key)                     |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Layer 3: Token Validation                                        |
|  +------------------------------------------------------------+  |
|  | - Expiry check (24h access, 7d refresh)                    |  |
|  | - Audience validation                                      |  |
|  | - Issuer validation                                        |  |
|  | - JTI for replay protection                                |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Layer 4: Offline Security                                        |
|  +------------------------------------------------------------+  |
|  | - Offline hash uses bcrypt (cost=12)                       |  |
|  | - Cache expiry (7 days default)                            |  |
|  | - Rate limiting (5 attempts/minute)                        |  |
|  | - Auto cache invalidation on password change               |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 10.2 Data Protection

| State | Method | Details |
|-------|--------|---------|
| At Rest | AES-256 | Sensitive fields encrypted |
| In Transit | TLS 1.3 | All network communication |
| P2P | AES-128 | Message-level encryption |
| LoRa | AES-128 | Radio-level encryption |

### 10.3 Node Trust Levels

```python
class NodeTrustLevel(Enum):
    OWNER = 5       # Node owner, full access
    VERIFIED = 4    # Hub-verified node
    TRUSTED = 3     # Manually trusted by owner
    KNOWN = 2       # Seen before, limited trust
    UNKNOWN = 1     # First contact, minimal trust
    BLOCKED = 0     # Explicitly blocked
```

---

## 11. Database Models

### 11.1 Core Models

```python
# core/system/authentication/backend/models.py

class UserGlobalMapping(models.Model):
    """Maps global user UUID to local Django user"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Global identity (nullable for local-only users)
    global_uuid = models.UUIDField(unique=True, null=True, blank=True)

    # Local reference
    local_user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='global_mapping'
    )

    # Contact info
    email = models.EmailField(db_index=True)
    name = models.CharField(max_length=255, blank=True)

    # Organization (from hub)
    organization_id = models.UUIDField(null=True, blank=True)

    # Cached permissions
    cached_permissions = models.JSONField(default=dict)

    # Offline authentication
    offline_password_hash = models.CharField(max_length=128, blank=True)
    offline_auth_enabled = models.BooleanField(default=True)

    # Cache management
    cached_at = models.DateTimeField(auto_now=True)
    cache_valid_until = models.DateTimeField(null=True)

    # Hub sync
    is_linked_to_hub = models.BooleanField(default=False)
    last_synced_with_hub = models.DateTimeField(null=True)

    class Meta:
        db_table = 'auth_user_global_mapping'


class DataExportSettings(models.Model):
    """Data export control per node"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.OneToOneField('nodes.Node', on_delete=models.CASCADE)

    # Master kill switch
    master_kill_switch = models.BooleanField(default=False)

    # Module settings (JSON)
    module_settings = models.JSONField(default=dict)

    # Advanced
    require_confirmation = models.BooleanField(default=True)
    log_all_exports = models.BooleanField(default=True)
    new_modules_default_off = models.BooleanField(default=True)
    allow_local_mesh = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'data_export_settings'


class DataExportLog(models.Model):
    """Audit log for data exports"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey('nodes.Node', on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)
    module = models.CharField(max_length=50)
    data_type = models.CharField(max_length=100)

    destination_type = models.CharField(max_length=20)
    destination_id = models.CharField(max_length=100)

    record_count = models.IntegerField()
    size_bytes = models.BigIntegerField()

    status = models.CharField(max_length=20)
    error_message = models.TextField(blank=True)

    user = models.ForeignKey(UserGlobalMapping, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'data_export_log'
        ordering = ['-timestamp']


class ConflictRecord(models.Model):
    """Track data conflicts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    module = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)

    local_record_id = models.CharField(max_length=100)
    remote_record_id = models.CharField(max_length=100)

    local_data = models.JSONField()
    remote_data = models.JSONField()

    local_timestamp = models.DateTimeField()
    remote_timestamp = models.DateTimeField()

    local_node = models.ForeignKey('nodes.Node', on_delete=models.CASCADE)
    remote_source = models.CharField(max_length=100)

    strategy = models.CharField(max_length=20, blank=True)
    resolved = models.BooleanField(default=False)
    resolution_data = models.JSONField(null=True)
    resolved_by = models.ForeignKey(UserGlobalMapping, null=True, on_delete=models.SET_NULL)
    resolved_at = models.DateTimeField(null=True)

    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_conflict_record'
```

---

## 12. API Specifications

### 12.1 Hub Auth API

```yaml
# POST /api/v1/auth/register/
request:
  email: string (required)
  password: string (required, min 8)
  name: string (optional)
  organization_name: string (optional)

response:
  user:
    uuid: string
    email: string
    name: string
  organization:
    id: string
    name: string
  tokens:
    access: string (24h)
    refresh: string (7d)
  offline_hash: string

# POST /api/v1/auth/login/
request:
  email: string
  password: string

response:
  user: {...}
  organization: {...}
  tokens: {...}
  offline_hash: string

# POST /api/v1/auth/refresh/
request:
  refresh: string

response:
  access: string
  refresh: string (optional rotation)

# POST /api/v1/auth/link-node/
headers:
  Authorization: Bearer <token>
request:
  node_uuid: string
  node_name: string
  local_user_uuid: string (optional)

response:
  linked: boolean
  merged_records: integer
  conflicts: array
```

### 12.2 Node Auth API

```yaml
# POST /api/v1/local/auth/register/
request:
  email: string (required)
  password: string (required)
  name: string (optional)

response:
  user:
    local_id: integer
    email: string
    uuid: string (local)
  token: string (local JWT)

# POST /api/v1/local/auth/login/
request:
  email: string
  password: string

response:
  user: {...}
  token: string
  is_offline: boolean

# POST /api/v1/local/auth/link-hub/
request:
  hub_token: string

response:
  linked: boolean
  global_uuid: string
  merge_result: object
```

### 12.3 Sync API

```yaml
# POST /api/v1/sync/init/
request:
  node_uuid: string
  version_vector: object
  modules: array

response:
  sync_id: string
  hub_version: object
  changes_available: integer

# POST /api/v1/sync/pull/
request:
  sync_id: string
  batch_size: integer

response:
  records: array
  has_more: boolean
  conflicts: array

# POST /api/v1/sync/push/
request:
  sync_id: string
  records: array

response:
  accepted: integer
  rejected: array
  conflicts: array
```

---

## 13. Mobile Integration

### 13.1 Auth Service (Flutter)

```dart
class AuthService {
  final Dio _hubClient;
  final FlutterSecureStorage _storage;

  String? _accessToken;
  String? _refreshToken;
  UnibosUser? _currentUser;
  bool _isOffline = false;

  /// Login with hub account
  Future<AuthResult> loginHub(String email, String password) async {
    try {
      final response = await _hubClient.post('/api/v1/auth/login/', data: {
        'email': email,
        'password': password,
      });

      _accessToken = response.data['tokens']['access'];
      _refreshToken = response.data['tokens']['refresh'];
      _currentUser = UnibosUser.fromJson(response.data['user']);
      _isOffline = false;

      await _storage.write(key: 'access_token', value: _accessToken);
      await _storage.write(key: 'refresh_token', value: _refreshToken);
      await _storage.write(key: 'offline_hash', value: response.data['offline_hash']);

      return AuthResult.success(_currentUser!);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError) {
        return _attemptOfflineLogin(email, password);
      }
      return AuthResult.failure(e.message ?? 'Login failed');
    }
  }

  /// Login to local node directly
  Future<AuthResult> loginLocal(String nodeUrl, String email, String password) async {
    final nodeClient = Dio(BaseOptions(baseUrl: nodeUrl));
    final response = await nodeClient.post('/api/v1/local/auth/login/', data: {
      'email': email,
      'password': password,
    });

    _accessToken = response.data['token'];
    _currentUser = UnibosUser.fromJson(response.data['user']);
    _isOffline = response.data['is_offline'] ?? false;

    return AuthResult.success(_currentUser!, isOffline: _isOffline);
  }

  /// Offline login with cached credentials
  Future<AuthResult> _attemptOfflineLogin(String email, String password) async {
    final cachedUser = await _storage.read(key: 'user_data');
    final offlineHash = await _storage.read(key: 'offline_hash');

    if (cachedUser == null || offlineHash == null) {
      return AuthResult.failure('No cached credentials');
    }

    final user = UnibosUser.fromJson(jsonDecode(cachedUser));
    if (user.email != email) {
      return AuthResult.failure('Email mismatch');
    }

    if (!_verifyOfflinePassword(password, offlineHash)) {
      return AuthResult.failure('Invalid password');
    }

    _currentUser = user;
    _isOffline = true;
    return AuthResult.success(user, isOffline: true);
  }
}
```

### 13.2 Node Discovery (Flutter)

```dart
class NodeDiscoveryService {
  static const String SERVICE_TYPE = '_unibos._tcp';

  final List<DiscoveredNode> _discoveredNodes = [];
  final StreamController<List<DiscoveredNode>> _nodesController =
      StreamController.broadcast();

  Stream<List<DiscoveredNode>> get nodesStream => _nodesController.stream;

  Future<void> startDiscovery() async {
    final MDnsClient client = MDnsClient();
    await client.start();

    await for (final PtrResourceRecord ptr in client.lookup<PtrResourceRecord>(
      ResourceRecordQuery.serverPointer(SERVICE_TYPE),
    )) {
      // Parse node info from TXT records
      final node = await _parseNode(client, ptr);
      _addOrUpdateNode(node);
    }
  }

  void _addOrUpdateNode(DiscoveredNode node) {
    final existingIndex = _discoveredNodes.indexWhere((n) => n.uuid == node.uuid);
    if (existingIndex >= 0) {
      _discoveredNodes[existingIndex] = node;
    } else {
      _discoveredNodes.add(node);
    }
    _nodesController.add(_discoveredNodes);
  }
}
```

---

## 14. Implementation Phases

### Phase 1: Local Identity (Week 1-2)

```
[ ] 1.1 User Model Enhancement
    [ ] Add global_uuid field (nullable)
    [ ] Add email requirement
    [ ] Add offline_password_hash
    [ ] Migration scripts

[ ] 1.2 Local Authentication
    [ ] Email-based registration
    [ ] Password hashing (bcrypt)
    [ ] Local JWT generation
    [ ] Session management

[ ] 1.3 Node Setup Wizard
    [ ] Owner creation step
    [ ] Email validation
    [ ] Initial permissions

[ ] 1.4 Database Models
    [ ] UserGlobalMapping
    [ ] DataExportSettings
    [ ] DataExportLog
```

### Phase 2: Hub Integration (Week 3-4)

```
[ ] 2.1 Hub Auth Endpoints
    [ ] POST /auth/register/
    [ ] POST /auth/login/
    [ ] POST /auth/refresh/
    [ ] POST /auth/link-node/

[ ] 2.2 Federated Auth (Nodes)
    [ ] JWT verification (RS256)
    [ ] Hub token validation
    [ ] Local cache fallback
    [ ] User mapping

[ ] 2.3 Account Linking
    [ ] Email verification
    [ ] Local-to-hub linking
    [ ] Conflict detection
    [ ] Merge UI

[ ] 2.4 Permission Sync
    [ ] Permission propagation
    [ ] WebSocket notifications
    [ ] Cache invalidation
```

### Phase 3: Data Export Control (Week 5-6)

```
[ ] 3.1 Export Settings UI
    [ ] Kill switch toggle
    [ ] Module toggles
    [ ] Granular controls
    [ ] Settings persistence

[ ] 3.2 Export Middleware
    [ ] Request interception
    [ ] Permission check
    [ ] Logging
    [ ] Blocking logic

[ ] 3.3 Audit System
    [ ] Export logging
    [ ] Log viewer UI
    [ ] Reports
```

### Phase 4: Sync Engine (Week 7-8)

```
[ ] 4.1 Sync Core
    [ ] Version vectors
    [ ] Diff calculation
    [ ] Batch transfer

[ ] 4.2 Conflict Resolution
    [ ] Auto-resolution rules
    [ ] Manual resolution UI
    [ ] Merge execution

[ ] 4.3 Offline Queue
    [ ] Queue management
    [ ] Priority handling
    [ ] Retry logic
```

### Phase 5: P2P Communication (Week 9-10)

```
[ ] 5.1 Discovery
    [ ] mDNS advertisement
    [ ] mDNS scanner
    [ ] Node registry

[ ] 5.2 P2P Protocol
    [ ] Message format
    [ ] WebSocket transport
    [ ] Message signing

[ ] 5.3 LoRa Integration (Optional)
    [ ] LoRa beacon
    [ ] Mesh routing
    [ ] Emergency alerts
```

### Phase 6: Mobile Integration (Week 11-12)

```
[ ] 6.1 Auth Service (Flutter)
    [ ] Hub login
    [ ] Local login
    [ ] Offline login
    [ ] Token management

[ ] 6.2 Node Connection
    [ ] Node discovery
    [ ] Connection management
    [ ] Auto-reconnect

[ ] 6.3 Data Sync
    [ ] Sync status UI
    [ ] Conflict resolution UI
    [ ] Export settings UI
```

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Hub** | Identity provider and sync coordinator |
| **Node** | Local data server |
| **Global UUID** | User ID from hub |
| **Local UUID** | User ID on node |
| **Kill Switch** | Master export blocker |
| **Mesh** | Node-to-node network |
| **LoRa** | Long Range radio |
| **mDNS** | Multicast DNS discovery |
| **JWT** | JSON Web Token |
| **Offline Hash** | Cached password for offline auth |

---

## Appendix B: Configuration

### Node Data Flow Configuration

```json
{
  "export": {
    "master_kill_switch": false,
    "require_confirmation": true,
    "log_all_exports": true,
    "new_modules_default_off": true,
    "allow_local_mesh": true,
    "emergency_bypass": ["birlikteyiz.earthquake_alerts"]
  },
  "sync": {
    "enabled": true,
    "interval_minutes": 15,
    "hub_url": "https://unibos.recaria.org",
    "modules": ["currencies", "birlikteyiz"],
    "conflict_strategy": "newer_wins"
  },
  "p2p": {
    "mdns_enabled": true,
    "lora_enabled": false,
    "auto_relay": true,
    "trusted_nodes": ["pi-002-uuid", "pi-003-uuid"]
  }
}
```

---

**Document Version:** 2.0.0
**Last Updated:** 2025-12-05
**Author:** Claude (AI Assistant) based on Berk Hatirli's specifications
**Previous Versions:** See archive/planning/TODO_DATA_PROCESS_v1.0.0.md
