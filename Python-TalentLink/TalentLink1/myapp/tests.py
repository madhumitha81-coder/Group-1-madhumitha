from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileSignalTest(TestCase):
    def test_profile_created(self):
        u = User.objects.create_user(username='tester', password='pass')
        self.assertTrue(hasattr(u, 'profile'))
        self.assertEqual(u.profile.user.username, 'tester')
