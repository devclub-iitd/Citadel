# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import operator
import shutil
import errno

# Django Imports
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import OrderedDict

#Custom JSON Database Creator
from books import JSONcreator as jsc


DATABASE_DIR = "../media/database"
DATABASE_URL = "/media/database"
UNAPPROVED_DIR = "../media/unapproved/"
DATABASE_DICT_FILE_NAME = "database.json"

def index(request):
	return render(request,'books/shelf.html')

def getFileName(course_code,sem,year,type_file,prof,filename,other):
	toWriteFileName = ""
	fileNamePrefix = "[" + sem + year[2:] + "]"
	if(other != 'None' and any(x.isalpha() for x in other) ):
		origFileName = other
	else:
		origFileName = '.'.join(filename.split('.')[:-1])
	fileExtension = "." + filename.split('.')[-1]
	dirPath = course_code[0:2] + "_" + course_code + "_"

	if(type_file == 'Minor1' or type_file == 'Minor2' or type_file == 'Major'):
		dirPath = dirPath + "Question-Papers" + "_" + type_file + "_" 
		toWriteFileName = dirPath + fileNamePrefix + "-" + type_file + fileExtension
	elif(type_file == 'Books' or type_file == 'Others'):
		dirPath = dirPath + type_file + "_"
		toWriteFileName = dirPath + origFileName + fileExtension
	else:
		dirPath = dirPath + "Professors" + "_" + prof + "_" + type_file + "_"
		toWriteFileName = dirPath + fileNamePrefix + "-" + origFileName + fileExtension
	return toWriteFileName


## Controller to Handle Upload of Documents
def upload(request):
	if request.method == 'POST':
		course_code = request.POST.get('course_code',"None").upper()
		sem 		= request.POST.get('sem',"None")
		year		= request.POST.get('year',"None")
		type_file 	= request.POST.get('type_file',"None")
		prof 		= request.POST.get('professor',"None")
		documents 	= request.FILES.getlist('documents')
		other_text  = request.POST.get('customFilename',"None")
		if(len(documents)>1):
			other_text = 'None'
		for document in documents:
			filename = getFileName(course_code,sem,year,type_file,prof,document.name,other_text)
			destination = open(UNAPPROVED_DIR+filename,"wb+")
			for chunk in document.chunks():
				destination.write(chunk)
			destination.close()
		return render(request,'books/thanks.html')
	else:
		profs = json.loads(open("profs.json","r").read(), object_pairs_hook=OrderedDict)
		return render(request, 'books/upload.html',{"profs":profs})

## Controller to Handle approval of requests
@login_required
def approve(request):	
	unapproved_documents = []
	for path, subdirs, files in os.walk(UNAPPROVED_DIR):
		for filename in files:
			f = os.path.join(path, filename)
			unapproved_documents.append(str(f)[str(f).rindex("/")+1:])
	if(len(unapproved_documents)==0):
		error = "No Unapproved documents present, please ask people to upload material and contribute to the Citadel"
	else:
		error=''
	return render(request, 'books/approve.html', {'unapproved_documents':unapproved_documents,'error': error})

@login_required
def remove_unapproved_document(request):
	try:
		os.remove(UNAPPROVED_DIR+request.GET.get('name','none'))
	except:
		return HttpResponse('<h1>No such file exists. Maybe it was manually deleted</h1>')
	return redirect('/books/approve')

@login_required
def approve_unapproved_document(request):
	fileName = request.GET.get('name','none')
	seperatedlist = fileName.split("_")
	try:
		destination = DATABASE_DIR
		for directory in seperatedlist:
			destination = destination + "/" + directory
		shutil.copy(UNAPPROVED_DIR+fileName,destination)
		jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
		return redirect('/books/remove_unapproved_document?name='+fileName)
	except IOError as e:
		if e.errno != errno.ENOENT:
			raise
		os.makedirs(os.path.dirname(destination))
		shutil.copy(UNAPPROVED_DIR+fileName, destination)	
		jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
		return redirect('/books/remove_unapproved_document?name='+fileName)

@login_required
def rename(request):
	if request.method=="GET":
		return render(request,"books/rename.html",{"org":request.GET.get('name','none')})
	elif request.method=="POST":
		shutil.copy(UNAPPROVED_DIR+request.POST.get('org'),UNAPPROVED_DIR+request.POST.get('final'))
		return redirect('/books/remove_unapproved_document?name='+request.POST.get('org'))
	else:
		return HttpResponse('<h1> Invalid use of Rename API</h1>')

def userlogin(request):
	if request.method=='POST':
		user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
		if user is not None:
			login(request,user)
			return redirect('/books/approve')
		else:
			render(request,'books/login.html')
	return render(request,'books/login.html')

def userlogout(request):
	logout(request)
	return redirect("/books/")


#api
@api_view()
def APIstructure(request):
	f = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
	path = request.GET.get('path',"/")
	print (path)
	depth = int(request.GET.get('depth',3))
	try:
		db = jsc.navigate_path(f,path)
	except Exception as e:
		print("invalid path")
		return Response({})
	else:
		truncated_db = jsc.truncate_db(db,depth)
		return Response(truncated_db)