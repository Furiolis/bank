from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from banking.models import Account

class Transfer(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    connected_account_number = models.CharField(_("connected account number"), max_length = 6, validators=[RegexValidator(r'\d{6}')])
    connected_account_name = models.CharField(_("connected account name"),max_length=100, null = True, blank=True)
    money = models.IntegerField(_("money"))
    date = models.DateField(_("date"), auto_now_add=True)
    title = models.CharField(_("title"), max_length=100)

    internal_transfer_type = models.BooleanField(_("internal transfer type"),default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.money} {self.title}"
    