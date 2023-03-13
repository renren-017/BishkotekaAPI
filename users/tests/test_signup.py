from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser, Customer, Organization
from events.models import Category


class RegistrationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Category.objects.create(title='Charity')
        Category.objects.create(title='Some other charity')

    def test_customer_registration(self):
        """
        Ensure we can register a new customer user.
        """
        url = reverse('customer-signup')
        data = {
            'username': "renee",
            'email': 'customer@test.com',
            'password': 'testpassword1',
            'password2': 'testpassword1',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'interests_ids': [1, 2]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'customer@test.com')
        self.assertFalse(CustomUser.objects.get().is_active)

    def test_organization_registration(self):
        """
        Ensure we can register a new organization user.
        """
        url = reverse('organization-signup')
        data = {
            'email': 'org@test.com',
            'password': 'testpassword1',
            'password2': 'testpassword1',
            'name': 'Test Organization',
            'description': 'Test description',
            'type': 'Charity'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'org@test.com')
        self.assertFalse(CustomUser.objects.get().is_active)
