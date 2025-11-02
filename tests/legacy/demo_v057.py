#!/usr/bin/env python3
"""
Demo script for unibosoft v057
Shows interface modes without interactive input
"""

import os
import sys

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_interfaces():
    """Demo different interface modes"""
    print("🎨 unibosoft v057 - Interface Demo")
    print("=" * 50)
    
    try:
        from main import UnibosoftMain
        app = UnibosoftMain()
        
        # Demo Modern Interface
        print("\n🚀 MODERN INTERFACE MODE:")
        print("-" * 30)
        app.interface_mode = "modern"
        app.display_header_modern()
        app.display_menu_modern()
        
        # Demo DOS Interface
        print("\n\n💻 DOS INTERFACE MODE:")
        print("-" * 30)
        app.interface_mode = "dos"
        app.display_header_dos()
        app.display_menu_dos()
        
        # Demo Minimal Interface
        print("\n\n⚡ MINIMAL INTERFACE MODE:")
        print("-" * 30)
        app.interface_mode = "minimal"
        app.display_header_minimal()
        app.display_menu_minimal()
        
        print("\n\n" + "=" * 50)
        print("✅ All interface modes working successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def show_status():
    """Show module status"""
    print("\n📊 MODULE STATUS REPORT:")
    print("-" * 30)
    
    # Import availability checks from main
    try:
        from main import CURRENCIES_AVAILABLE, INFLATION_AVAILABLE, RECARIA_AVAILABLE, BIRLIKTEYIZ_AVAILABLE, WEB_AVAILABLE
        
        modules = {
            "Currencies": CURRENCIES_AVAILABLE,
            "Personal Inflation": INFLATION_AVAILABLE, 
            "Recaria": RECARIA_AVAILABLE,
            "Birlikteyiz": BIRLIKTEYIZ_AVAILABLE,
            "Web Interface": WEB_AVAILABLE
        }
        
        for name, status in modules.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {name}: {'Available' if status else 'Not Available'}")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    demo_interfaces()
    show_status()
    print("\n🌍 ve ışınlanmak hep serbest ve ücretsiz olacak. yaşasın recaria! 🚀✨")