#!/usr/bin/env python3
import subprocess
import time
import os

# Enable debug mode
os.environ['UNIBOS_DEBUG'] = 'true'
os.environ['NO_SPLASH'] = '1'

# Clear old logs
os.system('rm -f /tmp/unibos_*debug.log')

print("Starting unibos-dev with debug mode for 3 seconds...")
print("Try pressing Enter on a menu item...")

# Start unibos-dev
p = subprocess.Popen(['unibos-dev'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)

# Wait
time.sleep(3)

# Send 'q' to quit
try:
    p.stdin.write(b'q')
    p.stdin.flush()
except:
    pass

# Wait a bit more
time.sleep(0.5)

# Terminate if still running
p.terminate()
time.sleep(0.5)

print("\nDebug logs:")
print("=" * 60)

# Show debug logs
for logfile in ['/tmp/unibos_key_debug.log', '/tmp/unibos_tui_debug.log']:
    if os.path.exists(logfile):
        print(f"\n{logfile}:")
        with open(logfile, 'r') as f:
            print(f.read()[:2000])

print("=" * 60)