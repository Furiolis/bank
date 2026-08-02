from django.test import TestCase

from datetime import date

from banking.models import Client, Account, Card

class TestClientManager(TestCase):
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
        
        cls.user = Client.objects.create_user(first_name="Tom2",
                                            last_name="Furiolis2",
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
            data = {** self.user_test_data, field:None}
            with self.assertRaises(ValueError):
                Client.objects.create_user(**data)

    def test_superuser_proper_flags(self):
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_superuser_missing_field(self):
        fields = {"email", "username", "pesel"}
        for field in fields:
            data = {** self.superuser_test_data, field:None}
            with self.assertRaises(ValueError):
                Client.objects.create_superuser(** data)