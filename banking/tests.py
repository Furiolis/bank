from django.test import TestCase
from . models import Client, validate_pesel, validate_pesel_match_date_birth, validate_date_birth_above_18_today, provide_pesel_birthdate
from datetime import date
from django.core.exceptions import ValidationError


class ClientTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.client = Client.objects.create_user(first_name="Tom",
                                                 last_name="Furiolis",
                                                 email="test@gmail.com",
                                                 phone_number= "123456789",
                                                 pesel="89010100003",
                                                 date_birth=date(year=1989, month=1, day=1))
    
    def test_validation_pesel_(self):
        self.assertTrue(validate_pesel(self.client.pesel))

        self.client.pesel = "79010100004"
        self.assertTrue(validate_pesel(self.client.pesel))
        self.client.pesel = "89310100002"
        self.assertTrue(validate_pesel(self.client.pesel))
        self.client.pesel = "66410100006"
        self.assertTrue(validate_pesel(self.client.pesel))
        self.client.pesel = "89110100006"
        self.assertTrue(validate_pesel(self.client.pesel))
        self.client.pesel = "89010400004"
        self.assertTrue(validate_pesel(self.client.pesel))


        self.client.pesel = "79010100008"
        self.assertFalse(validate_pesel(self.client.pesel))
        with self.assertRaises(ValidationError):
            self.client.clean()
        self.client.pesel = "89310100004"
        self.assertFalse(validate_pesel(self.client.pesel))
        with self.assertRaises(ValidationError):
            self.client.clean()
        self.client.pesel = "66410100007"
        self.assertFalse(validate_pesel(self.client.pesel))
        with self.assertRaises(ValidationError):
            self.client.clean()
        self.client.pesel = "89110100003"
        self.assertFalse(validate_pesel(self.client.pesel))
        with self.assertRaises(ValidationError):
            self.client.clean()
        self.client.pesel = "89010400002"
        self.assertFalse(validate_pesel(self.client.pesel))
        with self.assertRaises(ValidationError):
            self.client.clean()


    def test_validation_pesel_match_date_birth(self):
        self.assertTrue(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing different year but same century
        self.client.pesel = "79010100004"
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
        with self.assertRaises(ValidationError):
            self.client.clean()

        # testing different century only
        self.client.pesel = "89310100002"
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
        with self.assertRaises(ValidationError):
            self.client.clean()

        # testing both above
        self.client.pesel = "66410100006"
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
        with self.assertRaises(ValidationError):
            self.client.clean()

        # testing different month
        self.client.pesel = "89110100006"
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
        with self.assertRaises(ValidationError):
            self.client.clean()

        # testing different day
        self.client.pesel = "89010400004"
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
        with self.assertRaises(ValidationError):
            self.client.clean()

    def test_validation_user_has_proper_age(self):
        self.assertTrue(validate_date_birth_above_18_today(self.client.date_birth))

        self.client.date_birth = date(year=2007, month=12, day=25)
        self.assertFalse(validate_date_birth_above_18_today(self.client.date_birth))
        # with self.assertRaises(ValidationError):
        #     self.client.clean()

class PeselProviderTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.pesel, cls.birth_date = provide_pesel_birthdate()
        print(cls.pesel)
        print(cls.birth_date)

    def test_provide_pesel(self):
        self.assertTrue(validate_pesel(self.pesel))

    def test_provide_birhtdate_match_pesel(self):
        self.assertTrue(validate_pesel_match_date_birth(self.pesel, self.birth_date))

    def test_date_birth_above_18(self):
        self.assertTrue(validate_date_birth_above_18_today(self.birth_date))

