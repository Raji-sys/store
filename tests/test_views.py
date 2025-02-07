from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from inventory.models import *
from inventory.views import *
from inventory.forms import *


class InventoryViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some test data (adjust as needed)
        for i in range(20):
            Item.objects.create(name=f'Test Item {i}', unit_price=10, total_purchased_quantity=10, added_by=self.user)

            Record.objects.create(item=Item.objects.get(name=f'Test Item {i}'), quantity=5, issued_by=self.user)

        # Create a request factory for testing views
        self.factory = RequestFactory()

    def test_custom_login_view(self):
        # Test if the custom login view redirects authenticated users
        request = self.factory.get('/login/')
        request.user = self.user
        response = CustomLoginView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # 302 is the status code for a redirect

    def test_index_view(self):
        # Test if the index view is accessible to authenticated users
        request = self.factory.get('/index/')
        request.user = self.user
        response = index(request)
        self.assertEqual(response.status_code, 200)  # 200 is the status code for a successful HTTP request


    def test_worth_view(self):
        # Test if the worth view is accessible to superusers
        self.user.is_superuser = True
        self.user.save()

        request = self.factory.get('/worth/')
        request.user = self.user
        response = worth(request)
        self.assertEqual(response.status_code, 200)


    def test_create_item_view(self):
        # Test if the create_item view is accessible to authenticated users
        request = self.factory.get('/create_item/')
        request.user = self.user
        response = create_item(request)
        self.assertEqual(response.status_code, 200)


    def test_create_record_view(self):
        # Test if the create_record view is accessible to authenticated users
        request = self.factory.get('/create_record/')
        request.user = self.user
        response = create_record(request)
        self.assertEqual(response.status_code, 200)


    def test_get_items_for_unit_view(self):
        # Create a test user
        user = User.objects.create_user(username='testuser123', password='testpassword')

        # Log in the test user
        self.client.login(username='testuser123', password='testpassword')

        # Create a request with the logged-in user
        request = self.factory.get('/get_items_for_unit/', {'unit_id': 1})
        request.user = user

        # Ensure that the view is accessible and returns the expected response
        response = get_items_for_unit(request)
        self.assertEqual(response.status_code, 200)


class PDFViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some test data (adjust as needed)
        for i in range(20):
            Item.objects.create(name=f'Test Item {i}', unit_price=10, total_purchased_quantity=10, added_by=self.user)

            Record.objects.create(item=Item.objects.get(name=f'Test Item {i}'), quantity=5, issued_by=self.user)

        # Create a request factory for testing views
        self.factory = RequestFactory()

    def test_item_pdf_view(self):
        # Test if the item_pdf view is accessible to authenticated users
        request = self.factory.get('/item_pdf/')
        request.user = self.user
        response = item_pdf(request)
        self.assertEqual(response.status_code, 200)


    def test_record_pdf_view(self):
        # Test if the record_pdf view is accessible to authenticated users
        request = self.factory.get('/record_pdf/')
        request.user = self.user
        response = record_pdf(request)
        self.assertEqual(response.status_code, 200)

