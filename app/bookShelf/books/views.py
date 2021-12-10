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
from PIL import Image

# Django Imports
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, HttpResponse
from django.http import Http404, response
from django.urls import reverse
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import OrderedDict

# Custom Modules
from books import JSONcreator as jsc
from books import search as search
from books import scraper as scraper

DATABASE_DIR = os.path.join('..', 'protected', 'database')
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
# file to store profs list
PROF_FILE = 'profs.json'
# file to store course list
COURSE_FILE = 'courses.json'
# file to store requested material details
REQUESTS_FILE = 'requests.json'
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
# image format extensions supported
IMG_EXT = ['jpg', 'jpeg', 'png', 'gif']


@login_required
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

def createMetaFile(file_path, tags):
    keys = []
    destination_meta = file_path + '.meta'
    if os.path.isfile(destination_meta):
        keys = [line.rstrip('\n') for line in open(destination_meta)]
    metafile = open(destination_meta, "a+")
    for k in range(len(tags)):
        if tags[k] not in keys and tags[k].rstrip()!='':
            metafile.write(tags[k] + '\n')
    metafile.close()

@login_required
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
        image_order = request.POST.get('image-order', "")
        image_order_list = []
        if len(image_order)>0:
            for order in image_order.split(TAG_SEPARATOR):
                image_order_list.append(int(order))
        taglist=tagstring.split(TAG_LIST_SEPARATOR)
        for i in range(len(taglist)):
            taglist[i]=taglist[i].split(TAG_SEPARATOR)
        if len(taglist)!=len(documents):
            return HttpResponse(content="Bad Request, incorrectly formatted tags",status=400)

        ## Ignoring the alternate filename filed when number of files uploaded is more than 1
        if len(documents) > 1:
            other_text = 'None'

        # Remove material request if present
        removeRequest(course_code, sem, year, prof, type_file)

        j=0
        # Treat image files differently: to concatenate them(if more than 1) and convert to PDF
        img_files = []
        img_tags = []
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
            
            # Separate supported image files
            ext = file_path.split('.')[-1]
            if ext in IMG_EXT:
                img_files.append(file_path)
                img_tags.extend(taglist[j])
            else:
                tags=taglist[j]
                createMetaFile(file_path, tags)
            j+=1

        if len(img_files)>0:
            imgs = []
            for img_path in img_files:
                im = Image.open(img_path)
                if im.mode == 'RGBA':
                    im = im.convert('RGB')
                imgs.append(im)

            minsize = min(im.size for im in imgs)

            for i in range(len(imgs)):
                imgs[i] = imgs[i].resize(minsize)

            # Get the correct page order of images to be concatenated. 
            reordered_imgs = list(imgs)
            if len(image_order_list)>0:
                if len(imgs)==len(image_order_list):
                    i=0
                    for order in image_order_list:
                        reordered_imgs[order-1] = imgs[i]
                        i+=1

            file_path = '.'.join(img_files[0].split('.')[:-1])
            file_path += '.pdf'

            if len(reordered_imgs) > 1:
                reordered_imgs[0].save(file_path, save_all=True, append_images=reordered_imgs[1:])
            else:
                reordered_imgs[0].save(file_path, save_all=True)

            createMetaFile(file_path, img_tags)
            ##Remove Images after PDF creation from unapproved dir
            for img_file in img_files:
                if os.path.isfile(img_file):
                    os.remove(img_file)

        return render(request, 'books/thanks.html')

    else:
        profs = json.loads(open("profs.json", "r").read(), object_pairs_hook=OrderedDict)
        return render(request, 'books/upload.html', {"profs": profs})

@login_required
def download_course(request):
    """
        Function to serve the zip files of entire courses. The function updates the course_downloaded database appropriately.
    """
    course = request.GET.get('course', 'None')
    if course == 'None':
        return redirect('/books/')
    zip_location = os.path.join(DATABASE_DIR, course + '.zip')
    try:
        if not (os.path.isfile(zip_location)):
            zip_course(course)

        if not os.path.isfile(STATS_FILE):
            shutil.copy(stats_loc, STATS_FILE)

        with open(STATS_FILE, "r") as file:
            stats = json.load(file)
        course_stat = jsc.navigate_path(stats, course, True)

        try:
            course_stat['downloads'] += 1
        except:
            course_stat['downloads'] = 1
            course_stat['last'] = ''
        course_stat['last'] = datetime.now().strftime("%Y%m%d")

        stats = jsc.update_db(stats, course, course_stat)
        
        with open(STATS_FILE, "w") as file:
            json.dump(stats, file)
        
        return redirect(DATABASE_URL + '/' + course + '.zip')
    
    except OSError as e:
        return HttpResponse(status=400,content="Bad Request")
    


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
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


def Healthz(request):
    if request.method == "GET":
        return HttpResponse('Ok Healthy!',status=200)


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
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



@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
def finalize_approvals(request):
    if request.method == "GET":
        finalize_function()
        return redirect('/books/')
    else:
        return redirect('/books/')


@user_passes_test(lambda u: u.is_superuser)
def updateProfList(request):
    """
        scrape profs list and update profs.json 
    """
    if request.method == "GET":
        #print(os.path.isfile(PROF_FILE))
        scraper.getProfList(PROF_FILE)
        return redirect('/books/')
    else:
        return redirect('/books/')

@user_passes_test(lambda u: u.is_superuser)
def updateCourseList(request):
    """
        scrape profs list and update profs.json 
    """
    if request.method == "GET":
        #print(os.path.isfile(COURSE_FILE))
        scraper.getCourseList(COURSE_FILE)
        return redirect('/books/')
    else:
        return redirect('/books/')


@login_required
def request_material(request):
    """
        Controller for handling request_material form
    """
    if request.method == 'POST':
        course_code = request.POST.get('course_code', "None")
        sem = request.POST.get('sem', "None")
        year = request.POST.get('year', "None")
        type_file = request.POST.get('type_file', "None")
        prof = request.POST.get('professor', "None")
        other = request.POST.get('other_info', '')

        with open(REQUESTS_FILE, 'r') as file:
            data = json.load(file)
        
        new_request = {
            "course_code": course_code.upper(),
            "sem": sem,
            "year": year,
            "type_file": type_file,
            "prof": prof,
            "other_info": other
        }
        if len(data) == 0:
            data = []
        data.append(new_request)

        with open(REQUESTS_FILE, 'w') as file:
            json.dump(data, file)
        
        return response.HttpResponseRedirect(reverse('requests'))

    else:
        profs = json.loads(open("profs.json", "r").read(), object_pairs_hook=OrderedDict)
        return render(request, 'books/requestsForm.html', {"profs": profs})

@login_required
def requests_page(request):
    """
        Controller for handling requested_materials page
    """
    if request.method == 'GET':
        profs = json.loads(open("profs.json", "r").read(), object_pairs_hook=OrderedDict)
        return render(request, 'books/requests.html', {"profs": profs})



def removeRequest(course_code, sem, year, prof, type_file):
    requested_material = {
        'course_code': course_code.upper(),
        'sem': sem,
        'year': year,
        'prof': prof,
        'type_file': type_file,
        'other_info': r'*'
    }

    with open(REQUESTS_FILE, 'r') as file:
        requests_data = json.load(file)

    for data in requests_data:
        matched = True
        for key in list(data.keys())[:-1]:
            if data[key]!='None' and requested_material[key]!='None' and data[key]!=requested_material[key]:
                matched = False
                break
        if matched:
            index = requests_data.index(data)
            requests_data.pop(index)
            break

    with open(REQUESTS_FILE, 'w') as file:
        json.dump(requests_data, file)
    

def userlogin(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('/books/')

            # return redirect('/books/approve')
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

@api_view(['GET', 'POST'])
def APIrequests(request):
    """
        returns a list of all requests raised for unavailable material for a GET request
        or receives an index to be deleted from requests raised for a POST request 
    """
    err = False
    try:
        with open(REQUESTS_FILE, 'r') as file:
            data = json.load(file)
    except Exception as e:
        err = True
        data = []

    
    if request.method == 'GET':
        if err:
            return Response({})
        else:
            return Response({"requests_data": data})

    else:
        course_code = request.POST.get('course_code', "None")
        sem = request.POST.get('sem', "None")
        year = request.POST.get('year', "None")
        type_file = request.POST.get('type_file', "None")
        prof = request.POST.get('professor', "None")
        
        if err or course_code=="None" or type_file=="None":
            return HttpResponse(content='Bad Response', status=400)
        else:
            removeRequest(course_code, sem, year, prof, type_file)
            return Response(status=200)


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
    
    zip_path = []
    zip_present = {}
    while len(sorted_tasks) > 0:
        tasks_handler(sorted_tasks)
        task = sorted_tasks.pop(0) 

        zip_path.clear()
        separated_file_path = task[PATH].split(os.sep)
        # ex. path in task[PATH]: CO/COL100/Question-Papers/Major/<filename>.pdf
        # store ['CO/COL100', 'CO/COL100/Question-Papers', 'CO/COL100/Question-Papers/Major'] in zip_path
        for i in range(2, len(separated_file_path)):
            zip_path.append((os.sep).join(separated_file_path[:i]))

        # Append all nodes in a dict with value indicating if zip file already present or not
        for path in zip_path:
            zip_location = os.path.join(DATABASE_DIR, path + '.zip')
            if os.path.isfile(zip_location):
                zip_present[path] = 1
            else:
                zip_present[path] = 0
    
    # Modify zips
    for path in zip_present.keys():
        if zip_present[path] == 1:
            zip_location = os.path.join(DATABASE_DIR, path + '.zip')
            os.remove(zip_location)
            zip_course(path)


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
    if not (os.path.isfile(REQUESTS_FILE)):
        requests_data = []
        with open(REQUESTS_FILE, "w") as file:
            json.dump(requests_data, file)
    finalize_function()


def zip_course(course):
    """
     Function to zip a directory given it's path
    """
    zip_location = os.path.join(DATABASE_DIR, course + '.zip')
    course_path = os.path.join(DATABASE_DIR, course)
    if not os.path.isdir(course_path):
        raise OSError
    zf = zipfile.ZipFile(zip_location, "w")
    for dirname, _, files in os.walk(course_path):
        for filename in files:
            if not filename.lower().endswith(('.meta', '.zip')):
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

@login_required
def protectedMedia(request):
    try:
        response = HttpResponse(status=200)
        url = request.path.replace('media', 'protected')
        response['Content-Type'] = ''
        # response['X-Accel-Redirect'] = '/code/protected' + request.path
        response['X-Accel-Redirect'] = url
        print('Redirecting to ',response['X-Accel-Redirect'],flush=True)
        return response
    except:
        return HttpResponse(status=400)