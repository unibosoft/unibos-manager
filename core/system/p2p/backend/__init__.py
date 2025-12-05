"""
UNIBOS P2P Communication System

Provides:
- mDNS discovery for local network node detection
- WebSocket transport for direct node-to-node communication
- Message signing for secure P2P messaging
- Dual-path routing: Hub relay or direct P2P
"""

default_app_config = 'core.system.p2p.backend.apps.P2PConfig'
