from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from .forms import NewClientForm
from .models import Client, Account, Card
from random import randint


def index(request):
    if request.user.is_authenticated:
        
        return render(request, "banking/index.html",{})
        """ wyswietlanie produktow """
    else:
        """ logowanie """
        """ lub rejestracja """

        return render(request, "banking/logout.html",{})

    
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
    return render(request, "banking/logout.html",{})


def new_client(request):
    if request.method == "POST":
        form = NewClientForm(request.POST)
        if form.is_valid():
            client = form.save()
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


def new_account(request):
    if request.user.is_authenticated:
        return render(request, "banking/new_account.html")
    else:
        return render(request, "banking/logout.html")


def new_loan(request):
    if request.user.is_authenticated:
        return render(request, "banking/new_loan.html")
    else:
        return render(request, "banking/logout.html")

def new_credit_card(request):
    if request.user.is_authenticated:
        return render(request, "banking/new_credit_card.html")
    else:
        return render(request, "banking/logout.html")