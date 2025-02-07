from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class InventoryViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

# For test_index_view
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to login

    # For test_unauthenticated_access
    def test_unauthenticated_access(self):
        urls = ['create_item', 'create_record', 'record', 'get_items_for_unit', 'list', 'report', 'item_report', 'record_report', 'worth']
        for url in urls:
            response = self.client.get(reverse(url))
            self.assertRedirects(response, f'/login/?next={reverse(url)}')

    def test_signin_view(self):
        # Test the signin view
        url = reverse('signin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_create_item_view(self):
        # Test the create_item view
        url = reverse('create_item')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login when not authenticated

        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/create_item.html')
   
    def test_create_record_view(self):
        # Test the create_item view
        url = reverse('create_record')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login when not authenticated

        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/create_record.html')