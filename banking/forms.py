from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Client, Account, Card
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class NewClientForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "pesel", "date_birth", "email", "phone_number"]
        widgets = {
            "date_birth": forms.DateInput(attrs={'type': 'date'})
        }

        error_messages = {"first_name":{
                        "invalid":_("First name is invalid, use letters, spaces, apostrophes, hyphen"),
                        "max_length":_("First name must be shorter than 150 characters")},
                    "last_name":{
                        "invalid":_("Last name is invalid, use letters, spaces, apostrophes, hyphen"),
                        "max_length":_("Last name must be shorter than 150 characters")},
                    "email":{
                        "invalid":_("Incorrect email")},
                    "pesel":{
                        "consist":_("PESEL is required to consist only 11 digits"),
                        "invalid":_("Incorrect PESEL")},
                    "date_birth":{
                                "required_age":_("Age is required to be above 18")},
                    "phone_number":{ 
                                "invalid":_("Phone number is required to contains only 9 digits")}}
    

    def clean(self):
        cleaned_data = super().clean()
        date_birth = cleaned_data.get("date_birth")
        pesel = cleaned_data.get("pesel")

        if not pesel or not date_birth:
            return
        
        month_to_year = {"0":"19","1":"19","2":"20","3":"20","4":"21","5":"21","6":"22","7":"22","8":"18","9":"18"}
        month = pesel[2:4]
        day = pesel[4:6]
        year = month_to_year[month[0]] + pesel[:2]
        if year != str(date_birth.year) or int(day) != date_birth.day or int(month) % 20 != date_birth.month:
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
    TYPE_CHOICES = (
        ("PERSONAL",_("Personal")),
        ("SAVING",_("Saving")),
    )
    type_account = forms.ChoiceField(choices=TYPE_CHOICES)
    add_card = forms.BooleanField(required=False)

    def save(self, owner: Client):
        account = Account(owner=owner, type_account=self.cleaned_data["type_account"])
        account.save()
        return account
    
class NewCreditForm(forms.Form):
    money = forms.IntegerField(label=_("How much money you need"))
    add_card = forms.BooleanField(required=False)

    def save(self, owner:Client):
        account = Account(owner=owner, type_account="CREDIT", money = self.cleaned_data["money"])
        account.save()
        return account

class AccountManagerForm(forms.Form):
    accounts = forms.ModelChoiceField(queryset=Account.objects.none())

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args,**kwargs)
        self.owner = owner
        if self.owner:
            self.fields["accounts"].queryset = self.owner.account_set.all().order_by("-money")
            # equals to line below, left for my personal educational purpose
            # self.fields["accounts"].queryset = Account.objects.filter(owner=self.owner).order_by("-money")
    
    def get_blocked_options(self):
        blocked_options = {}

        if not self.owner:
            return blocked_options
        
        accounts = self.owner.account_set.select_related("card").all()
        # equals to line below, left for my personal educational purpose
        # accounts = Account.objects.select_related("card").filter(owner=self.owner)

        for account in accounts:
            if hasattr(account, "card"):
                blocked_options[f"{account.id}"] = "True"
            else:
                blocked_options[f"{account.id}"] = "False"
        return blocked_options


