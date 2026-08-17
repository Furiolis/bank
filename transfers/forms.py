from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db import transaction


from .models import Transfer
from banking.models import Account

class TransferFormBase(ModelForm):
    class Meta:
        model = Transfer
        exclude = ["date", "internal_transfer_type"]
        labels = {"account": _("From"),
                  "money": _("Amount"),
                  "connected_account_name": _("Recipient name"),
                  "connected_account_number": _("Recipient account number")
                  }
        
    def __init__(self,  *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_internal = False
        self.owner = owner  
        self.queryset_ = self.owner.accounts.all()
        self.fields["account"].queryset = self.queryset_.filter(money__gt = 0).order_by("-money")

    def clean(self):
        cleaned_data = super().clean()
        if "account" not in self.errors and "money" not in self.errors:
            account = cleaned_data["account"]
            money = cleaned_data["money"]
            if account.money < money:
                raise ValidationError(_("Not enaught money to transfer"))
            if money <= 0:
                raise ValidationError(_("Money must be positive"))
        return cleaned_data

    def save(self):
        cleaned_data =  self.cleaned_data
        money = cleaned_data["money"]
        from_acc = cleaned_data["account"]

        if self.is_internal:
            to_acc = cleaned_data["account_internal"]
            to_acc_name = to_acc.owner.full_name
        else:
            to_acc = self.temporary_account
            to_acc_name = cleaned_data["connected_account_name"]

        with transaction.atomic():
            transfer_from_acc = Transfer(account = from_acc, 
                                         connected_account_number = str(to_acc.number), 
                                         connected_account_name = to_acc_name,
                                         money = -money, 
                                         title = cleaned_data["title"],
                                         internal_transfer_type = self.is_internal)
            
            transfer_to_acc = Transfer(account = to_acc, 
                                       connected_account_number = str(from_acc.number), 
                                       connected_account_name = from_acc.owner.full_name,
                                       money = money, 
                                       title = cleaned_data["title"],
                                       internal_transfer_type = self.is_internal)
            transfer_from_acc.save()
            transfer_to_acc.save()
            Account.transfer_money(from_acc, to_acc, money, safe_transfer=True) # <---- there will be another atomic
        return transfer_from_acc, transfer_to_acc
            
class InternalTransferForm(TransferFormBase):
    account_internal = forms.ModelChoiceField(queryset=Account.objects.none())
    class Meta(TransferFormBase.Meta):
        exclude = TransferFormBase.Meta.exclude + ["connected_account_name", "connected_account_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_internal = True
        self.fields["account_internal"].queryset = self.queryset_

    def clean(self):
        self.cleaned_data = super().clean()
        if "account" not in self.errors:
            if self.cleaned_data.get("account") == self.cleaned_data.get("account_internal"):
                raise ValidationError(_("Both accounts are the same"))
        return self.cleaned_data

class ExternalTransferForm(TransferFormBase):
    def clean_connected_account_number(self):
        connected_account_number = self.cleaned_data["connected_account_number"]
        account = Account.objects.filter(number = connected_account_number).first()
        if not account:
            raise ValidationError(_("Account with that number does not exist"))
        # To save some effort we are returning account instead number, later we would do the same,
        # as we are handling save() this is allowed I belive. lines below are left for educational purpose
        # EDIT: we cant return account
        self.temporary_account = account
        # self.cleaned_data["temporary_account"] = account
        return connected_account_number
    
    def clean(self):
        self.cleaned_data = super().clean()
        if "account" not in self.errors:
            if self.cleaned_data.get("account").number == self.cleaned_data.get("connected_account_number"):
                raise ValidationError(_("Both accounts are the same"))
        return self.cleaned_data
