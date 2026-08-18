from django.test import TestCase
from django.urls import reverse

from banking.models import Account, Client
from transfers.models import Transfer
from banking.some_utility import provide_pesel_birthdate

class TestTransferView(TestCase):
    @classmethod
    def setUpTestData(cls):
        pesel, date_birth = provide_pesel_birthdate()
        cls.client_1 = Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel=pesel,
                                            date_birth=date_birth,
                                            password="passwordhashed")
        cls.account_11 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.PERSONAL, money=1000)
        cls.account_12 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.SAVING, money=3000)
        cls.account_13 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.CREDIT, money=2000)
        cls.account_14 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.CREDIT, money=0)

        pesel, date_birth = provide_pesel_birthdate()
        cls.client_2 = Client.objects.create_user(first_name="Tomas",
                                            last_name="Fox",
                                            email="test@GMail.COM",
                                            phone_number= "123456789",
                                            pesel=pesel,
                                            date_birth=date_birth,
                                            password="passwordhashed")
        cls.account_21 = Account.objects.create(owner=cls.client_2, type_account=Account.Type.PERSONAL, money=1000)
        cls.account_22 = Account.objects.create(owner=cls.client_2, type_account=Account.Type.SAVING, money=3000)

        cls.data_external = {"account": cls.account_11.id, 
                 "money":100, 
                 "connected_account_number":cls.account_22.number, 
                 "connected_account_name":"some client", 
                 "title":"some title"}

        cls.data_internal = {"account": cls.account_13.id, 
                 "money":200, 
                 "account_internal":cls.account_14.id, 
                 "title":"different title"}

    def test_not_logged_user_redirects(self):
        response = self.client.get(reverse("transfers:transfer"))
        self.assertRedirects(response, expected_url=f"/?next={reverse("transfers:transfer")}")

    def test_user_sees_in_forms_only_owned_account(self):
        self.client.force_login(self.client_1)
        response = self.client.get(reverse("transfers:transfer"))
        self.assertQuerySetEqual(response.context["internal_form"].fields["account"].queryset, [self.account_12,self.account_13,self.account_11])
        self.assertNotIn(self.account_14, response.context["internal_form"].fields["account"].queryset)
        
        self.assertQuerySetEqual(response.context["internal_form"].fields["account_internal"].queryset, [self.account_11,self.account_12,self.account_13,self.account_14], ordered=False)
        self.assertNotIn(self.account_22, response.context["internal_form"].fields["account_internal"].queryset)
        self.assertNotIn(self.account_21, response.context["internal_form"].fields["account_internal"].queryset)

        self.assertQuerySetEqual(response.context["external_form"].fields["account"].queryset, [self.account_12,self.account_13,self.account_11])
        self.assertNotIn(self.account_14, response.context["external_form"].fields["account"].queryset)

    def test_view_external_transfer_(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:transfer"), data={** self.data_external, "form_type":"external"})
        self.assertRedirects(response, expected_url=reverse("banking:dashboard"))
        self.account_11.refresh_from_db()
        self.assertEqual(self.account_11.money, 900)
        self.account_22.refresh_from_db()
        self.assertEqual(self.account_22.money, 3100)
        self.assertEqual(Transfer.objects.count(), 2)

    def test_view_internal_transfer_(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:transfer"), data={** self.data_internal, "form_type":"internal"})
        self.assertRedirects(response, expected_url=reverse("banking:dashboard"))
        self.account_13.refresh_from_db()
        self.assertEqual(self.account_13.money, 1800)
        self.account_14.refresh_from_db()
        self.assertEqual(self.account_14.money, 200)
        self.assertEqual(Transfer.objects.count(), 2)

    def test_view_with_failed_form(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:transfer"), data={"form_type":"internal"})
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "transfers/transfers.html")

    def test_proper_form_is_used(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:transfer"),data={"form_type": "external"})
        self.assertEqual(response.context["external_form"].__class__.__name__,"ExternalTransferForm")
