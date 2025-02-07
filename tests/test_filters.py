from django.test import TestCase
from inventory.filters import *
from inventory.models import *

class ItemFilterTest(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.unit = Unit.objects.create(name='Sample Unit')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.item1 = Item.objects.create(name='Item1', unit=self.unit, added_by=self.user, vendor='Vendor1')
        self.item2 = Item.objects.create(name='Item2', unit=self.unit, added_by=self.user, vendor='Vendor2')

    def test_item_filter(self):
        # Prepare filter data
        filter_data = {
            'name': 'Item1',
            'date_added': '2023-01-01',
            'expiration_date1': '2023-02-01',
            'expiration_date2': '2023-02-28',
            'vendor': 'Vendor1',
            'added_by': 'testuser',
            'unit': 'Sample Unit',
        }

        # Create the filter with the filter data
        item_filter = ItemFilter(data=filter_data, queryset=Item.objects.all())

        # Assert that the filter is valid
        self.assertTrue(item_filter.is_valid())

        # Apply the filter to the queryset
        filtered_items = item_filter.qs

        # Perform assertions based on your specific data and filter criteria
        # ...

    def test_invalid_item_filter(self):
        # Prepare invalid filter data
        invalid_filter_data = {
            'name': 'NonexistentItem',
            'date_added': 'invalid_date_format',
            # Add more invalid filter criteria as needed
            # ...
        }

        # Create the filter with the invalid filter data
        item_filter = ItemFilter(data=invalid_filter_data, queryset=Item.objects.all())

        # Assert that the filter is not valid
        self.assertFalse(item_filter.is_valid())

        # Additional assertions if needed
        # ...

class RecordFilterTest(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.unit = Unit.objects.create(name='Sample Unit')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.item = Item.objects.create(name='SampleItem', unit=self.unit, added_by=self.user, vendor='SampleVendor')
        self.record1 = Record.objects.create(item=self.item, unit=self.unit, department_issued_to='Department1', quantity=5, issued_by=self.user)
        self.record2 = Record.objects.create(item=self.item, unit=self.unit, department_issued_to='Department2', quantity=10, issued_by=self.user)

    def test_record_filter(self):
        # Prepare filter data
        filter_data = {
            'date_issued': '2023-01-01',
            'item': 'SampleItem',
            'unit': 'Sample Unit',
            'vendor': 'SampleVendor',
            'department_issued_to': 'Department1',
            'quantity': 5,
            'issued_by': 'testuser',
            'date_added1': '2023-02-01',
            'date_added2': '2023-02-28',
        }

        # Create the filter with the filter data
        record_filter = RecordFilter(data=filter_data, queryset=Record.objects.all())

        # Assert that the filter is valid
        self.assertTrue(record_filter.is_valid())

        # Apply the filter to the queryset
        filtered_records = record_filter.qs

        # Perform assertions based on your specific data and filter criteria
        # ...

    def test_invalid_record_filter(self):
        # Prepare invalid filter data
        invalid_filter_data = {
            'date_issued': 'invalid_date_format',
            'item': 'NonexistentItem',
            'unit': 'NonexistentUnit',
            'vendor': 'NonexistentVendor',
            'department_issued_to': 'NonexistentDepartment',
            'quantity': -5,  # Invalid negative quantity
        }

        # Create the filter with the invalid filter data
        record_filter = RecordFilter(data=invalid_filter_data, queryset=Record.objects.all())

        # Assert that the filter is not valid
        self.assertFalse(record_filter.is_valid())

  