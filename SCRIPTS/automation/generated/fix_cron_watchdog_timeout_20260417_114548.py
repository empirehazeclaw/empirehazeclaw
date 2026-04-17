#!/usr/bin/env python3
"""
cron_watchdog.py - Enforce timeouts for commands executed by cron.

Usage
-----
    # Run a single command with a timeout
    python3 cron_watchdog.py --command "my_script.py arg1" --timeout 300

    # Run multiple jobs defined in a JSON config file
    python3 cron_watchdog.py --config /etc/cron_watchdog.json

Config file format (JSON)::

    [
        {
            "name": "backup",
            "command": "/usr/local/bin/backup.sh",
            "timeout": 600,
            "grace": 10,
            "interval": 3600
        },
        ...
    ]

Exit codes
----------
    0 – command finished successfully within the timeout.
    1 – command timed out or returned a non‑zero exit code.
    2 – invalid arguments or configuration error.
"""

import argparse
import json
import logging
import os
import signal
import subprocess