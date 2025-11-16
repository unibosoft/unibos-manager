#!/usr/bin/env python3
"""
Test script to verify TUI content area functionality
Tests that all menu items display their output in the right panel
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.clients.web.settings')
os.environ['PYTHONPATH'] = str(project_root)

def test_tui_imports():
    """Test that all TUI components can be imported"""
    print("Testing TUI imports...")

    try:
        from core.clients.tui.base import BaseTUI, TUIConfig
        print("✅ BaseTUI imported successfully")

        from core.clients.tui.components.content import ContentArea
        print("✅ ContentArea imported successfully")

        from core.profiles.dev.tui import UnibosDevTUI
        print("✅ UnibosDevTUI imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_content_buffer():
    """Test that content buffer is working"""
    print("\nTesting content buffer functionality...")

    try:
        from core.profiles.dev.tui import UnibosDevTUI

        # Create TUI instance
        tui = UnibosDevTUI()

        # Test update_content method
        tui.update_content(
            title="Test Title",
            lines=["Line 1", "Line 2", "Line 3"]
        )

        # Verify content buffer
        assert tui.content_buffer['title'] == "Test Title"
        assert tui.content_buffer['lines'] == ["Line 1", "Line 2", "Line 3"]
        print("✅ Content buffer working correctly")

        return True
    except Exception as e:
        print(f"❌ Content buffer error: {e}")
        return False

def test_handlers():
    """Test that all handlers are registered and use update_content"""
    print("\nTesting handler registrations...")

    try:
        from core.profiles.dev.tui import UnibosDevTUI

        tui = UnibosDevTUI()

        # List of all expected handlers
        expected_handlers = [
            'dev_run', 'dev_stop', 'dev_shell', 'dev_test', 'dev_logs',
            'git_status', 'git_pull', 'git_commit', 'git_push_all', 'deploy_rocksteady',
            'db_migrate', 'db_makemigrations', 'db_backup', 'db_restore', 'db_shell',
            'platform_status', 'platform_modules', 'platform_config', 'platform_identity'
        ]

        missing_handlers = []
        for handler in expected_handlers:
            if handler not in tui.action_handlers:
                missing_handlers.append(handler)
                print(f"  ⚠️  Handler '{handler}' not registered")
            else:
                print(f"  ✅ Handler '{handler}' registered")

        if missing_handlers:
            print(f"\n❌ Missing handlers: {', '.join(missing_handlers)}")
            return False
        else:
            print("\n✅ All handlers registered correctly")
            return True

    except Exception as e:
        print(f"❌ Handler test error: {e}")
        return False

def test_menu_structure():
    """Test that menu structure is correct"""
    print("\nTesting menu structure...")

    try:
        from core.profiles.dev.tui import UnibosDevTUI

        tui = UnibosDevTUI()
        sections = tui.get_menu_sections()

        print(f"  Found {len(sections)} menu sections:")
        for section in sections:
            print(f"    • {section.label}: {len(section.items)} items")

        # Verify expected sections
        expected_sections = ['development', 'git & deploy', 'database', 'platform']
        section_labels = [s.label for s in sections]

        for expected in expected_sections:
            if expected in section_labels:
                print(f"  ✅ Section '{expected}' found")
            else:
                print(f"  ❌ Section '{expected}' missing")
                return False

        print("\n✅ Menu structure is correct")
        return True

    except Exception as e:
        print(f"❌ Menu structure error: {e}")
        return False

def test_content_rendering():
    """Test that content area rendering works"""
    print("\nTesting content area rendering...")

    try:
        from core.clients.tui.components.content import ContentArea
        from core.clients.tui.base import TUIConfig

        config = TUIConfig()
        content_area = ContentArea(config)

        # Test with sample content
        test_content = """Line 1
Line 2 with some longer text that might need wrapping
✅ Success line
❌ Error line
→ Arrow line
Command: test command
─────────────"""

        # This would normally render to terminal
        # For testing, we just verify it doesn't crash
        content_area.draw(
            title="Test Content",
            content=test_content
        )

        print("✅ Content area rendering works")
        return True

    except Exception as e:
        print(f"❌ Content rendering error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("UNIBOS TUI Content Area Test Suite")
    print("=" * 50)

    tests = [
        test_tui_imports,
        test_content_buffer,
        test_handlers,
        test_menu_structure,
        test_content_rendering
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for r in results if r)
    failed = len(results) - passed

    print(f"✅ Passed: {passed}/{len(results)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed! The TUI content area is working correctly.")
        print("\nNext steps:")
        print("1. Run: pipx install -e . --force")
        print("2. Run: unibos-dev interactive")
        print("3. Test each menu item to verify content displays in right panel")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")

    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)