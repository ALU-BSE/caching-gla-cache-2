from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Passenger, Rider
from django.core.exceptions import ValidationError

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', password='password123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class PassengerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='passenger@example.com', 
            password='password123',
            user_type='passenger'
        )

    def test_create_passenger(self):
        passenger = Passenger.objects.create(
            user=self.user,
            passenger_id='P12345',
            home_address='123 Test St'
        )
        self.assertEqual(passenger.user.email, 'passenger@example.com')
        self.assertEqual(passenger.passenger_id, 'P12345')

    def test_invalid_user_type_for_passenger(self):
        rider_user = User.objects.create_user(
            email='rider@example.com', 
            password='password123',
            user_type='rider'
        )
        with self.assertRaises(ValidationError):
            Passenger.objects.create(
                user=rider_user,
                passenger_id='P67890',
                home_address='456 Test St'
            )
