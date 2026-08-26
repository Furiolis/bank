from django.test import TestCase
from django.urls import reverse

from banking.models import Account, Client
from transfers.models import Transfer
from banking.some_utility import provide_pesel_birthdate
from transfers.forms import InternalTransferForm, ExternalTransferForm

class TestTransferView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # TODO make create_test_user_funtion for tests
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

class TestHistoryView(TestCase):
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

        internal_transfer_data = (
            (cls.account_11,cls.account_12,500,"transfer1"),
            (cls.account_11,cls.account_14,300,"transfer2"),
            (cls.account_12,cls.account_14,123,"transfer3"),
            (cls.account_12,cls.account_14,1200,"transfer4"),
            (cls.account_12,cls.account_13,150,"transfer5",))
        
        for case in internal_transfer_data:
            form = InternalTransferForm(owner=case[0].owner, data={"account":case[0], "account_internal":case[1],"money":case[2],"title":case[3]})
            form.is_valid()
            form.save()

        external_transfer_data = (
            (cls.account_13,cls.account_21.number,cls.account_21.owner.full_name,333,"transfer6"),
            (cls.account_22,cls.account_11.number,cls.account_11.owner.full_name,7,"transfer7",),
            (cls.account_22,cls.account_12.number,cls.account_12.owner.full_name,2500,"transfer8"))

        for case in external_transfer_data:
            form = ExternalTransferForm(owner=case[0].owner, data={"account":case[0], "connected_account_number":case[1],"connected_account_name":case[2],"money":case[3], "title":case[4]})
            form.is_valid()
            form.save()
        
    def test_client_not_sees_others_transfers(self):
        self.assertEqual(Transfer.objects.count(), 16)

        self.client.force_login(self.client_2)
        response = self.client.get(reverse("transfers:history"))
        self.assertEqual(response.context["transfers"].count(), 3)
        self.assertNotContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertNotContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertNotContains(response,"transfer5")

    def test_client_sees_all_his_own_transfers(self):
        self.assertEqual(Transfer.objects.count(), 16)
        self.client.force_login(self.client_1)
        response = self.client.get(reverse("transfers:history"))
        self.assertEqual(response.context["transfers"].count(), 13)
        self.assertContains(response,"transfer1")
        self.assertContains(response,"transfer2")
        self.assertContains(response,"transfer3")
        self.assertContains(response,"transfer4")
        self.assertContains(response,"transfer5")
        self.assertContains(response,"transfer6")
        self.assertContains(response,"transfer7")
        self.assertContains(response,"transfer8")

        self.client.force_login(self.client_2)
        response = self.client.get(reverse("transfers:history"))
        self.assertContains(response,"transfer6")
        self.assertContains(response,"transfer7")
        self.assertContains(response,"transfer8")

    def test_selected_account_returns_corresponding_transfers(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":str(self.account_11.pk), "external":True, "internal":True, "crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())

        self.assertContains(response,"transfer1")
        self.assertContains(response,"transfer2")
        self.assertContains(response,"transfer7")

        self.assertNotContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertNotContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertNotContains(response,"transfer8")

        response = self.client.post(reverse("transfers:history"), data={"accounts":str(self.account_13.pk), "external":True, "internal":True,"crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())

        self.assertContains(response,"transfer5")
        self.assertContains(response,"transfer6")

        self.assertNotContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertNotContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertNotContains(response,"transfer7")
        self.assertNotContains(response,"transfer8")

    def test_external_internal_check_boxes_returns_corresponding_transfers(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":False, "internal":True,"crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertContains(response,"transfer1")
        self.assertContains(response,"transfer2")
        self.assertContains(response,"transfer3")
        self.assertContains(response,"transfer4")
        self.assertContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertNotContains(response,"transfer7")
        self.assertNotContains(response,"transfer8")

        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":False,"crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertNotContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertNotContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertNotContains(response,"transfer5")
        self.assertContains(response,"transfer6")
        self.assertContains(response,"transfer7")

    def test_none_of_external_internal_checkbox_selected(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":False, "internal":False,"crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 0)

    def test_money_fields_limits_transfers(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True, "lower_limit_money": 400, "higher_limit_money":2000, "crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 4)
        self.assertContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertNotContains(response,"transfer3")
        self.assertContains(response,"transfer4")
        self.assertNotContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertNotContains(response,"transfer7")
        self.assertNotContains(response,"transfer8")

        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True, "lower_limit_money": 50, "higher_limit_money":300,"crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 6)
        self.assertNotContains(response,"transfer1")
        self.assertContains(response,"transfer2")
        self.assertContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertNotContains(response,"transfer7")
        self.assertNotContains(response,"transfer8")

        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True, "lower_limit_money": 450, "crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 5)
        self.assertContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertNotContains(response,"transfer3")
        self.assertContains(response,"transfer4")
        self.assertNotContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertNotContains(response,"transfer7")
        self.assertContains(response,"transfer8")

        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True, "higher_limit_money":250, "crediting":True, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 5)
        self.assertNotContains(response,"transfer1")
        self.assertNotContains(response,"transfer2")
        self.assertContains(response,"transfer3")
        self.assertNotContains(response,"transfer4")
        self.assertContains(response,"transfer5")
        self.assertNotContains(response,"transfer6")
        self.assertContains(response,"transfer7")
        self.assertNotContains(response,"transfer8")

    def test_failed_limiting_in_views(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True, "lower_limit_money": 300, "higher_limit_money":200, "crediting":True, "debiting":True})
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 0)

    def test_crediting_debiting_check_boxes_returns_corresponding_transfers(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True,"crediting":True, "debiting":False})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 7)
        self.assertContains(response,"500.00")
        self.assertContains(response,"300.00")
        self.assertContains(response,"123.00")
        self.assertContains(response,"1200.00")
        self.assertContains(response,"150.00")
        self.assertNotContains(response,"333.00")
        self.assertContains(response,"7.00")
        self.assertContains(response,"2500.00")
        self.assertNotContains(response,"-500.00")
        self.assertNotContains(response,"-300.00")
        self.assertNotContains(response,"-123.00")
        self.assertNotContains(response,"-1200.00")
        self.assertNotContains(response,"-150.00")

        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True,"crediting":False, "debiting":True})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 6)
        self.assertContains(response,"-500.00")
        self.assertContains(response,"-300.00")
        self.assertContains(response,"-123.00")
        self.assertContains(response,"-1200.00")
        self.assertContains(response,"-150.00")
        self.assertContains(response,"-333.00")
        self.assertNotContains(response,"2500.00")
        self.assertNotContains(response,"7.00")

    def test_none_of_debiting_crediting_checkbox_selected(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("transfers:history"), data={"accounts":"all", "external":True, "internal":True,"crediting":False, "debiting":False})
        self.assertTrue(response.context["form"].is_valid())
        self.assertEqual(response.context["transfers"].count(), 0)