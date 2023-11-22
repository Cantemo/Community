#!/usr/bin/env python3
"""
Script for Mac Agent that sends the original path on the client side as "Description" metadata on the resulting item.

Generates an XML sidecar file for each media that the Agent picks up during upload.

Caveats:

1. The sidecar files are never removed from the client side.

2. "originalUri" would be the logical metadata field for this data, the same field where Import from Storage
workflow stores it. However this CAN NOT be used as the import job of the media automatically overwrites this value
with empty for Agent uploads.
To get this value stored in "originalUri" after the upload one should use a custom metadata field, and either a
Vidispine jobstep or Rules Engine 3 rule that after the import job sets "originalUri" from the custom metadata field
value.
"""

import json
import logging
import os
import pathlib
import select
import sys


def write_status(data) -> None:
    """
    Write status to stdout (to the Agent), ending in a newline character, and flush the buffer so receiver
    can handle it.

    :param data: dict, converted to JSON
    """
    log.debug("Writing response: %r", data)
    json.dump(data, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


def write_metadata_sidecar(media_file_path: str) -> dict:
    """
    Write a metadata sidecar file for the media. The sidecar sets originalUri metadata field value.

    Returns a dictionary with "status" and "message" values to return for this file to the Agent.
    """
    sidecar_comment = "created with mac_agent_upload_with_original_uri_in_metadata.py"
    sidecar_path = os.path.splitext(media_file_path)[0] + ".xml"

    status = None
    message = None
    # Check is a sidecar already exists
    if os.path.exists(sidecar_path):
        # Exists, check if it was created with this script. If not do not overwrite and
        # decline this file: we don't want to overwrite an existing sidecar.
        with open(sidecar_path, "r") as sidecar_input:
            if sidecar_comment not in sidecar_input.read():
                log.debug(f"sidecar_comment '{sidecar_comment}' not found in {sidecar_path}")
                message = f"Sidecar file {sidecar_path} already exists"
                status = "failed"
            else:
                log.debug(f"sidecar_comment {sidecar_comment} was found in {sidecar_path}, will overwrite")

    # Not failed - proceed to write a sidecar file
    if not status:
        with open(sidecar_path, "w") as sidecar_output:
            sidecar_output.write(
                # Note: For demo purpose sing the default "Description" field portal_mf619153 here to store the value,
                # this field always exists on a default Cantemo setup. This will override any "Description" set by
                # the user in the Agent metadata.
                #
                # For actual workflow should use another custom field for this and remote the line that sets metadata
                # field group (<group>Film</group>).
                #
                # See comment at start of this script for more information.
                f"""<MetadataDocument xmlns="http://xml.vidispine.com/schema/vidispine">
                        <!-- {sidecar_comment} -->
                        <group>Film</group>
                        <timespan start="-INF" end="+INF">
                            <field>
                                <name>portal_mf619153</name>
                                <value>{pathlib.Path(media_file_path).as_uri()}</value>
                            </field>
                        </timespan>
                    </MetadataDocument>"""
            )
        status = "ok"
        message = f"Sidecar file {sidecar_path} added"
    # Also log the message
    log.info(message)
    return {"status": status, "message": message}


# Setup logging into a file in same directory as source file
basedir = os.path.abspath(os.path.dirname(__file__))
log_filename = os.path.join(basedir, "mac_agent_upload_with_original_uri_in_metadata.log")
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
    # Else return status per file
    request = json.loads(data_in)
    operation = request.get("operation")

    if operation == "file_ready":
        # Files are ready and readable - check with mediainfo
        files = request.get("files", [])
        for f in files:
            sidecar_status = write_metadata_sidecar(f["path"])
            # Update the dict we return to the Agent
            f.update(sidecar_status)

        write_status({"status": "done", "files": files})
    else:
        # Any other operation - do not accept or decline any files
        # ESPECIALLY we don't want to "approve" if "file_new" happens to come *after* file_ready.
        # Note: This script does not handle "open_with", so "Open with..." from Cantemo will not do anything.
        write_status({})

log.debug("Done")
