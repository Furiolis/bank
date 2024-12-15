from django.shortcuts import render
from .forms import ClientForm
from .models import Client
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password


def index(request):
    return render(request, "bankowanie/index.html")

def review(request):
    pass

def login(request):
    pass

def new_client(request):
    pass

def confirm(request):
    pass
