# Agent Helper App V2 scripts

This directory includes example scripts for the Portal Mac and Windows Agent customization.

For more information, see 
https://doc.cantemo.com/latest/AdministrationGuide/apps/nleintegration/main.html#version-2-helper-app

The `mac_*` examples work as such on Mac and `win_*` on Windows - there is only minor changes to how
standard in/out is handled.

## Installation

* Download the .py file to your computer
* In Agent Preferences, set Helper App to the script file
* Upload a file through the Agent - the script gets executed before the file is accepted


## List of scripts

### mac_agent_hook_handler_fail_upper_case.py

Simple script implementation. Disallows user to upload files with upper case characters.

### mac_agent_check_mediainfo.py
    
Run `mediainfo` to parse media parameters, disallow vertically aligned videos, and videos with less
than Full HD resolution. Uses functions for cleaner code.

### mac_agent_upload_with_original_uri_in_metadata.py

Adds path on client side as a metadata value on the uploaded file.
    
### win_agent_hook_handler_fail_upper_case.py

Windows version of `mac_agent_hook_handler_fail_upper_case.py` using functions for a cleaner
script setup. `sys.stdin.isatty()` used to check stdin beore reading.