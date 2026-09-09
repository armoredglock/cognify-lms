# Agile Traceability Matrix — Cognify LMS

This document tracks every Functional Requirement (FR) to its assigned module owner, implementation files, and database entities.

---

## Traceability Mapping Table

| Requirement ID | Module | Primary Owner | Secondary Reviewer | Target File Paths | Database Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LMS-AUTH-01` | Auth & RBAC | @saanvi-singhal | @armoredglock | `backend/apps/users/` | `User` model, JWT token blacklisting |
| `LMS-CRS-02` | Course Hierarchy | @saanvi-singhal | @armoredglock | `backend/apps/courses/models.py` | `Course`, `Module`, `Lesson`, `Enrollment` |
| `LMS-CRS-03` | Course REST APIs | @saanvi-singhal | @armoredglock | `backend/apps/courses/views.py` | Serializers, Querysets, Permission classes |
| `LMS-CRS-04` | DB Indexes & Seed | @saanvi-singhal | @armoredglock | `backend/apps/courses/management/` | Indexes on category, foreign keys, seed script |
| `LMS-VID-01` | Redis Playback Cache | @BibekTripathy | @armoredglock | `backend/services/redis_cache.py` | Redis `video:user:{uid}:lesson:{lid}` |
| `LMS-VID-02` | Video Heartbeat API | @BibekTripathy | @armoredglock | `backend/apps/tracking/views.py` | High-frequency playback tick endpoint |
| `LMS-VID-03` | Redis-to-PG Sync | @BibekTripathy | @armoredglock | `backend/apps/tracking/services.py`| Batch write-behind sync to `LessonProgress` |
| `LMS-VID-04` | Progress Analytics | @BibekTripathy | @armoredglock | `backend/apps/tracking/views.py` | Aggregated student course completion % |
| `LMS-QZ-01` | Assessment Schema | @swatisaumya | @armoredglock | `backend/apps/assessments/models.py` | `Quiz`, `Question`, `Option`, `QuizAttempt` |
| `LMS-QZ-02` | Timed Session (TTL) | @swatisaumya | @armoredglock | `backend/services/exam_session.py` | Redis `quiz_session:{attempt_id}` with TTL |
| `LMS-QZ-03` | Atomic Submissions | @swatisaumya | @armoredglock | `backend/apps/assessments/views.py` | `@transaction.atomic` auto-grader |
| `LMS-QZ-04` | Quiz Review & Hist | @swatisaumya | @armoredglock | `backend/apps/assessments/views.py` | Query historical attempts and answers |
| `LMS-GAM-01` | Redis Leaderboard | @MEHELIGHOSH | @armoredglock | `backend/services/leaderboard.py` | Redis Sorted Set `leaderboard:course:{id}` |
| `LMS-GAM-02` | Leaderboard API | @MEHELIGHOSH | @armoredglock | `backend/apps/gamification/views.py`| `ZREVRANGE` top 10 & `ZREVRANK` user rank |
| `LMS-GAM-03` | Certificate Logic | @MEHELIGHOSH | @armoredglock | `backend/apps/gamification/models.py`| `Certificate` verification hash generation |
| `LMS-GAM-04` | Gradebook Views | @MEHELIGHOSH | @armoredglock | `backend/apps/gamification/views.py`| SQL aggregation queries (Avg, Count, Max) |
| `LMS-AI-01` | AI Artifact Schema | @armoredglock | @BibekTripathy | `backend/apps/ai_generator/models.py`| `AIArtifact` table storing JSON payloads |
| `LMS-AI-02` | Transcript Pipeline | @armoredglock | @BibekTripathy | `backend/apps/ai_generator/services.py`| Prompt templates, JSON MCQ generation |
| `LMS-FE-03` | React Setup & Auth | @armoredglock | @BibekTripathy | `frontend/src/` | AuthContext, Protected routes, Vite config |
| `LMS-FE-04` | Dashboard & UI | @armoredglock | @BibekTripathy | `frontend/src/pages/` | Video player, Quiz modal, Leaderboard widget|
