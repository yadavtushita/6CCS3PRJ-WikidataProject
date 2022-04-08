# Code and algorithm adapted from Research Paper: Towards Linked Data for Wikidata Revisions and Twitter Trending Hashtags
# Github: https://github.com/D01110788/TwitterWikidata
# Paula Dooley and Bojan Božić. 2019. Towards Linked Data for Wikidata Revisions and Twitter Trending Hashtags. In
# Proceedings of the 21st International Conference on Information Integration and Web-based Applications & Services (
# iiWAS2019). Association for Computing Machinery, New York, NY, USA, 166–175.
# DOI:https://doi.org/10.1145/3366030.3366048

import xml.etree.ElementTree as etree
import os
import re
import csv
import datetime
import time
from io import open

# Name of Folder where parsed CSV files are stored
subdir = "wd_1"
here = os.path.dirname(os.path.realpath(__file__))

# Function to check the QID of the Wikidata page
def match(id):
    # Regex pattern to check for QIDs in pagetitle
    pattern = '[Q]+[0-9]+$'
    isAcceptable = False
    try:
        isAcceptable = re.search(pattern, id)
    except Exception as ex:
        print(ex)
        return ('No')

    if isAcceptable:
        return ('Yes')
    else:
        return ('No')


# Selecting the time period for revisions
# colecting revisions from 1st October, 2016 to 31st December, 2016
start_time = time.time()
d2 = datetime.datetime(2016, 9, 30)
d22 = datetime.datetime(d2.year, d2.month, d2.day)
d3 = datetime.datetime(2017, 1, 1)
d33 = datetime.datetime(d3.year, d3.month, d3.day)

# Converting the timestamp to the required format
def convert_date_time(dt):
    f = "%Y-%m-%dT%H:%M:%S%fZ"
    dt1 = datetime.datetime.strptime(dt, f)
    dt2 = datetime.datetime(dt1.year, dt1.month, dt1.day)
    return dt2

# Creates a new CSV File with the required rows
def newfilecreation(filename, articlesWriter):
    print('NEW PROCESS')
    articlesWriter = csv.writer(filename, quoting=csv.QUOTE_MINIMAL)
    articlesWriter.writerow(['pageid', 'pagetitle', 'revisionid', 'timestamp', 'comment', 'type', 'editentity', 'parentid', 'userid', 'username'])
    pagetitle = ''
    pageid = 0
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
    type = ''
    editentity = ''
    userid = ''
    username = ''
    return articlesWriter


# Closes the CSV file once 1 million items have been written or the XML file is comletely parsed
def closeoldfile(filename):
    print(filename)
    filename.flush()
    filename.close()
    # Sleep time added to ensure file is written completely
    time.sleep(5)
    print('SLEEPING')
    # Create a file defining the subdirectory 'subdir' and adding the file name 'wikidata' appending the
    # current date time with file extension .csv
    filepath = os.path.join(here, subdir, 'wikidata' + '.' + time.strftime('%Y%m%d-%H%M%S') + '.csv')
    filename = open(filepath, 'w', newline='', encoding="utf-8")
    print(filename)
    print('OPENED')
    return filename


counter = 0
wikidata_folder_path = os.path.join("C:\wikidata\Wikidata_9")
# In order to get the list of all files that ends with ".xml"
# get list of all files, and consider only the ones that ends with "xml"
wikidata_files = [x for x in os.listdir(wikidata_folder_path) if x.endswith(".xml")]
wikidata_data = list()
print(wikidata_files)
for wikidata_file in wikidata_files:
    print('#####    NEW FILE ######')
    print(wikidata_file)
    filepath = os.path.join(here, subdir, 'wikidata' + '-' + time.strftime('%Y%m%d-%H%M%S') + '.csv')
    print(filepath)
    filename = open(filepath, 'w', newline='', encoding="utf-8")
    articlesWriter = csv.writer(filename, quoting=csv.QUOTE_MINIMAL)
    articlesWriter.writerow(['pageid', 'pagetitle', 'revisionid', 'timestamp', 'comment', 'type', 'editentity', 'parentid', 'userid', 'username'])
    pagetitle = ''
    pageid = 0
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
    type = ''
    editentity = ''
    userid = ''
    username = ''
    pathWikiXML = os.path.join(wikidata_folder_path, wikidata_file)
    print('#####  OPEN NEW FILE ######')

    # Parsing the XML File
    with open(pathWikiXML, 'rb') as f:
        try:
            for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
                if event == 'start':

                    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                        pagetitle = ''
                        pageid = 0
                        inrevision = False
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title':
                        pagetitle = elem.text
                        isAMatch = match(pagetitle)
                        if (pagetitle is None):
                            pagetitle = ''
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id' and not inrevision:
                        pageid = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}revision':
                        if (
                                pagetitle != '' and pageid != 0 and isAMatch == "Yes" and revisionid != 0 and timestamp != '' and timestamp is not None and convert_date_time(
                                timestamp) > d22 and convert_date_time(timestamp) < d33):

                            # Writes 1 million revisions to the CSV file
                            # If 1 million revisions have been written a new CSV file is created
                            if counter == 1000000:
                                print('CREATE NEW FILE')
                                filename = closeoldfile(filename)
                                articlesWriter = newfilecreation(filename, articlesWriter)
                                print('NEW FILE CREATED')
                                counter = 0
                                print(filename)

                            if (comment is None):
                                comment = ''
                            if (userid is None):
                                userid = ''
                            if (username is None):
                                username = ''
                            articlesWriter.writerow(
                                [pageid, pagetitle, revisionid, timestamp, comment.encode('utf8'), type, editentity, parentid, userid, username.encode('utf8')])
                            counter += 1
                            print(counter)
                            # print([pageid, pagetitle, revisionid, timestamp, comment.encode('utf8'), type, editentity, parentid, userid, username])

                        revisionid = 0
                        inrevision = True
                        timestamp = ''
                        comment = ''
                        type = ''
                        editentity = ''
                        parentid = 0
                        userid = ''
                        username = ''
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id' and inrevision:
                        revisionid = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}comment' and inrevision:
                        comment = elem.text
                        # Adding proxies and edit entities to the CSV file
                        # Proxies are determined by using the revision comment
                        if comment is not None and comment != '':
                            comment_text = comment.lower()

                            comment_proxies = ["-create", "-add", "-set", "-update", "-remove", "restore", "merge", "revert", "undo"]
                            comment_edit_entities = ["description", "alias", "sitelink", "claim", "entity", "reference", "label", "vandalism", "mergeitems", "qualifier"]

                            for w in comment_proxies:
                                if w in comment_text:
                                    if '-' in w:
                                        type = w[1:]
                                    else:
                                        type = w

                            # 2 outliers detected with no clear type
                            # wbsetclaimvalue
                            # wbsetlabeldescriptionaliases
                            if type == '':
                                if 'set' in comment_text:
                                    type = 'set'

                            for w in comment_edit_entities:
                                if w in comment_text:
                                    editentity = w

                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}timestamp' and inrevision:
                        timestamp = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}parentid' and inrevision:
                        parentid = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}contributor' and inrevision:
                        for child in elem:
                            if child.tag == '{http://www.mediawiki.org/xml/export-0.10/}id':
                                userid = child.text
                            elif child.tag == '{http://www.mediawiki.org/xml/export-0.10/}username':
                                username = child.text

                elem.clear()
        except Exception as ex:
            print(ex)
