# This class parses an wikidata xml files containing revision details extracting
# the details of the revision. The additional retrieval of the revision
# title from by a call to the SPARQL API to retrieve the title via the 'QID'
# identifier

# !C:/Python37-32/python.exe -u
import xml.etree.ElementTree as etree
import os
import re
import csv
import datetime
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from io import open

# Location of created .csv files output with the wikidat revision details including
# SPARQL API retrieved title
subdir = "data"
here = os.path.dirname(os.path.realpath(__file__))


def get_uri_from_wiki_id(wiki_id):
    returnLabel = ''
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        queryData = 'SELECT DISTINCT * WHERE {wd:' + wiki_id + ' rdfs:label ?label . FILTER (langMatches( lang(?label), "EN" ) ) } LIMIT 1'
        sparql.setQuery(queryData)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        returnLabel = (results['results']['bindings'][0]['label']['value'])
    except Exception as ex:
        print(ex)
        print(str(ex))  # output the exception message
        print(ex.args)  # the arguments that the exception has been called with.
        # the first one is usually the message.
        return ('')
    return returnLabel


# Function to match the string
def match(id):
    # regex
    pattern = '[Q]+[0-9]+$'
    # searching pattern
    isAcceptable = False
    try:
        isAcceptable = re.search(pattern, id)
    except Exception as ex:
        print(ex)
        print(str(ex))  # output the exception message
        print(ex.args)  # the arguments that the exception has been called with.
        # the first one is usually the message.
        return ('No')

    if isAcceptable:
        return ('Yes')
    else:
        return ('No')


# Define the start data and time the wikidata revision date much be after
start_time = time.time()
d2 = datetime.datetime(2016, 10, 1)
d22 = datetime.datetime(d2.year, d2.month, d2.day)
d3 = datetime.datetime(2017, 2, 1)
d33 = datetime.datetime(d3.year, d3.month, d3.day)


# Function to parse revision date time for filter of the revision datetime
# so that only revisions after 15th March 2019 are considered.
def convert_date_time(dt):
    f = "%Y-%m-%dT%H:%M:%S%fZ"
    dt1 = datetime.datetime.strptime(dt, f)
    dt2 = datetime.datetime(dt1.year, dt1.month, dt1.day)
    return dt2


# Function to create a new .csv file conaining the revision output data
def newfilecreation(filename, articlesWriter):
    print('NEW PROCESS')
    articlesWriter = csv.writer(filename, quoting=csv.QUOTE_MINIMAL)
    articlesWriter.writerow(['pageid', 'pagetitle', 'label', 'revisionid', 'timestamp', 'comment', 'parentid'])
    pagetitle = ''
    pageid = 0
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
    label = ''
    return articlesWriter


# Function to close a file and open a new file to contain the revision output data
def closeoldfile(filename):
    print(filename)
    filename.flush()
    filename.close()
    # A sleep time is required to allow the proccess to complete otherwise the closing of the
    # previous file and opening of the new file will result in an exception as the process
    ## has not been completed before starting processing the next revision.
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
wikidata_folder_path = os.path.join("C:\wikidata")
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
    articlesWriter.writerow(['pageid', 'pagetitle', 'label', 'revisionid', 'timestamp', 'comment', 'parentid'])
    pagetitle = ''
    pageid = 0
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
    label = ''
    pathWikiXML = os.path.join(wikidata_folder_path, wikidata_file)
    print('#####  OPEN NEW FILE ######')
    # Process the wikidata xml file
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
                        if isAMatch == "Yes":
                            label = get_uri_from_wiki_id(pagetitle)
                        if (pagetitle is None):
                            pagetitle = ''
                            label = ''
                        if (isAMatch == "No"):
                            label = ''
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id' and not inrevision:
                        pageid = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}revision':
                        if (
                                pagetitle != '' and pageid != 0 and label != '' and revisionid != 0 and timestamp != '' and timestamp is not None and convert_date_time(
                                timestamp) > d22 and convert_date_time(timestamp) < d33):

                            # If the total number of items processed is == 1000 close the current file and open a new file
                            # to add the wikidata revision output.
                            if counter == 1000:
                                print('CREATE NEW FILE')
                                filename = closeoldfile(filename)
                                articlesWriter = newfilecreation(filename, articlesWriter)
                                print('NEW FILE CREATED')
                                counter = 0
                                print(filename)

                            if (comment is None):
                                comment = ''
                            articlesWriter.writerow(
                                [pageid, pagetitle, label, revisionid, timestamp, comment.encode('utf8'), parentid])
                            counter += 1
                            print(counter)
                        revisionid = 0
                        inrevision = True
                        timestamp = ''
                        comment = ''
                        parentid = 0
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}id' and inrevision:
                        revisionid = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}comment' and inrevision:
                        comment = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}timestamp' and inrevision:
                        timestamp = elem.text
                    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}parentid' and inrevision:
                        parentid = elem.text
                elem.clear()
        except Exception as ex:
            print(ex)
            print(str(ex))  # # output the exception message
            print(ex.args)  # the arguments that the exception has been called with.
            # the first one is usually the message.
