#!/opt/cantemo/python/bin/python
"""
Rules Engine 3 script to do Recreate Thumbnails on a video/image item.

Installation:
- From Portal UI, Admin > Rules Engine 3 > Add a new script
- Select this file from your computer, and Upload
- Create a rule, for example Manual Process, or triggered by a Saved Search
- in Create Rule, select Run shell script and select "recreate_thumnnails.py" from the dropdown

The script outputs to /var/log/cantemo/portal.log, a successful run outputs for example:

2017-11-08T08:27:11.296574+00:00 centos6-portal32 portal: portal.plugins.rulesengine3.shellscripts.recreate_thumbnails
 - MainProcess[8710] - INFO - Started job: {'status': 'READY', 'started': '2017-11-08T08:27:10.021+0000',
 'jobId': 'VX-3', 'priority': 'MEDIUM', 'user': 'admin', 'type': 'THUMBNAIL'} on item VX-2
"""
# Add Portal classes to path and setup Django environment.
import sys
import os

sys.path.append("/opt/cantemo/portal")
os.environ['DJANGO_SETTINGS_MODULE'] = 'portal.settings'

# Settings must be imported to setup logging correctly
from portal import settings
import logging
# Logging through standard Portal logging, i.e. to /var/log/cantemo/portal/portal.log
log = logging.getLogger('portal.plugins.rulesengine3.shellscripts.recreate_thumbnails')

item_id = os.environ.get('portal_itemId')
if item_id:
    from portal.vidispine.iitem import ItemHelper

    ith = ItemHelper()  # Note: Runs as admin
    item = ith.getItem(item_id)
    if item.getMediaType() in ['video', 'image']:
        job_data = ith.recreateThumbnails(item_id)
        log.info('Started job: %s on item %s', job_data, item_id)
    else:
        log.info('Item %s ignored due to media type: %s', item_id, item.getMediaType())
else:
    log.info('portal_itemId not set in environment')
