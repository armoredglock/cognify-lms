from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Lesson

User = get_user_model()


class CourseHierarchyTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='prof_smith',
            email='smith@univ.edu',
            password='Password123!',
            role=User.Role.INSTRUCTOR
        )
        self.course = Course.objects.create(
            title='Relational Database Management Systems',
            slug='rdbms-101',
            description='Comprehensive database systems course.',
            category='Computer Science',
            instructor=self.instructor,
            is_published=True
        )

    def test_course_creation(self):
        self.assertEqual(str(self.course), 'Relational Database Management Systems')
        self.assertEqual(self.course.instructor.username, 'prof_smith')

    def test_module_and_lesson_creation(self):
        module = Module.objects.create(
            course=self.course,
            title='Module 1: Relational Algebra',
            order=1
        )
        lesson = Lesson.objects.create(
            module=module,
            title='Lesson 1: Select and Project Operations',
            duration_seconds=600,
            transcript='Introduction to relational algebra unary operations.',
            order=1
        )
        self.assertEqual(module.course, self.course)
        self.assertEqual(lesson.module, module)
