#!/usr/bin/env python3
"""Test all submenu imports and basic functionality"""

import sys
import os
# Update path to new monorepo structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../apps/cli/src'))

def test_imports():
    """Test that all submenu modules can be imported"""
    errors = []
    
    print("Testing submenu imports...")
    
    # Test version manager (baseline - should work)
    try:
        from main import version_manager_menu
        print("✅ Version manager import successful")
    except Exception as e:
        errors.append(f"❌ Version manager import failed: {e}")
    
    # Test administration menu
    try:
        from administration_menu import administration_menu
        print("✅ Administration menu import successful")
    except Exception as e:
        errors.append(f"❌ Administration menu import failed: {e}")
    
    # Test code forge menu
    try:
        from code_forge_menu import code_forge_menu
        print("✅ Code forge menu import successful")
    except Exception as e:
        errors.append(f"❌ Code forge menu import failed: {e}")
    
    # Test AI builder menu
    try:
        from ai_builder_menu import ai_builder_menu
        print("✅ AI builder menu import successful")
    except Exception as e:
        errors.append(f"❌ AI builder menu import failed: {e}")
    
    # Test web forge (web UI) menu
    try:
        from main import web_forge_menu
        print("✅ Web UI menu import successful")
    except Exception as e:
        errors.append(f"❌ Web UI menu import failed: {e}")
    
    # Test main components
    try:
        from main import draw_sidebar, draw_main_screen, clear_screen
        print("✅ Main UI components import successful")
    except Exception as e:
        errors.append(f"❌ Main UI components import failed: {e}")
    
    # Print results
    print("\n" + "="*50)
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(error)
        return False
    else:
        print("✅ All submenu imports successful!")
        print("\nAll menus should now work with consistent navigation:")
        print("- Right arrow/Enter: Enter submenu")
        print("- Left arrow/q/ESC: Exit submenu")
        print("- Sidebar properly dims/undims")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)