import uuid
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from apps.courses.models import Course, Module, Lesson
from apps.assessments.models import Quiz, Question, Option, QuizAttempt, StudentAnswer
from services.exam_session import (
    start_quiz_session,
    is_session_active,
    clear_quiz_session,
    get_session_key,
    get_session_data,
    get_remaining_seconds,
    GRACE_PERIOD_SECONDS,
)

User = get_user_model()

TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-quiz-cache',
    }
}


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


@override_settings(CACHES=TEST_CACHES)
class TimedQuizSessionServiceTest(TestCase):
    """Unit tests for the Redis Timed Quiz Session Manager [LMS-QZ-02]."""

    def setUp(self):
        cache.clear()
        self.attempt_id = uuid.uuid4()
        self.quiz_id = uuid.uuid4()

    def tearDown(self):
        cache.clear()

    def test_session_key_pattern(self):
        """Verify Redis session key pattern matches quiz_session:{attempt_id} [LMS-QZ-02]."""
        key = get_session_key(self.attempt_id)
        self.assertEqual(key, f"quiz_session:{self.attempt_id}")

    def test_start_quiz_session_stores_ttl_and_metadata(self):
        """Test start_quiz_session writes session metadata to cache with buffer [LMS-QZ-02]."""
        session_data = start_quiz_session(
            attempt_id=self.attempt_id,
            quiz_id=self.quiz_id,
            duration_minutes=15,
            student_id=123
        )
        self.assertEqual(session_data['attempt_id'], str(self.attempt_id))
        self.assertEqual(session_data['quiz_id'], str(self.quiz_id))
        self.assertEqual(session_data['duration_minutes'], 15)
        self.assertEqual(session_data['grace_buffer_seconds'], GRACE_PERIOD_SECONDS)

        # Verify key exists in cache
        cached_data = get_session_data(self.attempt_id)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['quiz_id'], str(self.quiz_id))

    def test_is_session_active_positive(self):
        """Test active session returns True with remaining seconds > 0 [LMS-QZ-02]."""
        start_quiz_session(self.attempt_id, self.quiz_id, duration_minutes=10)
        is_active, remaining_seconds = is_session_active(self.attempt_id)

        self.assertTrue(is_active)
        self.assertGreater(remaining_seconds, 0)
        self.assertLessEqual(remaining_seconds, 600)
        self.assertGreater(get_remaining_seconds(self.attempt_id), 0)

    def test_is_session_active_expired(self):
        """Test when Redis key expires, is_session_active returns False and 0 remaining [LMS-QZ-02]."""
        start_quiz_session(self.attempt_id, self.quiz_id, duration_minutes=10)

        # Evict key from cache to simulate Redis TTL expiry
        cache.delete(get_session_key(self.attempt_id))

        is_active, remaining_seconds = is_session_active(self.attempt_id)
        self.assertFalse(is_active)
        self.assertEqual(remaining_seconds, 0)
        self.assertEqual(get_remaining_seconds(self.attempt_id), 0)

    def test_clear_quiz_session(self):
        """Test clearing session removes key from cache upon submission [LMS-QZ-02]."""
        start_quiz_session(self.attempt_id, self.quiz_id, duration_minutes=10)
        self.assertIsNotNone(get_session_data(self.attempt_id))

        clear_quiz_session(self.attempt_id)
        self.assertIsNone(get_session_data(self.attempt_id))
        is_active, remaining = is_session_active(self.attempt_id)
        self.assertFalse(is_active)


@override_settings(CACHES=TEST_CACHES)
class TimedQuizSessionAPITest(TestCase):
    """Integration tests for quiz session endpoints and submission TTL enforcement [LMS-QZ-02]."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        # Users
        self.instructor = User.objects.create_user(
            username='instructor_bob',
            email='bob@example.com',
            password='Password123!',
            role=User.Role.INSTRUCTOR
        )
        self.student = User.objects.create_user(
            username='student_carol',
            email='carol@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.other_student = User.objects.create_user(
            username='student_dan',
            email='dan@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )

        # Course hierarchy
        self.course = Course.objects.create(
            title='Algorithms',
            slug='algo-101',
            instructor=self.instructor,
            is_published=True
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson = Lesson.objects.create(module=self.module, title='Lesson 1', order=1)

        # Quiz with 15 minute limit
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Sorting Algorithms Quiz',
            time_limit_minutes=15,
            passing_score=50
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='Worst-case time complexity of QuickSort?',
            question_type=Question.Type.MCQ,
            points=1
        )
        self.option_correct = Option.objects.create(
            question=self.question,
            option_text='O(N^2)',
            is_correct=True
        )
        self.option_wrong = Option.objects.create(
            question=self.question,
            option_text='O(N)',
            is_correct=False
        )

    def tearDown(self):
        cache.clear()

    def test_unauthenticated_cannot_start_quiz(self):
        """Unauthenticated requests must be rejected with 401 Unauthorized [LMS-QZ-02]."""
        url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_start_quiz_creates_attempt_and_redis_session(self):
        """POST /quizzes/{id}/start/ creates attempt and registers Redis key with TTL [LMS-QZ-02]."""
        self.client.force_authenticate(user=self.student)
        url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attempt_id', response.data)
        self.assertIn('expires_at', response.data)
        self.assertEqual(response.data['duration_minutes'], 15)
        self.assertFalse(response.data['resumed'])

        attempt_id = response.data['attempt_id']
        key = get_session_key(attempt_id)
        cached_data = cache.get(key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['quiz_id'], str(self.quiz.id))

    def test_start_quiz_resumes_existing_active_session(self):
        """Calling start_quiz again for an active uncompleted attempt resumes the session [LMS-QZ-02]."""
        self.client.force_authenticate(user=self.student)
        url = f"/api/assessments/quizzes/{self.quiz.id}/start/"

        first_resp = self.client.post(url)
        self.assertEqual(first_resp.status_code, status.HTTP_201_CREATED)
        attempt_id = first_resp.data['attempt_id']

        # Second call resumes active attempt
        second_resp = self.client.post(url)
        self.assertEqual(second_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(second_resp.data['attempt_id'], attempt_id)
        self.assertTrue(second_resp.data['resumed'])
        self.assertGreater(second_resp.data['remaining_seconds'], 0)

    def test_get_quiz_session_countdown_status(self):
        """GET /attempts/{id}/session/ returns real-time countdown status [LMS-QZ-02]."""
        self.client.force_authenticate(user=self.student)
        start_url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        start_resp = self.client.post(start_url)
        attempt_id = start_resp.data['attempt_id']

        session_url = f"/api/assessments/attempts/{attempt_id}/session/"
        session_resp = self.client.get(session_url)

        self.assertEqual(session_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(session_resp.data['is_active'])
        self.assertFalse(session_resp.data['is_completed'])
        self.assertGreater(session_resp.data['remaining_seconds'], 0)

    def test_other_student_cannot_view_quiz_session(self):
        """Students cannot inspect or poll sessions belonging to other students [LMS-QZ-02]."""
        self.client.force_authenticate(user=self.student)
        start_url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        attempt_id = self.client.post(start_url).data['attempt_id']

        # Another student attempts to poll session
        self.client.force_authenticate(user=self.other_student)
        session_url = f"/api/assessments/attempts/{attempt_id}/session/"
        response = self.client.get(session_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_late_submission_rejected_after_redis_ttl_expiration(self):
        """
        Acceptance Criteria:
        Submissions sent after Redis TTL key expiration are automatically rejected with 400 Bad Request [LMS-QZ-02].
        """
        self.client.force_authenticate(user=self.student)
        start_url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        attempt_id = self.client.post(start_url).data['attempt_id']

        # Evict session from Redis (simulating TTL expiry)
        cache.delete(get_session_key(attempt_id))

        submit_url = f"/api/assessments/attempts/{attempt_id}/submit/"
        submit_payload = {
            'answers': [
                {'question_id': str(self.question.id), 'option_id': str(self.option_correct.id)}
            ]
        }
        submit_resp = self.client.post(submit_url, data=submit_payload, format='json')

        self.assertEqual(submit_resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', submit_resp.data)
        self.assertEqual(submit_resp.data['error'], 'Exam session has expired. Submission rejected.')

    def test_ontime_submission_succeeds_and_clears_redis_session(self):
        """Submitting on time computes grade and cleans up Redis session key [LMS-QZ-02, LMS-QZ-03]."""
        self.client.force_authenticate(user=self.student)
        start_url = f"/api/assessments/quizzes/{self.quiz.id}/start/"
        attempt_id = self.client.post(start_url).data['attempt_id']

        # Verify session is active
        key = get_session_key(attempt_id)
        self.assertIsNotNone(cache.get(key))

        submit_url = f"/api/assessments/attempts/{attempt_id}/submit/"
        submit_payload = {
            'answers': [
                {'question_id': str(self.question.id), 'option_id': str(self.option_correct.id)}
            ]
        }
        submit_resp = self.client.post(submit_url, data=submit_payload, format='json')

        self.assertEqual(submit_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_resp.data['score'], 100)
        self.assertTrue(submit_resp.data['is_passed'])

        # Redis key must be purged
        self.assertIsNone(cache.get(key))
