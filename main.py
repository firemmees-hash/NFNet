#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Network Freedom NETwork (NFNET) Protocol Console
Build Date: 03/15/2013
Build Version: 1.0.0.143
Copyright (c) 2013 Network Freedom Systems
All Rights Reserved. Patents Pending.
"""

import sys
import os
import time

# Add libs to path
libs_path = os.path.join(os.path.dirname(__file__), 'libs')
if os.path.exists(libs_path):
    sys.path.insert(0, libs_path)
else:
    print "[ERROR] libs directory not found!"
    print "Please ensure libs/ folder exists with required modules"
    sys.exit(1)

def startup_sequence():
    """Show the system startup sequence"""
    print "INITIALIZING SYSTEM..."
    time.sleep(0.3)
    
    messages = [
        "Loading kernel modules... OK",
        "Initializing network stack... OK",
        "Starting protocol handlers... OK",
        "Checking system integrity... OK",
        "Loading NFNET core... OK",
        "Establishing secure channels... OK"
    ]
    
    for msg in messages:
        print "  %s" % msg
        time.sleep(0.2)
    
    print "SYSTEM READY"
    print ""

def main_header():
    """Display the main header"""
    print ""
    print "================================================================"
    print "     NFNET PROTOCOL CONSOLE v1.0 (Build 143)"
    print "     (c) 2013 Network Freedom Systems"
    print "================================================================"
    print "Type 'help' for available commands"
    print ""

def main():
    """Main entry point"""
    
    # Check Python
    if sys.version_info[0] != 2:
        print "[WARN] This system was optimized for Python 2.7"
        print "[WARN] Running on non-standard interpreter"
        print ""
    
    startup_sequence()
    
    # Import after path is set
    try:
        from libs.console import Console
    except ImportError as e:
        print "[ERROR] Could not load console module: %s" % str(e)
        print "[ERROR] Make sure all files are in libs/ directory"
        sys.exit(1)
    
    main_header()
    
    # Start console
    console = Console()
    console.run()

if __name__ == "__main__":
    main()