#!/usr/bin/env python
"""
Example Windows Agent Helper App which disallows user to upload files with upper case characters.
"""

# setup logging to a file
import json
import logging
import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
log_filename = os.path.join(basedir, 'fail_upper_case.log')
logging.basicConfig(
    filename=log_filename,
    format='%(asctime)s - %(levelname)s: %(message)s',
    level=logging.DEBUG)

log = logging.getLogger(__name__)
data_in = None

log.debug("Started")
# On Windows must check sys.stdin.isatty() before reading stdin.
if not sys.stdin.isatty():
    data_in = sys.stdin.read()
    log.debug("data_in: " + data_in)
else:
    log.debug("data_in: empty")


def write_status(data):
    """
    Write status to stdout, ending in a newline character, and flush the buffer so receiver
    can handle it.

    :param data: dict, converted to JSON
    """
    json.dump(data, sys.stdout)
    sys.stdout.write('\n')
    sys.stdout.flush()


if not data_in:
    # No input - give API level response so Agent can detect support
    write_status({'api_version': 2, 'app_name': 'Mac Agent Lower Case Example'})
else:
    # Else return status per file - we don't need to care about the
    # input "operation" here
    request = json.loads(data_in)

    file_statuses = []
    for f in request.get('files', []):
        filename = os.path.basename(f['path'])
        file_status = {'path': f['path'], 'status': 'ok', 'message': 'Filename OK'}
        # Check if filename has uppercase characters, if so fail it
        if any(c.isupper() for c in filename):
            file_status['status'] = 'failed'
            file_status['message'] = 'Filename must not contain upper case'
        file_statuses.append(file_status)
    write_status({'status': 'done', 'files': file_statuses})

log.debug("END")
