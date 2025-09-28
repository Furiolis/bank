from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from random import randint
from django.contrib.auth.hashers import make_password, check_password
from unidecode import unidecode
from django.core.exceptions import ValidationError
from datetime import timedelta, date

class ClientManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password = None, username = "", **extra_fields):
        # if not first_name:
        #     raise ValueError("User must have a first name")
        # if not last_name:
        #     raise ValueError("User must have a last name")
        # if not email:
        #     raise ValueError("User must have an email")
        # if not phone_number:
        #     raise ValueError("User must have a phone number")
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
                                validators=[UnicodeUsernameValidator()],
                                help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
                                error_messages={"unique": _("A user with that username already exists.")}
                                )
    first_name = models.CharField(max_length=150, validators=[UnicodeUsernameValidator()])   # [RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
    last_name = models.CharField(max_length=150, validators=[UnicodeUsernameValidator()]) # [RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
    email = models.EmailField()
    password = models.CharField(max_length=128)
    pesel = models.CharField(validators=[RegexValidator(r'\d{11}')], unique=True)
    date_birth = models.DateField()
    phone_number = models.CharField(validators=[RegexValidator(r'\d{9}')],)
    # Client.account_set.all()
    # Client.card_set.all()
    
    objects = ClientManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number", "first_name", "last_name", "date_birth"]
    
    def clean(self):
        super().clean()
        if not validate_pesel(self.pesel):
            raise ValidationError("Incorrect pesel")
        if not validate_pesel_match_date_birth(self.pesel, self.date_birth): 
            raise ValidationError("PESEL does not match birth date")
        if not validate_date_birth_above_18_today(self.date_birth):
            raise ValidationError("Required age above 18")

class Account(models.Model):
    TYPE_CHOICES = (
        ("REGULAR","Regular"),
        ("SAVING","Saving"),
        ("CREDIT","Credit")
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
        super().save()
        return self

def validate_pesel(pesel : str) -> bool:
    wage_factors = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
    digit = int(str(sum(int(i) * j for i, j in zip(pesel, wage_factors)))[-1]) # last_digit_of_control_sum
    control_digit = (10 - digit) if digit != 0 else 0
    return pesel[10] == str(control_digit)

def validate_pesel_match_date_birth(pesel : str, date_birth: date) -> bool:
    month_to_year = {"0":"19","1":"19","2":"20","3":"20","4":"21","5":"21","6":"22","7":"22","8":"18","9":"18"}
    month = pesel[2:4]
    day = pesel[4:6]
    year = month_to_year[month[0]] + pesel[:2]
    return year == str(date_birth.year) and int(day) == date_birth.day and int(month) % 20 == date_birth.month
    
def validate_date_birth_above_18_today(date_birth: date) -> bool:
    return date.today() - date_birth > timedelta(days=365*18)
