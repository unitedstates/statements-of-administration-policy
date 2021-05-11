# Sanity check the data files.

import glob
import rtyaml
import os.path
import traceback

for fn in glob.glob("archive/*.yaml"):
	metadata = rtyaml.load(open(fn))
	for item in metadata:
		try:
			assert isinstance(item.get("bills"), list)
			assert isinstance(item.get("document_title"), str)
			assert isinstance(item.get("congress"), int)
			assert isinstance(item.get("date_issued"), str) and len(item["date_issued"]) == 10
			assert isinstance(item.get("fetched_from_url"), str)
			assert item["file"] and os.path.exists("archive/" + item["file"])
		except AssertionError as e:
			print(fn)
			print("-" * len(fn))
			print(rtyaml.dump(item).rstrip())
			print("-" * len(fn))
			traceback.print_exc()
			print()