from django.db import models
from django.utils.translation import gettext_lazy as _

from banking.models import Account

class Transfer(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    money = models.PositiveIntegerField()
    date = models.DateField(auto_now=True, auto_now_add=False)
    title = models.CharField(max_length=100)

    # Differentiation based on the transfer recipient
    internal_transfer_type = models.BooleanField(default=False)
    internal_transfer_account = models.ForeignKey(Account, related_name="internal_account", on_delete=models.CASCADE, null=True)
    external_recipient_number = models.IntegerField(null=True)
    external_recipient_name = models.CharField(max_length=100, blank=True)
    