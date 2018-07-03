# A script used to remove specific metadata changes which have been done on items.
#
# It gives differents options to filter the changes by specific users, dates, fields
# or specific text changes.
#
# To be copied and executed on the Portal path. 
#
# With the --help option it gives details about the different options and usage, e.g:
# (on Portal path) /opt/cantemo/python/bin/python remove_specific_items_metadata_changes.py --help
import optparse
import re
import requests
import ConfigParser
import json
import dateutil.parser
import calendar


class FormattedOptionParser(optparse.OptionParser):
    def format_epilog(self, formatter):
        return self.expand_prog_name(self.epilog)


PARSER_HELP_EPILOG = """
For the date option, the date should match the YYYY-MM-DD format, but not all of the components
are required, but there cannot be missing components from left to right. So you can just specify the year,
or the year and month, but you can't skip the month and set the date, for instance.

So for instance, the following options would be valid:
* 2018 - anything year 2018
* 2018-1 - INVALID, since month is not two numbers and cannot be parsed
* 2018-05 - During May 2018
* 2018-05-0 - INVALID
* 2018-05-08 - May 8th 2018

Seconds will never be taken into account, even if specified.
"""

parser = FormattedOptionParser(epilog=PARSER_HELP_EPILOG)

parser.add_option("--user", dest="user",
                  help="The user who did the changes before")

parser.add_option("--metadatafield", dest="metadatafield",
                  help="A metadata field name")

parser.add_option("--date", dest="timestamp",
                  help="The date to look for changes in YYYY-MM-DD format. ")

parser.add_option("--text", dest="text_to_match",
                  help="Text to match")

parser.add_option("--dry-run", dest="dry_run", type="int",
                  help="If set to 1, list the items hose match the given patterns, without applying the changes",
                  default=0)

(options, args) = parser.parse_args()

config = ConfigParser.SafeConfigParser()
config.read('/etc/cantemo/portal/portal.conf')
vs_username = config.get("vidispine", "VIDISPINE_USERNAME")
vs_password = config.get("vidispine", "VIDISPINE_PASSWORD")
vs_hostname = config.get("vidispine", "VIDISPINE_URL")
vs_port = config.get("vidispine", "VIDISPINE_PORT")
vs_baseurl = "%s:%s/API" % (vs_hostname, vs_port)

# validate text
if options.text_to_match is None:
    parser.error("Option --text not provided.")

# validate user
if options.user is None:
    parser.error("Option --user not provided.")

# validate meta field name format:
if options.metadatafield is None:
    parser.error("Option --metadatafield not provided.")
else:
    pattern = re.compile("^portal_mf\d{6}$")
    field_matches_pattern = pattern.match(options.metadatafield)
    if not field_matches_pattern:
        parser.error("Invalid Metadata Field Name. It should be in the following format: portal_mfXXXXXX.")

# va1idate timestamp format
if options.timestamp is None:
    parser.error("Option --date not provided.")
else:
    # valid options are like:
    # + 2018
    # + 2018-01
    # + 2018-01-01
    isoformat_date_pattern = re.compile('^\d{4}(-\d\d(-\d\d)?)?$')
    timestamp_matches_pattern = isoformat_date_pattern.match(options.timestamp)

    if not timestamp_matches_pattern:
        parser.error("Invalid date format. Look at the help for more information.")

    try:
        dateutil.parser.parse(options.timestamp)
    except calendar.IllegalMonthError:
        parser.error("Invalid Month Value. Look at the help for more information.")
    except ValueError as e:
        parser.error("date field error: %s" % e.message)

    # remove seconds if included:
    if len(options.timestamp) == 19:
        options.timestamp = options.timestamp[:-3]

if options.dry_run not in [1, 0]:
    parser.error("Invalid --dry-run option.")
dry_run = options.dry_run == 1


def get_all_items_ids():
    number = 1000
    processed = 0
    hits = 1
    matrix = {'number': number}
    items_ids = []

    while processed < hits:
        first = processed + 1
        rest_url = '%s/item;number=%s;first=%s' % (vs_baseurl, number, first)
        result = requests.get(rest_url,
                              params={'matrix': matrix},
                              auth=(vs_username, vs_password),
                              headers={'accept': 'application/json'}
                              )

        result = json.loads(result.content)
        hits = int(result['hits'])

        if len(result['item']) < 1:
            break

        result_items_ids = [item["id"] for item in result['item']]
        items_ids += result_items_ids
        processed += len(result_items_ids)

    # return set, so we avoid duplicated ids in case they exist.
    return set(items_ids)


def get_item_changes(item_id):
    changes_response = requests.get("%s/item/%s/metadata/changes" % (vs_baseurl, item_id),
                                    auth=(vs_username, vs_password),
                                    headers={'accept': 'application/json'}
                                    )

    if changes_response.status_code != 200:
        print "Warning: Error on trying to get changes list for Item %s" % item_id
        return []

    parsed_response = json.loads(changes_response.text)
    return parsed_response['changeSet']


def get_changes_ids_to_remove(user_to_match, metadata_field_name, text_to_match, timestamp_to_match, changes_list):
    def change_filter_function(change):
        if change.get('metadata') is None:
            return False

        change_timestamp = change['metadata'].get('timespan')
        if not change_timestamp:
            return False

        fields_affected = change_timestamp[0].get('field')
        if fields_affected is None:
            return False

        for field_change in fields_affected:
            field_change_name = field_change['name']
            field_change_timestamp = field_change['timestamp']
            field_change_user = field_change['user']

            if (field_change_name == metadata_field_name) and \
                    field_change_timestamp.startswith(timestamp_to_match) and \
                    (field_change_user == user_to_match):

                field_values = field_change['value']
                if any(text_to_match in value_change['value'] for value_change in field_values):
                    return True

        return False

    changes_to_remove = filter(lambda change: change_filter_function(change), changes_list)
    return [change['id'] for change in changes_to_remove]


all_items_ids = get_all_items_ids()
data_to_remove = []
items_qty = len(all_items_ids)
print ""
print "Looking for changes in %s items..." % items_qty

for idx, item_id in enumerate(all_items_ids):
    if idx % 500 == 0:
        print "> Looking for changes on items: %s/%s" % (idx, items_qty)

    item_changes = get_item_changes(item_id)

    changes_ids_to_remove = get_changes_ids_to_remove(
        options.user, options.metadatafield,
        options.text_to_match, options.timestamp, item_changes
    )

    if changes_ids_to_remove:
        if dry_run:
            print ">> Dry Run: Item with ID: '%s' matches the provided arguments, so it has changes to be removed."\
                  % item_id
        else:
            data_to_remove.append((item_id, changes_ids_to_remove))

if dry_run is False:
    changes_to_remove_qty = len(data_to_remove)
    print "Removing changes on %s items..." % changes_to_remove_qty
    for idx, (item_id, changes_ids_to_remove) in enumerate(data_to_remove):
        if idx % 500 == 0:
            print "> Removing changes for changes: %s/%s" % (idx, changes_to_remove_qty)

        for change_id in changes_ids_to_remove:
            requests.delete("%s/item/%s/metadata/changes/%s" % (vs_baseurl, item_id, change_id),
                            auth=(vs_username, vs_password)
                            )

print "Done."
