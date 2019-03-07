#!/usr/bin/env python
"""
Example Agent Helper App which disallows user to upload files with upper case characters.
"""
import json
import os
import select
import sys

# Check if there is incoming data on STDIN and read it
r_list, w_list, x_list = select.select([sys.stdin], [], [], 0)
if not r_list:
    # No input - give API level response so Agent can detect support
    json.dump({'api_version': 2, 'app_name': 'Disallow Uppercase'}, sys.stdout)
else:
    # Else return status per file - we don't need to care about the
    # input "operation" here
    request = json.loads(sys.stdin.read())
    file_statuses = []

    for f in request.get('files', []):
        filename = os.path.basename(f['path'])
        file_status = {'path': f['path'], 'status': 'ok', 'message': 'Filename OK'}
        # Check if filename has uppercase characters, if so fail it
        if any(c.isupper() for c in filename):
            file_status['status'] = 'failed'
            file_status['message'] = 'Filename must not contain upper case'
        file_statuses.append(file_status)

    json.dump({'status': 'done', 'files': file_statuses}, sys.stdout)
