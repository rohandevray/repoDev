from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate,login,logout, update_session_auth_hash
from .models import Profile, Account 
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request,'index.html',{})
    
def register_user(request):
    if request.method == 'POST':
        try:
            prevuser = User.objects.get(username=request.POST['username'])
            return render(request,'register.html',{'warning':"User already exists!!"})
        except User.DoesNotExist:
            if request.POST['password']==request.POST['password2']:
                user=User.objects.create_user(request.POST['username'],request.POST['email'].lower(),request.POST['password'])
                # user.last_name=request.POST['lname']
                # user.first_name=request.POST['fname']
                user.save()
                profile = Profile(first_name=request.POST['fname'],last_name=request.POST['lname'],phone_number=request.POST['phone'],gender=request.POST['gender'] )
                profile.save()
                account = Account(profile=profile,user=user)                 
                account.save()
                return redirect('/userauth/login')

                
            else:
                return render(request,'register.html',{'warning':"Passwords do not match!!"})
    return render(request,'register.html',{})

def login_user(request):
    if request.method=='POST':
        user = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request,user)
            return redirect('/userauth')
        else:
            return render(request,'login.html',{'warning':"Incorrect username or password"})

    return render(request,'login.html',{})
    
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
      
    return redirect('/userauth')


def home(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user.id)
        print(account) 
        return render(request,'home.html',{'account':account})
    else:
        return render(request,'index.html')

def menu(request):
    if request.user.is_authenticated:
        return render(request,'account_settings.html',{'user':request.user})
    else:
        return redirect('/userauth/login')
def change_password(request):
    if not request.user.is_authenticated:
         return redirect('/userauth/login')
    if request.method=='POST':
        cur_pwd=request.POST['cur_password']
        pwd=request.POST['password']
        pwd2=request.POST['password2']
        username=request.user.get_username()
        user = User.objects.get(username__exact=username)
        check =auth.authenticate(request, username=username, password=cur_pwd)
        
        if check is None:
            messages.info(request,'Current Password is not correct!!!')
            return redirect('userauth:change_password')
        if(pwd==pwd2):            
            user.set_password(pwd)
            user.save()
            update_session_auth_hash(request, user)
            messages.info(request,'Password changed successfully!!!')
            return redirect('userauth:change_password')
        else:
            messages.info(request,'New Passwords do not match!!!')
            return redirect('userauth:change_password')
    else:
        return render(request,'settings.html')