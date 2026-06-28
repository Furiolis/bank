from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Transfer

class TranferFormBase(ModelForm):
    class Meta:
        model = Transfer
        fields = ["account", "money", "title"]

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.fields["account"].queryset = self.owner.account_set.all().filter(money__gt = 0).order_by("-money")



    # def clean_money(self):
    #     money = self.cleaned_data["money"]
    #     if money <= 0:
    #         raise forms.ValidationError(_("Put positive number"))
    #     account = self.cleaned_data["account"]
    #     return money
        
        

class InternalTransferForm(TranferFormBase):
    class Meta(TranferFormBase.Meta):
        fields = TranferFormBase.Meta.fields + ["internal_transfer_type"]





class ExternalTransferForm(TranferFormBase):
    class Meta(TranferFormBase.Meta):
        fields = TranferFormBase.Meta.fields + ["external_recipient_number", "external_recipient_name"]




    