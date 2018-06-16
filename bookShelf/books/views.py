# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
import json
import operator
import shutil
import errno
import urllib.parse
import zipfile

# Django Imports
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, HttpResponse
from django.http import Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import OrderedDict

# Custom Modules
from books import JSONcreator as jsc
from books import search as search

DATABASE_DIR = os.path.join('..', 'media', 'database')
DATABASE_URL = "/media/database"
BULK_UP_DIR = os.path.join('..', 'media', 'bulk')
UNAPPROVED_DIR = os.path.join('..', 'media', 'unapproved')
TREE_DIR = os.path.join('..', 'make_folder', 'DATA')
MAKE_FOLDER_SCRIPT = os.path.join('..', 'make_folder', 'make_folder.py')
DATABASE_DICT_FILE_NAME = "database.json"
SEPARATOR = "$"
META_SPLIT_COMPONENTS = 3
META_EXTENSION = ".meta"
TAG_SEPARATOR = ','
TAG_LIST_SEPARATOR = ',,'
# time limit to store download stats of zip files
ZIP_TIME_LIMIT = timedelta(days=92, hours=0, minutes=0)
# file to record download stats of zips
STATS_FILE = "course_downloads.json"
# file to record all changes to database_dir
JOURNAL = "task_file.json"
# tags to exclude from appearing in meta files
EXCLUDED_TAGS = ['Assignments', 'Question-Papers', 'Minor1', 'Minor2', 'Major', 'Books', 'Others', 'Professors',
                 'Tutorials', 'Notes', 'Lectures/Slides', 'Lectures', 'Slides']
# handles for addition and removal of files to database_dir
add = "additions"
rm = "removals"
# original locations for json files
stats_loc = os.path.join('..', 'make_folder', STATS_FILE)
journal_loc = os.path.join('..', 'make_folder', JOURNAL)
# task_file list key names
COURSE = 'course'
PATH = 'path'
TYPE = 'type'
TIMESTAMP = 'timestamp'


def index(request):
    return render(request, 'books/browse.html')


def getFileName(course_code, sem, year, type_file, prof, filename, other):
    if not validator(course_code, sem, year, type_file, prof, filename, other):
        return "None"
    fileNamePrefix = "[" + sem + year[2:] + "]"
    if other != 'None' and any(x.isalpha() for x in other):
        origFileName = other
    else:
        origFileName = '.'.join(filename.split('.')[:-1])
    fileExtension = "." + filename.split('.')[-1]
    course_code = course_code.upper()
    dirPath = course_code[0:2] + SEPARATOR + course_code

    if (type_file == 'Minor1' or type_file == 'Minor2' or type_file == 'Major'):
        dirPath = dirPath + SEPARATOR + "Question-Papers" + SEPARATOR + type_file
        toWriteFileName = dirPath + SEPARATOR + fileNamePrefix + "-" + course_code + "-" + type_file + fileExtension
    elif (type_file == 'Books' or type_file == 'Others'):
        dirPath = dirPath + SEPARATOR + type_file
        toWriteFileName = dirPath + SEPARATOR + origFileName + fileExtension
    else:
        dirPath = dirPath + SEPARATOR + "Professors" + SEPARATOR + prof + SEPARATOR + type_file
        toWriteFileName = dirPath + SEPARATOR + fileNamePrefix + "-" + origFileName + fileExtension
    return toWriteFileName


def upload(request):
    """
        Controller to Handle Upload of Documents
    """
    if request.method == 'POST':
        course_code = request.POST.get('course_code', "None")
        sem = request.POST.get('sem', "None")
        year = request.POST.get('year', "None")
        type_file = request.POST.get('type_file', "None")
        prof = request.POST.get('professor', "None")
        documents = request.FILES.getlist('documents')
        other_text = request.POST.get('customFilename', "None")
        tagstring = request.POST.get('tag-string', "")
        taglist=tagstring.split(TAG_LIST_SEPARATOR)
        for i in range(len(taglist)):
            taglist[i]=taglist[i].split(TAG_SEPARATOR)
        if len(taglist)!=len(documents):
            return HttpResponse(content="Bad Request, incorrectly formatted tags",status=400)

        ## Ignoring the alternate filename filed when number of files uploaded is more than 1
        if len(documents) > 1:
            other_text = 'None'

        j=0
        for document in documents:
            filename = getFileName(course_code, sem, year, type_file, prof, document.name, other_text)
            if filename == "None":
                return HttpResponse(content="Bad Request, incorrect form data", status=400)
            directory = os.path.dirname(os.path.join(UNAPPROVED_DIR, filename))
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(UNAPPROVED_DIR, filename)

            ## Make sure that two files in unapproved directory don't have same name
            if os.path.isfile(file_path):
                i=1
                file_root = '.'.join(file_path.split('.')[:-1]) 
                ext = file_path.split('.')[-1]
                while os.path.isfile(file_path):
                    file_path = file_root + '(' + str(i) + ')' + '.' + ext
                    i += 1

            destination = open(file_path, "wb+")
            for chunk in document.chunks():
                destination.write(chunk)
            destination.close()
            
            tags=taglist[j]
            keys = []
            destination_meta = file_path + '.meta'
            if os.path.isfile(destination_meta):
                keys = [line.rstrip('\n') for line in open(destination_meta)]
            metafile = open(destination_meta, "a+")
            for k in range(len(tags)):
                if tags[k] not in keys and tags[k].rstrip()!='':
                    metafile.write(tags[k] + '\n')
            metafile.close()
            j+=1
        return render(request, 'books/thanks.html')

    else:
        profs = json.loads(open("profs.json", "r").read(), object_pairs_hook=OrderedDict)
        return render(request, 'books/upload.html', {"profs": profs})


def download_course(request):
    """
        Function to serve the zip files of entire courses. The function updates the course_downloaded database appropriately.
    """
    course = request.GET.get('course', 'None')
    if course == 'None':
        return redirect('/books/')
    parent_dir = course[0:2]
    zip_location = os.path.join(DATABASE_DIR, parent_dir, course + '.zip')
    try:
        if not (os.path.isfile(zip_location)):
            zip_course(course)

        with open(STATS_FILE, "r") as file:
            stats = json.load(file)
        if course not in stats:
            stats[course] = {
                "downloads": 0,
                "last": "",
            }
        stats[course]["downloads"] = stats[course]["downloads"] + 1
        stats[course]["last"] = datetime.now().strftime("%Y%m%d")
        with open(STATS_FILE, "w") as file:
            json.dump(stats, file)
        
        loc = DATABASE_DIR.split(os.sep)
        path = '/'.join(loc)
        return redirect('/' + path + '/' + parent_dir + '/' + course + '.zip')
    
    except OSError as e:
        return HttpResponse(status=400,content="Bad Request")
    


@login_required
def approve(request):
    """
        Controller to Handle approval of requests
    """
    pending_approvals = False
    with open(JOURNAL, "r") as file:
        tasks = json.load(file)
    if len(tasks) > 0:
        pending_approvals = True
    unapproved_documents = []
    for path, dirs, files in os.walk(UNAPPROVED_DIR):
        for filename in files:
            if not filename.endswith('.meta'):
                f = os.path.join(path, filename)
                unapproved_documents.append(str(f)[str(f).rindex(os.sep) + 1:])

    if len(unapproved_documents) == 0:
        error = "No Unapproved documents present, please ask people to upload material and contribute to the Citadel"
    else:
        error = ''
    return render(request, 'books/approve.html', {'unapproved_documents': unapproved_documents,
                                                  'pending_approvals': pending_approvals, 'error': error})


@login_required
def remove_unapproved_document(request):
    path_to_file = os.path.join(UNAPPROVED_DIR, request.GET.get('name', 'None'))
    path_to_meta = path_to_file + '.meta'
    flag = 0
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)
    else:
        flag = flag + 1
    if os.path.isfile(path_to_meta):
        os.remove(path_to_meta)
    else:
        flag = flag + 2

    def switch(arg):
        result = {
            1: '<h1>No such file exists. Maybe it was manually deleted. MetaFile was successfully deleted.</h1>',
            2: '<h1>MetaFile didn\'t exist. Maybe it was manually deleted. File was successfully deleted.</h1>',
            3: 'No such file or corresponding metafile existed. Maybe they were deleted manually'
        }
        return result.get(arg, "Something went wrong. Please check manually")
    if flag == 0:
        return redirect('/books/approve')
    else:
        return HttpResponse(switch(flag))


@login_required
def approve_unapproved_document(request):
    """
        controller to approve the files and create the meta file of those files alongside in the database_dir
    """
    fileName = request.GET.get('name', 'None')
    if fileName =="None":
        return HttpResponse(content="Bad Request, name parameter missing", status=400)

    fileMeta = fileName + '.meta'
    
    seperatedlist = fileName.split(SEPARATOR)
    destination = DATABASE_DIR
    for directory in seperatedlist:
        destination = os.path.join(destination, directory)
    destination_meta = destination + '.meta'

    if os.path.isfile(os.path.join(UNAPPROVED_DIR, fileName)) and os.path.isfile(os.path.join(UNAPPROVED_DIR, fileMeta)):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(os.path.join(UNAPPROVED_DIR, fileName), destination)
        shutil.copy(os.path.join(UNAPPROVED_DIR, fileMeta), destination_meta)
        add_tasks(add, [os.path.relpath(destination, DATABASE_DIR)])
        fileName = urllib.parse.quote(fileName.encode('utf-8'))
        return redirect('/books/remove_unapproved_document?name=' + fileName)
    else:
        return HttpResponse(content="The file has missing metafile, rename it to generate a meta file and then approve it<br> Or the name passed as argument does not exist.",status=400)


@login_required
def rename(request):
    #use try blocks
    if request.method == "GET":
        if request.GET.get('name', '')=='':
            return HttpResponse('<h1> Invalid use of Rename API</h1>',status=400)
        with open(os.path.join(UNAPPROVED_DIR, request.GET.get('name') + '.meta'), "r") as file:
            taglist=[]
            for line in file:
                strip_line=line.rstrip()
                if strip_line != '':
                    taglist.append(strip_line)
        return render(request, "books/rename.html", {"org": request.GET.get('name'), "tags": ', '.join(taglist)})
    elif request.method == "POST":
        with open(os.path.join(UNAPPROVED_DIR, request.POST.get('org') + '.meta'), "w") as file:
            for tag in request.POST.get("tags",'').split(','):
                if tag.rstrip()!='':
                    file.write(tag.rstrip() + '\n')
        if request.POST.get('final') != '' and request.POST.get('final') != request.POST.get('org'):
            directory = os.path.dirname(os.path.join(UNAPPROVED_DIR, request.POST.get('final')))

            if not os.path.exists(directory):
                os.makedirs(directory)
            meta_final = request.POST.get('final') + '.meta'
            meta_org = request.POST.get('org') + '.meta'
            shutil.copy(os.path.join(UNAPPROVED_DIR, request.POST.get('org')),
                        os.path.join(UNAPPROVED_DIR, request.POST.get('final')))
            shutil.copy(os.path.join(UNAPPROVED_DIR, meta_org),
                        os.path.join(UNAPPROVED_DIR, meta_final))
            filename = urllib.parse.quote(request.POST.get('org').encode('utf-8'))
            return redirect('/books/remove_unapproved_document?name=' + filename)
        return redirect('/books/approve')
    else:
        return HttpResponse('<h1> Invalid use of Rename API</h1>')


@login_required
def bulk_approve(request):
    """
        controller to approve the bulk pasted files
        admin needs to click on finalize approvals once after manually pasting new files.
    """
    if request.method == "GET":
        build_meta_files()
        paths = export_files()
        add_tasks(add, paths)
        restore_structure()
        return redirect('/books/finalize_approvals')
    else:
        return redirect('/books/approve')


def generate_path_meta_tags(inner_path):
    tags = []
    inner_path = os.path.split(inner_path)[0]
    while os.path.split(inner_path)[0] is not '':
        tag = os.path.split(inner_path)[1] 
        if tag not in EXCLUDED_TAGS:
            tags.append(tag)
        inner_path = os.path.split(inner_path)[0]
    return tags



@login_required
def force_integrity(request):
    """
        controller to force recreate the json heirarchy and also take care of
        dangling meta files, and create missing meta files
    """
    if request.method == "GET":
        for root, dirs, files in os.walk(DATABASE_DIR):
            for filename in files:
                if not filename.endswith('.zip'):
                    if filename.endswith('.meta'):
                        pathname = os.path.join(root, '.'.join(filename.split('.')[:-1]))
                        if not (os.path.isfile(pathname)):
                            os.remove(os.path.join(root, filename))
                    else:
                        metafilename = filename + '.meta'
                        metafile = os.path.join(root, metafilename)
                        if not (os.path.isfile(metafile)):
                            tags = generate_path_meta_tags(os.path.relpath(metafile, DATABASE_DIR))
                            with open(metafile,"w") as f:
                                f.write('\n'.join(tags))

        jsc.recreate_path(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
        return redirect('/books/')
    else:
        return redirect('/books/')


@login_required
def finalize_approvals(request):
    if request.method == "GET":
        finalize_function()
        return redirect('/books/')
    else:
        return redirect('/books/')


def userlogin(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('/books/approve')
        else:
            render(request, 'books/login.html')
    return render(request, 'books/login.html')


def userlogout(request):
    logout(request)
    return redirect("/books/")


@api_view()
def APIstructure(request):
    f = jsc.path_to_dict(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
    path = request.GET.get('path', os.sep)
    depth = int(request.GET.get('depth', 3))
    try:
        db = jsc.navigate_path(f, path, False)
    except Exception as e:
        return Response({})
    else:
        truncated_db = jsc.truncate_db(db, depth)
        return Response(truncated_db)


@api_view()
def APIsearch(request):
    """
        gives a list of all path_prefix objects matching search terms
    """
    f = jsc.path_to_dict(DATABASE_DIR, DATABASE_DICT_FILE_NAME)  ####can this be drier? repeated code
    keyword_list = (request.GET.get('query', "")).split()
    path = request.GET.get('path', "/")
    path_prefix = search.get_path_prefix(path)
    try:
        db = jsc.navigate_path(f, path, False)
    except Exception as e:
        print("invalid path")
        return Response({})
    else:
        result = search.search_dic(db, path_prefix, keyword_list)
        return Response({"result": result})


def export_files():
    """
        Function to export the pasted files from bulk_up_dir to database_dir
    """
    paths = []
    for root, _, files in os.walk(BULK_UP_DIR):
        for filename in files:
            from_link = os.path.join(root, filename)
            to_link = os.path.join(DATABASE_DIR, os.path.relpath(from_link, BULK_UP_DIR))
            directory = os.path.dirname(to_link)
            if not os.path.exists(directory):
                os.makedirs(directory)
            shutil.move(from_link, to_link)
            if not filename.endswith('.meta'):
                paths.append(os.path.relpath(to_link, DATABASE_DIR))

    return paths


def build_meta_files():
    """
        Function to build meta files for all the files which are manually pasted (uses the location) and appends tags to original meta file if present
    """
    for root, _, files in os.walk(BULK_UP_DIR, topdown=True):
        for filename in files:
            if not filename.lower().endswith('.meta'):
                file_loc = os.path.join(root, filename)
                metafile_loc = file_loc + '.meta'

                ## Read tags already added by the user                 
                old_tags = []
                if os.path.isfile(metafile_loc):
                    with open(metafile_loc,"r") as f: 
                        old_tags = f.readlines()
                    old_tags = [tag.strip() for tag in old_tags]
            
                new_tags = generate_path_meta_tags(os.path.relpath(metafile_loc, BULK_UP_DIR))
                final_tags = old_tags + list( set(new_tags) - set(old_tags))
                with open(metafile_loc,"w") as f:
                    f.write('\n'.join(final_tags))
                    

def add_tasks(type_of_change, paths):
    """
     Function to add tasks to task_file.json, either in bulk or on each approval
    """
    with open(JOURNAL, "r") as file:
        tasks = json.load(file)
    for path in paths:
        task = {}
        separated_path = path.split(os.sep)
        task[COURSE] = separated_path[1]
        task[TYPE] = type_of_change
        task[PATH] = path
        task[TIMESTAMP] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tasks.append(task)
    with open(JOURNAL, "w") as file:
        json.dump(tasks, file)


def finalize_function():
    """
        Function to execute task_file.json course wise, task wise and modify zips and database.json
    """
    with open(JOURNAL, "r") as file:
        tasks = json.load(file)
    sorted_tasks = sorted(tasks, key=lambda k: k[COURSE])
    if len(sorted_tasks) > 0:
        task = sorted_tasks[0]
        previous_course = task[COURSE]
        zip_location = os.path.join(DATABASE_DIR, previous_course[0:2], previous_course + '.zip')
        if os.path.isfile(zip_location):
            zip_present = 1
            os.remove(zip_location)
        else:
            zip_present = 0
    while len(sorted_tasks) > 0:

        tasks_handler(sorted_tasks)
        task = sorted_tasks.pop(0)
        if task[COURSE] != previous_course:
            if zip_present == 1:
                zip_course(previous_course)
            previous_course = task[COURSE]
            zip_location = os.path.join(DATABASE_DIR, previous_course[0:2], previous_course + '.zip')
            if os.path.isfile(zip_location):
                os.remove(zip_location)
                zip_present = 1
            else:
                zip_present = 0

    with open(JOURNAL, "w") as file:
        json.dump(sorted_tasks, file)

def tasks_handler(tasks):
    """
        Controller to modify database.json according to task
    """
    with open(DATABASE_DICT_FILE_NAME, "r") as file:
        data = json.load(file)
    for task in tasks:
        if task[TYPE]=="additions":
            db=data
            separated_path=(task[PATH]).split(os.sep)
            db=jsc.navigate_path(db, (os.sep).join(separated_path[:-1]), True)
            db[separated_path[-1]]=(DATABASE_DIR + task[PATH])[2:]
    with open(DATABASE_DICT_FILE_NAME, "w") as file:
        json.dump(data, file)

def startup_function():
    """
        Function called on each server start
    """
    if not (os.path.isfile(STATS_FILE)):
        shutil.copy(stats_loc, STATS_FILE)
    if not (os.path.isfile(JOURNAL)):
        tasks = []
        with open(JOURNAL, "w") as file:
            json.dump(tasks, file)
    finalize_function()


def zip_course(course):
    """
     Function to zip courses given a course code
    """
    parent_dir = course[0:2]
    zip_location = os.path.join(DATABASE_DIR, parent_dir, course + '.zip')
    course_path = os.path.join(DATABASE_DIR, parent_dir, course)
    if not os.path.isdir(course_path):
        raise OSError
    zf = zipfile.ZipFile(zip_location, "w")
    for dirname, _, files in os.walk(course_path):
        for filename in files:
            if not filename.lower().endswith('.meta'):
                path = os.path.join(dirname, filename)
                to_write = os.path.relpath(path, course_path)
                zf.write(path, arcname=to_write)
    zf.close()


def restore_structure():
    """
    Function to restore the folder tree structure of BULK_DIR after exporting files
    """
    if not os.listdir(TREE_DIR):
        dir = os.path.dirname(MAKE_FOLDER_SCRIPT)
        os.system("cd " + dir + " && " + "python " + MAKE_FOLDER_SCRIPT)
    for dirpath, _, _ in os.walk(BULK_UP_DIR, topdown=False):
        structure = os.path.join(TREE_DIR, os.path.relpath(dirpath, BULK_UP_DIR))
        if not os.path.isdir(structure):
            shutil.rmtree(dirpath)


def validator(course_code, sem, year, type_file, prof, filename, other):
    """
    function to validate the form parameters, only shadows the JS form validator for consistency
    """
    pattern = r'\b[a-zA-Z]{3}[0-9]{3}\b'
    result = True
    if (type_file == 'Minor1' or type_file == 'Minor2' or type_file == 'Major') and (sem == "None" or year == "None"):
        result = False
    elif type_file == 'Books' or type_file == 'Others':
        result = True
    elif sem == "None" or year == "None" or prof == "None":
        result = False

    if course_code == "None":
        result = False

    if not re.match(pattern, course_code):
        result = False

    return result


