"""
P2P Discovery Service

mDNS-based node discovery for local network and WiFi Direct.
Uses Zeroconf library for cross-platform support.
"""

import socket
import logging
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

try:
    from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, ServiceInfo
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    # Define dummy base class if zeroconf not available
    class ServiceListener:
        pass
    ServiceInfo = None
    ServiceBrowser = None
    Zeroconf = None

logger = logging.getLogger(__name__)


# UNIBOS mDNS service type
SERVICE_TYPE = "_unibos._tcp.local."


@dataclass
class DiscoveredNode:
    """Represents a discovered UNIBOS node"""
    node_id: str
    hostname: str
    addresses: List[Dict[str, any]] = field(default_factory=list)
    port: int = 8000
    version: str = ""
    platform: str = ""
    node_type: str = "node"
    capabilities: Dict = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    discovery_method: str = "mdns"

    def get_primary_address(self) -> Optional[str]:
        """Get primary IP address (prefer non-link-local)"""
        for addr in self.addresses:
            ip = addr.get('ip', '')
            # Prefer non-link-local addresses
            if ip and not ip.startswith('169.254.') and not ip.startswith('fe80:'):
                return ip
        # Fallback to first address
        if self.addresses:
            return self.addresses[0].get('ip')
        return None


class UNIBOSServiceListener(ServiceListener):
    """
    Zeroconf service listener for UNIBOS nodes.
    """

    def __init__(self, on_discovered: Callable[[DiscoveredNode], None] = None,
                 on_removed: Callable[[str], None] = None,
                 on_updated: Callable[[DiscoveredNode], None] = None):
        self.on_discovered = on_discovered
        self.on_removed = on_removed
        self.on_updated = on_updated
        self.discovered_nodes: Dict[str, DiscoveredNode] = {}
        self._lock = threading.Lock()

    def _parse_txt_records(self, info: ServiceInfo) -> Dict[str, str]:
        """Parse TXT records from service info"""
        txt = {}
        if info.properties:
            for key, value in info.properties.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                txt[key] = value
        return txt

    def _build_node(self, name: str, info: ServiceInfo) -> DiscoveredNode:
        """Build DiscoveredNode from ServiceInfo"""
        txt = self._parse_txt_records(info)

        # Get all addresses
        addresses = []
        for addr in info.addresses:
            ip = socket.inet_ntoa(addr)
            addresses.append({
                'ip': ip,
                'port': info.port,
                'interface': 'unknown'
            })

        # Also check parsed_addresses (IPv6 etc)
        if hasattr(info, 'parsed_addresses'):
            for addr in info.parsed_addresses():
                if addr not in [a['ip'] for a in addresses]:
                    addresses.append({
                        'ip': addr,
                        'port': info.port,
                        'interface': 'unknown'
                    })

        return DiscoveredNode(
            node_id=txt.get('node_id', txt.get('id', '')),
            hostname=name.replace(f'.{SERVICE_TYPE}', '').replace('UNIBOS Node on ', ''),
            addresses=addresses,
            port=info.port,
            version=txt.get('version', ''),
            platform=txt.get('platform', ''),
            node_type=txt.get('type', 'node'),
            capabilities={
                'has_gpu': txt.get('has_gpu', 'false').lower() == 'true',
                'has_camera': txt.get('has_camera', 'false').lower() == 'true',
                'modules': txt.get('modules', '').split(',') if txt.get('modules') else []
            },
            discovery_method='mdns'
        )

    def add_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a new service is discovered"""
        info = zc.get_service_info(service_type, name)
        if info:
            node = self._build_node(name, info)
            with self._lock:
                self.discovered_nodes[name] = node

            logger.info(f"Discovered UNIBOS node: {node.hostname} at {node.get_primary_address()}")

            if self.on_discovered:
                self.on_discovered(node)

    def remove_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a service is removed"""
        with self._lock:
            if name in self.discovered_nodes:
                node = self.discovered_nodes.pop(name)
                logger.info(f"Node removed: {node.hostname}")

                if self.on_removed:
                    self.on_removed(name)

    def update_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a service is updated"""
        info = zc.get_service_info(service_type, name)
        if info:
            node = self._build_node(name, info)
            node.last_seen = datetime.now()

            with self._lock:
                if name in self.discovered_nodes:
                    # Preserve discovered_at
                    node.discovered_at = self.discovered_nodes[name].discovered_at
                self.discovered_nodes[name] = node

            logger.debug(f"Node updated: {node.hostname}")

            if self.on_updated:
                self.on_updated(node)


class P2PDiscoveryService:
    """
    Main P2P discovery service.

    Manages mDNS service advertisement and discovery.
    Supports multiple network interfaces (Ethernet + WiFi).
    """

    def __init__(self, node_id: str, hostname: str, port: int = 8000,
                 version: str = "", platform: str = ""):
        self.node_id = node_id
        self.hostname = hostname
        self.port = port
        self.version = version
        self.platform = platform

        self.zeroconf: Optional[Zeroconf] = None
        self.browser: Optional[ServiceBrowser] = None
        self.service_info: Optional[ServiceInfo] = None
        self.listener: Optional[UNIBOSServiceListener] = None

        self._running = False
        self._lock = threading.Lock()

        # Callbacks
        self.on_peer_discovered: Optional[Callable[[DiscoveredNode], None]] = None
        self.on_peer_removed: Optional[Callable[[str], None]] = None

    def _get_local_addresses(self) -> List[bytes]:
        """Get all local IP addresses for advertisement"""
        addresses = []

        # Get all network interfaces using ifaddr (zeroconf dependency)
        try:
            import ifaddr
            for adapter in ifaddr.get_adapters():
                for ip in adapter.ips:
                    # IPv4 addresses only
                    if isinstance(ip.ip, str) and not ip.ip.startswith('127.'):
                        try:
                            addresses.append(socket.inet_aton(ip.ip))
                        except socket.error:
                            pass
        except ImportError:
            # Fallback: use socket to get primary address
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
                s.close()
                addresses.append(socket.inet_aton(ip))
            except Exception:
                pass

        # Also try hostname resolution as fallback
        if not addresses:
            try:
                hostname = socket.gethostname()
                for ip in socket.gethostbyname_ex(hostname)[2]:
                    if not ip.startswith('127.'):
                        addr = socket.inet_aton(ip)
                        if addr not in addresses:
                            addresses.append(addr)
            except Exception:
                pass

        return addresses

    def start(self, register_service: bool = True):
        """
        Start discovery service and optionally advertise this node.

        Args:
            register_service: If True, register mDNS service. Set to False if avahi
                            is already advertising (to avoid NonUniqueNameException).
        """
        if not ZEROCONF_AVAILABLE:
            logger.error("Zeroconf not available. Install with: pip install zeroconf")
            return False

        with self._lock:
            if self._running:
                return True

            try:
                # Create Zeroconf instance
                self.zeroconf = Zeroconf()

                # Only register service if requested and avahi isn't handling it
                if register_service:
                    # Get local addresses
                    addresses = self._get_local_addresses()
                    if not addresses:
                        logger.warning("No local addresses found for mDNS advertisement")

                    # Create service info for advertisement
                    properties = {
                        b'node_id': self.node_id.encode(),
                        b'version': self.version.encode(),
                        b'platform': self.platform.encode(),
                        b'type': b'node',
                    }

                    service_name = f"UNIBOS Node on {self.hostname}.{SERVICE_TYPE}"
                    self.service_info = ServiceInfo(
                        SERVICE_TYPE,
                        service_name,
                        port=self.port,
                        properties=properties,
                        addresses=addresses,
                    )

                    try:
                        # Register our service
                        self.zeroconf.register_service(self.service_info)
                        logger.info(f"Registered mDNS service: {service_name}")
                    except Exception as e:
                        # Service might already be registered by avahi
                        if "NonUniqueNameException" in str(type(e).__name__):
                            logger.info("mDNS service already registered (likely by avahi), using browse-only mode")
                            self.service_info = None
                        else:
                            raise

                # Create listener for discovery
                self.listener = UNIBOSServiceListener(
                    on_discovered=self._on_peer_discovered,
                    on_removed=self._on_peer_removed,
                    on_updated=self._on_peer_updated
                )

                # Start browsing for other nodes
                self.browser = ServiceBrowser(self.zeroconf, SERVICE_TYPE, self.listener)
                logger.info("Started P2P discovery service (browse mode)")

                self._running = True
                return True

            except Exception as e:
                logger.error(f"Failed to start discovery service: {e}", exc_info=True)
                self.stop()
                return False

    def stop(self):
        """Stop discovery service"""
        with self._lock:
            if not self._running:
                return

            try:
                if self.service_info and self.zeroconf:
                    self.zeroconf.unregister_service(self.service_info)

                if self.browser:
                    self.browser.cancel()
                    self.browser = None

                if self.zeroconf:
                    self.zeroconf.close()
                    self.zeroconf = None

                logger.info("Stopped P2P discovery service")

            except Exception as e:
                logger.error(f"Error stopping discovery service: {e}")

            finally:
                self._running = False

    def _on_peer_discovered(self, node: DiscoveredNode):
        """Handle peer discovery"""
        # Skip self
        if node.node_id == self.node_id:
            return

        logger.info(f"Peer discovered: {node.hostname} ({node.get_primary_address()})")

        if self.on_peer_discovered:
            self.on_peer_discovered(node)

    def _on_peer_removed(self, name: str):
        """Handle peer removal"""
        logger.info(f"Peer removed: {name}")

        if self.on_peer_removed:
            self.on_peer_removed(name)

    def _on_peer_updated(self, node: DiscoveredNode):
        """Handle peer update"""
        if node.node_id == self.node_id:
            return

        logger.debug(f"Peer updated: {node.hostname}")

    def get_discovered_peers(self) -> List[DiscoveredNode]:
        """Get list of currently discovered peers"""
        if not self.listener:
            return []

        with self.listener._lock:
            # Filter out self
            return [
                node for node in self.listener.discovered_nodes.values()
                if node.node_id != self.node_id
            ]

    def is_running(self) -> bool:
        """Check if service is running"""
        return self._running


# Singleton instance
_discovery_service: Optional[P2PDiscoveryService] = None


def get_discovery_service() -> Optional[P2PDiscoveryService]:
    """Get the global discovery service instance"""
    return _discovery_service


def init_discovery_service(node_id: str, hostname: str, port: int = 8000,
                           version: str = "", platform: str = "") -> P2PDiscoveryService:
    """Initialize the global discovery service"""
    global _discovery_service

    if _discovery_service is None:
        _discovery_service = P2PDiscoveryService(
            node_id=node_id,
            hostname=hostname,
            port=port,
            version=version,
            platform=platform
        )

    return _discovery_service
