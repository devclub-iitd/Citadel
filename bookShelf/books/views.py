# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect
from books import JSONcreator as jsc
from django.http import HttpResponse, HttpResponseNotAllowed
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

DATABASE_DIR = "../media/database"
UNAPPROVED_DIR = "../media/unapproved/"

def track_hits(request,template_path,context,co):
        try:
                co.pagehits+=1
        except:
                co.pagehits = 1
        co.save()
        return render(request,template_path,context)

def index(request):
	print(jsc.path_to_dict(DATABASE_DIR,"database.txt"))
	list = jsc.path_to_dict(DATABASE_DIR,"database.txt")
	# print(os.getcwd())
	return render(request,'books/index.html',{"list":list})

def indexl(request):
	list = jsc.path_to_dict(DATABASE_DIR,"database.txt")
	return render(request,'books/indexl.html',{"list":list})

def display(request):
	department_id=request.GET.get('department','None')
	course_code_id=request.GET.get('course_code','None')

	db_list = jsc.path_to_dict(DATABASE_DIR,"database.txt")

	if department_id not in db_list:
		return render(request,'books/index.html',{"list":db_list})
	elif course_code_id not in db_list[department_id]:
		return render(request,'books/get_course_codes.html',{"list":db_list,"sellist":db_list[department_id],"department_id":department_id})
	else:
		return render(request,'books/get_papers.html',{"list":db_list,"sellist":db_list[department_id][course_code_id],"first":list(db_list[department_id][course_code_id])[0],"department_id":department_id,"course_code_id":course_code_id})

def displayl(request):
	department_id=request.GET.get('department','None')
	course_code_id=request.GET.get('course_code','None')

	db_list = jsc.path_to_dict(DATABASE_DIR,"database.txt")
	# db_list = dict(sorted(db_list.items(), key=operator.itemgetter(0)))
	print db_list
	if department_id not in db_list:
		return render(request,'books/indexl.html',{"list":db_list})
	elif course_code_id not in db_list[department_id]:
		return render(request,'books/get_course_codesl.html',{"list":db_list,"sellist":db_list[department_id],"department_id":department_id})
	else:
		return render(request,'books/get_papersl.html',{"list":db_list,"sellist":db_list[department_id][course_code_id],"first":list(db_list[department_id][course_code_id])[0],"department_id":department_id,"course_code_id":course_code_id})


# ####upload file
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
		return render(request, 'books/model_form_upload.html')

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
		return render(request, 'books/model_form_uploadl.html')

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
		if seperatedlist[3] == "book":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Books/"+seperatedlist[5]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,"database.txt")
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "other":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Others/"+seperatedlist[5]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,"database.txt")
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "minor1":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Minor1/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,"database.txt")
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "minor2":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Minor2/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,"database.txt")
			return redirect('/books/remove_unapproved_document?name='+fileName)
		elif seperatedlist[3] == "major":
			destination = DATABASE_DIR+"/"+dep+"/"+seperatedlist[0]+"/Question_Papers/"+"Major/"+seperatedlist[2]+"_sem"+seperatedlist[1]+seperatedlist[6]
			copyfile(UNAPPROVED_DIR+fileName,destination)
			jsc.recreate_path(DATABASE_DIR,"database.txt")
			return redirect('/books/remove_unapproved_document?name='+fileName)
	except:
		return HttpResponse('<h1> Such a course code does not exist</h1><h1>Ask the developers to add the course code and then try again</h1>')

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
	f = json.loads(open("database.txt").read())
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
