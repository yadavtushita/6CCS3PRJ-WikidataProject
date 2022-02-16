import xml.etree.ElementTree as etree
from gzip import GzipFile
import codecs
import csv
import re
import datetime
import time


def valid_page_title(q_id):
    pattern = '[Q]+[0-9]+$'
    isValid = False
    try:
        isValid = re.search(pattern, q_id)
    except Exception as ex:
        print(ex)
        print(str(ex))  # output the exception message
        print(ex.args)  # the arguments that the exception has been called with.
        # the first one is usually the message.
        return False

    if isValid:
        return True
    else:
        return False


# Define the start data and time the wikidata revision date much be after
# After 30th September
# Before Jan 1st
# 3 months - Oct, Nov, Dec 2016
start_time = time.time()
d2 = datetime.datetime(2016, 9, 30)
d22 = datetime.datetime(d2.year, d2.month, d2.day)
d3 = datetime.datetime(2017, 1, 1)
d33 = datetime.datetime(d3.year, d3.month, d3.day)


# Function to parse revision date time for filter of the revision datetime
# so that only revisions after 15th March 2019 are considered.
def convert_date_time(dt):
    f = "%Y-%m-%dT%H:%M:%S%fZ"
    dt1 = datetime.datetime.strptime(dt, f)
    dt2 = datetime.datetime(dt1.year, dt1.month, dt1.day)
    return dt2


FILENAME_ARTICLES = 'C:\wikidata\zipfilescsv\samplefile1.csv'
ENCODING = "utf-8"

page_title = ''
page_id = ''
page_ns = ''
revision_id = ''
timestamp = ''
comment = ''
type = ''
edit_entity = ''
parent_id = ''

xmL = 'C:\wikidata\zipfiles\wikidatawiki-20220120-stub-meta-history1.xml.gz'

hfile = codecs.open(FILENAME_ARTICLES, 'w', ENCODING)
hfilecsv = csv.writer(hfile)

print ("Created csv file")

hfilecsv.writerow(
    ['page_id', 'page_title', 'page_ns', 'revision_id', 'timestamp', 'comment', 'type', 'edit_entity', 'parent_id'])
print("Added headers to csv")
with GzipFile(xmL) as xml_file:
    print("Opened zip file")
    try:
        for event, elem in etree.iterparse(xml_file, events=('start', 'end',)):
            print("Started parsing")

            if event == 'start':
                if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}mediawiki':
                    root = elem
                    print("inside start")

            if event == 'end':
                if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                    page_title_elem = elem.find('{http://www.mediawiki.org/xml/export-0.10/}title')
                    if page_title_elem is None: continue
                    page_title = page_title_elem.text
                    if page_title is None: continue
                    is_valid_page_title = valid_page_title(page_title)
                    if not is_valid_page_title: continue

                    page_ns_elem = elem.find('{http://www.mediawiki.org/xml/export-0.10/}ns')
                    if page_ns_elem is None: continue
                    page_ns = page_ns_elem.text
                    if page_ns is None: continue

                    page_id_elem = elem.find('{http://www.mediawiki.org/xml/export-0.10/}id')
                    if page_id_elem is None: continue
                    page_id = page_id_elem.text
                    if page_id is None: continue

                    revision = elem.find('{http://www.mediawiki.org/xml/export-0.10/}revision')
                    if revision is None: continue
                    revision_id_elem = revision.find('{http://www.mediawiki.org/xml/export-0.10/}id')
                    if revision_id_elem is None: continue
                    revision_id = revision_id_elem.text
                    if revision_id is None: continue

                    timestamp_elem = revision.find('{http://www.mediawiki.org/xml/export-0.10/}timestamp')
                    if timestamp_elem is None: continue
                    timestamp = timestamp_elem.text
                    if timestamp is None: continue
                    converted_timestamp = convert_date_time(timestamp)
                    if not (converted_timestamp > d22 and converted_timestamp < d33): continue

                    comment_elem = revision.find('{http://www.mediawiki.org/xml/export-0.10/}comment')
                    if comment_elem is None: continue
                    comment = comment_elem.text
                    if comment is None: continue
                    comment_proxies = ["-create", "-add", "-set", "-update", "-remove", "restore", "merge", "revert",
                                       "undo"]
                    comment_edit_entities = ["description", "alias", "sitelink", "claim", "entity", "reference", "label",
                                             "vandalism", "mergeitems", "qualifier"]
                    comment_text = comment.lower()

                    for w in comment_proxies:
                        if w in comment_text:
                            if '-' in w:
                                type = w[1:]
                            else:
                                type = w

                    # for 2 outliers detetcted with no clear type
                    # wbsetclaimvalue
                    # wbsetlabeldescriptionaliases
                    if type == '':
                        if 'set' in comment_text:
                            type = 'set'

                    for w in comment_edit_entities:
                        if w in comment_text:
                            editentity = w

                    parent_id_elem = revision.find('{http://www.mediawiki.org/xml/export-0.10/}parentid')
                    if parent_id_elem is None: continue
                    parent_id = parent_id_elem.text
                    if parent_id is None: continue

                    print([page_id, page_title, page_ns, revision_id, timestamp, comment, type, edit_entity, parent_id])
                    hfilecsv.writerow(
                        [page_id, page_title, page_ns, revision_id, timestamp, comment, type, edit_entity, parent_id])

                    root.clear()
    except Exception as ex:
        print(ex)
        print(str(ex))  # # output the exception message
        print(ex.args)  # the arguments that the exception has been called with.
        # the first one is usually the message.
