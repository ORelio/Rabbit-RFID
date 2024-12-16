#!/usr/bin/env python3

# ==================================================================
# Rabbits RFID
#
# Service for monitoring RFID events and
# handling newer tag types supported by the newer NFC card,
# without touching the existing pynab codebase
#
# By ORelio (c) 2023-2024 - CDDL 1.0
# ==================================================================

import os

# Make sure working directory is script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Static initialization
import rfid
import nabstate
