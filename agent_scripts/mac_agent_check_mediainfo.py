#!/usr/bin/env python
"""
Example script for Agent pre- post-hook testing using mediainfo for media parameters.

Disallow vertically aligned videos, and videos with less than Full HD resolution.

Tested with Mac Agent and MediaInfo Command line, MediaInfoLib - v0.7.85

Depends on "mediainfo" executable - available for Mac from https://mediaarea.net/en/MediaInfo/Download/Mac_OS
or with brew: "brew install media-info"

Please check that MEDIAINFO_EXECUTABLE is valid if command fails.
"""

import json
import logging
import os
import select
import subprocess
import sys

# Path to mediainfo executable
MEDIAINFO_EXECUTABLE = '/usr/local/bin/mediainfo'

# Setup logging into a file in same directory as source file
basedir = os.path.abspath(os.path.dirname(__file__))
log_filename = os.path.join(basedir, 'mac_agent_check_mediainfo.log')
logging.basicConfig(
    filename=log_filename,
    format='%(asctime)s - %(process)d - %(levelname)s: %(message)s',
    level=logging.DEBUG)
log = logging.getLogger(__name__)

data_in = None

# Check if there is incoming data on STDIN and read it
r_list, w_list, x_list = select.select([sys.stdin], [], [], 0)
log.debug('Start - r_list: %r - args: %r - os.getcwd(): %s', r_list, sys.argv, os.getcwd())
if r_list:
    data_in = sys.stdin.read()
log.debug('Started - data in: %r', data_in)


def write_status(data):
    """
    Write status to stdout, ending in a newline character, and flush the buffer so receiver
    can handle it.

    :param data: dict, converted to JSON
    """
    log.debug('Writing response: %r', data)
    json.dump(data, sys.stdout)
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_mediainfo_output(path):
    """
    Get output of MediaInfo for a given file

    :param path: Full path to media file, including filename
    :return: A dict with all info fields as output by mediainfo - e.g. {'Video':{'Width':'1 920 pixels'}, ...
             None if mediainfo failed or there was some error parsing the results
    """
    log.debug('get_mediainfo_output, path: %r', path)
    result = None
    try:
        result = subprocess.check_output([MEDIAINFO_EXECUTABLE, path])
        info = {}
        current_header = None
        for line in result.splitlines():
            if not line:
                continue
            if ':' not in line:
                current_header = line
                info[current_header] = {}
            else:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                info[current_header][key] = value
        return info
    except Exception:
        log.exception("Failed to run mediainfo, output: %s", result)
        return None


def get_video_width_height(mediainfo):
    """
    Get video width and height, in pixels

    :param mediainfo: dict from get_mediainfo_output()
    :return: (width, height), or (None, None) if not available
    """
    width = height = None
    try:
        width_str = mediainfo['Video']['Width']
        height_str = mediainfo['Video']['Height']
        width = int(width_str.replace('pixels', '').replace(' ', ''))
        height = int(height_str.replace('pixels', '').replace(' ', ''))
    except (KeyError, ValueError) as e:
        log.warning("Could not get video width/height: %s", e)
    return width, height


def get_video_rotation(mediainfo):
    """
    Get rotation angle value

    :param mediainfo: dict from get_mediainfo_output()
    :return: Angle value, e.g. '270\xc2\xb0' or '00\xc2\xb0' - None if not found
    """
    try:
        return mediainfo['Video']['Rotation']
    except KeyError:
        return None


if not data_in:
    # No input - give API level response so Agent can detect support
    write_status({'api_version': 2, 'app_name': 'Check Mediainfo'})
else:
    # Else return status per file
    request = json.loads(data_in)
    operation = request.get('operation')

    if operation == 'file_ready':
        # Files are ready and readable - check with mediainfo
        files = request.get('files', [])
        # Simulate failed opening of a file
        for f in files:
            mediainfo = get_mediainfo_output(f['path'])
            log.debug('MediaInfo: %r', mediainfo)
            # Default to failed
            f['status'] = 'failed'
            if not mediainfo:
                f['message'] = 'Failed to get media info'
            else:
                video_width, video_height = get_video_width_height(mediainfo)
                rotation = get_video_rotation(mediainfo)
                log.debug('Video width: %s, height: %s, rotation: %r', video_width, video_height, rotation)

                if not video_width or not video_height:
                    f['message'] = 'Not a video file: Invalid width %s or height %s' % (video_width, video_height)
                else:
                    # Check for rotation in video
                    if rotation and (rotation.startswith('270') or rotation.startswith('90')):
                        # Swap width/height for comparison
                        log.debug('Rotation detected, swapping width/height')
                        video_width, video_height = video_height, video_width

                    if video_height < 1080:
                        f['message'] = 'Video resolution is too low, not Full HD (%s)' % video_height
                    elif video_height > video_width:
                        f['message'] = 'Vertical videos not allowed: %s < %s' % (video_width, video_height)
                    else:
                        f['status'] = 'ok'
                        f['message'] = 'Video approved - resolution %sx%s' % (video_width, video_height)

        write_status({'status': 'done', 'files': files})
    else:
        # Any other operation - do not accept or decline any files
        # ESPECIALLY we don't want to "approve" if "file_new" happens to come *after* file_ready.
        # Note: This script does not handle "open_with", so "Open with..." from Portal will not do anything.
        write_status({})

log.debug('Done')
