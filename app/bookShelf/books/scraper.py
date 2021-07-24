import os
import requests
import json
import re
import collections
from bs4 import BeautifulSoup as bs


# URLs to scrape
ROOT_URL = 'http://ldap1.iitd.ernet.in/LDAP/'
COURSE_LIST_URL = ROOT_URL + 'courses/gpaliases.html'
ORG_LIST_URL = ROOT_URL + 'dcs.html'

# File paths
COURSE_FILE = 'courses.json'
PROF_FILE = 'profs.json'

# Org Units to be ignored while scraping
COMMON_ORG_UNITS = [
    'admin', 'courses', 'hospital', 'hpc', 'iitd', 'library', 'visitor', 'circular', 'cc', 'fitt', 'ird', 'irdtest', 'nctu',
]



def getCourseList(path_to_file):
    """
    Function to scrape the course list
    """
    courses = []
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file:
            courses = json.load(file)
    
    try:
        response = requests.get(COURSE_LIST_URL)
    except requests.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        #raise e
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        #raise e
    except Exception as e:
        print(f"Some other error occurred: {e}")
        #raise e
    
    html = response.content
    soup = bs(html, "html.parser")

    table_body = soup.find('table')
    cells = table_body.find_all('a')

    for cell in cells:
        course_code = cell.text.strip()
        if validateCourseCode(course_code):
            if course_code not in courses:
                courses.append(course_code)

    with open(path_to_file, 'w') as file:
        json.dump(courses, file, indent='\t')

def validateCourseCode(course_code):
    pattern = r'\b[a-zA-Z]{3}[0-9]{3}\b'
    result = True
    
    if course_code == None:
        result = False
    elif len(course_code) != 6:
        result = False
    elif not re.match(pattern, course_code):
        result = False
    
    return result



def getProfList(path_to_file):
    """
    Function to scrape the prof list
    path_to_file is the relative path to the profs.json file. A new file is created if it does not exist, else the 
    old file is updated.
    """
    profs=  {}
    if os.path.isfile(path_to_file):
        with open(path_to_file, 'r') as file:
            profs = json.load(file)

    try:
        response = requests.get(ORG_LIST_URL)
    except requests.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        #raise e
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        #raise e
    except Exception as e:
        print(f"Some other error occurred: {e}")
        #raise e
    
    html = response.content
    soup = bs(html, "html.parser")
    
    table_body = soup.find('table')
    cells = table_body.find_all('a')

    for cell in cells:
        org = cell.text.strip()
        if org not in COMMON_ORG_UNITS:
            org_url = ROOT_URL + cell.get('href')   # Page has relative url links
            faculty_urls = getFacultyURLs(org_url)
            
            for url in faculty_urls:
                if url is not None:
                    table = getFacultyTable(url)
                    if table is not None:
                        rows = table.find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) == 2:
                                prof_id = cols[0].text.strip()
                                prof_name = cols[1].text.strip()

                                if prof_id and prof_name:
                                    profs[prof_id] = prof_name
    
    
    sorted_prof_list = collections.OrderedDict(sorted(profs.items()))
    with open(path_to_file, 'w') as file:
        json.dump(sorted_prof_list, file, indent='\t')

def getFacultyURLs(url):
    """
    Get the urls of all faculty list pages in an org page (org_faculty, org_vfaculty, org_retfaculty etc.)
    """
    try:
        response = requests.get(url)
    except requests.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        #raise e
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        #raise e
    except Exception as e:
        print(f"Some other error occurred: {e}")
        #raise e
    
    html = response.content
    soup = bs(html, "html.parser")

    table = soup.find_all('table')[0]
    
    pattern = r'.*[_].{0,4}faculty$|.*[.].{0,4}faculty$'
    faculty = table.find_all('a', string = re.compile(pattern))

    faculty_urls = []
    if faculty is not None:
        for f in faculty:
            faculty_url = '/'.join(url.split('/')[:-1] + [f.get('href')])
            faculty_urls.append(faculty_url)
    
    return faculty_urls

def getFacultyTable(url):
    """
    Function to get the table of name and id of all faculty in a faculty list page 
    """
    try:
        response = requests.get(url)
    except requests.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        #raise e
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        #raise e
    except Exception as e:
        print(f"Some other error occurred: {e}")
        #raise e
    
    html = response.content
    soup = bs(html, "html.parser")

    table = soup.find('table')
    
    return table