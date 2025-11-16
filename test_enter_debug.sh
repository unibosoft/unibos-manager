#!/bin/bash

echo "Testing Enter key with debug mode..."
echo "Press Enter on a menu item and check /tmp/unibos_key_debug.log"
echo "==========================================="

# Clear old log
rm -f /tmp/unibos_key_debug.log

# Run with debug mode
UNIBOS_DEBUG=true NO_SPLASH=1 unibos-dev