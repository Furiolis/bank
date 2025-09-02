from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from .forms import NewClientForm
from .models import Client, Account, Card
from random import randint

def index(request):
    if request.user.is_authenticated:
        
        return render(request, "banking/index.html",{
            "is_logged": request.user.is_authenticated,
            # """ wyswietlanie produktow """
            })
    else:
        """ logowanie """
        """ lub rejestracja """

        return render(request, "banking/index.html",{
            "is_logged": request.user.is_authenticated,
            })

    
    
def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_user(request, user)
            return redirect("main_panel")
    else:
        form = AuthenticationForm()
    return render(request, "banking/login.html", {"form":form})

def logout(request):
    logout_user(request)
    return redirect("main_panel")

def new_client(request):
    if request.method == "POST":
        form = NewClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            """account = Account(number = randint(a = 11111111,b = 99999999), owner = client, money = 0)
            account.save()
            card = Card(number )"""

            request.session["confirmation_client_id"] = client.id
            return redirect("confirmation") 
    else:
        form = NewClientForm()
    return render(request, "banking/new_client.html",{"form": form})

def confirmation(request):
    client_id = request.session.pop("confirmation_client_id",None)
    if client_id:
        client = Client.objects.get(id=client_id)
    else:
        client = None
    return render(request, "banking/confirm.html",{"client":client})
