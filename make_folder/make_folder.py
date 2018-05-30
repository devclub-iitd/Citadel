import json
import os
import shutil

STATS_FILE = 'course_downloads.txt'
dest = os.path.join('..', 'bookShelf', STATS_FILE)

shutil.copy(STATS_FILE, dest)


with open('course_codes.json') as data_file:    
    courses = json.load(data_file)

with open('course_dept.json') as data_file:    
    courses_dept = json.load(data_file)

if not os.path.exists('DATA'):
    os.makedirs('DATA')


for course in courses:
    course_start = course[:2]
    # if course_start not in courses_dept:
        # continue

    # dept = courses_dept[course_start]
    dept = course_start
    print(course, dept)
    if not os.path.exists('DATA/'+dept):
        os.makedirs('DATA/'+dept)
    if not os.path.exists('DATA/'+dept+'/'+course):
        os.makedirs('DATA/'+dept+'/'+course)
    if not os.path.exists('DATA/'+dept+'/'+course+'/Question-Papers'):
        os.makedirs('DATA/'+dept+'/'+course+'/Question-Papers')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Question-Papers/Minor1'):
        os.makedirs('DATA/'+dept+'/'+course+'/Question-Papers/Minor1')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Question-Papers/Minro2'):
        os.makedirs('DATA/'+dept+'/'+course+'/Question-Papers/Minor2')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Question-Papers/Major'):
        os.makedirs('DATA/'+dept+'/'+course+'/Question-Papers/Major')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Books'):
        os.makedirs('DATA/'+dept+'/'+course+'/Books')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Others'):
        os.makedirs('DATA/'+dept+'/'+course+'/Others')
    if not os.path.exists('DATA/'+dept+'/'+course+'/Professors'):
        os.makedirs('DATA/'+dept+'/'+course+'/Professors')  

