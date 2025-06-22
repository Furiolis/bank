from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Client

class NewClientForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "pesel", "date_birth", "email", "phone_number"]
        widgets = {
            "date_birth": forms.DateInput(attrs={'type': 'date'})
        }
    
    def save(self, commit=True):
        print("TO SIE DZIEJE")
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
