# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import operator
import shutil
import errno


# Django Imports
from django.shortcuts import render, redirect, HttpResponse

import zipfile

# Django Imports
from django.shortcuts import render, redirect
from django.http import Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import OrderedDict
from books import search as search

# Custom JSON Database Creator
from books import JSONcreator as jsc

DATABASE_DIR = "../media/database"
DATABASE_URL = "/media/database"
FILESV_CODE = "..-media-files"
FILESV_DIR = "../media/files"
UNAPPROVED_DIR = "../media/unapproved/"
DATABASE_DICT_FILE_NAME = "database.json"
SEPARATOR = "\\"
TAG = "=="
META_SPLIT_COMPONENTS=3
META_EXTENSION=".meta"


def index(request):
	return render(request, 'books/browse.html')


def getFileName(course_code, sem, year, type_file, prof, filename, other):
	toWriteFileName = ""
	fileNamePrefix = "[" + sem + year[2:] + "]"
	if (other != 'None' and any(x.isalpha() for x in other)):
		origFileName = other
	else:
		origFileName = '.'.join(filename.split('.')[:-1])
	fileExtension = "." + filename.split('.')[-1]
	dirPath = course_code[0:2] + SEPARATOR + course_code + SEPARATOR

	if (type_file == 'Minor1' or type_file == 'Minor2' or type_file == 'Major'):
		dirPath = dirPath + "Question-Papers" + SEPARATOR + type_file + SEPARATOR
		toWriteFileName = dirPath + fileNamePrefix + "-" + type_file + "-" + course_code + fileExtension + TAG + course_code + SEPARATOR + type_file
	elif (type_file == 'Books' or type_file == 'Others'):
		dirPath = dirPath + type_file + SEPARATOR
		toWriteFileName = dirPath + origFileName + fileExtension + TAG + course_code + SEPARATOR + prof
	else:
		dirPath = dirPath + "Professors" + SEPARATOR + prof + SEPARATOR + type_file + SEPARATOR
		toWriteFileName = dirPath + fileNamePrefix + "-" + origFileName + fileExtension + TAG + course_code + SEPARATOR + prof
	return toWriteFileName


# Controller to Handle Upload of Documents
def upload(request):
	if request.method == 'POST':
		course_code = request.POST.get('course_code', "None").upper()
		sem = request.POST.get('sem', "None")
		year = request.POST.get('year', "None")
		type_file = request.POST.get('type_file', "None")
		prof = request.POST.get('professor', "None")
		documents = request.FILES.getlist('documents')
		other_text = request.POST.get('customFilename', "None")
		if (len(documents) > 1):
			other_text = 'None'
		for document in documents:
			filename = getFileName(course_code, sem, year, type_file, prof, document.name, other_text)
			directory = os.path.dirname(UNAPPROVED_DIR + filename)
			if not os.path.exists(directory):
				os.makedirs(directory)
			destination = open(UNAPPROVED_DIR + filename, "wb+")
			for chunk in document.chunks():
				destination.write(chunk)
			destination.close()
		return render(request, 'books/thanks.html')
	else:
		profs = json.loads(open("profs.json", "r").read(), object_pairs_hook=OrderedDict)
		return render(request, 'books/upload.html', {"profs": profs})


def download_course(request):
	course = request.GET.get('course', 'none')
	if course == 'none':
		return redirect('/books/')
	parent_dir = course[0:2]
	zip_location = DATABASE_DIR + '/' + parent_dir + '/' + course + '.zip'
	if os.path.exists(zip_location) and os.path.isfile(zip_location):
		return redirect('/../media/database/' + parent_dir + '/' + course + '.zip')
	else:
		course_path = DATABASE_DIR + '/' + parent_dir + '/' + course
		zf = zipfile.ZipFile(zip_location, "w")
		for dirname, sudirs, files in os.walk(course_path):
			for filename in files:
				if not filename.lower().endswith('.meta'):
					path = os.path.join(dirname, filename)
					to_write = os.path.relpath(path, course_path)
					zf.write(path, arcname=to_write)
				else:
					meta_file = os.path.split(filename)[1]
					file_loc = get_file_loc(meta_file)[1]
					path = os.path.join(dirname, filename)
					to_write = os.path.join(os.path.split(os.path.relpath(path, course_path))[0], os.path.split(file_loc)[1])
					zf.write(file_loc, arcname=to_write)
		zf.close()
		return redirect('/../media/database/' + parent_dir + '/' + course + '.zip')

# Controller to Handle approval of requests
@login_required
def approve(request):
	unapproved_documents = []
	for path, subdirs, files in os.walk(UNAPPROVED_DIR):
		for filename in files:
			f = os.path.join(path, filename)
			unapproved_documents.append(str(f)[str(f).rindex("/") + 1:])
	if len(unapproved_documents) == 0:
		error = "No Unapproved documents present, please ask people to upload material and contribute to the Citadel"
	else:
		error = ''
	return render(request, 'books/approve.html', {'unapproved_documents': unapproved_documents, 'error': error})


@login_required
def remove_unapproved_document(request):
	try:
		os.remove(UNAPPROVED_DIR + request.GET.get('name', 'none'))
	except:
		return HttpResponse('<h1>No such file exists. Maybe it was manually deleted</h1>')
	return redirect('/books/approve')


@login_required
def approve_unapproved_document(request):
	fileDes = request.GET.get('name', 'none')
	fileName = fileDes.split(TAG)
	seperatedlist = fileName[0].split(SEPARATOR)
	tags = fileName[1].split(SEPARATOR)
	destination = DATABASE_DIR
	for directory in seperatedlist:
		destination = destination + "/" + directory
	file = destination.split('.')
	try:
		shutil.copy(UNAPPROVED_DIR + fileDes, destination)
		destination_meta = '.'.join(file[:-1]) + "." + file[-1] + TAG + FILESV_CODE + TAG + '.meta'
		keys = []
		if os.path.exists(destination_meta) and os.path.isfile(destination_meta):
			keys = [line.rstrip('\n') for line in open(destination_meta)]
		metafile = open(destination_meta, "a+")
		for k in range(len(tags)):
			if tags[k] not in keys:
				metafile.write(tags[k] + '\n')
		metafile.close()
	#    jsc.recreate_path(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
		return redirect('/books/remove_unapproved_document?name=' + fileDes)
	except IOError as e:
		if e.errno != errno.ENOENT:
			raise
		os.makedirs(os.path.dirname(destination), exist_ok=True)
		shutil.copy(UNAPPROVED_DIR + fileDes, destination)
		destination_meta = '.'.join(file[:-1]) + "." + file[-1] + TAG + FILESV_CODE + TAG + '.meta'
		keys = []
		if os.path.exists(destination_meta) and os.path.isfile(destination_meta):
			keys = [line.rstrip('\n') for line in open(destination_meta)]
		metafile = open(destination_meta, "a+")
		for k in range(len(tags)):
			if tags[k] not in keys:
				metafile.write(tags[k] + '\n')
		metafile.close()
	#    jsc.recreate_path(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
		return redirect('/books/remove_unapproved_document?name=' + fileDes)


@login_required
def rename(request):
	if request.method == "GET":
		return render(request, "books/rename.html", {"org": request.GET.get('name', 'none')})
	elif request.method == "POST":
		directory = os.path.dirname(UNAPPROVED_DIR + request.POST.get('final'))
		if not os.path.exists(directory):
			os.makedirs(directory)
		shutil.copy(UNAPPROVED_DIR + request.POST.get('org'), UNAPPROVED_DIR + request.POST.get('final'))
		return redirect('/books/remove_unapproved_document?name=' + request.POST.get('org'))
	else:
		return HttpResponse('<h1> Invalid use of Rename API</h1>')


@login_required
def finalize_approvals(request):
	if request.method == "GET":
		jsc.recreate_path(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
		return redirect('/books/approve')
	else:
		return redirect('/books/approve')


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


# api
@api_view()
def APIstructure(request):
	f = jsc.path_to_dict(DATABASE_DIR, DATABASE_DICT_FILE_NAME)
	path = request.GET.get('path', "/")
	print(path)
	depth = int(request.GET.get('depth', 3))
	try:
		db = jsc.navigate_path(f, path)
	except Exception as e:
		print("invalid path")
		return Response({})
	else:
		truncated_db = jsc.truncate_db(db, depth)
		return Response(truncated_db)

@api_view()
def APIsearch(request):
	f = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)    ####can this be drier? repeated code
	keyword_list=(request.GET.get('query',"")).split()    
	print(keyword_list)
	path=request.GET.get('path',"/")
	path_prefix=search.get_path_prefix(path)
	try:
		db = jsc.navigate_path(f,path)
	except Exception as e:
		print("invalid path")
		return Response({})
	else:
		result=search.search_dic(db,path_prefix,keyword_list)
		return Response({"result":result})



# testAPI
@api_view()
def heartbeat(request):
	return Response({"message": "Server is up!"})


def zip_courses():
	for root, dirs, files in os.walk(DATABASE_DIR, topdown=True):
		flag = 0
		for name in dirs:
			if len(name) == 2:
				flag = 1
				break
		if root[len(DATABASE_DIR)+1:].count(os.sep) == 0 and flag == 0:
			for course in dirs:
				course_path = os.path.join(root, course)
				zip_file = os.path.join(root, course) + ".zip"
				if os.path.exists(zip_file) and os.path.isfile(zip_file):
					zf = zipfile.ZipFile(zip_file, "a")
					for dirname, sudirs, files in os.walk(os.path.join(root, course)):
						for filename in files:
							if not filename.lower().endswith('.meta'):
								path = os.path.join(dirname, filename)
								to_write = os.path.relpath(path, course_path)
								zf.write(path, arcname=to_write)
					zf.close()
				else:
					is_changed = 0
					for dirname, sudirs, files in os.walk(os.path.join(root, course)):
						for filename in files:
							if is_changed == 0:
								zf = zipfile.ZipFile(zip_file, "w")
								is_changed = 1
							if not filename.lower().endswith('.meta'):
								path = os.path.join(dirname, filename)
								to_write = os.path.relpath(path, course_path)
								zf.write(path, arcname=to_write)
							else:
								meta_file = os.path.split(filename)[1]
								file_loc = get_file_loc(meta_file)[1]
								path = os.path.join(dirname, filename)
								to_write = os.path.join(os.path.split(os.path.relpath(path, course_path))[0],
								os.path.split(file_loc)[1])
								zf.write(file_loc, arcname=to_write)
					if is_changed == 1:
						zf.close()


def export_files():
	for root, dirs, files in os.walk(DATABASE_DIR):
		for filename in files:
			if not filename.lower().endswith(('.zip','.meta')):
				from_link = os.path.join(root, filename)
				to_link = FILESV_DIR + '/' + os.path.split(from_link)[1]
				shutil.move(from_link, to_link)


def get_file_loc(meta_file):
	desc = meta_file.split(TAG)
	if (len(desc)==3):
		if(desc[-1]==META_EXTENSION):
			file_name = desc[0]
			raw_loc = desc[1]
			dirs = raw_loc.split('-')
			file_dir = '/'.join(dirs)
			file_loc = file_dir + '/' + file_name
			return (file_name, file_loc)
	return (meta_file, None)

def build_meta_files():
	for root, dirs, files in os.walk(DATABASE_DIR, topdown=True):
		for filename in files:
			if not filename.lower().endswith(('.meta', '.zip')):
				file_loc = os.path.join(root, filename)
				metafile_loc = file_loc + TAG + FILESV_CODE + TAG + '.meta'
				if not (os.path.exists(metafile_loc) and os.path.isfile(metafile_loc)):
					f = open(metafile_loc, 'w')
					inner_path = os.path.relpath(metafile_loc, DATABASE_DIR)
					inner_path = os.path.split(inner_path)[0]
					inner_path = os.path.split(inner_path)[0]
					while os.path.split(inner_path)[0] is not '':
						f.write(os.path.split(inner_path)[1] + '\n')
						inner_path = os.path.split(inner_path)[0]
					f.close()


