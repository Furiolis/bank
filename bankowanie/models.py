from django.db import models
from random import randint



class Client(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Account(models.Model):
    number = models.IntegerField(unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
