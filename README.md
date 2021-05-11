Statements of Administration Policy
===================================

By the Flatgov team

Statements of Administration Policy (SAP) are statements prepared by the Office of Management and Budget on behalf of the President stating the President's position on legislation before Congress. Statements typically indicate support or opposition to a single bill, with a bill number given.

This repository contains an archive of SAPs from previous presidents (which are no longer available on WhiteHouse.gov) and a scraper for downloading SAPs from the current White House website (currently https://www.whitehouse.gov/omb/statements-of-administration-policy/).

To run the current scraper, first install Python modules:

	pip install -r requirements.txt

Then start the scraper:

	scrapy runspider scraper.py --loglevel=ERROR

