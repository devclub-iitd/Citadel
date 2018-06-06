import json
import os
from datetime import datetime, timedelta

STATS_FILE = "course_downloads.json"
DATABASE_DIR = os.path.join('..', 'media', 'database')
ZIP_TIME_LIMIT = timedelta(days=92, hours=0, minutes=0)

"""
    script to delete less frequently used zips, whose last download was before the specified time limit
    currently needs to be called manually (in testing phase)
"""
with open(STATS_FILE, "r") as file:
    stats = json.load(file)
for course in stats:
    parent_dir = course[0:2]
    zip_location = os.path.join(DATABASE_DIR, parent_dir, course + '.zip')
    if os.path.exists(zip_location) and os.path.isfile(zip_location):
        last_download = stats[course]["last"]
        if last_download == '' or datetime.now() > datetime.strptime(last_download, '%d/%m/%Y') + ZIP_TIME_LIMIT:
            os.remove(zip_location)
