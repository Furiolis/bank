from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db import models

from .models import Client, Account
from .validators import validate_pesel_match_birth_date, validate_pesel, validate_date_birth_above_18_today

class NewClientForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "pesel", "date_birth", "email", "phone_number"]
        widgets = {
            "date_birth": forms.DateInput(attrs={"type": "date"})
        }

        error_messages = {
            "first_name":{
                "invalid":_("First name is invalid, use letters, spaces, apostrophes, hyphen"),
                "max_length":_("First name must be shorter than 150 characters")},
            "last_name":{
                "invalid":_("Last name is invalid, use letters, spaces, apostrophes, hyphen"),
                "max_length":_("Last name must be shorter than 150 characters")},
            "email":{
                "invalid":_("Incorrect email")},
            "pesel":{
                "consist":_("PESEL must consist of 11 digits"),
                "invalid":_("Incorrect PESEL")},
            "date_birth":{
                        "required_age":_("Age is required to be above 18")},
            "phone_number":{ 
                        "invalid":_("Phone number is required to contains only 9 digits")}}


    def clean_pesel(self):
        pesel = self.cleaned_data["pesel"]
        validate_pesel(pesel)
        return pesel

    def clean_date_birth(self):
        date_birth = self.cleaned_data["date_birth"]
        validate_date_birth_above_18_today(date_birth)
        return date_birth
    
    def clean(self):
        cleaned_data = super().clean()
        date_birth = cleaned_data.get("date_birth")
        pesel = cleaned_data.get("pesel")

        if self.errors.get("pesel") or self.errors.get("date_birth"):
            return cleaned_data

        if not pesel or not date_birth:
            return cleaned_data

        if not validate_pesel_match_birth_date(pesel, date_birth):
            self.add_error("pesel",_("PESEL does not match birth date"))
            self.add_error("date_birth",_("PESEL does not match birth date"))
            
        return cleaned_data


    def save(self):
        user = Client.objects.create_user(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            pesel=self.cleaned_data["pesel"],
            date_birth=self.cleaned_data["date_birth"],
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            password=self.cleaned_data["password1"])
        return user


class NewAccountForm(forms.Form):
    class Type(models.TextChoices):
        PERSONAL="PERSONAL", _("Personal")
        SAVING="SAVING", _("Saving")
    
    type_account = forms.ChoiceField(choices=Type.choices)
    add_card = forms.BooleanField(required=False)

    def save(self, owner: Client):
        account = Account(owner=owner, type_account=self.cleaned_data["type_account"])
        account.save()
        return account
    
class NewCreditForm(forms.Form):
    money = forms.DecimalField(label=_("How much money you need"), decimal_places=2, max_digits=15)
    add_card = forms.BooleanField(required=False)

    def save(self, owner:Client):
        account = Account(owner=owner, type_account=Account.Type.CREDIT, money = self.cleaned_data["money"])
        account.save()
        return account

class AccountManagerForm(forms.Form):
    accounts = forms.ModelChoiceField(queryset=Account.objects.none())

    def __init__(self, *args, owner, action=None, **kwargs):
        super().__init__(*args,**kwargs)
        self.owner = owner
        self.action = action
        self.fields["accounts"].queryset = self.owner.accounts.all().order_by("-money")
        # equals to line below, left for my personal educational purpose
        # self.fields["accounts"].queryset = Account.objects.filter(owner=self.owner).order_by("-money")
            
    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get("accounts")
        if self.action == "add_card" and hasattr(account, "card"):
            self.add_error("accounts", _(f"Card already exists to {account.number}"))
        elif self.action == "delete_card" and not hasattr(account, "card"):
            self.add_error("accounts", _(f"Account {account.number} has no card"))
        return cleaned_data

    def get_blocked_options(self):
        blocked_options = {}        
        accounts = self.owner.accounts.select_related("card").all()
        # equals to line below, left for my personal educational purpose
        # accounts = Account.objects.select_related("card").filter(owner=self.owner)

        # line below saved to remember, filter accounts without card
        # self.fields["accounts"].queryset = self.owner.account_set.filter(card__isnull=True)

        for account in accounts:
            if hasattr(account, "card"):
                blocked_options[f"{account.id}"] = "True"
            else:
                blocked_options[f"{account.id}"] = "False"
        return blocked_options
      