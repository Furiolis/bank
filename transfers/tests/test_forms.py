from django.test import TestCase
from django.core.exceptions import ValidationError

from banking.models import Client, Account
from transfers.models import Transfer
from transfers.forms import TransferFormBase, ExternalTransferForm, InternalTransferForm
from banking.some_utility import provide_pesel_birthdate


class TestTransferForms(TestCase):
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

        cls.data_external = {"account": cls.account_12, 
                 "money":100, 
                 "connected_account_number":cls.account_22.number, 
                 "connected_account_name":"some client", 
                 "title":"some title"}

        cls.data_internal = {"account": cls.account_12, 
                 "money":200, 
                 "account_internal":cls.account_13, 
                 "title":"different title"}

    def test_form_provide_correct_accounts_list(self):
        form = TransferFormBase(owner=self.client_1)

        self.assertQuerySetEqual(form.fields["account"].queryset, [self.account_12,self.account_13,self.account_11])
        self.assertNotIn(self.account_14, form.fields["account"].queryset)

    def test_external_form_creates_two_transfers_with_correct_fields(self):
        form = ExternalTransferForm(owner=self.client_1, data={**self.data_external})
        self.assertTrue(form.is_valid())
        form.save()

        transfer_1, transfer_2 = Transfer.objects.all()

        self.assertEqual(transfer_1.connected_account_number, transfer_2.account.number)
        self.assertEqual(transfer_2.connected_account_number, transfer_1.account.number)

        self.assertEqual(transfer_1.title, transfer_2.title)
        self.assertEqual(transfer_1.title, "some title")

        self.assertEqual(transfer_1.money, -transfer_2.money)

        self.account_12.refresh_from_db()
        self.assertEqual(self.account_12.money, 2900)

        self.account_22.refresh_from_db()
        self.assertEqual(self.account_22.money, 3100)

        self.assertEqual(transfer_1.connected_account_name, "some client")
        self.assertEqual(transfer_2.connected_account_name, self.account_12.owner.full_name)

    def test_internal_form_creates_two_transfers_with_correct_fields(self):
        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal})
        self.assertTrue(form.is_valid())
        form.save()

        transfer_1, transfer_2 = Transfer.objects.all()

        self.assertEqual(transfer_1.connected_account_number, transfer_2.account.number)
        self.assertEqual(transfer_2.connected_account_number, transfer_1.account.number)

        self.assertEqual(transfer_1.title, transfer_2.title)
        self.assertEqual(transfer_1.title, "different title")

        self.assertEqual(transfer_1.money, -transfer_2.money)

        self.account_12.refresh_from_db()
        self.assertEqual(self.account_12.money, 2800)

        self.account_13.refresh_from_db()
        self.assertEqual(self.account_13.money, 2200)

        self.assertEqual(transfer_1.connected_account_name, transfer_2.connected_account_name)
        self.assertEqual(transfer_2.connected_account_name, self.account_12.owner.full_name)

    def test_failed_transfer_not_move_money(self):
        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "money":-1000000})
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError) as error:
            form.save()
        self.assertEqual(str(error.exception), "Transfer amount must be positive")

        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "money":0})
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError) as error:
            form.save()
        self.assertEqual(str(error.exception), "Transfer amount must be positive")

        self.account_12.refresh_from_db()
        self.account_21.refresh_from_db()
        self.account_22.refresh_from_db()
        self.account_13.refresh_from_db()
        self.assertEqual(self.account_12.money, 3000)
        self.assertEqual(self.account_21.money, 1000)
        self.assertEqual(self.account_22.money, 3000)
        self.assertEqual(self.account_13.money, 2000)
        self.assertEqual(Transfer.objects.count(), 0)

    def test_failed_transfer_from_or_to_account_not_owned(self):
        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "account":self.account_22})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "account", "Select a valid choice. That choice is not one of the available choices.")

        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "account_internal":self.account_21})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "account_internal", "Select a valid choice. That choice is not one of the available choices.")

        form = ExternalTransferForm(owner=self.client_2, data={**self.data_external})
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "account", "Select a valid choice. That choice is not one of the available choices.")
        
        self.assertEqual(Transfer.objects.count(), 0)

    def test_failed_transfer_to_same_account(self):
        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "account_internal":self.account_12})
        self.assertFalse(form.is_valid())

        form = ExternalTransferForm(owner=self.client_1, data={**self.data_external, "connected_account_number":self.account_12})
        self.assertFalse(form.is_valid())

        self.assertEqual(Transfer.objects.count(), 0)

    def test_failed_transfer_to_nonexistent_account(self):
        form = ExternalTransferForm(owner=self.client_1, data={**self.data_external, "connected_account_number":"999999"})
        self.assertFalse(form.is_valid())
        self.assertEqual(Transfer.objects.count(), 0)

    def test_failed_transfer_when_insufficient_funds(self):
        form = InternalTransferForm(owner=self.client_1, data={**self.data_internal, "money":10000})
        self.assertFalse(form.is_valid())

        form = ExternalTransferForm(owner=self.client_1, data={**self.data_external, "money":10000})
        self.assertFalse(form.is_valid())

        self.assertEqual(Transfer.objects.count(), 0)


        # cls.data_external = {"account": cls.account_12, 
        #          "money":100, 
        #          "connected_account_number":cls.account_22.number, 
        #          "connected_account_name":"some client", 
        #          "title":"some title"}

        # cls.data_internal = {"account": cls.account_12, 
        #          "money":200, 
        #          "account_internal":cls.account_13, 
        #          "title":"different title"}

        # cls.account_11 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.PERSONAL, money=1000)
        # cls.account_12 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.SAVING, money=3000)
        # cls.account_13 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.CREDIT, money=2000)
        # cls.account_14 = Account.objects.create(owner=cls.client_1, type_account=Account.Type.CREDIT, money=0)

        # cls.account_21 = Account.objects.create(owner=cls.client_2, type_account=Account.Type.PERSONAL, money=1000)
        # cls.account_22 = Account.objects.create(owner=cls.client_2, type_account=Account.Type.SAVING, money=3000)