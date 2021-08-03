# Sanity check the data files.

import glob
import rtyaml
import re
import os.path
import traceback
import sys

any_errors = False

for fn in glob.glob("archive/*.yaml"):
	filenames = set()
	metadata = rtyaml.load(open(fn))
	for item in metadata:
		try:
			assert isinstance(item.get("bills"), list)
			for bill in item["bills"]:
				assert re.match(r"^(hr|s|hjres|sjres|hconres|sconres|hres|sres)(\d+)$", bill)
			assert isinstance(item.get("document_title"), str)
			assert not re.search(r"\(\d+ page", item["document_title"])
			assert isinstance(item.get("congress"), int)
			assert isinstance(item.get("date_issued"), str) and len(item["date_issued"]) == 10
			assert isinstance(item.get("file"), str) or isinstance(item.get("url"), str)
			if isinstance(item.get("file"), str):
				assert isinstance(item.get("fetched_from_url"), str)
				assert os.path.exists("archive/" + item["file"])
				filenames.add(item.get("file"))
		except AssertionError as e:
			print(fn)
			print("-" * len(fn))
			print(rtyaml.dump(item).rstrip())
			print("-" * len(fn))
			traceback.print_exc(file=sys.stdout)
			print()
			any_errors = True

	for pdf_fn in glob.glob(fn.replace(".yaml", "").replace("archive/", "archive/statements/") + "/*/*.pdf"):
		if pdf_fn.replace("archive/", "") not in filenames:
			print(pdf_fn, "should be deleted.")
			any_errors = True

if any_errors:
	sys.exit(1)