from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import NewClientForm, NewAccountForm, CheatForm
from .models import Client, Account, Card
from .some_utility import provide_pesel_birthdate


def front_page(request):
    return render(request, "banking/front_page.html",{"logged": request.user.is_authenticated})

@login_required
def dashboard(request):
    accounts = list(request.user.account_set.all())
    accounts_regular = []
    accounts_saving = []
    accounts_credit = []
    for account in accounts:
        if account.type_account == "SAVING":
            accounts_saving.append(account)
        if account.type_account == "REGULAR":
            accounts_regular.append(account)
        if account.type_account == "CREDIT":
            accounts_credit.append(account)

    funds = sum([account.money for account in accounts_regular])
    savings = sum([account.money for account in accounts_saving])
    credits = sum([account.money for account in accounts_credit])

    accounts_regular.sort(reverse=True, key= lambda x:x.money)
    accounts_saving.sort(reverse=True, key= lambda x:x.money)
    accounts_credit.sort(reverse=True, key= lambda x:x.money)

    accounts_to_view = accounts_regular + accounts_saving
    accounts_to_view.sort(reverse = True, key= lambda x:x.money)

    return render(request, "banking/dashboard.html",{
        "logged": request.user.is_authenticated,
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
            "form":form})

def logout(request):
    if request.user.is_authenticated:
        logout_user(request)
        messages.success(request, _("You where log out succesfully"))
    return render(request, "banking/logout.html")


def new_client(request):
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
        "birth_date": birth_date.strftime('%d-%m-%Y')})


def confirmation(request):
    client_id = request.session.pop("confirmation_client_id",None)
    if client_id:
        client = Client.objects.get(id=client_id)
    else:
        client = None
    return render(request, "banking/confirm_client_creation.html",{"client":client})


def new_account(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = NewAccountForm(request.POST)
            if form.is_valid():
                user = request.user
                account = form.save(owner=user)
                if form.data.get("add_card") == "on":
                    card = Card(owner=user, account=account)
                    card.save()
                    messages.success(request, f"Account {account.number}, with a card was created succesfully")
                else:

                    messages.success(request, f"Account {account.number} was created succesfully")
                return redirect("main_panel")


        else: # request.method == "GET" 
            form = NewAccountForm()

        return render(request, "banking/new_account.html", {"form": form})
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
    
@login_required
def accounts(request):
    accounts = list(request.user.account_set.all())
    accounts_regular = []
    accounts_saving = []
    accounts_credit = []
    for account in accounts:
        if account.type_account == "SAVING":
            accounts_saving.append(account)
        if account.type_account == "REGULAR":
            accounts_regular.append(account)
        if account.type_account == "CREDIT":
            accounts_credit.append(account)

    savings = sum([account.money for account in accounts_saving])
    funds = sum([account.money for account in accounts_regular])
    credit = sum([account.money for account in accounts_credit])

    accounts_regular.sort(reverse=True, key= lambda x:x.money)
    accounts_saving.sort(reverse=True, key= lambda x:x.money)
    accounts_credit.sort(reverse=True, key= lambda x:x.money)

    form = CheatForm()

    if request.method == "POST":
        form_filled = CheatForm(request.POST)
        if form_filled.is_valid():
            money = form_filled["money"]
            account = Account.objects.get(number=int(form_filled["account"]))
            account.money += money
            account.save()
            
    return render(request, "banking/accounts.html",{
        "logged": request.user.is_authenticated,
        "account": accounts,
        "accounts_saving": accounts_saving,
        "accounts_regular": accounts_regular,
        "accounts_credit": accounts_credit,
        "form":form})