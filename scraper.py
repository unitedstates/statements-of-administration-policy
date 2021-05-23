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
        ps = con.findAllNext('p')[1:]

        for item in ps:
            if not item.find("a"): continue

            date_issued = item.text.split('(')[-2].split(')')[0]

            text = item.find('a').text
            for split_char in ('—', '–', '-'): # em dash, en dash, hyphen
            	if split_char in text:
            		bill_numbers = text.split(split_char)[0].strip()
            		break
            else:
            	raise ValueError("Could not find bill number(s) in document title text.")
            bill_numbers = bill_numbers.split(",")
            bill_numbers = [re.sub(r"[\s\.]", "", b.lower()) for b in bill_numbers]

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

        # Don't update date_fetched when we don't download a PDF, so
        # pull in the existing fetch date for files we already have
        # so that we can pull the dates forward.
        self.file_date_fetched = { }
        if os.path.exists(self.fn):
            with open(self.fn) as f:
                for item in rtyaml.load(f):
                    self.file_date_fetched[item["file"]] = item["date_fetched"]

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
        # Save to YAML file.
        with open(self.fn, "w") as f:
            rtyaml.dump(self.data, f)

