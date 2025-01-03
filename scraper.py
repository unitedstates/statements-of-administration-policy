# Statements of Administration Policy scraper for the Biden Administration.

import re
import datetime
import os
import os.path

import requests
import scrapy
from bs4 import BeautifulSoup as bs4
import rtyaml
import dateutil.parser

# See https://stackoverflow.com/a/52989487/628748

dashes = re.compile('[—–-]') # em dash, en dash, hyphen

class SAPSpider(scrapy.Spider):
    name = "sap"

    AdministrationCode = "46-Biden"

    allowed_domains = ['www.whitehouse.gov']
    start_urls = ['https://www.whitehouse.gov/omb/statements-of-administration-policy/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'scraper.SAPPipeline': 300,
        }
    }

    def parse(self, response):
        soup = bs4(response.text, 'html.parser')

        con = soup.find('section', {'class': 'body-content'})
        con = con.find('div', {'class': 'container'})
        con = con.find('div', {'class': 'row'})
        ps = con.findAllNext('p')#[1:]

        for item in ps:
            if not item.find("a"): continue

            if "Opt in to send and receive text messages from President Biden" in item.text:
                continue

            # Could not parse bill number
            if "Israel Security Supplemental Appropriations Act" in item.text:
                continue
            if "Limit, Save, Grow Act" in item.text:
                continue

            date_issued = re.search(r"\(((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d+,\s*\d+)\)", item.text).group(1)
            date_issued = re.sub(r",(?=\d)", ", ", date_issued) # a missing space after the comma in the date breaks dateutil.parser, as happened for 46-Biden/117/2021-09-21_hr5305

            text = item.find('a').text
            number_title_split = re.split(dashes, text)
            if len(number_title_split) <= 1:
                # This would ideally be an exception but there's one with a
                # bill number: Limit, Save, Grow Act  (April 25, 2023).
                print(f"Could not find bill number(s) in document title text: '{text}'.")
                continue
            bill_numbers = number_title_split[0].strip()
            bill_numbers = bill_numbers.split(",")
            bill_numbers = [re.sub(r"[\s\.]", "", b.lower()) for b in bill_numbers]

            # Sanitize bill numbers.
            bill_numbers = [
                re.sub("((senate|house)?(substitute)?amendmentto(the)?)+", "", bn)
                for bn in bill_numbers
            ]

            yield {
                'bills': bill_numbers,
                'document_title': text,
                'congress': self.get_congress_number(date_issued[-4:]),
                'date_issued': dateutil.parser.parse(date_issued).date().isoformat(),
                'file': None, # inserted later
                'fetched_from_url': item.find('a', href=True)['href'],
                'date_fetched': None, # inserted later
                'source': response.request.url,
            }

    def get_congress_number(self, year):
        # This is not quite right but the edge cases of SAPs
        # issued between Jan 1 and Jan 3 at noon of odd years,
        # which will be in the previous Congres, hopefully can be ignored.
        congress = 0
        const_year = 2022
        const_congress = 117
        dif = const_year - int(year)
        congress = const_congress - (dif // 2)
        return congress

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(cls.custom_settings or {}, priority='spider')

class SAPPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        # Collect scraped data here.
        self.data = []

        # Save here.
        self.fn = "archive/" + spider.AdministrationCode + ".yaml"

        # Read an existing metadata file if it exists.
        self.file_date_fetched = { }
        self.rescinded = [ ]
        if os.path.exists(self.fn):
            with open(self.fn) as f:
                existing_items = rtyaml.load(f)
                for i, item in enumerate(existing_items):
                    # In order to not update date_fetched when we don't download
                    # a PDF, we need the previously set value so we can pull it forward.
                    self.file_date_fetched[item["file"]] = item["date_fetched"]

                    # Very rarely (once?) a SAP disappears. If we manually mark it as
                    # rescinded, we'll re-insert it into the newly scraped data.
                    # Keep the rescinded items and ordering information so we can
                    # insert it into the right place.
                    if item.get("rescinded"):
                        self.rescinded.append({
                            "item": item,
                            "order": {
                                jitem["file"]: (i < j)
                                for j, jitem in enumerate(existing_items)
                                if i != j
                            }
                        })

    def process_item(self, item, spider):
        # Construct a filename for saving the SAP PDF and put
        # that into the metadata.
        item["file"] = "statements/{}/{}/{}_{}.pdf".format(
            spider.AdministrationCode,
            item["congress"],
            item["date_issued"],
            ",".join(item["bills"])
        )
        fn = "archive/" + item["file"]

        # If we haven't yet downloaded that file, do so.
        if not os.path.exists(fn):
            os.makedirs(os.path.dirname(fn), exist_ok=True)
            with open(fn, "wb") as f:
                with requests.get(item['fetched_from_url']) as response:
                    f.write(response.content)
            item['date_fetched'] = datetime.datetime.now().isoformat()

        # If we have downloaded the file already, pull forward
        # the date_fetched value from the last run.
        elif item["file"] in self.file_date_fetched:
            item["date_fetched"] = self.file_date_fetched[item["file"]]

        # The file is on disk but somehow it wasn't mentioned in
        # the YAML file previously saved, so just reset date_fetched to now.
        # This should never occur except in testing.
        else:
            item['date_fetched'] = datetime.datetime.now().isoformat()

        # Add metadata to output document.
        self.data.append(dict(item))

    def close_spider(self, spider):
        # Add back any resinded items.
        for item in self.rescinded:
            # Find the best index to insert it at using the
            # ordering information stored when we loaded it.
            # Find the index that agrees most with the original
            # sorted order, treating new items has coming before.
            index = max(range(len(self.data) + 1),
                key = lambda i : sum([
                    (1 if (i <= j) == item["order"].get(jitem["file"], False) else -1)
                    for j, jitem in enumerate(self.data)
                ]))
            self.data.insert(index, item["item"])

        # Save to YAML file.
        with open(self.fn, "w") as f:
            rtyaml.dump(self.data, f)

