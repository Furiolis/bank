from django.test import SimpleTestCase, TestCase
from django.core.exceptions import ValidationError

from datetime import date

from banking.some_utility import provide_pesel_birthdate
from banking.validators import validate_pesel, validate_date_birth_above_18_today, validate_pesel_match_birth_date


class PeselValidatorTests(SimpleTestCase):

    def test_correct_pesel(self):
        correct_pesel = "89010100003"
        validate_pesel(correct_pesel)

        correct_pesel = "79010100004"
        validate_pesel(correct_pesel)

        correct_pesel = "89310100002"
        validate_pesel(correct_pesel)

        correct_pesel = "66410100006"
        validate_pesel(correct_pesel)

        correct_pesel = "89110100006"
        validate_pesel(correct_pesel)

        correct_pesel = "89010400004"
        validate_pesel(correct_pesel)

        correct_pesel = "00010100008"
        validate_pesel(correct_pesel)

    def test_incorrect_pesel(self):
        incorrect_pesel = "79010100008"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "invalid")

        incorrect_pesel = "89310100004"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "invalid")

        incorrect_pesel = "66410100007"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "invalid")

        incorrect_pesel = "89110100003"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "invalid")

        incorrect_pesel = "89010400002"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "invalid")

        incorrect_pesel = "8901010s003"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "consist")

        incorrect_pesel = "8901010003"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "consist")

        incorrect_pesel = "890101000003"
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "consist")

        incorrect_pesel = ""
        with self.assertRaises(ValidationError) as error:
            validate_pesel(incorrect_pesel)
        self.assertEqual(error.exception.code, "consist")

class TestValidatorAgeAboveRequired18(SimpleTestCase):

    def test_ages_passing(self):
        date_passing = date(year = 1900, month=1, day=1)
        validate_date_birth_above_18_today(date_passing)
        date_passing = date(year = 2000, month=5, day=31)
        validate_date_birth_above_18_today(date_passing)
        date_passing = date(year = 2008, month=7, day=31)
        validate_date_birth_above_18_today(date_passing)

    def test_ages_not_passing(self):
        date_not_passing = date(year = 2015, month=1, day=1)
        with self.assertRaises(ValidationError):
            validate_date_birth_above_18_today(date_not_passing)
        date_not_passing = date(year = 2010, month=12, day=31)
        with self.assertRaises(ValidationError):
            validate_date_birth_above_18_today(date_not_passing)
        date_not_passing = date(year = 2008, month=12, day=1)
        with self.assertRaises(ValidationError):
            validate_date_birth_above_18_today(date_not_passing)


class TestValidatorPeselMatchBirthDate(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date_birth_1 = date(year = 1989, month = 1, day = 1)
        cls.pesel_1 = "89010100003"

        cls.date_birth_2 = date(year = 1902, month = 10, day = 13)
        cls.pesel_2 = "02101300007" 

        cls.date_birth_3 = date(year = 1925, month = 9, day = 7)
        cls.pesel_3 = "25090700001" 

        cls.date_birth_4 = date(year = 1994, month = 8, day = 12)
        cls.pesel_4 = "94081200000" 

        cls.date_birth_5 = date(year = 1959, month = 10, day = 22)
        cls.pesel_5 = "59102200003" 

    def test_validation_pesel_match_date_birth(self):
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_1, self.date_birth_1))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_2, self.date_birth_2))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_3, self.date_birth_3))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_4, self.date_birth_4))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_5, self.date_birth_5))

    def test_validation_pesel_not_match_date_birth(self):

        # testing different year but same century
        not_match_pesel = "79010100004"
        validate_pesel(not_match_pesel)
        self.assertFalse(validate_pesel_match_birth_date(not_match_pesel, self.date_birth_1))

        # testing different century only
        not_match_pesel  = "89310100002"
        validate_pesel(not_match_pesel)
        self.assertFalse(validate_pesel_match_birth_date(not_match_pesel, self.date_birth_1))

        # testing both above
        not_match_pesel  = "66410100006"
        validate_pesel(not_match_pesel)
        self.assertFalse(validate_pesel_match_birth_date(not_match_pesel, self.date_birth_1))

        # testing different month
        not_match_pesel = "89110100006"
        validate_pesel(not_match_pesel)
        self.assertFalse(validate_pesel_match_birth_date(not_match_pesel, self.date_birth_1))

        # testing different day
        not_match_pesel = "89010400004"
        validate_pesel(not_match_pesel)
        self.assertFalse(validate_pesel_match_birth_date(not_match_pesel, self.date_birth_1))

class PeselProviderTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pesel_1, cls.birth_date_1 = provide_pesel_birthdate()
        cls.pesel_2, cls.birth_date_2 = provide_pesel_birthdate()
        cls.pesel_3, cls.birth_date_3 = provide_pesel_birthdate()
        cls.pesel_4, cls.birth_date_4 = provide_pesel_birthdate()
        cls.pesel_5, cls.birth_date_5 = provide_pesel_birthdate()

    def test_provided_pesel_is_correct(self):
        validate_pesel(self.pesel_1)
        validate_pesel(self.pesel_2)
        validate_pesel(self.pesel_3)
        validate_pesel(self.pesel_4)
        validate_pesel(self.pesel_5)

    def test_provided_date_birth_above_18_today(self):
        validate_date_birth_above_18_today(self.birth_date_1)
        validate_date_birth_above_18_today(self.birth_date_2)
        validate_date_birth_above_18_today(self.birth_date_3)
        validate_date_birth_above_18_today(self.birth_date_4)
        validate_date_birth_above_18_today(self.birth_date_5)

    def test_provided_pesel_match_birth_date(self):
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_1, self.birth_date_1))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_2, self.birth_date_2))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_3, self.birth_date_3))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_4, self.birth_date_4))
        self.assertTrue(validate_pesel_match_birth_date(self.pesel_5, self.birth_date_5))
