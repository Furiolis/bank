from django.db import models
from .. banking import Account
from datetime import date

class Transfer(models.Model):
    sender = models.ForeignKey(Account)
    recipient = models.ForeignKey(Account)
    money = models.IntegerField()
    date = models.DateField(auto_now=True, auto_now_add=False)
    title = models.CharField(max_length=100)

    