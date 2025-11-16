#!/usr/bin/env python3
"""
Quick test to verify TUI launches and handlers work
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

def test_handler_simulation():
    """Simulate handler calls to verify they work without exiting"""
    from core.profiles.dev.tui import UnibosDevTUI
    from core.clients.cli.framework.ui import MenuItem

    print("Testing TUI handler simulations...\n")

    tui = UnibosDevTUI()

    # Test a few key handlers
    test_items = [
        MenuItem(id='dev_logs', label='view logs', description='Test', enabled=True),
        MenuItem(id='git_status', label='git status', description='Test', enabled=True),
        MenuItem(id='platform_identity', label='node identity', description='Test', enabled=True)
    ]

    for item in test_items:
        print(f"Testing handler: {item.id}")
        try:
            # Call handler - it should update content buffer
            result = tui.handle_action(item)

            if result:
                # Check that content buffer was updated
                if tui.content_buffer['lines']:
                    print(f"  ✅ Handler '{item.id}' updated content buffer")
                    print(f"     Title: {tui.content_buffer['title']}")
                    print(f"     Lines: {len(tui.content_buffer['lines'])} lines")
                else:
                    print(f"  ⚠️  Handler '{item.id}' did not update content buffer")
            else:
                print(f"  ❌ Handler '{item.id}' returned False (would exit TUI)")

        except Exception as e:
            print(f"  ❌ Handler '{item.id}' error: {e}")

        print()

    print("\n✅ Handler simulation complete!")
    print("\nTo test the actual TUI:")
    print("Run: unibos-dev interactive")
    print("\nAll menu items should now display their output in the right content area.")

if __name__ == "__main__":
    test_handler_simulation()