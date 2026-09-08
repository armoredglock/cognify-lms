# Contributing to Cognify LMS — Agile Workflow & Traceability Rules

This project runs a structured Agile build for our **DBMS Course Project**. Because our timeline is tight and five people are working in parallel on independently owned modules, the rules below exist to stop silent contract drift and ensure smooth coordination.

Follow them exactly: they are cheap when followed and expensive when skipped.

---

## 1. Golden Rule: Everything Traces to a Requirement

Every unit of work — issue, branch, commit, and Pull Request — **must be traceable back to a Requirement ID** from the Software Requirements Specification (e.g., `LMS-AUTH-01`, `LMS-VID-02`, `LMS-QZ-03`, etc.) or an explicit design section in `docs/TRACEABILITY.md` and `docs/DBMS_ER_DIAGRAM.md`.

For non-functional changes (tooling, typo fixes, CI configuration) — tag the PR with `[no-req]`. 

> [!IMPORTANT]
> The automated CI traceability check (`.github/workflows/traceability-check.yml`) requires a valid requirement ID or `[no-req]` in the PR title or body. Unlinked PRs cannot be merged.

---

## 2. Branching Model

- `main` is always demo-able, stable, and protected. Direct pushes to `main` are restricted.
- All development happens on dedicated feature branches.
- **Branch Naming Standard**: `<owner>/<type>/<short-slug>-<req-id>`
  - `<owner>`: First name of the member in lowercase (`saanvi`, `bibek`, `swati`, `meheli`, `sagnik`).
  - `<type>`: `feat`, `fix`, `docs`, `refactor`, `test`.
  - `<short-slug>`: Brief 2-3 word kebab-case description.
  - `<req-id>`: Requirement code (e.g., `LMS-CRS-02`).

**Examples:**
```bash
saanvi/feat/course-models-LMS-CRS-02
bibek/feat/redis-playback-cache-LMS-VID-01
swati/feat/quiz-timer-ttl-LMS-QZ-02
meheli/feat/leaderboard-zset-LMS-GAM-01
sagnik/feat/ai-mcq-generator-LMS-AI-02
```

---

## 3. Commit Message Standards

Commit messages must be clear and reference the scope and requirement ID:
```
<type>(<scope>): <concise description> [<req-id>]
```
**Examples:**
- `feat(auth): implement custom user model with role-based permissions [LMS-AUTH-01]`
- `feat(tracking): cache video playback timestamps in redis [LMS-VID-01]`
- `fix(assessments): wrap quiz submission in atomic transaction [LMS-QZ-03]`

---

## 4. Pull Request & Code Review Process

1. **Keep PRs focused**: One requirement per PR. Do not bundle unrelated changes.
2. **Review Ownership**:
   - As declared in `.github/CODEOWNERS`, either Co-Lead (**@armoredglock** or **@saanvi-singhal**) can review and approve any PR.
   - The module author is also requested for review on their respective components.
3. **Database Migration Checks**:
   - If your PR introduces or alters Django models, always commit the generated migration files (`python manage.py makemigrations`).
   - Run `python manage.py check` and verify that migrations apply cleanly.
4. **CI Passes**:
   - `PR Traceability Check` must be green.
   - `Backend CI` (Django check & migrations) must be green.
   - `Frontend CI` (React build) must be green.

---

## 5. Development Steps

```bash
# 1. Fetch latest changes
git checkout main
git pull origin main

# 2. Create your feature branch
git checkout -b <owner>/feat/<task-name>-<req-id>

# 3. Implement, test, and commit
git add .
git commit -m "feat(<module>): <description> [<req-id>]"

# 4. Push to origin and open a PR on GitHub
git push -u origin <owner>/feat/<task-name>-<req-id>
```
