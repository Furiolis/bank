from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator


class Client(AbstractUser):
    # username created automatically from first_name and last_name, inherited from AbstractUser
    # first_name inherited from AbstractUser
    # last_name inherited from AbstractUser
    # email inherited from AbstractUser
    # password inherited from AbstractUser
    # account declared on Account model
    pesel = models.CharField(max_length=11)
    date_birth = models.DateField()
    phone_number = models.CharField(max_length=9)

    # groups = models.ManyToManyField(Group, related_name='client_set', blank=True)
    # user_permissions = models.ManyToManyField(Permission, related_name='client_permissions_set', blank=True)
    

class Account(models.Model):
    ACCOUNT_TYPE = {
        "NORMAL": "Normalne",
        "DEBET": "Debetowe",
        "CREDIT": "Kredytowe",
        "SAVINGS": "Oszczędnościowe",
    }
    type = models.CharField(max_length = 10, choices = ACCOUNT_TYPE, default = "NORMAL")
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    money = models.BigIntegerField(default = 0)

class Card(models.Model):
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
