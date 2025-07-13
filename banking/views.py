from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewClientForm
from .models import Client

def main_panel(request):
    pass

def login(request):
    pass

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
