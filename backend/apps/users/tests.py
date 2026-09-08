from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_student_user(self):
        user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.assertEqual(user.username, 'teststudent')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_password('Password123!'))

    def test_create_instructor_user(self):
        user = User.objects.create_user(
            username='testinstructor',
            email='instructor@example.com',
            password='Password123!',
            role=User.Role.INSTRUCTOR
        )
        self.assertEqual(user.role, User.Role.INSTRUCTOR)
