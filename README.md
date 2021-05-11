Statements of Administration Policy
===================================

By the Flatgov team

Statements of Administration Policy (SAP) are statements prepared by the Office of Management and Budget on behalf of the President stating the President's position on legislation before Congress. Statements typically indicate support or opposition to a single bill, with a bill number given.

This repository contains an archive of SAPs from previous presidents (which are no longer available on WhiteHouse.gov) and a scraper for downloading SAPs from the current White House website (currently https://www.whitehouse.gov/omb/statements-of-administration-policy/).

Data Format
-----------

Statements of Administration policy are grouped by presidential administration (i.e. president) in files named:

	archive/44-Obama.yaml
	archive/45-Trump.yaml
	archive/46-Biden.yaml

Additionally, PDFs for the Statements are stored in this repository and are organized by administration and Congress in files named such as:

	archive/statements/44-Obama/112/2012-02-06_hr1734.pdf

Each YAML file is a list of records, one per issued Statement of Administration Policy. Each record has a self-explanatory format shown in this example record:

```yaml
- bills:
  - hr1734
  document_title: Civilian Property Realignment Act (2 pages, 223 kb)
  congress: 112
  date_issued: '2012-02-06'
  file: statements/44-Obama/112/2012-02-06_hr1734.pdf
  fetched_from_url: https://obamawhitehouse.archives.gov/sites/default/files/omb/legislative/sap/112/saphr1734h_20120206.pdf
  date_fetched: '2021-01-27T18:10:54.379Z'
```

Notes:

* Each Statement of Administration Policy may relate to more than one bill, although this is rare.
* Bill IDs are given in the same format as `bill_id`s in the congress project scraper (see [https://github.com/unitedstates/congress/wiki/bills](https://github.com/unitedstates/congress/wiki/bills)), except that the Congress number is stored in a separate field.
* The file name for each record is in the metadata --- you don't need to construct a file name. Assume the file names are arbitrary.
* The `fetched_from_url` will be invalid after the end of the administration but may be resolvable on the Internet Archive Wayback Machine.

Adding New Statements of Administration Policy
----------------------------------------------

To run the current scraper, first install Python modules:

	pip install -r requirements.txt

Then start the scraper to fetch new Statements of Administration Policy:

	scrapy runspider scraper.py --loglevel=ERROR

This will update the latest YAML file and download new PDFs.

You can also test the metadata integrity by runing
	
	python3 test.py