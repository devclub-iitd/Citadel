# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect
from books import JSONcreator as jsc
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import Http404
import os
import json
from shutil import copyfile
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from rest_framework.decorators import api_view
from rest_framework.response import Response

import operator
from collections import OrderedDict


DATABASE_DIR = "../media/database"
DATABASE_URL = "/media/database"
UNAPPROVED_DIR = "../media/unapproved/"
DATABASE_DICT_FILE_NAME = "database.json"

def track_hits(request,template_path,context,co):
	try:
			co.pagehits+=1
	except:
			co.pagehits = 1
	co.save()
	return render(request,template_path,context)

def index(request):
	list = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
	return render(request,'books/index.html',{"list":list})

def indexl(request):
	list = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
	return render(request,'books/indexl.html',{"list":list})

def display(request):
	department_id=request.GET.get('department','None')
	course_code_id=request.GET.get('course_code','None')

	db_list = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)

	if department_id not in db_list:
		return render(request,'books/index.html',{"list":db_list})
	elif course_code_id not in db_list[department_id]:
		return render(request,'books/get_course_codes.html',{"list":db_list,"sellist":db_list[department_id],"department_id":department_id})
	else:
		return render(request,'books/get_papers.html',{"list":db_list,"sellist":db_list[department_id][course_code_id],"first":list(db_list[department_id][course_code_id])[0],"department_id":department_id,"course_code_id":course_code_id})

def displayl(request):
	department_id=request.GET.get('department','None')
	course_code_id=request.GET.get('course_code','None')
	dir_id= request.GET.get('dir_id','None')

	file_path = DATABASE_DIR +'/'+department_id+'/'+course_code_id+'/'+ dir_id
	static_file_path = '/media/database'+'/'+department_id+'/'+course_code_id+'/'+ dir_id
	if(os.path.isfile(file_path)):
		return redirect(static_file_path)

	db_list = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
	
	if department_id not in db_list:
		return render(request,'books/indexl.html',{"list":db_list})
	elif course_code_id not in db_list[department_id]:
		return render(request,'books/get_course_codesl.html',{"list":db_list,"sellist":db_list[department_id],"department_id":department_id})
	else:
		list_to_show = db_list[department_id][course_code_id].copy()
		actual_path_list = ['None']
		if(dir_id != 'None'):
			actual_path_list = []
			dir_list = dir_id.split("/");
			for path in dir_list:
				if(list(list_to_show[path].values()).count('file') != 0):
					break
				list_to_show = list_to_show[path]
				actual_path_list.append(path)
		actual_path_taken = '%2F'.join(actual_path_list)
		display_path = '/'.join(actual_path_list)

		return render(request,'books/get_papersl.html',{"list":db_list,"sellist":list_to_show,"first":list(list_to_show)[0],"department_id":department_id,"course_code_id":course_code_id,"dir_id":actual_path_taken,"display_path":display_path})

def browse(request,path):
	main_path = request.path.strip("/")
	path = path.strip("/")
	prefix = "/"+main_path[:(-len(path))]
	print("main_path- \""+main_path+"\"")
	print("prefix- \""+prefix+"\"")
	print("path - \""+path+"\"")

	nav_path = jsc.build_nav_path(prefix,path)

	root_db = jsc.path_to_dict(DATABASE_DIR,DATABASE_DICT_FILE_NAME)
	try:
		db = jsc.navigate_path(root_db,path)
	except jsc.InvalidPath as e:
		raise Http404("No such file or directory")
	except jsc.FilePath as e:
		file_url = os.path.join(DATABASE_URL,path)
		return redirect(file_url)
	except Exception as e:
		raise Http404("No such file or directory")
	else:
		return render(request,'books/shelf.html',{"path": nav_path,"db": db})
##### Upload file
def thanks(request):
	return render(request,'books/thanks.html')
def thanksl(request):
	return render(request,'books/thanksl.html')


def model_form_upload(request):
	if request.method == 'POST':
		course_code = request.POST.get('course_code',"None").upper()
		sem 		= request.POST.get('sem',"None").upper()
		year		= request.POST.get('year',"None").upper()
		type_exam 	= request.POST.get('type_exam',"None").upper()
		prof 		= request.POST.get('professor',"None").upper()
		other_text  = request.POST.get('other_text',"None").upper()
		document 	= request.FILES['document']

		destination = open(UNAPPROVED_DIR+course_code+"_"+sem+"_"+year+"_"+type_exam+"_"+prof+"_"+other_text+"_"+document.name[request.FILES['document'].name.rindex('.'):],"wb+")
		for chunk in document.chunks():
			destination.write(chunk)
		destination.close()
		return render(request,'books/thanks.html')

	else:
		profs = json.loads(open("profs.json","r").read(), object_pairs_hook=OrderedDict)
		return render(request, 'books/model_form_upload.html',{"profs":profs})

def model_form_uploadl(request):
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
		profs = json.loads(open("profs.json","r").read(), object_pairs_hook=OrderedDict)
		return render(request, 'books/model_form_uploadl.html',{"profs":profs})

#approvals
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

#login to approve
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
	else:
		copyfile(UNAPPROVED_DIR+request.POST.get('org'),UNAPPROVED_DIR+request.POST.get('final'))
		return redirect('/books/remove_unapproved_document?name='+request.POST.get('org'))

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
	return redirect("/books/dark/")


#api
@api_view()
def APIstructure(request):
	f = json.loads(open(DATABASE_DICT_FILE_NAME).read())
	print (f)
	return Response(f)
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
