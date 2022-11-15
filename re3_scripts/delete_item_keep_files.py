#!/opt/cantemo/python/bin/python
#
# This is a script that can be executed with Rules Engine 3,
# or from the command line.
#
description = """
Permanently delete an item, keep files on storage intact.

USE WITH CAUTION! This script permanently deletes an item. Only recovery is
through external backups.

By default leaves all item files on all storages intact.

This can be modified with the arguments. Cantemo 5.3.0 supports arguments for scripts in rules.
"""

epilog = """
Example: Keep original, delete files for all other shapes (e.g. lowres):
--keepShapeTagMedia=original

Example: Keep all media in storage VX-1, delete from other storages
--keepShapeTagStorage=VX-1

Both of these accept multiple values, comma separated. If both are defined, only files
that match BOTH are kept. For example:

--keepShapeTagMedia=original,lowres
--keepShapeTagStorage=VX-1,VX-2

... means: Keep "original" and "lowres" files on storages VX-1 and VX-2, delete everything else.

Additionally --dryrun can be used to only print the requests that would be made, but not
delete anything. This is useful for local testing. Note that as a Rules Engine 3 script this 
expects a item ID in the "portal_itemId" environment variable, run like this from the commandline:

portal_itemId=VX-1979 /opt/cantemo/portal/portal/plugins/rulesengine3/shellscripts/delete_item_keep_files.py
"""

import os
import sys

import django

sys.path.append("/opt/cantemo/portal")
os.environ["DJANGO_SETTINGS_MODULE"] = "portal.settings"

django.setup()
# Now Cantemo/Django environment is setup and helper classes are available

import argparse
import logging

# Logging through standard Cantemo logging, i.e. to /var/log/cantemo/portal/portal.log
log = logging.getLogger("portal.plugins.rulesengine3.shellscripts")


def print_and_log(text):
    print(text)
    log.info(text)


def delete_item(item_id, args):
    # Import only when successfully trying to delete
    from portal.vidispine.iitem import ItemHelper
    from RestAPIBase.resturl import RestURL
    from RestAPIBase.utility import prepare_request
    from RestAPIBase.utility import perform_request

    if args.keepShapeTagMedia is None and args.keepShapeTagStorage is None:
        # Both arguments undefined -> default to * = keep every file
        args.keepShapeTagMedia = args.keepShapeTagStorage = "*"

    # Add the arguments which have defined value as query parameters
    query = {}
    if args.keepShapeTagMedia is not None:
        query["keepShapeTagMedia"] = args.keepShapeTagMedia
    if args.keepShapeTagStorage is not None:
        query["keepShapeTagStorage"] = args.keepShapeTagStorage

    print_and_log(f"Deleting item {item_id}, keeping files, query values: {query}")

    # No runas-parameter, runs as admin.
    item_helper = ItemHelper()

    # ItemHelper removeItem() function does not currently support additional parameters, so we
    # create the URL and request here.
    rest_url = RestURL(f"{item_helper.itemapi.vsapi.super_url}API/item/{item_id}")
    rest_url.addQuery(query)
    param_dict = prepare_request(item_helper.itemapi.vsapi.base64string, rest_url.geturl(), method="DELETE")

    if args.dryrun:
        print_and_log(f"Dry-run: Would do DELETE request to {rest_url.geturl()}")
    else:
        print_and_log(f"Performing DELETE request to {rest_url.geturl()}")
        # This raises on any HTTP error - let that exit the script.
        perform_request(**param_dict)
        print_and_log(f"DELETE success.")


def main():
    parser = argparse.ArgumentParser(
        description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Default value * means keep all shapes in all storages
    # See https://apidoc.vidispine.com/22.3/ref/item/item.html#delete-an-item
    parser.add_argument(
        "--keepShapeTagMedia",
        default=None,
        help="Comma separated list of shapetags to keep (default is keep all shapes)",
    )
    parser.add_argument(
        "--keepShapeTagStorage",
        default=None,
        help="Comma separated list of storages on which to keep files (default is keep all shapes on all storages)",
    )
    parser.add_argument("--dryrun", action="store_true")
    args = parser.parse_args()
    if args.dryrun:
        print_and_log("--dryrun defined, will not do any requests to delete item.")

    item_id = os.environ.get("portal_itemId")
    if item_id:
        delete_item(item_id, args)
    else:
        print_and_log("portal_itemId env variable not set, quitting. See --help for usage example")


main()
