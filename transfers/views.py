from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import InternalTransferForm, ExternalTransferForm

@login_required
def transfer(request):
    owner = request.user

    if request.method == "POST":
        internal_form = InternalTransferForm(request.POST, owner=owner)
        external_form = ExternalTransferForm(request.POST, owner=owner)

        form_type = request.POST.get("form_type")
        if form_type == "internal" and internal_form.is_valid():
            internal_form.save()
            messages.success(request, _("Transfer accomplished, money are send"))
            return redirect("banking:dashboard")
        elif form_type == "external" and external_form.is_valid():
            external_form.save()
            messages.success(request, _("Transfer accomplished, money are send"))
            return redirect("banking:dashboard")
    else:
        internal_form = InternalTransferForm(owner=owner)
        external_form = ExternalTransferForm(owner=owner)
    return render(request,"transfers/transfers.html",{
        "external_form":external_form,
        "internal_form":internal_form})

def history(request):
    pass

