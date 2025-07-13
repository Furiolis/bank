from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from random import randint
from django.utils.translation import gettext_lazy as _

class ClientManager(BaseUserManager):

    def create_user(self, email, phone_number, first_name, last_name, password = None, username = "", **extra_fields):
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")
        if not email:
            raise ValueError("User must have an email")
        if not phone_number:
            raise ValueError("User must have a phone number")
        
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
                          phone_number = phone_number,
                          first_name = first_name, 
                          last_name = last_name,
                          **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, phone_number, first_name, last_name, password = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, phone_number, first_name, last_name, password, **extra_fields)

class Client(AbstractUser, PermissionsMixin):
    username = models.CharField(_("username"),  # username created automatically from first_name and last_name
                                max_length=30,
                                unique=True,
                                validators=[UnicodeUsernameValidator()],
                                help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
                                error_messages={"unique": _("A user with that username already exists.")}
                                )
    # first_name inherited from AbstractUser
    # last_name inherited from AbstractUser
    # email inherited from AbstractUser
    # password inherited from AbstractUser
    # account declared on Account model
    pesel = models.CharField(max_length=11,)
    date_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=9)

    objects = ClientManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number", "first_name", "last_name", "date_birth"]

class Account(models.Model):
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    money = models.BigIntegerField(default = 0)

class Card(models.Model):
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
