# Scripts

This directory contains various different scripts that run outside of
Portal but which interacts with it in different ways.


## List of scripts

* generate_random_videos.py

   A script which creates lots of small quicktime video files with
   unique content. Each file is a 1 second video file which displays a
   unique checksum in text. This can be useful when testing ingesting
   or filesystem performance where the size of the ingested video is
   irrelevant, but where you need lots of files.

* calculate_portal_total_items_duration.py

   A script which calculates the total duration of Portal items in seconds.
   Best is to execute it with portal management shell:
      /opt/cantemo/portal/manage.py shell < calculate_portal_total_items_duration.py
