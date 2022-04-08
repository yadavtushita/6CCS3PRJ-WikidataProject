from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# Scrapes the names of bots off the following url
# Stores the bots in a CSV file called wikidata_bots.csv

# Need to install a certificate for the below url
my_url = 'https://hgztools.toolforge.org/botstatistics/?lang=www&project=wikidata&dir=desc&sort=ec'

# Opens a connection with the webpage and downloads the webpage
uClient = uReq(my_url)
# Read would dump the webpage which is then stored in page_html
page_html = uClient.read()
# Close the connection with the client
uClient.close()

# html parsing
page_soup = soup(page_html, "html.parser")
# print(page_soup.head)

# Grabs all the tr tags on the webpage
table_all = page_soup.findAll("tr")
# Removes first 3 tags to collect all the bots in the remaining tags
table_bots = table_all[3:]
# print(len(table_bots))
# print(table_bots[0])

filename = "wikidata_bots.csv"
f = open(filename, "w", newline='', encoding="utf-8")

header = "bot_name\n"

f.write(header)

no_of_bots = 0
for bot_data in table_bots:
    count = 0
    for td_rows in bot_data:
        a_tags = td_rows.findAll("a")
        count += 1
        if count == 2:
            print(a_tags[0].text)
            bot_name = a_tags[0].text
            f.write(bot_name + "\n")
            no_of_bots += 1

print(no_of_bots)
f.close()






