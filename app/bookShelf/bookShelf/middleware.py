from django.shortcuts import redirect
from django.urls import reverse_lazy
import jwt
import requests
import json
import time

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
LOGOUT_PATH = '/logout/'

USER_MODEL = User

# An array of paths that will not be processed by the middleware
# PUBLIC_PATHS = ['/public/','/'] 
PUBLIC_PATHS = ['/static/','/'] 

# A dictionary for roles for given paths, '*' denotes all other paths except the PUBLIC_PATHS
ROLES = {
    '*' : ['external_user'],
    '/admin/': ['dc_core','admin']
}
UNAUTHORIZRED_HANDLER = lambda request: HttpResponse("Alas You are out of scope! Go get some more permissions dude",status=401)

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
        except :
            token = None

        try:
            rememberme = request.COOKIES[REFRESH_TOKEN]
        except:
            rememberme = None
            

        if(not token and not rememberme):
            return self.redirect(request)
        
        if(token is not None):
            try:
                decoded = jwt.decode(token,self.public_key,algorithms='RS256')
                
                if(float(decoded['exp']) - time.time() < MAX_TTL_ALLOWED):
                    decoded['user'] = self.refresh(request=request,token={SSO_TOKEN:token})

                if(not self.authorize_roles(request, decoded['user'])):
                    return UNAUTHORIZRED_HANDLER(request)
                self.assign_user(request, decoded['user'])

            except Exception as err:
                print(err)
                return self.redirect(request)
        else:
            try:
                decoded = jwt.decode(rememberme,self.public_key,algorithms='RS256')
                user = self.refresh(request,{REFRESH_TOKEN:rememberme})

                if(not self.authorize_roles(request, decoded['user'])):
                    return UNAUTHORIZRED_HANDLER(request)
                self.assign_user(request,user_payload=user)

            except Exception as err:
                print(err)
                return self.redirect(request)

        response = self.get_response(request)

        if(self.cookies is not None):
            response._headers['set-cookie'] = ('Set-Cookie',self.cookies)

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
            return
        try:
            user = USER_MODEL.objects.get(email=user_payload['email'])
        except:
            user = USER_MODEL.objects.create_user(email=user_payload['email'],username=user_payload['username'])
        
        user.first_name = user_payload['firstname']
        user.last_name = user_payload['lastname']
        user.username = user_payload['username']
        user.save()

        login(request, user)
    
    def authorize_roles(self,request,user_payload):
        if(len(ROLES.keys()) == 0 or request.path in PUBLIC_PATHS):
            return True
        try:
            user_roles = user_payload['roles']
        except:
            return False
            
        if(request.path in ROLES.keys()):
            reqd_roles = ROLES[request.path]
        else:
            reqd_roles = ROLES['*']
        
        for role in reqd_roles:
            if(role not in user_roles):
                return False
        
        return True
        
    
    def refresh(self,request,token):
        r=requests.post(REFRESH_URL,data=token)
        self.cookies = r.headers['Set-Cookie'].replace('Lax,','Lax,\nSet-Cookie:')
        return json.loads(r.text)['user']

    def logout(self,request):
        logout(request)
        response = self.get_response(request)
        response.delete_cookie(SSO_TOKEN)
        response.delete_cookie(REFRESH_TOKEN)
        return response
    
    def redirect(self,request):
        if(request.path in PUBLIC_PATHS):
            return self.get_response(request)
        return redirect(AUTH_URL+f"/?{QUERY_PARAM}={request.build_absolute_uri()}")
