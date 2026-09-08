# DBMS Schema & Architecture Specification — Cognify LMS

## 1. System Architecture Overview

Cognify LMS employs a multi-tiered architecture with a hybrid data-storage strategy:
- **PostgreSQL**: Relational storage adhering to 3NF (Third Normal Form) for persistent data (users, courses, enrollments, quiz records, gradebooks, certificates, AI artifacts).
- **Redis**: In-memory high-throughput data store used for transient playback heartbeats, session TTL management for exams, and real-time sorted leaderboard sets.
- **Django REST Framework**: Backend application layer enforcing ACID transactions and business logic.
- **React (Vite)**: Single Page Application frontend.
- **AI Processing Pipeline**: Transcript summarizer and MCQ generator.

---

## 2. PostgreSQL Relational Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USER ||--o{ ENROLLMENT : places
    USER ||--o{ QUIZ_ATTEMPT : submits
    USER ||--o{ LESSON_PROGRESS : tracks
    USER ||--o{ CERTIFICATE : earns
    COURSE ||--o{ MODULE : contains
    COURSE ||--o{ ENROLLMENT : has
    COURSE ||--o{ CERTIFICATE : issues
    MODULE ||--o{ LESSON : contains
    LESSON ||--o{ LESSON_PROGRESS : recorded_in
    LESSON ||--o{ QUIZ : assesses
    LESSON ||--o{ AI_ARTIFACT : generates
    QUIZ ||--o{ QUESTION : contains
    QUIZ ||--o{ QUIZ_ATTEMPT : attempted_in
    QUESTION ||--o{ OPTION : has
    QUESTION ||--o{ STUDENT_ANSWER : answered_with
    QUIZ_ATTEMPT ||--o{ STUDENT_ANSWER : records

    USER {
        uuid id PK
        string email UK
        string username
        string role "STUDENT | INSTRUCTOR | ADMIN"
        string password_hash
        timestamp created_at
    }

    COURSE {
        uuid id PK
        string title
        string slug UK
        text description
        string category
        uuid instructor_id FK
        boolean is_published
        timestamp created_at
    }

    MODULE {
        uuid id PK
        uuid course_id FK
        string title
        int order
    }

    LESSON {
        uuid id PK
        uuid module_id FK
        string title
        string video_url
        int duration_seconds
        text transcript
        int order
    }

    ENROLLMENT {
        uuid id PK
        uuid student_id FK
        uuid course_id FK
        timestamp enrolled_at
        float overall_progress_percent
    }

    LESSON_PROGRESS {
        uuid id PK
        uuid student_id FK
        uuid lesson_id FK
        int last_watched_second
        boolean is_completed
        timestamp updated_at
    }

    QUIZ {
        uuid id PK
        uuid lesson_id FK
        string title
        int time_limit_minutes
        int passing_score
        timestamp created_at
    }

    QUESTION {
        uuid id PK
        uuid quiz_id FK
        text question_text
        string question_type "MCQ | TRUE_FALSE"
        int points
    }

    OPTION {
        uuid id PK
        uuid question_id FK
        text option_text
        boolean is_correct
    }

    QUIZ_ATTEMPT {
        uuid id PK
        uuid student_id FK
        uuid quiz_id FK
        int total_score
        boolean is_passed
        timestamp started_at
        timestamp completed_at
    }

    STUDENT_ANSWER {
        uuid id PK
        uuid attempt_id FK
        uuid question_id FK
        uuid selected_option_id FK
    }

    CERTIFICATE {
        uuid id PK
        uuid student_id FK
        uuid course_id FK
        string verification_hash UK
        timestamp issue_date
    }

    AI_ARTIFACT {
        uuid id PK
        uuid lesson_id FK
        string artifact_type "QUIZ | FLASHCARD | SUMMARY"
        jsonb generated_payload
        timestamp created_at
    }
```

---

## 3. Redis In-Memory Key Design & Caching Architecture

| Key Pattern | Data Structure | TTL | Purpose |
| :--- | :--- | :--- | :--- |
| `video:user:{uid}:lesson:{lid}` | Hash (`last_sec`, `updated_at`) | 24 Hours | Absorbs high-frequency video playback ticks without overloading PostgreSQL disk writes. |
| `quiz_session:{attempt_id}` | String / Hash (`quiz_id`, `start_time`) | Quiz duration + 2 min grace | Strict countdown enforcement. Submissions rejected after key expires. |
| `leaderboard:course:{course_id}`| Sorted Set (`ZSET`) | None (Persistent) | Real-time course ranking computed via score + progress points (`ZADD`, `ZREVRANGE`). |

---

## 4. Normalization & Indexing Strategy

1. **3NF Compliance**:
   - Every non-key attribute is dependent solely on the primary key (no transitive dependencies).
   - Quiz questions and options are decoupled from attempts, ensuring quiz edits do not distort historical scores.
2. **PostgreSQL Indexing**:
   - **Composite Index**: `(student_id, lesson_id)` on `LessonProgress` for $O(1)$ progress lookups.
   - **B-Tree Index**: `Course.category`, `Course.instructor_id`, and `Enrollment.student_id`.
   - **Unique Constraints**: Prevent duplicate enrollments (`student_id`, `course_id`) and unique certificate hashes.
