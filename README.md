Statements of Administration Policy
===================================

By the Flatgov team

Statements of Administration Policy (SAP) are statements prepared by the Office of Management and Budget on behalf of the President stating the President's position on legislation before Congress. Statements typically indicate support or opposition to a single bill, with a bill number given. See the [CRS report explaining what they are](https://www.everycrsreport.com/reports/R44539.html).

This repository contains an archive of SAPs from previous presidents (which are no longer available on whitehouse.gov) and a scraper for downloading SAPs from the current White House website (currently https://www.whitehouse.gov/omb/statements-of-administration-policy/).

Data Format
-----------

This repository contains metadata for each Statement of Administration Policy (since the start of President Obama's administration), PDF files for each SAP, and a file with basic information for each president.

### Metadata

Metadata for SAPs are grouped by presidential administration (i.e. president) in files named:

	archive/44-Obama.yaml
	archive/45-Trump.yaml
	archive/46-Biden.yaml

Each YAML file is a list of records, one record per SAP. Each record has a self-explanatory format shown in this example record:

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

* Each Statement of Administration Policy may relate to more than one bill, although this is uncommon.
* Bill IDs are given in the same format as `bill_id`s in the congress project scraper (see [https://github.com/unitedstates/congress/wiki/bills](https://github.com/unitedstates/congress/wiki/bills)), except that the Congress number is stored in a separate field.
* The `fetched_from_url` will be invalid after the end of the administration but may be resolvable on the Internet Archive Wayback Machine.

### PDFs

PDFs for SAPs are also stored in this repository and are organized by administration and Congress in files named such as:

	archive/statements/44-Obama/112/2012-02-06_hr1734.pdf

The file name for each SAP is in the metadata record for the SAP --- don't try to construct the file name. Assume the file names are arbitrary.

### Information about Presidents

The file `presidents.yaml` in the main directory of this repository contains basic information about each president for which SAPs are available in this repository. The information is modeled off of the [executive.yaml](https://github.com/unitedstates/congress-legislators/blob/main/executive.yaml) file in the [congress-legislators](https://github.com/unitedstates/congress-legislators/) project.

`presidents.yaml` is a dictionary whose keys are the file names of the SAP metadata files without the `.yaml` extension. Here is an excerpt:

```yaml
44-Obama:
  id:
    bioguide: O000167
    govtrack: 400629
  name:
    first: Barack
    last: Obama
  terms:
    start: '2009-01-20'
    end: '2013-01-20'
```

Adding New Statements of Administration Policy
----------------------------------------------

To run the current scraper, first install Python modules:

	pip install -r requirements.txt

Then start the scraper to fetch new Statements of Administration Policy:

	scrapy runspider scraper.py --loglevel=ERROR

This will update the latest YAML file and download new PDFs.

You can also test the metadata integrity by runing
	
	python3 test.py