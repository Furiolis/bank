from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from random import randint

class ClientManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password = None, username = "", **extra_fields):
        """if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")
        if not email:
            raise ValueError("User must have an email")
        if not phone_number:
            raise ValueError("User must have a phone number")"""
        if username == "":
            usernames = Client.objects.values_list("username", flat=True)
            username = "username"
            while True:
                random_number = randint(1000, 9999)
                username = first_name.lower()[:6] + str(random_number) + last_name.lower()[:6]
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
    first_name = models.CharField(max_length=150, validators=[RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
    last_name = models.CharField(max_length=150, validators=[RegexValidator(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+")])
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


class Account(models.Model):
    number = models.IntegerField(unique=True,)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    money = models.BigIntegerField(default = 0)
    # Account.card_set.all()


class Card(models.Model):
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


def validate_pesel(pesel):
    _pesel = str(pesel)
    wage_factors = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
    digit = int(str(sum(int(i) * j for i, j in zip(_pesel, wage_factors)))[-1]) # last_digit_of_control_sum
    control_digit = (10 - digit) if digit != 0 else 0
    return _pesel[10] == str(control_digit)
    

def validate_pesel_match_date_birth(pesel, date_birth):
    month_to_year = {"0":"19","1":"19","2":"20","3":"20","4":"21","5":"21","6":"22","7":"22","8":"18","9":"18"}
    _pesel = str(pesel)
    year = _pesel[:2]
    month = _pesel[2:4]
    day = _pesel[4:6]
    return (month_to_year[month[0]] +  year) == str(date_birth.year) and int(day) == date_birth.day and (int(month) % 20) == date_birth.month