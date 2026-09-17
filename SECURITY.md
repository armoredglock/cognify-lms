# Security Policy 🛡

The Cognify LMS team takes the security of our platform, APIs, user data, and academic records seriously. This document outlines our security policies and procedures for reporting vulnerabilities.

---

## 📦 Supported Versions

We provide security updates and patches for the following versions:

| Version | Supported |
| :--- | :--- |
| `1.0.x` (Current / Main) | ✅ Supported |
| `< 1.0.0` | ❌ End of Life |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability in Cognify LMS, **please do not open a public GitHub issue**. Doing so may expose the platform and its users to premature risk.

Instead, please report vulnerabilities privately:

- **Primary Contact**: Sagnik Datta ([@armoredglock](https://github.com/armoredglock))
- **Email**: [sagnik.datta111@gmail.com](mailto:sagnik.datta111@gmail.com)
- **Subject Line**: `[SECURITY] Cognify LMS Vulnerability Report - <Brief Description>`

### What to Include in Your Report:
1. **Description**: A clear overview of the issue and its potential impact.
2. **Steps to Reproduce**: Detailed reproduction steps, curl commands, or a minimal Proof of Concept (PoC).
3. **Affected Components**: Specific endpoints, models, or frontend views involved.
4. **Proposed Fix (Optional)**: If you have a remediation patch or recommendation.

### Response Timeline:
- **Initial Response**: We will acknowledge receipt of your report within **48 hours**.
- **Assessment & Triage**: We will investigate and confirm validity within **5 business days**.
- **Fix & Disclosure**: Once resolved, we will publish a patch and credit the reporter in release notes (unless anonymity is requested).

---

## 🔒 Security Architecture & Best Practices

Cognify LMS implements defense-in-depth measures across all layers:

### 1. Role-Based Access Control (RBAC)
- All API endpoints strictly enforce permissions (`IsAuthenticated`, `IsInstructor`, `IsAdminUser`).
- Multi-tenancy checks verify that students can only access modules, assessments, and progress data for courses they are legitimately enrolled in.

### 2. Timed Assessment Session Security
- Exam durations are enforced exclusively on the backend via PostgreSQL timestamps (`started_at`, `expires_at`).
- Submissions are evaluated within an ACID transactional block using row-level locking (`select_for_update`) to prevent race conditions, replay attacks, and clock manipulation.

### 3. SQL Injection Prevention
- Relational operations rely on Django's ORM parameterized query builders.
- Raw SQL queries are avoided or strictly audited with explicit query parameters.

### 4. Authentication & Token Management
- Authentication relies on SimpleJWT tokens.
- Passwords are encrypted using Django's default PBKDF2 with SHA-256 (or Argon2).
- Sensitive tokens must be transmitted exclusively over secure HTTPS channels.

### 5. AI Engine Safety
- User inputs to the AI generation pipeline (lecture transcripts, student prompts) are sanitized before dispatch to LLM APIs.
- AI responses are validated against expected JSON schemas before persistence in PostgreSQL.

### 6. Secrets & Environment Isolation
- All API keys, database credentials, and secret keys are loaded strictly via environment variables.
- Production `.env` files must never be tracked in version control.

---

Thank you for helping keep Cognify LMS safe and trustworthy!
