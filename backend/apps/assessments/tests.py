from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.courses.models import Course, Module, Lesson
from apps.assessments.models import Quiz, Question, Option, QuizAttempt, StudentAnswer

User = get_user_model()


class AssessmentSchemaTest(TestCase):
    def setUp(self):
        # Instructor & Course Hierarchy
        self.instructor = User.objects.create_user(
            username='instructor_jane',
            email='jane@example.com',
            password='Password123!',
            role=User.Role.INSTRUCTOR
        )
        self.course = Course.objects.create(
            title='Database Engineering',
            slug='db-eng',
            description='Advanced SQL & Relational Models',
            category='Computer Science',
            instructor=self.instructor,
            is_published=True
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1: Relational Normal Forms',
            order=1
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1.1: 3NF Decompositions',
            duration_seconds=900,
            order=1
        )

        # Student
        self.student = User.objects.create_user(
            username='student_alice',
            email='alice@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )

        # Quiz
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Normal Forms Assessment',
            time_limit_minutes=20,
            passing_score=75
        )

    def test_quiz_creation_and_lesson_onetoone(self):
        """Test Quiz model creation and 1-to-1 constraint with Lesson [LMS-QZ-01]."""
        self.assertEqual(str(self.quiz), 'Normal Forms Assessment')
        self.assertEqual(self.quiz.lesson, self.lesson)
        self.assertEqual(self.quiz.time_limit_minutes, 20)
        self.assertEqual(self.quiz.passing_score, 75)
        self.assertIsNotNone(self.quiz.created_at)

        # Enforce OneToOne: cannot attach a second quiz to the same lesson
        with self.assertRaises(IntegrityError):
            Quiz.objects.create(
                lesson=self.lesson,
                title='Duplicate Quiz for Same Lesson',
                time_limit_minutes=10,
                passing_score=60
            )

    def test_question_types_and_points(self):
        """Test Question model types (MCQ, TRUE_FALSE) and points [LMS-QZ-01]."""
        q_mcq = Question.objects.create(
            quiz=self.quiz,
            question_text='Which normal form eliminates transitive functional dependencies?',
            question_type=Question.Type.MCQ,
            points=2
        )
        q_tf = Question.objects.create(
            quiz=self.quiz,
            question_text='Every relation in BCNF is also in 3NF.',
            question_type=Question.Type.TRUE_FALSE,
            points=1
        )

        self.assertEqual(q_mcq.question_type, 'MCQ')
        self.assertEqual(q_tf.question_type, 'TRUE_FALSE')
        self.assertEqual(self.quiz.questions.count(), 2)
        self.assertEqual(self.quiz.total_points, 3)

    def test_option_creation_and_correctness(self):
        """Test Option model linked to Question with is_correct boolean [LMS-QZ-01]."""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='What is the primary key of a 1NF table?',
            question_type=Question.Type.MCQ,
            points=1
        )
        opt_wrong1 = Option.objects.create(
            question=question,
            option_text='Any non-prime attribute',
            is_correct=False
        )
        opt_wrong2 = Option.objects.create(
            question=question,
            option_text='A nullable attribute',
            is_correct=False
        )
        opt_correct = Option.objects.create(
            question=question,
            option_text='A minimal candidate key',
            is_correct=True
        )

        self.assertEqual(question.options.count(), 3)
        self.assertFalse(opt_wrong1.is_correct)
        self.assertFalse(opt_wrong2.is_correct)
        self.assertTrue(opt_correct.is_correct)
        self.assertEqual(question.correct_option, opt_correct)

    def test_quiz_attempt_and_student_answer_lifecycle(self):
        """Test QuizAttempt and StudentAnswer creation with timestamps [LMS-QZ-01]."""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Select the 3NF definition.',
            question_type=Question.Type.MCQ,
            points=1
        )
        option = Option.objects.create(
            question=question,
            option_text='No non-prime attribute depends on another non-prime attribute.',
            is_correct=True
        )

        # Create Quiz Attempt
        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=self.quiz,
            total_score=0,
            is_passed=False
        )
        self.assertIsNotNone(attempt.started_at)
        self.assertIsNone(attempt.completed_at)

        # Record Student Answer with timestamp
        answer = StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=option
        )
        self.assertEqual(answer.attempt, attempt)
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.selected_option, option)
        self.assertIsNotNone(answer.answered_at)

    def test_unique_constraint_on_attempt_and_question(self):
        """Test unique constraint on (attempt, question) in StudentAnswer [LMS-QZ-01]."""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Identify the lossless-join property.',
            question_type=Question.Type.MCQ,
            points=1
        )
        opt1 = Option.objects.create(question=question, option_text='Property A', is_correct=True)
        opt2 = Option.objects.create(question=question, option_text='Property B', is_correct=False)

        attempt = QuizAttempt.objects.create(student=self.student, quiz=self.quiz)

        # First answer succeeds
        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=opt1
        )

        # Second answer to the SAME question within the SAME attempt must fail with IntegrityError
        with self.assertRaises(IntegrityError):
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=opt2
            )

    def test_3nf_decoupling_eliminates_duplication(self):
        """Verify 3NF schema eliminates duplication of questions and options across multiple attempts."""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Is BCNF strictly stronger than 3NF?',
            question_type=Question.Type.TRUE_FALSE,
            points=1
        )
        opt_true = Option.objects.create(question=question, option_text='True', is_correct=True)

        student2 = User.objects.create_user(
            username='student_bob',
            email='bob@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )

        attempt1 = QuizAttempt.objects.create(student=self.student, quiz=self.quiz)
        attempt2 = QuizAttempt.objects.create(student=student2, quiz=self.quiz)

        # Both attempts reference the SAME normalized Question and Option foreign keys
        ans1 = StudentAnswer.objects.create(attempt=attempt1, question=question, selected_option=opt_true)
        ans2 = StudentAnswer.objects.create(attempt=attempt2, question=question, selected_option=opt_true)

        self.assertEqual(ans1.question.id, ans2.question.id)
        self.assertEqual(ans1.selected_option.id, ans2.selected_option.id)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Option.objects.count(), 1)
