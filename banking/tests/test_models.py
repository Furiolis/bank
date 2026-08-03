from django.test import TestCase, TransactionTestCase
from django.utils.translation import gettext_lazy as _

from datetime import date

from banking.models import Client, Account, Card

class TestClient(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_test_data = {
            "first_name":"Tom",
            "last_name":"Furiolis",
            "email":"test@GMail.COM",
            "phone_number": "123456789",
            "pesel":"89010100003",
            "date_birth":date(year=1989,month=1,day=1),
            "password":"passwordhashed"}
        
        cls.superuser_test_data = {
            "username":"SuperAdmin",
            "email":"test2@GMail.COM",
            "pesel":"79010100004",
            "password":"passwordhashed"}
        
        cls.user = Client.objects.create_user(first_name="Tom",
                                            last_name="Furiolis",
                                            email="test3@GMail.COM",
                                            phone_number= "123456789",
                                            pesel="89010400004",
                                            date_birth=date(year=1989,month=1,day=4),
                                            password="passwordhashed")
        
        cls.superuser = Client.objects.create_superuser(
                                            username="SuperAdmin",
                                            email="test4@GMail.COM",
                                            pesel="89110100006",
                                            password="passwordhashed")
        
    def test_is_email_normalized(self):
        self.assertEqual(self.user.email, "test3@gmail.com")

    def test_username_created(self):
        self.assertNotEqual(self.user.username, "")
        self.assertIn("tom", self.user.username)
        self.assertIn("furiol", self.user.username)

    def test_password_is_hashed(self):
        self.assertTrue(self.user.check_password("passwordhashed"))

    def test_user_missing_field(self):
        fields = {"first_name", "last_name", "email", "phone_number", "pesel", "date_birth"}
        for field in fields:
            with self.subTest(field=field):
                data = {** self.user_test_data, field:None}
                with self.assertRaises(ValueError):
                    Client.objects.create_user(**data)

    def test_superuser_proper_flags(self):
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_superuser_missing_field(self):
        fields = {"email", "username", "pesel"}
        for field in fields:
            with self.subTest(field=field):
                data = {** self.superuser_test_data, field:None}
                with self.assertRaises(ValueError):
                    Client.objects.create_superuser(** data)

class TestAccount(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Client.objects.create_user(first_name="Tom",
                                    last_name="Furiolis",
                                    email="test3@GMail.COM",
                                    phone_number= "123456789",
                                    pesel="89010400004",
                                    date_birth=date(year=1989,month=1,day=4),
                                    password="passwordhashed")
        cls.account_1 = Account.objects.create(owner=cls.user, type_account=Account.Type.PERSONAL)
        cls.account_2 = Account.objects.create(owner=cls.user, type_account=Account.Type.PERSONAL)
        #cls.account_3 = Account.objects.create(owner=cls.user, type_account=Account.Type.PERSONAL, number="123456")

    def test_account_number_is_created(self):
        self.assertNotEqual(self.account_1.number, self.account_2.number)
        self.assertTrue(self.account_1.number.isnumeric() and len(self.account_1.number) == 6)
        self.assertTrue(self.account_2.number.isnumeric() and len(self.account_2.number) == 6)
        #self.assertTrue(self.account_3.number.isnumeric() and len(self.account_3.number) == 6)
    
class TestAccountTransaction(TransactionTestCase):
    def setUp(self):
        self.user_1 = Client.objects.create_user(first_name="Tom",
                                    last_name="Furiolis",
                                    email="test3@GMail.COM",
                                    phone_number= "123456789",
                                    pesel="89010400004",
                                    date_birth=date(year=1989,month=1,day=4),
                                    password="passwordhashed")
        self.account_1 = Account.objects.create(owner=self.user_1, type_account=Account.Type.PERSONAL, money = 100)
        self.account_2 = Account.objects.create(owner=self.user_1, type_account=Account.Type.SAVING, money = 1000)

        self.user_2 = Client.objects.create_user(first_name="John",
                                    last_name="Reese",
                                    email="test1@GMail.COM",
                                    phone_number= "123456789",
                                    pesel="89110100006",
                                    date_birth=date(year=1989,month=11,day=1),
                                    password="passwordhashed")
        
        self.account_3 = Account.objects.create(owner=self.user_2, type_account=Account.Type.SAVING, money = 1000)

    def test_successful_transfer(self):
        Account.transfer_money(self.account_2, self.account_1, 100)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.assertEqual(self.account_2.money, 900)
        self.assertEqual(self.account_1.money, 200)

        Account.transfer_money(self.account_2, self.account_1, 300)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.assertEqual(self.account_2.money, 600)
        self.assertEqual(self.account_1.money, 500)

        Account.transfer_money(self.account_3, self.account_2, 500)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.account_3.refresh_from_db()
        self.assertEqual(self.account_3.money, 500)
        self.assertEqual(self.account_2.money, 1100)
        self.assertEqual(self.account_1.money, 500)

        Account.transfer_money(self.account_1, self.account_3, 50)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.account_3.refresh_from_db()
        self.assertEqual(self.account_3.money, 550)
        self.assertEqual(self.account_2.money, 1100)
        self.assertEqual(self.account_1.money, 450)

    def test_unsuccessful_transfer_not_enaugh_funds(self):
        with self.assertRaises(ValueError) as error:
            Account.transfer_money(self.account_1, self.account_3, 10000)
        self.assertEqual(str(error.exception), _("Not enough funds"))
        self.assertEqual(self.account_1.money, 100)
        self.assertEqual(self.account_3.money, 1000)

        with self.assertRaises(ValueError) as error:
            Account.transfer_money(self.account_1, self.account_2, 10000)
        self.assertEqual(str(error.exception), _("Not enough funds"))
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.assertEqual(self.account_2.money, 1000)
        self.assertEqual(self.account_1.money, 100)

    def test_successful_transfer_making_debt(self):
        Account.transfer_money(self.account_1, self.account_2, 2000, safe_transfer=False)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.assertEqual(self.account_2.money, 3000)
        self.assertEqual(self.account_1.money, -1900)

        Account.transfer_money(self.account_2, self.account_3, 3500, safe_transfer=False)
        self.account_1.refresh_from_db()
        self.account_2.refresh_from_db()
        self.account_3.refresh_from_db()
        self.assertEqual(self.account_3.money, 4500)
        self.assertEqual(self.account_2.money, -500)
        self.assertEqual(self.account_1.money, -1900)

    def test_negative_or_zero_amount(self):
        with self.assertRaises(ValueError) as error:
            Account.transfer_money(self.account_2, self.account_3, -100)
        self.assertEqual(str(error.exception), _("Transfer amount must be positive"))

        with self.assertRaises(ValueError) as error:
            Account.transfer_money(self.account_2, self.account_3, 0)
        self.assertEqual(str(error.exception), _("Transfer amount must be positive"))

    def test_transefer_to_same_account(self):
        with self.assertRaises(ValueError) as error:
            Account.transfer_money(self.account_2, self.account_2, 100)
        self.assertEqual(str(error.exception), _("Not possible to transfer money to same account"))

