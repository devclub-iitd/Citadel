# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import operator
# Django Imports
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import Http404
from shutil import copyfile
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

## Controller to Handle Upload of Documents
def upload(request):
	if request.method == 'POST':
		course_code = request.POST.get('course_code',"None").upper()
		sem 		= request.POST.get('sem',"None").upper()
		year		= request.POST.get('year',"None").upper()
		type_exam 	= request.POST.get('type_exam',"None").upper()
		other_text  = request.POST.get('other_text',"None").upper()
		prof 		= request.POST.get('professor',"None").upper()
		document 	= request.FILES['document']
		destination = open(UNAPPROVED_DIR+course_code+"_"+sem+"_"+year+"_"+type_exam+"_"+prof+"_"+other_text+"_"+document.name[request.FILES['document'].name.rindex('.'):],"wb+")
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
	return render(request, 'books/approve.html', {'unapproved_documents':unapproved_documents})

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
	dep = seperatedlist[0][0:2]

	try:
		if seperatedlist[3] == "LECNOTE":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Professors/"+seperatedlist[4]+"/"+seperatedlist[5].title()+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "BOOK":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Books/"+seperatedlist[5].title()+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "OTHER":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Others/"+seperatedlist[5].title()+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "MINOR1":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Minor1/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "MINOR2":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Minor2/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "MAJOR":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Major/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
			return redirect('/books/remove_unapproved_document?name='+fileName)
	except FileNotFoundError:
		if os.path.isdir(DATABASE_DIR+"/"+dep):
			if os.path.isdir(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]):
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Professors/"+seperatedlist[4]+"/")
				destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Professors/"+seperatedlist[4]+"/"+seperatedlist[5].title()+seperatedlist[6]
				copyfile(UNAPPROVED_DIR+fileName,destination)
				jsc.recreate_path(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
				return redirect('/books/remove_unapproved_document?name='+fileName)
			else:
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0])
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Professors/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Books/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Others/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/Minor1/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/Minor2/")
				os.makedirs(DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/Major/")
				return approve_unapproved_document(request)
		else:
			os.makedirs(DATABASE_DIR+"/"+dep)
			return approve_unapproved_document(request)

@login_required
def rename(request):
	if request.method=="GET":
		return render(request,"books/rename.html",{"org":request.GET.get('name','none')})
	elif request.method=="POST":
		copyfile(UNAPPROVED_DIR+request.POST.get('org'),UNAPPROVED_DIR+request.POST.get('final'))
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
	depth = int(request.GET.get('depth',3))
	try:
		db = jsc.navigate_path(f,path)
	except Exception as e:
		print("invalid path")
		return Response({})
	else:
		truncated_db = jsc.truncate_db(db,depth)
		return Response(truncated_db)
@csrf_exempt
def APIupload(request):
	if request.method == 'POST':
		course_code = request.POST.get('course_code',"None").upper()
		sem 		= request.POST.get('sem',"None").upper()
		year		= request.POST.get('year',"None").upper()
		type_exam 	= request.POST.get('type_exam',"None").upper()
		other_text  = request.POST.get('other_text',"None").upper()
		prof 		= request.POST.get('professor',"None").upper()
		document 	= request.FILES['document']
		destination = open(UNAPPROVED_DIR+course_code+"_"+sem+"_"+year+"_"+type_exam+"_"+prof+"_"+other_text+"_"+document.name[request.FILES['document'].name.rindex('.'):],"wb+")
		for chunk in document.chunks():
			destination.write(chunk)
		destination.close()
		return render(request,'books/thanksl.html')
	else:
		return HttpResponse('Only POST here')
