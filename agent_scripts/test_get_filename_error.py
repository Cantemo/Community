#!/usr/bin/env python3
"""
Quick and dirty test for get_filename_error in mac_agent_hook_handler_fail_slash_colon_etc.py
"""

from mac_agent_hook_handler_fail_slash_colon_etc import get_filename_error

import unicodedata

for filename, error_expected in [
    ("foobar124.mov", False),
    ('quote with Space and scands "äÖöÅå".MP4', False),
    ("colon : and et & and slash both ways \\/ ", True),
    # Test this string both NFD and NFD normalized
    (unicodedata.normalize("NFC", "NFC this is valid_ÖöÄäÅå 1234567890.png"), False),
    (unicodedata.normalize("NFD", "NFD this is valid_ÖöÄäÅå 1234567890.png"), False),
]:
    error = get_filename_error(filename)
    print(f"{filename} -> {error=}")
    if bool(error) != error_expected:
        print(f"******** FAIL: {error_expected=} {error=} *********")
