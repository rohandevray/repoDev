from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from userauth.models import Account, Profile


def index(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user.id)
        print(account) 
        return render(request,'home.html',{'account':account})
    else:
        return render(request,'index.html')