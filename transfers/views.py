from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import TranferFormBase

@login_required
def transfers(request):
    owner = request.user
    form = TranferFormBase(owner=owner)
    return render(request,"transfers/transfers.html",{"form":form})

def internal_transfer(request):
    pass

def external_transfer(request):
    pass


