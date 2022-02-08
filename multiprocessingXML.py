import xml.etree.ElementTree as etree
import os
import re
import csv
import datetime
import time
from io import open
from multiprocessing import Pool

subdir = "data_split"
here = os.path.dirname(os.path.realpath(__file__))


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
d3 = datetime.datetime(2017, 1, 1)
d33 = datetime.datetime(d3.year, d3.month, d3.day)


# Function to parse revision date time for filter of the revision datetime
def convert_date_time(dt):
    f = "%Y-%m-%dT%H:%M:%S%fZ"
    dt1 = datetime.datetime.strptime(dt, f)
    dt2 = datetime.datetime(dt1.year, dt1.month, dt1.day)
    return dt2


# Function to create a new .csv file conaining the revision output data
def newfilecreation(filename, articlesWriter):
    print('NEW PROCESS')
    articlesWriter = csv.writer(filename, quoting=csv.QUOTE_MINIMAL)
    articlesWriter.writerow(['pageid', 'pagetitle', 'revisionid', 'timestamp', 'comment', 'parentid'])
    pagetitle = ''
    pageid = 0
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
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


def processWikidata(wikidata_file):
    counter = 0
    print('#####    NEW FILE ######')
    print(wikidata_file)
    filepath = os.path.join(here, subdir, 'wikidata' + '-' + time.strftime('%Y%m%d-%H%M%S') + '.csv')
    print(filepath)
    filename = open(filepath, 'w', newline='', encoding="utf-8")
    articlesWriter = csv.writer(filename, quoting=csv.QUOTE_MINIMAL)
    articlesWriter.writerow(['pageid', 'pagetitle', 'revisionid', 'timestamp', 'comment', 'parentid'])
    pagetitle = ''
    pageid = 0
    validpageid = ''
    timestamp = ''
    comment = ''
    parentid = 0
    revisionid = 0
    pathWikiXML = os.path.join('C:\wikidata\extracted_incr_xml', wikidata_file)
    print('#####  OPEN NEW FILE ######')
    # Process the wikidata xml file
    with open(pathWikiXML, 'rb') as f:
        try:
            for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
                if event == 'start':

                    if 'page' in elem.tag:
                        print(elem.tag)
                        pagetitle = ''
                        pageid = 0
                        inrevision = False
                    elif 'title' in elem.tag:
                        pagetitle = elem.text
                        print(pagetitle)
                        validpageid = match(pagetitle)
                        # if isAMatch == "Yes":
                        #     label = get_uri_from_wiki_id(pagetitle)
                        if (pagetitle is None):
                            pagetitle = ''
                            validpageid = 'No'
                        # if (isAMatch == "No"):
                        #     # if it is not a match then the page does not have a qid
                        #     # they are other pages - we would not want them in the data I think
                        #     # if it  is not a valid page then the label is '' and it is checked in the condition
                        #     # prior to writing to the file
                        #     # therefore rename label to something else such as validPage after result from isAMatch
                        #     label = ''
                    elif 'id' in elem.tag and not inrevision:
                        pageid = elem.text
                    elif 'revision' in elem.tag:
                        if (
                                pagetitle != '' and pageid != 0 and validpageid != 'No' and revisionid != 0 and timestamp != '' and timestamp is not None and convert_date_time(
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
                                [pageid, pagetitle, revisionid, timestamp, comment.encode('utf8'), parentid])
                            counter += 1
                            print(counter)
                        revisionid = 0
                        inrevision = True
                        timestamp = ''
                        comment = ''
                        parentid = 0
                    elif 'id' in elem.tag and inrevision:
                        revisionid = elem.text
                    elif 'comment' in elem.tag and inrevision:
                        comment = elem.text
                    elif 'timestamp' in elem.tag and inrevision:
                        timestamp = elem.text
                    elif 'parentid' in elem.tag and inrevision:
                        parentid = elem.text
                elem.clear()
        except Exception as ex:
            print(ex)
            print(str(ex))  # # output the exception message
            print(ex.args)  # the arguments that the exception has been called with.
            # the first one is usually the message.


if __name__ == '__main__':
    # need to pass the directory which contains the split xml files
    # wikidata_folder_path = os.path.join("C:\wikidata\extracted_incr_xml")
    # In order to get the list of all files that ends with ".xml"
    # get list of all files, and consider only the ones that ends with "xml"
    # wikidata_files = [x for x in os.listdir(wikidata_folder_path) if x.endswith(".xml")]
    # print(wikidata_files)
    # wikidata_files will contain all the

    with Pool(4) as p:
        p.map(processWikidata, [x for x in os.listdir('C:\wikidata\extracted_incr_xml') if x.endswith(".xml")])
