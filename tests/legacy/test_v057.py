#!/usr/bin/env python3
"""
Test script for unibosoft v057
Verifies basic functionality without interactive input
"""

import os
import sys
import json
from pathlib import Path

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if core modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from core.utils.colors import Colors
        print("✅ Colors module imported successfully")
    except ImportError as e:
        print(f"❌ Colors module failed: {e}")
    
    try:
        from core.utils.logger import Logger
        print("✅ Logger module imported successfully")
    except ImportError as e:
        print(f"❌ Logger module failed: {e}")
    
    try:
        from core.database.database import get_db
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Database module failed: {e}")

def test_project_modules():
    """Test project module availability"""
    print("\n🎮 Testing project modules...")
    
    modules = {
        'currencies': 'projects.currencies.main',
        'inflation': 'projects.kisiselenflasyon.main', 
        'recaria': 'projects.recaria.main',
        'birlikteyiz': 'projects.birlikteyiz.main'
    }
    
    for name, module_path in modules.items():
        try:
            __import__(module_path)
            print(f"✅ {name.capitalize()} module available")
        except ImportError as e:
            print(f"❌ {name.capitalize()} module not available: {e}")

def test_web_interface():
    """Test web interface availability"""
    print("\n🌐 Testing web interface...")
    
    try:
        from core.web.server import run_server
        print("✅ Web interface available")
    except ImportError as e:
        print(f"❌ Web interface not available: {e}")

def test_version_info():
    """Test version information loading"""
    print("\n📋 Testing version information...")
    
    try:
        version_file = Path(__file__).parent / "VERSION.json"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
            print(f"✅ Version: {version_info.get('version', 'Unknown')}")
            print(f"✅ Build Date: {version_info.get('build_date', 'Unknown')}")
            print(f"✅ Author: {version_info.get('author', 'Unknown')}")
        else:
            print("❌ VERSION.json not found")
    except Exception as e:
        print(f"❌ Version info loading failed: {e}")

def test_main_class():
    """Test main application class instantiation"""
    print("\n🚀 Testing main application class...")
    
    try:
        from main import UnibosoftMain
        app = UnibosoftMain()
        print("✅ UnibosoftMain class instantiated successfully")
        print(f"✅ Interface mode: {app.interface_mode}")
        print(f"✅ Version info loaded: {bool(app.version_info)}")
        
        # Test version info loading
        version = app.version_info.get('version', 'Unknown')
        print(f"✅ Version from app: {version}")
        
    except Exception as e:
        print(f"❌ Main class instantiation failed: {e}")

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from core.database.database import get_db
        db = get_db()
        print(f"✅ Database connected: {db.db_type.upper()}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def main():
    """Run all tests"""
    print("🧪 unibosoft v057 - Functionality Test Suite")
    print("=" * 50)
    
    test_imports()
    test_project_modules()
    test_web_interface()
    test_version_info()
    test_main_class()
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨")

if __name__ == "__main__":
    main()