from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
from random import randint
from unidecode import unidecode
from .validators import validate_pesel, validate_date_birth_above_18_today


class ClientManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password = None, username = "", **extra_fields):
        if username == "":
            usernames = Client.objects.values_list("username", flat=True)
            username = "username"
            while True:
                random_number = randint(1000, 9999)
                username = unidecode(first_name.lower()[:6]) + str(random_number) + unidecode(last_name.lower()[:6])
                if username not in usernames:
                    break

        email = self.normalize_email(email)
        user = self.model(username = username, 
                          email = email, 
                          first_name = first_name, 
                          last_name = last_name,
                          **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(**extra_fields)


class Client(AbstractUser, PermissionsMixin):
    username = models.CharField(_("username"),  # username created automatically from first_name and last_name
                                max_length=150,
                                unique=True,
                                validators=[UnicodeUsernameValidator()])
    first_name = models.CharField(_("first name"), 
                                max_length=150, 
                                validators=[UnicodeUsernameValidator()], # [RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
                                error_messages={    
                                    "required" : "First name is required",
                                    "max_length": "First name must be shorter than 150 characters"})
    last_name = models.CharField(_("last name"), 
                                max_length=150, 
                                validators=[UnicodeUsernameValidator()], # [RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
                                error_messages={
                                    "required" : "Last name is required",
                                    "max_length": "Last name must be shorter than 150 characters"})
    email = models.EmailField(_("email address"))
    password = models.CharField(max_length=128)
    pesel = models.CharField("PESEL", validators=[validate_pesel], unique=True)
    date_birth = models.DateField(_("birth date"), validators=[validate_date_birth_above_18_today])
    phone_number = models.CharField(_("phone number"),validators=[RegexValidator(r'\d{9}')],)
    # Client.account_set.all()
    # Client.card_set.all()

    objects = ClientManager()
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number", "first_name", "last_name", "date_birth"]
    
    def clean(self):
        month_to_year = {"0":"19","1":"19","2":"20","3":"20","4":"21","5":"21","6":"22","7":"22","8":"18","9":"18"}
        month = self.pesel[2:4]
        day = self.pesel[4:6]
        year = month_to_year[month[0]] + self.pesel[:2]
        if year != str(self.date_birth.year) or int(day) != self.date_birth.day or int(month) % 20 != self.date_birth.month:
            raise ValidationError(_("PESEL does not match birth date"))

class Account(models.Model):
    TYPE_CHOICES = (
        ("REGULAR",_("Regular")),
        ("SAVING",_("Saving")),
        ("CREDIT",_("Credit"))
    )
    number = models.IntegerField(unique=True, null=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    money = models.BigIntegerField(default = 0)
    type_account = models.CharField(choices=TYPE_CHOICES, default="REGULAR")
    # Account.card

    def save(self, *args, **kwargs):
        if not self.number:
            accounts = Account.objects.values_list("number",flat=True)
            while True:
                random_number = randint(100000, 999999)
                if random_number not in accounts:
                    self.number = random_number
                    break
        super().save(*args, **kwargs)
        return self


class Card(models.Model):
    number = models.IntegerField(unique=True, null=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    pin = models.CharField(validators=[RegexValidator(r'\d{4}')], default="0000")

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)

    def chech_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def save(self, *args, **kwargs):
        if not self.number:
            cards = Card.objects.values_list("number", flat=True)
            while True:
                random_number = randint(1000,9999)
                if random_number not in cards:
                    self.number = random_number
                    break
            random_pin = str(randint(1000,9999))
            self.pin = random_pin
        super().save(self, *args, **kwargs)
        return self

