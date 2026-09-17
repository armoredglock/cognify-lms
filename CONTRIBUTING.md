# Contributing to Cognify LMS 🤝

Thank you for your interest in contributing to **Cognify LMS**! Whether you are implementing a new module, fixing bugs, improving documentation, or adding tests, your efforts help build a better learning platform.

Please take a few moments to review this guide before getting started.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Team & Domain Leads](#team--domain-leads)
- [Git Workflow & Branching Strategy](#git-workflow--branching-strategy)
- [Commit Message Conventions](#commit-message-conventions)
- [Development Guidelines](#development-guidelines)
  - [Backend (Django & DRF)](#backend-django--drf)
  - [Frontend (React)](#frontend-react)
  - [Database (PostgreSQL)](#database-postgresql)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

---

## 🤝 Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please treat fellow contributors with respect, give constructive feedback, and maintain professional collaboration at all times.

---

## 👥 Team & Domain Leads

If your contribution relates to a specific functional domain, consider tagging the respective module owner on your issue or pull request:

- **Core Architecture, RBAC & Course Models**: [@saanvi-singhal](https://github.com/saanvi-singhal) (Team Lead)
- **Video Analytics & Telemetry**: [@BibekTripathy](https://github.com/BibekTripathy)
- **Assessment Engine & Timed Sessions**: [@swatisaumya](https://github.com/swatisaumya)
- **Gamification, Leaderboards & Certification**: [@MEHELIGHOSH](https://github.com/MEHELIGHOSH)
- **AI Assessment Generator & Frontend UI**: [@armoredglock](https://github.com/armoredglock)

---

## 🌿 Git Workflow & Branching Strategy

We follow a feature-branch workflow. All feature development and bug fixes should originate from isolated branches.

### Branch Naming Scheme
- **Features**: `feat/<short-description>` or `feature/<module>-<description>` (e.g., `feat/video-tracking-api`, `feat/quiz-timer`)
- **Bug Fixes**: `fix/<issue-description>` (e.g., `fix/enrollment-constraint-bug`)
- **Documentation**: `docs/<topic>` (e.g., `docs/api-endpoints`)
- **Refactoring & Performance**: `refactor/<module>` or `perf/<target>`

### Step-by-Step Flow:
1. Fetch and pull the latest changes from `main`:
   ```bash
   git checkout main
   git pull origin main
   ```
2. Create and switch to your feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. Commit your changes logically adhering to our commit conventions.
4. Push your branch to GitHub:
   ```bash
   git push origin feat/your-feature-name
   ```
5. Open a Pull Request on GitHub against the `main` branch.

---

## 📝 Commit Message Conventions

We adhere to [Conventional Commits](https://www.conventionalcommits.org/). Each commit message should be concise and structured as follows:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Supported Types:
- `feat`: A new feature or endpoint
- `fix`: A bug fix
- `docs`: Documentation updates or additions
- `style`: Formatting, missing semicolons, whitespace changes (no production code change)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance or query optimization
- `test`: Adding or correcting unit/integration tests
- `chore`: Build process, dependencies, or configuration updates

### Examples:
- `feat(courses): add lesson completion status endpoint`
- `fix(assessments): enforce transaction lock on exam submit`
- `perf(leaderboard): add composite index for course ranking view`
- `docs(readme): update team allocation table`

---

## 🛠 Development Guidelines

### Backend (Django & DRF)
- Follow **PEP 8** style conventions.
- Keep business logic in services or model methods, keeping serializers and views clean.
- Ensure all new API endpoints are documented and secured with appropriate permission classes (`IsAuthenticated`, `IsInstructor`, etc.).
- Never commit secrets, credentials, or `.env` files.

### Frontend (React)
- Use functional components and React Hooks.
- Ensure component state is scoped appropriately; use custom hooks for shared logic.
- Follow responsive mobile-first styling principles with Tailwind CSS.
- Keep reusable UI components modular and isolated.

### Database (PostgreSQL)
- **No Redis Dependency**: All caching, timed session checks, and leaderboard aggregations are powered natively through PostgreSQL features (indexed lookups, timestamp comparisons, and window functions).
- Always generate migrations via `python manage.py makemigrations` and review migration files before committing.
- Ensure foreign keys and relational constraints have proper `on_delete` behaviors.
- Use `db_index=True` or explicit `indexes` on fields frequently used in filtering, joins, and leaderboard sorting.

---

## 🚀 Pull Request Process

1. **Self-Review**: Run local linting, migrations, and test suites to verify that nothing is broken.
2. **PR Title**: Ensure the PR title follows conventional commit formatting.
3. **PR Description**: Describe what was changed, why the change was made, and how reviewers can test it. Include relevant issue numbers (`Fixes #12`).
4. **Code Review**: At least one core team member review is required before merging.
5. **Merge**: Once approved, PRs will be squash-merged into `main` to preserve a clean commit history.

---

## 🐛 Reporting Issues

If you find a bug or have a suggestion:
1. Check the [GitHub Issues](https://github.com/armoredglock/cognify-lms/issues) tab to verify it hasn't been reported.
2. Open a new issue using a descriptive title.
3. Provide reproduction steps, expected vs. actual behavior, and environment details (OS, Python version, browser).

Thank you for helping make Cognify LMS exceptional! 🚀
