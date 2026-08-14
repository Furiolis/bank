from django.test import TestCase
from django.urls import reverse

from banking.models import Client, Account, Card
from banking.validators import validate_pesel, validate_date_birth_above_18_today, validate_pesel_match_birth_date
from banking.some_utility import provide_pesel_birthdate

import datetime

class TestRestrictedViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel="89010400004",
                                            date_birth=datetime.date(year=1989,month=1,day=4),
                                            password="passwordhashed")

    def test_not_authenticated_user_on_protectes_site_redirect(self):
        # attempt to login but incorrect password
        self.client.login(username=self.user.username, password="word") 
        response = self.client.get(reverse("banking:dashboard"))
        self.assertRedirects(response, expected_url=f"/?next={reverse("banking:dashboard")}")
        response = self.client.get(reverse("banking:products"))
        self.assertRedirects(response, expected_url=f"/?next={reverse("banking:products")}")
        response = self.client.get(reverse("banking:new_account"))
        self.assertRedirects(response, expected_url=f"/?next={reverse("banking:new_account")}")

    
    def test_authenticated_user_on_protectes_site(self):
        self.client.login(username=self.user.username, password="passwordhashed")
        response = self.client.get(reverse("banking:dashboard"))
        self.assertContains(response, "Welcome, Tom Furiolis", status_code = 200)

class TestUserRegisterAndConfirmationView(TestCase):

    def test_register_view_and_register_client_and_redirect_to_confirmation(self):
        data = {
            "first_name": "Tom",
            "last_name": "Furiolis",
            "email": "test@gmail.com",
            "phone_number":  "123456789",
            #"pesel": "89010100003",
            #"date_birth": "1989-01-01",
            "password1":"pass123word",
            "password2":"pass123word"}
        response = self.client.get(reverse("banking:new_client"))
        pesel = response.context["pesel"]
        birth_date = datetime.datetime.strptime(response.context["birth_date"], "%d-%m-%Y").date()
        validate_pesel(pesel)
        validate_date_birth_above_18_today(birth_date)
        self.assertTrue(validate_pesel_match_birth_date(pesel, birth_date))

        # missing pesel and birth_date
        response = self.client.post(reverse("banking:new_client"), data = {**data})
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Client.objects.count(), 0)

        response = self.client.post(reverse("banking:new_client"), data = {**data, "pesel":pesel, "date_birth": birth_date})
        self.assertRedirects(response, expected_url=reverse("banking:confirmation"))
        self.assertEqual(Client.objects.count(), 1)

        response = self.client.get(reverse("banking:confirmation"))
        self.assertTemplateUsed(response, template_name="banking/confirm_client_creation.html")

class TestUserLoginAndRedirect(TestCase):
    def test_login_success(self):
        pesel, date_birth = provide_pesel_birthdate()
        user= Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel=pesel,
                                            date_birth=date_birth,
                                            password="passwordhashed")

        response = self.client.post(reverse("banking:login"), data={"username":user.username, "password":"passwordhashed"})
        self.assertRedirects(response, expected_url=reverse("banking:dashboard"))

        response = self.client.get(reverse("banking:dashboard"))
        self.assertContains(response, "Welcome, Tom Furiolis", status_code = 200)

class TestUserSeesOwnedProductsOnly(TestCase):
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
        cls.card_11 = Card.objects.create(owner=cls.client_1, account=cls.account_11)
        cls.account_12 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.SAVING, money=2000)
        cls.card_12 = Card.objects.create(owner=cls.client_1, account=cls.account_12)
        cls.account_13 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.CREDIT, money=3000)

        pesel, date_birth = provide_pesel_birthdate()
        cls.client_2 = Client.objects.create_user(first_name="Tomas",
                                            last_name="Fox",
                                            email="test@GMail.COM",
                                            phone_number= "123456789",
                                            pesel=pesel,
                                            date_birth=date_birth,
                                            password="passwordhashed")

    def test_user_sees_owned_products(self):
        self.client.force_login(self.client_1)
        response = self.client.get(reverse("banking:dashboard"))
        self.assertContains(response, self.account_11.number)
        self.assertContains(response, self.account_12.number)
        self.assertContains(response, self.account_13.number)
        self.assertContains(response, self.card_11.number)
        self.assertContains(response, self.card_12.number)

        response = self.client.get(reverse("banking:products"))
        self.assertContains(response, self.account_11.number)
        self.assertContains(response, self.account_12.number)
        self.assertContains(response, self.account_13.number)
        self.assertContains(response, self.card_11.number)
        self.assertContains(response, self.card_12.number)

    def test_user_not_sees_others_products(self):
        self.client.force_login(self.client_2)
        response = self.client.get(reverse("banking:dashboard"))
        self.assertNotContains(response, self.account_11.number)
        self.assertNotContains(response, self.account_12.number)
        self.assertNotContains(response, self.account_13.number)
        self.assertNotContains(response, self.card_11.number)
        self.assertNotContains(response, self.card_12.number)

        response = self.client.get(reverse("banking:products"))
        self.assertNotContains(response, self.account_11.number)
        self.assertNotContains(response, self.account_12.number)
        self.assertNotContains(response, self.account_13.number)
        self.assertNotContains(response, self.card_11.number)
        self.assertNotContains(response, self.card_12.number)

class TestNewAccountAndNewCreditViews(TestCase):
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

    def test_new_account_view_without_card(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("banking:new_account"), data={"type_account":"SAVING"})
        self.assertRedirects(response, expected_url=reverse("banking:dashboard"))
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Card.objects.count(), 0)
        
    def test_new_credit_view_with_card(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("banking:new_credit"), data={"money":"1333","add_card":"on"})
        self.assertRedirects(response, expected_url=reverse("banking:dashboard"))
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Card.objects.count(), 1) 
        self.assertEqual(Account.objects.first().money, 1333)

    def test_invalid_form_new_credit_view(self):
        self.client.force_login(self.client_1)
        response = self.client.post(reverse("banking:new_credit"), data={})
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Account.objects.count(), 0)
