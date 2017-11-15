# A script which calculates the total duration of Portal's items in seconds.
#
# Best is to execute this with portal management shell:
#    /opt/cantemo/portal/manage.py shell < calculate_portal_total_items_duration.py
#
# This works for Portal version 2.3.x onwards, earlier versions should calculate on 'f_durationSeconds_flt' instead
# or 'durationSeconds'.
from portal.search.elastic import query_elastic

searchquery = '{"query": {"filtered": {"filter": {"bool": {"must": [{"and": {"filters": [{"term": {"search_interval": "all"}}]}}, {"missing": {"field": "portal_deleted"}}]}}, "query": {"match_all": {}}}}}'

first = 0
number = 100
duration = 0

while True:
    print "result from " + str(first) + ": " + str(duration) + "s"
    searchresults = query_elastic(searchquery, first, number)
    for hit in searchresults['hits']['hits']:
        if hit["_type"] != "item":
            continue
        if 'durationSeconds' in hit['_source']:
            duration = duration + float(hit['_source']['durationSeconds'][0])     
    if len(searchresults['hits']['hits']) < number:
        break
    first = first + number

print "Total duration is " + str(duration) + "s"
