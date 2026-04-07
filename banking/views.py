from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import NewClientForm, NewAccountForm, AccountManagerForm, NewCreditForm
from .models import Client, Account, Card
from .some_utility import provide_pesel_birthdate


def front_page(request):
    return render(request, "banking/front_page.html",{"not_logged": not request.user.is_authenticated})

@login_required
def dashboard(request):
    # TODO Move that logic to the AccountManager
    accounts = list(request.user.account_set.all())
    accounts_personal = []
    accounts_saving = []
    accounts_credit = []
    for account in accounts:
        if account.type_account == "SAVING":
            accounts_saving.append(account)
        if account.type_account == "PERSONAL":
            accounts_personal.append(account)
        if account.type_account == "CREDIT":
            accounts_credit.append(account)

    funds = sum([account.money for account in accounts_personal])
    savings = sum([account.money for account in accounts_saving])
    credits = sum([account.money for account in accounts_credit])

    accounts_personal.sort(reverse=True, key= lambda x:x.money)
    accounts_saving.sort(reverse=True, key= lambda x:x.money)
    accounts_credit.sort(reverse=True, key= lambda x:x.money)

    accounts_to_view = accounts_personal + accounts_saving
    accounts_to_view.sort(reverse = True, key= lambda x:x.money)

    return render(request, "banking/dashboard.html",{
        "owner": f"{request.user.first_name.capitalize()} {request.user.last_name.capitalize()}",
        "funds": funds,
        "savings": savings,
        "debts": credits,
        "accounts": accounts_to_view[:5],
        "accounts_credit": accounts_credit[:3],
        "last_login": request.user.last_login,})

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, _("You are already logged in"))
        return redirect("dashboard")
    else:
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login_user(request, user)
                messages.success(request, mark_safe(_(f"Welcome {user.get_short_name()}, you have logged in succesfully. What We are gonna do today?")))
                return redirect("dashboard")
            else:
                messages.warning(request, mark_safe(_("Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.") % {"username": form.username_field.verbose_name}))
        else: # request.method == "GET"
            form = AuthenticationForm()
        return render(request, "banking/login.html", {
            "form":form,
            "not_logged": True})

def logout(request):
    if request.user.is_authenticated:
        logout_user(request)
        messages.success(request, _("You where log out succesfully"))
    return redirect("front_page")

def new_client(request):
    if request.user.is_authenticated:
        messages.warning(request,_("You already are client of Fake Bank, and you are logged in"))
        return redirect("dashboard")
    else:
        if request.method == "POST":
            form = NewClientForm(request.POST)
            if form.is_valid():
                client = form.save()
                request.session["confirmation_client_id"] = client.id
                return redirect("confirmation") 
        else: # request.method == "GET"
            form = NewClientForm()
        pesel, birth_date = provide_pesel_birthdate()
        return render(request, "banking/new_client.html",{
            "form": form,
            "pesel": pesel,
            "birth_date": birth_date.strftime('%d-%m-%Y'),
            "not_logged": True})

def confirmation(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        client_id = request.session.pop("confirmation_client_id",None)
        if client_id:
            client = Client.objects.get(id=client_id)
        else:
            client = None
        return render(request, "banking/confirm_client_creation.html",{
            "client":client,
            "not_logged": True})

@login_required
def new_account(request):
    if request.method == "POST":
        form = NewAccountForm(request.POST)
        if form.is_valid():
            user = request.user
            account = form.save(owner=user)
            if form.data.get("add_card") == "on":
                # TODO Move adding card logic to save method
                card = Card(owner=user, account=account)
                card.save()
                messages.success(request, f"Account {account.number}, with a card was created succesfully")
            else:
                messages.success(request, f"Account {account.number} was created succesfully")
            return redirect("dashboard")
    else: # request.method == "GET" 
        form = NewAccountForm()
    return render(request, "banking/new_account.html", {"form": form})
    
@login_required
def new_credit(request):
    if request.method == "POST":
        form = NewCreditForm(request.POST)
        if form.is_valid():
            user = request.user
            account = form.save(owner=user)
            if form.data.get("add_card") == "on":
                # TODO Move adding card logic to save method
                card = Card(owner=user, account=account)
                card.save()
                messages.success(request, f"Account {account.number}, with a card was created succesfully")
            else:
                messages.success(request, f"Account {account.number} was created succesfully")
            return redirect("dashboard")
    else: # request.method == "GET" 
        form = NewCreditForm()
    return render(request, "banking/new_credit.html", {"form": form})

@login_required
def accounts(request):
    # TODO Move that logic to the AccountManager
    accounts = list(request.user.account_set.all())
    accounts_personal = []
    accounts_saving = []
    accounts_credit = []
    for account in accounts:
        if account.type_account == "SAVING":
            accounts_saving.append(account)
        if account.type_account == "PERSONAL":
            accounts_personal.append(account)
        if account.type_account == "CREDIT":
            accounts_credit.append(account)

    savings = sum([account.money for account in accounts_saving])
    funds = sum([account.money for account in accounts_personal])
    credit = sum([account.money for account in accounts_credit])

    accounts_personal.sort(reverse=True, key= lambda x:x.money)
    accounts_saving.sort(reverse=True, key= lambda x:x.money)
    accounts_credit.sort(reverse=True, key= lambda x:x.money)

    return render(request, "banking/accounts.html",{
        "account": accounts,
        "savings":savings,
        "funds":funds,
        "credit":credit,
        "accounts_saving": accounts_saving,
        "accounts_personal": accounts_personal,
        "accounts_credit": accounts_credit})

@login_required
def accounts_manage(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "delete_account" or action == "add_card":
            form = AccountManagerForm(request.POST, owner=request.user)
            if form.is_valid():
                account = form.cleaned_data["accounts"]
                if action == "delete_account":
                    account.delete()
                elif action == "add_card":
                    card = Card(account = account, owner = request.user)
                    card.save()
    else:
        form = AccountManagerForm(owner=request.user)
    print(form.get_blocked_options())
    return render(request, "banking/accounts_manage.html",{
        "form":form,
        "blocked_options": form.get_blocked_options()
    })

@login_required
def cards(request):
   return render(request, "banking/cards.html",)

@login_required
def cards_manage(request):
    return render(request, "banking/cards_manage.html",)
