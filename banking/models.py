from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction

from random import randint
from unidecode import unidecode
from datetime import date

from .validators import validate_pesel, validate_date_birth_above_18_today


class ClientManager(BaseUserManager):
    def create_user(self, email=None, pesel=None, date_birth=None, first_name=None, last_name=None, phone_number=None, password = None, **extra_fields):
        if not email:
            raise ValueError(_("Email is required"))
        if not pesel:
            raise ValueError(_("Pesel is required"))
        if not date_birth:
            raise ValueError(_("Date of birth is required"))
        if not first_name:
            raise ValueError(_("First name is required"))
        if not last_name:
            raise ValueError(_("Last name is required"))
        if not phone_number:
            raise ValueError(_("Phone number is required"))

        email = self.normalize_email(email)
    #   usernames = Client.objects.values_list("username", flat=True) # old solution
        first_name_truncated = first_name.lower()[:6]
        last_name_truncated = last_name.lower()[:6]
        while True:
            random_number = randint(1000, 9999)
            username = unidecode(first_name_truncated) + str(random_number) + unidecode(last_name_truncated)
    #       if username not in usernames: # old solution
            if Client.objects.filter(username=username).exists():
                continue

            user = self.model(username = username, 
                            email = email, 
                            first_name = first_name, 
                            last_name = last_name,
                            pesel = pesel,
                            date_birth = date_birth,
                            phone_number = phone_number,
                            **extra_fields)
            user.set_password(password)
            try: # just in case, AI suggested this, 
                user.save(using = self._db)
                return user
            except IntegrityError:
                continue


    def create_superuser(self, 
                        email, 
                        username,
                        pesel,
                        date_birth = date(year=1900, month=1, day=1), 
                        first_name = "Fake", 
                        last_name = "Bank", 
                        phone_number = "000000000", 
                        password = None, **extra_fields):
        if not email:
            raise ValueError(_("Email is required"))
        if not username:
            raise ValueError(_("Username is  required"))
        if not pesel:
            raise ValueError(_("Pesel is  required"))

        email = self.normalize_email(email)
        extra_fields["is_superuser"] = True
        extra_fields["is_staff"] = True

        superuser = self.model(username = username, 
                          email = email, 
                          first_name = first_name,
                          last_name = last_name,
                          pesel = pesel,
                          date_birth = date_birth,
                          phone_number = phone_number,
                          **extra_fields)
        superuser.set_password(password)
        superuser.save(using = self._db)
        return superuser


class Client(AbstractUser):
    username = models.CharField(_("username"),  # username created automatically from first_name and last_name
                                max_length=150,
                                unique=True,
                                validators=[UnicodeUsernameValidator()])
    first_name = models.CharField(_("first name"), 
                                max_length=150, 
                                validators=[RegexValidator(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+$")])
    last_name = models.CharField(_("last name"), 
                                max_length=150, 
                                validators=[RegexValidator(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż' -]+$")])
    email = models.EmailField(_("email address"), unique = True)                           
    # password = models.CharField(max_length=128)
    pesel = models.CharField("PESEL", validators=[validate_pesel], unique=True, 
                                error_messages={
                                    "required" : _("PESEL is required" ),
                                    "consist" : _("PESEL must consist of 11 digits"),
                                    "invalid" : _("Incorrect PESEL")})
    date_birth = models.DateField(_("birth date"), validators=[validate_date_birth_above_18_today],
                                error_messages={
                                    "required" :_("Date of birth is required"),
                                    "required_age" : _("Required age above 18")})
    phone_number = models.CharField(_("phone number"),validators=[RegexValidator(r'\d{9}')],
                                error_messages={
                                    "required" : _("Phone number is required"),
                                    "invalid" : _("Phone number is incorrect, can contains only 9 digits")})
    
    objects = ClientManager()
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number", "first_name", "last_name", "date_birth", "pesel"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Account(models.Model):

    class Type(models.TextChoices):
        PERSONAL="PERSONAL", _("Personal")
        SAVING="SAVING", _("Saving")
        CREDIT="CREDIT", _("Credit")

    number = models.CharField(unique=True, max_length=6, validators=[RegexValidator(r"^\d{6}$")], blank=True)
    owner = models.ForeignKey(Client, related_name="accounts", on_delete=models.CASCADE)
    money = models.DecimalField(decimal_places=2, max_digits=15, default=0)
    type_account = models.CharField(choices=Type.choices, default=Type.PERSONAL)

    def save(self, *args, **kwargs):
        if not self.number:
        #   accounts = Account.objects.values_list("number",flat=True) # old solution
            while True:
                random_number = str(randint(100000, 999999))
        #       if random_number not in accounts: # old solution
                if Account.objects.filter(number=random_number).exists():
                    continue
                self.number = random_number
                try:
                    super().save(*args, **kwargs)
                    return self
                except IntegrityError:
                    continue
        else:
            super().save(*args, **kwargs)
            return self
        

    @classmethod
    def transfer_money(cls, acc_from, acc_to, amount, safe_transfer):
        if safe_transfer and amount > acc_from.money:
            raise ValueError(_("Not enough funds"))
        if amount <= 0:
            raise ValueError(_("Transfer amount must be positive"))
        if acc_from == acc_to:
            raise ValueError(_("Not possible to transfer money to same account"))
        with transaction.atomic():
            from_acc = Account.objects.select_for_update().get(id = acc_from.id)
            to_acc = Account.objects.select_for_update().get(id = acc_to.id)
 
            from_acc.money -= amount
            to_acc.money += amount
            from_acc.save()
            to_acc.save()
        return True

    def __str__(self):
        return f"{self.get_type_account_display()} {_("account")} ({self.money} PLN)" 

class Card(models.Model):
    number = models.CharField(unique=True, max_length=4, validators=[RegexValidator(r"^\d{4}$")])
    owner = models.ForeignKey(Client, related_name="cards", on_delete=models.CASCADE)
    account = models.OneToOneField(Account, related_name="card", on_delete=models.CASCADE)
    pin = models.CharField(max_length=128)

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def save(self, *args, **kwargs):
        if not self.number:
        #   cards = Card.objects.values_list("number", flat=True) # old solution
            while True:
                random_number = str(randint(1000,9999))
        #       if random_number not in cards: # old solution
                if Card.objects.filter(number=random_number).exists():
                    continue
                self.number = random_number
                random_pin = str(randint(1000,9999))
                self.set_pin(random_pin)
                try:
                    super().save(*args, **kwargs)
                    return self
                except IntegrityError:
                    continue
        else:
            super().save(*args, **kwargs)
            return self

    def __str__(self):
        return f"{self.number} ({self.account.money})PLN"
