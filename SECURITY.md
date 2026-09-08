# Security Policy

## Cognify LMS (DBMS Course Project)

Cognify LMS handles user credentials, student performance records, timed assessment state, and AI integration keys. We take application security and data integrity seriously.

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities or credential leaks.**

Instead, report it privately to the project leads:
- **Sagnik Datta** ([@armoredglock](https://github.com/armoredglock)) — Co-Lead
- **Saanvi Singhal** ([@saanvi-singhal](https://github.com/saanvi-singhal)) — Group Leader

You can also use GitHub's **Private Vulnerability Reporting** for this repository (under the `Security` tab -> `Report a vulnerability`).

### What to Include:
- A clear description of the vulnerability and its potential impact (e.g., SQL Injection, unauthenticated quiz access, token leak).
- Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
- The affected component or file (e.g., `/backend/apps/assessments/views.py`).

We will acknowledge reports as quickly as possible and deploy necessary patches.
