import json
import os
from datetime import datetime, timedelta

STATS_FILE = "course_downloads.json"
DATABASE_DIR = os.path.join('..', 'media', 'database')
ZIP_TIME_LIMIT = timedelta(days=92, hours=0, minutes=0)
ZIP_SIZE_LIMIT = 5e10


def get_size():
    """
        function to get the size of entire database_dir (mostly zip files)
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(DATABASE_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


"""
    script to delete less frequently used zips, until the size of database_dir comes within the specified size limit
    currently needs to be called manually (in testing phase)
"""

"""
    CODE TO DELETE ACCORDING TO LAST DOWNLOAD TIME STAMP
    if os.path.isfile(zip_location):
        last_download = stats[course]["last"]
        if last_download == '' or datetime.now() > datetime.strptime(last_download, '%d/%m/%Y') + ZIP_TIME_LIMIT:
            os.remove(zip_location)
"""


def delete_zips():
    if not (get_size() < ZIP_SIZE_LIMIT):
        with open(STATS_FILE, "r") as file:
            stats = json.load(file)
        sorted_list = sorted(stats.keys(), key=lambda x: (stats[x]["downloads"], stats[x]["last"]))
        cntr = 0
        while get_size() > ZIP_SIZE_LIMIT:
            course = sorted_list[cntr]
            parent_dir = course[0:2]
            zip_location = os.path.join(DATABASE_DIR, parent_dir, course + '.zip')
            if os.path.isfile(zip_location):
                os.remove(zip_location)
            cntr = cntr + 1
