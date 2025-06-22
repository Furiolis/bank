from django.shortcuts import render
from django.http import HttpResponse
from .forms import NewClientForm

def main_panel(request):
    pass

def login(request):
    pass

def new_client(request):
    if request.method == "POST":
        form = NewClientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("dziala")
    else:
        form = NewClientForm()
    return render(request, "banking/new_client.html",{"form": form})

