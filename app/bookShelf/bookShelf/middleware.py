from django.shortcuts import redirect, render
from django.urls import reverse_lazy
import jwt
import requests
import json
import time
import re

from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from django.http.response import HttpResponse
from django.conf import settings

SSO_TOKEN = 'token'
REFRESH_TOKEN = 'rememberme'
AUTH_URL = 'https://auth.devclub.in/user/login'
REFRESH_URL = 'https://auth.devclub.in/auth/refresh-token'
PUBLIC_KEY = 'bookShelf/public.pem'
MAX_TTL_ALLOWED = 60 * 5
QUERY_PARAM = 'serviceURL'
LOGOUT_PATH = '/books/userlogout/'

USER_MODEL = User

SUPERUSER_ROLE = 'citadel_admin'

# An array of path regexes that will not be processed by the middleware
PUBLIC_PATHS = ['^/$','^/static/.*','^/healthz.*'] 

# A dictionary of path regexes mapping to the roles. A user needs to have all roles in order to be authorized
ROLES = {
    '^/admin.*': [SUPERUSER_ROLE],
    '^/books/approve/$': [SUPERUSER_ROLE],
    '^/books/remove_unapproved_document/$' : [SUPERUSER_ROLE],
    '^/books/approve_unapproved_document/$': [SUPERUSER_ROLE],
    '^/books/rename/$': [SUPERUSER_ROLE],
    '^/books/bulk_approve/$': [SUPERUSER_ROLE],
    '^/books/force_integrity/$': [SUPERUSER_ROLE],
    '^/books/finalize_approvals/$': [SUPERUSER_ROLE],
    '^/books/update_prof_list/$': [SUPERUSER_ROLE],
    '^/books/update_course_list/$': [SUPERUSER_ROLE]
}

DEFAULT_ROLES = ['iitd_user']
UNAUTHORIZED_HANDLER = lambda request: render(request, 'books/unauthorized.html')

class SSOMiddleware:
    def __init__(self, get_response):
        self.configure()
        self.get_response = get_response
        self.public_key = open(PUBLIC_KEY,'rb').read()
        self.cookies = None
        
    def __call__(self, request):
        
        if (request.path == LOGOUT_PATH):
            return self.logout(request)

        try:
            token = request.COOKIES[SSO_TOKEN]
        except:
            token = None

        try:
            rememberme = request.COOKIES[REFRESH_TOKEN]
        except:
            rememberme = None
            

        if(not token and not rememberme):
            self.log(request, 'no tokens')
            return self.redirect(request)
        
        if(token is not None):
            self.log(request, 'access token found')
            try:
                decoded = jwt.decode(token,self.public_key,algorithms='RS256')
                self.log(request, 'token decoded')
                if(float(decoded['exp']) - time.time() < MAX_TTL_ALLOWED):
                    self.log(request, 'Refreshing token')
                    decoded['user'] = self.refresh(request=request,token={SSO_TOKEN:token})

                if(not self.authorize_roles(request, decoded['user'])):
                    self.log(request, 'unauthorised user')
                    return UNAUTHORIZED_HANDLER(request)
                self.assign_user(request, decoded['user'])

            except Exception as err:
                self.log(request, err)
                return self.redirect(request)
        else:
            self.log(request, 'no access token')
            try:
                decoded = jwt.decode(rememberme,self.public_key,algorithms='RS256')
                user = self.refresh(request,{REFRESH_TOKEN:rememberme})

                if(not self.authorize_roles(request, decoded['user'])):
                    return UNAUTHORIZED_HANDLER(request)
                self.assign_user(request,user_payload=user)

            except Exception as err:
                self.log(request, err)
                return self.redirect(request)

        self.log(request, 'getting response')
        response = self.get_response(request)

        if(self.cookies is not None):
            response._headers['set-cookie1'] = ('Set-Cookie',self.cookies.split('\n')[0])
            try:
                response._headers['set-cookie2'] = ('Set-Cookie', self.cookies.split('\n')[1])
            except:
                pass
            
            self.cookies = None
        self.log(request, 'sending response')
        return response

    def configure(self):
        for key, value in globals().items():
            if(key.isupper()):
                new_val = getattr(settings, key, value)
                if(type(new_val) != type(value)):
                    err = f"Type Mismatch, {key} should be of {type(value)} but found as {type(new_val)}"
                    raise TypeError(err)
                globals()[key] = new_val

    def assign_user(self,request,user_payload):
        if(request.user.is_authenticated):
            self.log(request, 'user already authenticated')
            return
        try:
            user = USER_MODEL.objects.get(email=user_payload['email'])
        except:
            user = USER_MODEL.objects.create_user(email=user_payload['email'],username=user_payload['username'])
        
        user.first_name = user_payload['firstname']
        user.last_name = user_payload['lastname']
        user.username = user_payload['username']
        if self.check_superuser(request, user_payload):
            user.is_superuser = True
        user.save()
        self.log(request, 'logging in')
        login(request, user)
    
    def authorize_roles(self,request,user_payload):
        if(len(ROLES.keys()) == 0 or match_regex_list(request.path, PUBLIC_PATHS)):
            return True
        try:
            user_roles = user_payload['roles']
        except:
            return False
            
        match = match_regex_list(request.path, ROLES.keys())
        if(match is None):
            reqd_roles = DEFAULT_ROLES
        else:
            reqd_roles = ROLES[match]
        
        for role in reqd_roles:
            if(role not in user_roles):
                return False
        
        return True
        
    
    def check_superuser(self, request, user_payload):
        try:
            user_roles = user_payload['roles']
        except:
            return False

        superuser_role = SUPERUSER_ROLE
        for role in user_roles:
            if role == superuser_role:
                return True
        return False

    def refresh(self,request,token):
        r=requests.post(REFRESH_URL,data=token)
        self.cookies = r.headers['Set-Cookie'].replace('Lax,','Lax\n')
        return json.loads(r.text)['user']

    def logout(self,request):
        logout(request)
        response = self.get_response(request)
        response.delete_cookie(SSO_TOKEN,domain='devclub.in')
        response.delete_cookie(REFRESH_TOKEN,domain='devclub.in')
        return response
    
    def redirect(self,request):
        if(match_regex_list(request.path,PUBLIC_PATHS)):
            return self.get_response(request)
        return redirect(AUTH_URL+f"/?{QUERY_PARAM}={request.build_absolute_uri()}")

    def log(self, request, data):
        print(f"[{time.ctime()}] {request.path} {data}", flush=True)


def match_regex_list(key,regex_array):
    """ Match every  regex element in an array against the key"""
    for regex in regex_array:
        if(re.search(regex,key) is not None):
            return regex
    return None


