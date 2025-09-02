from django.test import TestCase
from . models import Client
from datetime import date
from .models import validate_pesel, validate_pesel_match_date_birth


class ClientTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create_user(first_name="Tom",
                                                 last_name="Furiolis",
                                                 email="somemail@gmail.com",
                                                 phone_number= "123456789",
                                                 pesel=89010100003,
                                                 date_birth=date(year=1989, month=1, day=1))
    
    def test_validation_pesel_(self):
        self.assertTrue(validate_pesel(self.client.pesel))

        self.client.pesel = 89010100001
        self.assertFalse(validate_pesel(self.client.pesel))

    def test_validation_pesel_match_date_birth(self):
        self.assertTrue(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing different year but same century
        self.client.pesel = 79010100003
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing different century only
        self.client.pesel = 89310100003
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing both above
        self.client.pesel = 66410100003
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing different month
        self.client.pesel = 89110100003
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))

        # testing different day
        self.client.pesel = 89010400003
        self.assertFalse(validate_pesel_match_date_birth(self.client.pesel, self.client.date_birth))
