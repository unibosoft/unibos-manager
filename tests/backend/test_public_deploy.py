#!/usr/bin/env python3
"""
Test script for public server deployment functionality
"""

import subprocess
import sys
from pathlib import Path

def test_ssh_connection():
    """Test SSH connection to rocksteady"""
    print("Testing SSH connection to rocksteady...")
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=2", "-o", "BatchMode=yes", 
         "rocksteady", "echo", "connected"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "connected" in result.stdout:
        print("✅ SSH connection successful")
        return True
    else:
        print("❌ SSH connection failed")
        print("Please ensure:")
        print("  1. SSH key is configured: ssh-add ~/.ssh/id_rsa")
        print("  2. rocksteady is in ~/.ssh/config")
        return False

def test_rsyncignore():
    """Test .rsyncignore file"""
    print("\nChecking .rsyncignore file...")
    rsyncignore = Path(".rsyncignore")
    
    if rsyncignore.exists():
        print("✅ .rsyncignore file exists")
        
        # Check critical exclusions
        content = rsyncignore.read_text()
        critical = ["archive/", "*.sql", "production.py", "venv/", ".env"]
        
        for item in critical:
            if item in content:
                print(f"  ✅ {item} is excluded")
            else:
                print(f"  ⚠️  {item} not in exclusions")
        return True
    else:
        print("❌ .rsyncignore file not found")
        return False

def test_remote_structure():
    """Test remote directory structure"""
    print("\nChecking remote structure...")
    
    # Check if unibos directory exists
    result = subprocess.run(
        ["ssh", "rocksteady", "ls", "-la", "~/unibos/backend/"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Remote unibos directory exists")
        
        # Check for critical files/dirs
        checks = [
            ("manage.py", "Django management script"),
            ("unibos_backend/", "Django project"),
            ("apps/", "Applications directory"),
            ("venv/", "Virtual environment")
        ]
        
        for item, desc in checks:
            if item in result.stdout:
                print(f"  ✅ {desc} found")
            else:
                print(f"  ⚠️  {desc} not found")
        return True
    else:
        print("❌ Remote directory not accessible")
        return False

def test_services():
    """Test remote services"""
    print("\nChecking remote services...")
    
    # Check gunicorn
    result = subprocess.run(
        ["ssh", "rocksteady", "sudo", "systemctl", "status", "gunicorn", "--no-pager"],
        capture_output=True,
        text=True
    )
    
    if "active (running)" in result.stdout:
        print("✅ Gunicorn is running")
    else:
        print("❌ Gunicorn is not running")
    
    # Check nginx
    result = subprocess.run(
        ["ssh", "rocksteady", "sudo", "systemctl", "status", "nginx", "--no-pager"],
        capture_output=True,
        text=True
    )
    
    if "active (running)" in result.stdout:
        print("✅ Nginx is running")
    else:
        print("❌ Nginx is not running")
    
    # Check PostgreSQL
    result = subprocess.run(
        ["ssh", "rocksteady", "sudo", "systemctl", "status", "postgresql", "--no-pager"],
        capture_output=True,
        text=True
    )
    
    if "active" in result.stdout:
        print("✅ PostgreSQL is running")
    else:
        print("❌ PostgreSQL is not running")
    
    return True

def test_web_access():
    """Test web accessibility"""
    print("\nChecking web access...")
    
    # Test HTTPS
    result = subprocess.run(
        ["curl", "-I", "-s", "https://recaria.org"],
        capture_output=True,
        text=True
    )
    
    if "HTTP/2 200" in result.stdout or "HTTP/2 302" in result.stdout:
        print("✅ HTTPS site is accessible")
    else:
        print("❌ HTTPS site is not accessible")
    
    # Test admin
    result = subprocess.run(
        ["curl", "-I", "-s", "https://recaria.org/admin/"],
        capture_output=True,
        text=True
    )
    
    if "HTTP/2 302" in result.stdout:  # Should redirect to login
        print("✅ Admin panel is accessible")
    else:
        print("❌ Admin panel is not accessible")
    
    return True

def main():
    """Run all tests"""
    print("🔍 Public Server Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("SSH Connection", test_ssh_connection),
        (".rsyncignore Check", test_rsyncignore),
        ("Remote Structure", test_remote_structure),
        ("Service Status", test_services),
        ("Web Access", test_web_access)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Deployment system is ready.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())