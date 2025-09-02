from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Client, validate_pesel, validate_pesel_match_date_birth
from django.core.exceptions import ValidationError

class NewClientForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "pesel", "date_birth", "email", "phone_number"]
        widgets = {
            "date_birth": forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        date_birth = cleaned_data.get("date_birth")
        pesel = cleaned_data.get("pesel")
        print(cleaned_data.get("pesel"))
        print(pesel, date_birth)
        if not validate_pesel_match_date_birth(pesel, date_birth):
            raise ValidationError("PESEL does not match birth date")
        if not validate_pesel(pesel):
            raise ValidationError("Incorrect pesel")
        return cleaned_data


    def save(self, commit=True):
        user = Client.objects.create_user(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            pesel=self.cleaned_data["pesel"],
            date_birth=self.cleaned_data["date_birth"],
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            password=self.cleaned_data["password1"])
        return user

class LoginClientForm(AuthenticationForm):
    pass
