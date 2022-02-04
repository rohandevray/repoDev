from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# Create your views here.
def menu(request):
    return render(request,'account_settings.html')

def change_password(request):
    if request.method=='POST':
        cur_pwd=request.POST['cur_password']
        pwd=request.POST['password']
        pwd2=request.POST['password2']
        username=request.user.get_username()
        user = User.objects.get(username__exact=username)
        check =auth.authenticate(request, username=username, password=cur_pwd)
        
        if check is None:
            messages.info(request,'Current Password is not correct!!!')
            return redirect('change_password')
        if(pwd==pwd2):            
            user.set_password(pwd)
            user.save()
            update_session_auth_hash(request, user)
            messages.info(request,'Password changed successfully!!!')
            return redirect('change_password')
        else:
            messages.info(request,'New Passwords do not match!!!')
            return redirect('change_password')
    else:
        return render(request,'change_password.html')