Javascript Jobsteps
===================

This directory contains different jobsteps which can be installed in
to Vidispine to customize the job processing.

In order to install a jobstep, you can use the following curl command.

```
# cat filename.xml | curl -X POST --data-binary @- -H "Content-type: application/xml" -u admin http://hostname:8080/API/task-definition
```

The Vidispine documentation for this is available at
http://apidoc.vidispine.com/latest/job/javascript-tasks.html

List of jobsteps
----------------

* add-item-to-project-collection.xml

   This script extracts the top level directory from the path of the
   file being ingested and adds an item to a collection with that
   name, creating the collection if neccesary.

* autoimport-wait-transcoding-closed.xml

   This script delays an auto import job until the file being ingested
   has the state CLOSED. This is useful if the file being ingested is
   still being recorded to and is of a format not supported by the
   growing file ingest.
