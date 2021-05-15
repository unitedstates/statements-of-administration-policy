# Spider for the UCSB American Presidency Project
# (https://www.presidency.ucsb.edu/)'s list of
# SAPs.

import re
import datetime

import scrapy
from bs4 import BeautifulSoup as bs4
import rtyaml
import dateutil.parser

now = datetime.datetime.now().isoformat()

Presidents = {
    # Skip presidents that we pull(ed) ourselves from authoritative sources.
    "Joseph R. Biden": None,
    "Donald J. Trump": None,
    "Barack Obama": None,

    # Map president names to filenames.
    "George W. Bush": "43-Bush",
    "William J. Clinton": "42-Clinton",
    "George Bush": "41-Bush",
    "Ronald Reagan": "40-Reagan",
}

class UCSBSpider(scrapy.Spider):
    name = "sap-uscb"

    allowed_domains = ['www.presidency.ucsb.edu']
    start_urls = ['https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/statements-administration-policy-reagan-1985']

    custom_settings = {
        'ITEM_PIPELINES': {
            'ucsb_scraper.UCSBPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 543,
        },
        'HTTPCACHE_ENABLED': True, # not sure if this is working
    }

    def parse(self, response):
        soup = bs4(response.text, 'html.parser')

        rows = soup.find('table', {'class': 'views-table'})\
                  .findAll('tr')[1:] # skip header

        for item in rows:
            bill_numbers = item.findAll('td')[0].text.strip()
            if not bill_numbers:
                bill_numbers = [] # no info on related bill numbers
            else:
                bill_numbers = [re.sub("-amend|senateamendmentto|conferencereportto|conferencereporton|confreporton|amendto", "",
                                  re.sub(r"[\s\.]|\(.*?\)", "", b.lower()))
                                for b in re.split(r"[,&]| and ", bill_numbers)]
                bill_numbers = [b for b in bill_numbers if b.strip() != "" and "_" not in b]

            president = item.findAll('td')[1].text.strip()

            date_issued = item.findAll('td')[2].text
            date_issued = dateutil.parser.parse(date_issued).date().isoformat()

            title = item.findAll('td')[3].text.strip()
            if title.startswith("Statement of Administration Policy: "):
                title = title[len("Statement of Administration Policy: "):]

            link = item.find('a', href=True)['href']

            yield {
            #'original_bills': item.findAll('td')[0].text.strip(),
                'president': president,
                'bills': bill_numbers,
                'document_title': title,
                'congress': self.get_congress_number(date_issued[:4]),
                'date_issued': date_issued,
                'url': link,
                'date_fetched': now,
                'source': self.start_urls[0],
            }

        # Scrape next page.
        a_next = soup.find('a', {'title': 'Go to next page'}, href=True)
        if a_next and "page=" in a_next["href"]:
            yield scrapy.Request(a_next["href"], self.parse)


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

class UCSBPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_item(self, item, spider):
        # Add metadata to output document.
        president = Presidents[item['president']]
        del item['president']
        if president:
            self.data.setdefault(president, [])\
                     .append(item)

    def open_spider(self, spider):
        # Collect scraped data here, organized by president.
        self.data = { }

    def close_spider(self, spider):
        # Write all data to YAML files by president.
        for admincode, saps in self.data.items():
            fn = "archive/" + admincode + ".yaml"

            # # Restore the existing date_fetched so that on re-scans
            # # we don't cause a change throughout the data files.
            # import os.path
            # if os.path.exists(fn):
            #     date_fetched = { }
            #     with open(fn) as f:
            #         for item in rtyaml.load(f):
            #             date_fetched[item["url"]] = item["date_fetched"]
            #     for item in saps:
            #         item["date_fetched"] = date_fetched[item["url"]]

            with open(fn, "w") as f:
                rtyaml.dump(saps, f)

