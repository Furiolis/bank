from django.test import TestCase
from django.utils.translation import gettext_lazy as _


from banking.models import Client, Account, Card
from banking.forms import NewClientForm, NewAccountForm, NewCreditForm, AccountManagerForm

from datetime import date
from banking.some_utility import provide_pesel_birthdate


class TestNewClientForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = {
            "first_name": "Tom",
            "last_name": "Furiolis",
            "email": "test@gmail.com",
            "phone_number":  "123456789",
            "pesel": "89010100003",
            "date_birth": "1989-01-01",
            "password1":"pass123word",
            "password2":"pass123word"}

    def test_invalid_client_creation_form(self):

        # first_name
        form = NewClientForm(data={**self.data, "first_name" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "first_name", "This field is required.")
        

        form = NewClientForm(data={**self.data, "first_name" : "Toma3:]"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "first_name", _("First name is invalid, use letters, spaces, apostrophes, hyphen"))

        form = NewClientForm(data={**self.data, "first_name" : f"{200*"s"}"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "first_name", _("First name must be shorter than 150 characters"))

        # last_name
        form = NewClientForm(data={**self.data, "last_name" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "last_name", "This field is required.")

        # email
        form = NewClientForm(data={**self.data, "email" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "email", "This field is required.")

        form = NewClientForm(data={**self.data, "email" : "email.incorrect"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "email", "Incorrect email")

        # phone_number
        form = NewClientForm(data={**self.data, "phone_number" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "phone_number", "This field is required.")      

        form = NewClientForm(data={**self.data, "phone_number" : "234gh4643"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "phone_number", "Phone number is required to contains only 9 digits")      

        form = NewClientForm(data={**self.data, "phone_number" : "2344643"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "phone_number", "Phone number is required to contains only 9 digits")      

        form = NewClientForm(data={**self.data, "phone_number" : "23454356443"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "phone_number", "Phone number is required to contains only 9 digits")   

        # pesel
        form = NewClientForm(data={**self.data, "pesel" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "pesel", "This field is required.")  

        form = NewClientForm(data={**self.data, "pesel" : "432435"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "pesel", "PESEL must consist of 11 digits")  

        form = NewClientForm(data={**self.data, "pesel" : "43243534534534535"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "pesel", "PESEL must consist of 11 digits")  

        form = NewClientForm(data={**self.data, "pesel" : "89010400003"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "pesel", "Incorrect PESEL")  

        form = NewClientForm(data={**self.data, "pesel" : "89110100006"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "pesel", "PESEL does not match birth date")  

        # date_birth
        form = NewClientForm(data={**self.data, "date_birth" : ""})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "date_birth", "This field is required.")  

        form = NewClientForm(data={**self.data, "date_birth" : "2020-01-01"})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "date_birth", "Required age above 18")  

    def test_valid_form_user_saved(self):
        form = NewClientForm(data = self.data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(Client.objects.count(), 1)
        saved_user = Client.objects.first()

        self.assertEqual(saved_user.first_name, self.data["first_name"])
        self.assertEqual(saved_user.email, self.data["email"])
        self.assertEqual(saved_user.pesel, self.data["pesel"])

    def test_invalid_form_user_not_save(self):
        form = NewClientForm(data={**self.data, "pesel":"5345"})
        self.assertFalse(form.is_valid())
        with self.assertRaises(KeyError):
            form.save()
        self.assertEqual(Client.objects.count(), 0)

        
class TestNewAccountForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel="89010400004",
                                            date_birth=date(year=1989,month=1,day=4),
                                            password="passwordhashed")


    def test_valid_new_personal_account_form_successful_save(self):
        form = NewAccountForm({"type_account": NewAccountForm.Type.PERSONAL})
        self.assertTrue(form.is_valid())
        form.save(owner = self.user)
        self.assertEqual(Account.objects.count(), 1)
        saved_account = Account.objects.first()
        self.assertEqual(saved_account.type_account, NewAccountForm.Type.PERSONAL)
        self.assertEqual(Card.objects.count(), 0)

    def test_valid_new_saving_account_form_successful_save(self):
        form = NewAccountForm({"type_account": NewAccountForm.Type.SAVING, "add_card":True})
        self.assertTrue(form.is_valid())
        form.save(owner = self.user)
        self.assertEqual(Account.objects.count(), 1)
        saved_account = Account.objects.first()
        self.assertEqual(saved_account.type_account, NewAccountForm.Type.SAVING)

class TestNewCreditForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel="89010400004",
                                            date_birth=date(year=1989,month=1,day=4),
                                            password="passwordhashed")
        
    def test_valid_new_credit_account_form_successful_save(self):
        form = NewCreditForm({"money":100})
        self.assertTrue(form.is_valid())
        form.save(owner = self.user)
        self.assertEqual(Account.objects.count(), 1)
        saved_account = Account.objects.first()
        self.assertEqual(saved_account.type_account, Account.Type.CREDIT,)
        self.assertEqual(saved_account.money, 100)

class TestAccountManagerForm(TestCase):
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
        
    def test_form_provide_correct_accounts_list(self):
        form = AccountManagerForm(owner=self.client_1)
        self.assertQuerySetEqual(form.fields["accounts"].queryset, [self.account_13,self.account_12,self.account_11])

    def test_cannot_select_account_other_client(self):
        form = AccountManagerForm(data = {"accounts":self.account_11},owner=self.client_2)

        self.assertFalse(form.is_valid())
        self.assertFormError(form,"accounts","Select a valid choice. That choice is not one of the available choices.")

    def test_valid_form_account_without_card(self):
        form = AccountManagerForm(owner=self.client_1, data= {"accounts":self.account_13}, action="add_card")
        self.assertTrue(form.is_valid())

    def test_invalid_form_account_with_card(self):
        form = AccountManagerForm(owner=self.client_1, data= {"accounts":self.account_11}, action="add_card")
        self.assertFalse(form.is_valid())

    def test_form_other_actions(self):
        form = AccountManagerForm(owner=self.client_1, data= {"accounts":self.account_11}, action="other_action")
        self.assertTrue(form.is_valid())

    def test_get_blocked_options_provide_correct_list(self):
        form = AccountManagerForm(owner=self.client_1)
        self.assertEqual(form.get_blocked_options(), {str(self.account_11.id):"True",str(self.account_12.id):"True",str(self.account_13.id):"False"})
