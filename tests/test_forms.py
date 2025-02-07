from django.test import TestCase
from inventory.forms import *
from inventory.models import *


class ItemFormTest(TestCase):
    def test_valid_item_form(self):
        # Create a sample unit for the form
        unit = Unit.objects.create(name='Sample Unit')
        # Prepare valid form data
        form_data = {
            'name': 'Sample Item',
            'vendor': 'Sample Vendor',
            'unit': unit.id,
            'unit_price': 10.0,
            'expiration_date': '2023-12-31',
            'total_purchased_quantity': 20,
        }
        # Create the form with the valid data
        form = ItemForm(data=form_data)

        # Assert that the form is valid
        self.assertTrue(form.is_valid())

        # Save the form to create an Item object
        item = form.save()

        # Assert that the Item was saved successfully
        self.assertIsNotNone(item)

    def test_invalid_item_form(self):
        # Prepare invalid form data (missing required fields)
        invalid_form_data = {}

        # Create the form with the invalid data
        form = ItemForm(data=invalid_form_data)

        # Assert that the form is not valid
        self.assertFalse(form.is_valid())


# class RecordFormTest(TestCase):
#     def setUp(self):
#         # Create a sample unit for the form
#         self.unit = Unit.objects.create(name='Sample Unit')

#         # Create a sample item for the form
#         self.item = Item.objects.create(
#             name='Sample Item',
#             unit=self.unit,
#             total_purchased_quantity=50,
#         )

#     def test_valid_record_form(self):
#         # Prepare valid form data
#         form_data = {
#             'unit': self.unit.id,
#             'item': self.item.id,
#             'department_issued_to': 'ACCOUNT',
#             'quantity': 10,
#         }

#         # Create the form with the valid data
#         form = RecordForm(data=form_data)
#         print(form.errors)
#         # Assert that the form is valid
#         self.assertTrue(form.is_valid())

#         # Save the form to create a Record object
#         record = form.save()

#         # Assert that the Record was saved successfully
#         self.assertIsNotNone(record)

#     def test_invalid_record_form(self):
#         # Prepare invalid form data (missing required fields)
#         invalid_form_data = {}

#         # Create the form with the invalid data
#         form = RecordForm(data=invalid_form_data)

#         # Assert that the form is not valid
#         self.assertFalse(form.is_valid())

class RecordFormTest(TestCase):
    def setUp(self):
        # Create necessary instances for testing
        self.unit = Unit.objects.create(name='Test Unit')
        self.item = Item.objects.create(
            name='Test Item',
            unit=self.unit,
            total_purchased_quantity=10,
        )
        self.user = User.objects.create(username='test_user')

    def test_valid_form(self):
        data = {
            'unit': self.unit.id,
            'item': self.item.id,
            'department_issued_to': 'CATERING',  # Replace with the actual department choice
            'quantity': 5,
        }
        form = RecordForm(data=data)
        self.assertTrue(form.is_valid())

        # Check if the balance is updated after saving the record
        form.save()
        self.assertEqual(self.item.current_balance, 5)

    def test_negative_quantity(self):
        data = {
            'unit': self.unit.id,
            'item': self.item.id,
            'department_issued_to': 'CATERING',
            'quantity': -5,
        }
        form = RecordForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_insufficient_balance(self):
        data = {
            'unit': self.unit.id,
            'item': self.item.id,
            'department_issued_to': 'CATERING',
            'quantity': 15,
        }
        form = RecordForm(data=data)

        # Print the form errors and cleaned data for debugging
        print("Form errors:", form.errors)
        print("Cleaned data:", form.cleaned_data)

        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertRegex(str(form.errors['quantity'][0]), 'not allowed.')

        # Ensure that the balance is not updated after a failed form submission
        self.assertEqual(self.item.current_balance, 10)