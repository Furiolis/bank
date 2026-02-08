from django.test import TestCase
from django.core.exceptions import ValidationError

from datetime import date

from . models import Client, validate_pesel, validate_date_birth_above_18_today
from . forms import NewClientForm
from .some_utility import provide_pesel_birthdate



class ClientTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client.objects.create_user(first_name="Tom",
                                                 last_name="Furiolis",
                                                 email="test@gmail.com",
                                                 phone_number= "123456789",
                                                 pesel="89010100003",
                                                 date_birth=date(year=1989, month=1, day=1))
        
    def test_validation_correct_pesel(self):
        validate_pesel(self.client.pesel)

        self.client.pesel = "79010100004"
        validate_pesel(self.client.pesel)
        self.client.pesel = "89310100002"
        validate_pesel(self.client.pesel)
        self.client.pesel = "66410100006"
        validate_pesel(self.client.pesel)
        self.client.pesel = "89110100006"
        validate_pesel(self.client.pesel)
        self.client.pesel = "89010400004"
        validate_pesel(self.client.pesel)

    def test_validation_incorrect_pesel(self):
        self.client.pesel = "79010100008"
        with self.assertRaises(ValidationError):
            validate_pesel(self.client.pesel)
        self.client.pesel = "89310100004"
        with self.assertRaises(ValidationError):
            validate_pesel(self.client.pesel)
        self.client.pesel = "66410100007"
        with self.assertRaises(ValidationError):
            validate_pesel(self.client.pesel)
        self.client.pesel = "89110100003"
        with self.assertRaises(ValidationError):
            validate_pesel(self.client.pesel)
        self.client.pesel = "89010400002"
        with self.assertRaises(ValidationError):
            validate_pesel(self.client.pesel)

    def test_validation_user_has_proper_age(self):
        validate_date_birth_above_18_today(self.client.date_birth)

        self.client.date_birth = date(year=2009, month=12, day=25)
        with self.assertRaises(ValidationError):
            validate_date_birth_above_18_today(self.client.date_birth)


class FormTest(TestCase):
    def setUp(self):
        self.data = {
            "first_name": "Tom",
            "last_name": "Furiolis",
            "email": "test@gmail.com",
            "phone_number":  "123456789",
            "pesel": "89010100003",
            "date_birth": "1989-01-01",
            "password1":"pass123word",
            "password2":"pass123word"}

    def test_validation_pesel_match_date_birth(self):
        form = NewClientForm(data = self.data)
        # print(form.errors)
        self.assertTrue(form.is_valid())

        # testing different year but same century
        self.data["pesel"] = "79010100004"
        form = NewClientForm(data = self.data)
        self.assertFalse(form.is_valid())

        # testing different century only
        self.data["pesel"]  = "89310100002"
        form = NewClientForm(data = self.data)
        self.assertFalse(form.is_valid())

        # testing both above
        self.data["pesel"]  = "66410100006"
        form = NewClientForm(data = self.data)
        self.assertFalse(form.is_valid())

        # testing different month
        self.data["pesel"] = "89110100006"
        form = NewClientForm(data = self.data)
        self.assertFalse(form.is_valid())

        # testing different day
        self.data["pesel"] = "89010400004"
        form = NewClientForm(data = self.data)
        self.assertFalse(form.is_valid())


class PeselProviderTest(TestCase):
    @classmethod
    def setUp(self):
        self.pesel, self.birth_date = provide_pesel_birthdate()

    def test_provide_pesel(self):
        validate_pesel(self.pesel)

    def test_provide_birhtdate_match_pesel(self):
        client = Client.objects.create_user(first_name="Tom",
                                                 last_name="Furiolis",
                                                 email="test@gmail.com",
                                                 phone_number= "123456789",
                                                 pesel= self.pesel,
                                                 date_birth=self.birth_date)
        client.clean()

    def test_date_birth_above_18(self):
        validate_date_birth_above_18_today(self.birth_date)

