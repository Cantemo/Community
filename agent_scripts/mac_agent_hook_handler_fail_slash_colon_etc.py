#!/usr/bin/env python3
"""
Script for Mac Agent that prevents any "odd" characters in filenames.

This is to prevent issues where some characters are handled differently depending on filesystem or OS.

You can modify ACCEPTED_CHARACTERS to suite your needs.
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import select
import string
import sys
import unicodedata

ACCEPTED_CHARACTERS = set(
    # Upper and lowercase ASCII letters,
    string.ascii_letters
    # 0123456789
    + string.digits
    # Allowed separators: Dot, space, underscore, single quote, parenthesis
    + ". _'()"
    # ... and ASCII double quote
    + '"'
    # And a few default scandinavian characters
    + "åÅäÄöÖ"
)


def get_filename_error(filename: str) -> str | None:
    errors = []
    # Macos normalizes unicode as NFD, e.g. ä = two characters "¨" and a
    # Check the string as NFC normalized to we check the individual characters instead
    for index, char in enumerate(unicodedata.normalize("NFC", filename)):
        if char not in ACCEPTED_CHARACTERS:
            errors.append(f"{char} ({unicodedata.name(char)}) at {index}")
    if errors:
        return f"Invalid filename, errors: {', '.join(errors)}"
    else:
        return None


def get_file_status(file_info: dict) -> dict:
    # Default: accept
    file_status = {"path": file_info["path"], "status": "ok", "message": "Filename OK"}
    filename = os.path.basename(file_info["path"])
    error = get_filename_error(filename)
    if error:
        file_status["status"] = "failed"
        file_status["message"] = error
    return file_status


def write_status(data: dict) -> None:
    """
    Write status to stdout (to the Agent), ending in a newline character, and flush the buffer so receiver
    can handle it.

    :param data: dict, converted to JSON
    """
    log.debug("Writing response: %r", data)
    json.dump(data, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__":
    # Setup logging into a file in same directory as source file, .log suffix
    log_filename = pathlib.Path(__file__).with_suffix(".log").resolve()
    logging.basicConfig(
        filename=log_filename, format="%(asctime)s - %(process)d - %(levelname)s: %(message)s", level=logging.DEBUG
    )
    log = logging.getLogger(__name__)

    data_in = None

    # Check if there is incoming data on STDIN and read it
    r_list, w_list, x_list = select.select([sys.stdin], [], [], 0)
    log.debug("Start - r_list: %r - args: %r - os.getcwd(): %s", r_list, sys.argv, os.getcwd())
    if r_list:
        data_in = sys.stdin.read()
    log.debug("Started - data in: %r", data_in)

    if not data_in:
        # No input - give API level response so Agent can detect support
        write_status({"api_version": 2, "app_name": "Check Mediainfo"})
    else:
        # Else return status per file. We don't need to care about the
        # input "operation" here as we only check filenames
        request = json.loads(data_in)

        files = request.get("files", [])
        file_statuses = []

        for file_info in request.get("files", []):
            file_status = get_file_status(file_info)
            file_statuses.append(file_status)

        write_status({"status": "done", "files": file_statuses})

    log.debug("Done")
