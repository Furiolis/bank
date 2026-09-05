from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .forms import InternalTransferForm, ExternalTransferForm, HistoryManagementForm
from .models import Transfer


@login_required
def transfer(request):
    owner = request.user

    if request.method == "POST":
        internal_form = InternalTransferForm(request.POST, owner=owner)
        external_form = ExternalTransferForm(request.POST, owner=owner)

        form_type = request.POST.get("form_type")
        if form_type == "internal":
            if internal_form.is_valid():
                internal_form.save()
                messages.success(request, _("Transfer accomplished, money are send"))
                return redirect("banking:dashboard")
        elif form_type == "external":
            if external_form.is_valid():
                external_form.save()
                messages.success(request, _("Transfer accomplished, money are send"))
                return redirect("banking:dashboard")
    else:
        internal_form = InternalTransferForm(owner=owner)
        external_form = ExternalTransferForm(owner=owner)
    return render(request,"transfers/transfers.html",{
        "external_form":external_form,
        "internal_form":internal_form})

@login_required
def history(request):
    client = request.user
    filtered_transfers = Transfer.objects.filter(account__owner=client).order_by("-date")
    if request.method == "POST":
        form = HistoryManagementForm(request.POST, owner=client)
        if form.is_valid():
            #print(form.cleaned_data["accounts"], form.cleaned_data["internal"], form.cleaned_data["external"],form.cleaned_data["lower_limit_money"],form.cleaned_data["higher_limit_money"])
            selected_account = form.cleaned_data["accounts"]
            if selected_account != "all":
                filtered_transfers = Transfer.objects.filter(account__owner=client)
                filtered_transfers = filtered_transfers.filter(account_id = selected_account)

            if not form.cleaned_data["internal"] and form.cleaned_data["external"]:
                filtered_transfers = filtered_transfers.filter(internal_transfer_type=False)
            elif form.cleaned_data["internal"] and not form.cleaned_data["external"]:
                filtered_transfers = filtered_transfers.filter(internal_transfer_type=True)
            elif not form.cleaned_data["internal"] and not form.cleaned_data["external"]:
                filtered_transfers = filtered_transfers.none()

            if not form.cleaned_data["crediting"] and form.cleaned_data["debiting"]:
                filtered_transfers = filtered_transfers.filter(money__lt=0)
            elif form.cleaned_data["crediting"] and not form.cleaned_data["debiting"]:
                filtered_transfers = filtered_transfers.filter(money__gt=0)
            elif not form.cleaned_data["crediting"] and not form.cleaned_data["debiting"]:
                filtered_transfers = filtered_transfers.none()

            if form.cleaned_data["lower_limit_money"] is not None and not form.cleaned_data["higher_limit_money"]:
                filtered_transfers = filtered_transfers.filter(Q(money__gte=form.cleaned_data["lower_limit_money"]) | Q(money__lte=-form.cleaned_data["lower_limit_money"]))
            elif form.cleaned_data["higher_limit_money"] is not None and not form.cleaned_data["lower_limit_money"]:
                filtered_transfers = filtered_transfers.filter(Q(money__lte=form.cleaned_data["higher_limit_money"]) & Q(money__gte=-form.cleaned_data["higher_limit_money"]))
            elif form.cleaned_data["higher_limit_money"] is not None and form.cleaned_data["lower_limit_money"] is not None:
                filtered_transfers = filtered_transfers.filter((Q(money__gte=-form.cleaned_data["higher_limit_money"]) & Q(money__lte=-form.cleaned_data["lower_limit_money"])) | (Q(money__lte=form.cleaned_data["higher_limit_money"]) & Q(money__gte=form.cleaned_data["lower_limit_money"])))

            if form.cleaned_data["higher_limit_date"] is not None:
                filtered_transfers = filtered_transfers.filter(date__gte=form.cleaned_data["higher_limit_date"])
            if form.cleaned_data["lower_limit_date"] is not None:
                filtered_transfers = filtered_transfers.filter(date__lte=form.cleaned_data["lower_limit_date"])

            filtered_transfers = filtered_transfers.order_by(form.cleaned_data["order_by"])
        else: filtered_transfers = filtered_transfers.none()
    else:
        form = HistoryManagementForm(owner=client)
    return render(request, "transfers/history.html",{
        "transfers":filtered_transfers,
        "owner":client,
        "form":form})
