"""
UNIBOS Node Interactive Mode
Interactive TUI mode for standalone nodes

Implements node-specific menu structure and actions for:
- Standalone/offline operation (raspberry pi, local mac)
- P2P mesh networking
- Local service management
- Sync with central server (when online)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.clients.cli.framework.interactive import InteractiveMode
from core.clients.cli.framework.ui import MenuItem, Colors
from core.version import __version__


class UnibosNodeInteractive(InteractiveMode):
    """
    Interactive mode for unibos (node) CLI

    Provides TUI interface for standalone node operations:
    - Local service management
    - P2P mesh networking
    - Module management
    - Sync with server (optional)
    """

    def __init__(self):
        super().__init__(
            title="unibos node",
            version=__version__
        )

    def get_sections(self):
        """
        Get menu sections for unibos node

        Returns:
            List of section dicts with menu items
        """
        return [
            {
                'id': 'node',
                'label': 'node management',
                'icon': '=�',
                'items': [
                    MenuItem(
                        id='node_status',
                        label='node status',
                        icon='=�',
                        description='show node health, services, and system info'
                    ),
                    MenuItem(
                        id='node_identity',
                        label='node identity',
                        icon='=',
                        description='show node uuid, name, and network info'
                    ),
                    MenuItem(
                        id='node_services',
                        label='local services',
                        icon='�',
                        description='manage local django, postgresql, redis'
                    ),
                    MenuItem(
                        id='node_web',
                        label='web interface',
                        icon='<',
                        description='start/stop local web ui'
                    ),
                ]
            },
            {
                'id': 'p2p',
                'label': 'p2p network',
                'icon': '=',
                'items': [
                    MenuItem(
                        id='p2p_discover',
                        label='discover peers',
                        icon='=',
                        description='scan local network for other unibos nodes'
                    ),
                    MenuItem(
                        id='p2p_peers',
                        label='connected peers',
                        icon='=e',
                        description='list all connected peer nodes'
                    ),
                    MenuItem(
                        id='p2p_broadcast',
                        label='broadcast message',
                        icon='=�',
                        description='send message to all peers in network'
                    ),
                    MenuItem(
                        id='p2p_mesh_status',
                        label='mesh status',
                        icon='=x',
                        description='show mesh network topology and health'
                    ),
                ]
            },
            {
                'id': 'modules',
                'label': 'modules',
                'icon': '=�',
                'items': [
                    MenuItem(
                        id='mod_list',
                        label='installed modules',
                        icon='=�',
                        description='show all installed modules and their status'
                    ),
                    MenuItem(
                        id='mod_start',
                        label='start module',
                        icon='�',
                        description='start a specific module'
                    ),
                    MenuItem(
                        id='mod_stop',
                        label='stop module',
                        icon='�',
                        description='stop a running module'
                    ),
                    MenuItem(
                        id='mod_config',
                        label='module config',
                        icon='�',
                        description='configure module settings'
                    ),
                ]
            },
            {
                'id': 'sync',
                'label': 'server sync',
                'icon': '=',
                'items': [
                    MenuItem(
                        id='sync_status',
                        label='sync status',
                        icon='=�',
                        description='show connection status to central server'
                    ),
                    MenuItem(
                        id='sync_now',
                        label='sync now',
                        icon='=',
                        description='manually trigger sync with server'
                    ),
                    MenuItem(
                        id='sync_queue',
                        label='offline queue',
                        icon='=�',
                        description='show queued operations waiting for sync'
                    ),
                    MenuItem(
                        id='sync_config',
                        label='sync settings',
                        icon='�',
                        description='configure sync frequency and options'
                    ),
                ]
            }
        ]

    def handle_action(self, item: MenuItem) -> bool:
        """
        Handle menu item action

        Args:
            item: Selected menu item

        Returns:
            True to continue menu loop, False to exit
        """
        import subprocess
        import os
        from core.clients.cli.framework.ui import clear_screen, Colors

        clear_screen()
        print(f"{Colors.ORANGE}{Colors.BOLD}� {item.label}{Colors.RESET}\n")

        try:
            # Node management
            if item.id == 'node_status':
                print(f"{Colors.DIM}checking node status...{Colors.RESET}\n")
                subprocess.run(['unibos', 'status'], check=True)

            elif item.id == 'node_identity':
                subprocess.run(['unibos', 'identity'], check=True)

            elif item.id == 'node_services':
                print(f"{Colors.DIM}local services status...{Colors.RESET}\n")
                subprocess.run(['systemctl', '--user', 'status', 'unibos-web', 'unibos-db'], check=False)

            elif item.id == 'node_web':
                print(f"{Colors.YELLOW}start or stop? (start/stop):{Colors.RESET} ", end='')
                action = input().strip().lower()
                if action in ['start', 'stop']:
                    subprocess.run(['systemctl', '--user', action, 'unibos-web'], check=True)

            # P2P network
            elif item.id == 'p2p_discover':
                print(f"{Colors.DIM}scanning local network for peers...{Colors.RESET}\n")
                # TODO: Implement P2P discovery
                print(f"{Colors.DIM}p2p discovery not yet implemented{Colors.RESET}")

            elif item.id == 'p2p_peers':
                print(f"{Colors.CYAN}connected peers:{Colors.RESET}\n")
                # TODO: Implement peer list
                print(f"{Colors.DIM}peer management not yet implemented{Colors.RESET}")

            # Module management
            elif item.id == 'mod_list':
                subprocess.run(['unibos', 'modules', 'list'], check=True)

            elif item.id == 'mod_start':
                print(f"{Colors.YELLOW}module name:{Colors.RESET} ", end='')
                module = input().strip()
                if module:
                    subprocess.run(['unibos', 'modules', 'start', module], check=True)

            # Sync management
            elif item.id == 'sync_status':
                print(f"{Colors.CYAN}server sync status:{Colors.RESET}\n")
                # TODO: Implement sync status
                print(f"{Colors.DIM}sync not yet implemented{Colors.RESET}")

            elif item.id == 'sync_now':
                print(f"{Colors.DIM}triggering sync with server...{Colors.RESET}\n")
                # TODO: Implement manual sync
                print(f"{Colors.DIM}sync not yet implemented{Colors.RESET}")

            else:
                print(f"{Colors.YELLOW}� action not yet implemented: {item.id}{Colors.RESET}")

        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.RED}L command failed with exit code {e.returncode}{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}� interrupted{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}L error: {e}{Colors.RESET}")

        # Pause before returning to menu
        print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
        input()

        return True  # Continue menu loop


def run_interactive():
    """Run unibos node in interactive mode"""
    interactive = UnibosNodeInteractive()
    interactive.run(show_splash=True)
