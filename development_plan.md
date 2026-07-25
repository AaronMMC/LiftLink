# Development Plan — Fitness Marketplace

*Companion to `fitness-app-learning-goals.md` (the why) and `PROJECT_STRUCTURE.md` (the where). This one is the when, in what order.*

## How to use this doc

- Check a box when a task is genuinely done, not just started: `- [ ]` -> `- [x]`.
- Optionally date-stamp finished tasks if you want a log to look back on later — e.g. `- [x] Table creates locally (2026-07-12)`.
- Update the status column in the table below as each phase wraps.
- Phases are ordered by dependency (you need the table before you can write handlers that read from it) — but a few tasks can jump the queue if you want variety. Frontend scaffolding, for instance, doesn't need to wait for every backend route to exist.
- Time estimates assume a part-time student pace and are relative, not calendar deadlines — stretch or compress freely. This is also running alongside the Sungka project, so treat these as the fitness app's slice of your time, not your whole week.

---

## Progress at a glance

| # | Phase | Focus | Status |
| --- | --- | --- | --- |
| 0 | Foundations & Guardrails | Account safety net, repo skeleton | Done (2026-07-25) |
| 1 | Data Layer | DynamoDB single-table design | Done (2026-07-25) |
| 2 | Auth Layer | Cognito, authN vs authZ | Done (2026-07-25) |
| 3 | Backend API | Lambda + API Gateway, all routes | Done (2026-07-25) |
| 4 | Frontend | UI wired to the real API, on S3 | Done (2026-07-25) |
| 5 | CI/CD | GitHub Actions, zero manual deploys | Done (2026-07-25) |
| 6 | Testing & Hardening | Confidence, not just "it ran once" | Done (2026-07-25) |
| 7 | Polish & Interview Prep | README, diagram, ADRs, demo | In progress |

> Swap statuses as you update: Not started -> In progress -> Done, or just rely on the checkboxes inside each phase — whichever you'll actually keep current.

---

## Phase 0 — Foundations & Guardrails

> ~2-4 days · nothing gets built until the safety net and skeleton exist

- [ ] Confirm the AWS account is on the **Free account plan**, not Paid
- [ ] Set up the Zero Spend Budget (Billing and Cost Management -> Budgets -> Zero spend budget template)
- [ ] Create a personal IAM user with MFA — stop using root from here on
- [ ] Install and verify: AWS CLI (`aws --version`), SAM CLI (`sam --version`), Docker (`docker --version`)
- [ ] Run `aws configure` with the IAM user's credentials
- [x] Decide SAM vs CDK (see `PROJECT_STRUCTURE.md` section 1) and write `docs/adr/0001-sam-over-cdk.md` (2026-07-25)
- [x] Scaffold the repo (`PROJECT_STRUCTURE.md` section 5) (2026-07-25)
- [x] `git init`, first commit, push to a new GitHub repo (2026-07-25)
- [x] Stub `README.md` — project name, one-line pitch, a "work in progress" badge is enough for now (2026-07-25)

**Done when:** `sam --version` and `aws sts get-caller-identity` run clean, the repo's on GitHub, and a Zero Spend Budget alert is live.

---

## Phase 1 — Data Layer (DynamoDB)

> ~3-5 days · the table exists, the schema is documented, reads/writes work locally

- [x] Design the PK/SK scheme for `INSTRUCTOR` and `PROGRESS_ENTRY` item types in one table (2026-07-25)
- [x] Decide the GSI(s) needed for "clients search instructors by specialty/location" (2026-07-25)
- [x] Write `docs/adr/0002-single-table-design.md` capturing the schema and reasoning (2026-07-25)
- [x] Define the table + GSI(s) in `template.yaml`, On-Demand capacity mode (2026-07-25)
- [ ] Run DynamoDB Local via Docker, confirm the table creates and a put/get round-trips
- [x] Implement key-builder helpers in `backend/src/handlers/shared/db.py` (2026-07-25)
- [x] Unit test the key-builder logic (2026-07-25)

**Done when:** you can explain out loud why one table holds two item types, and a local put/get works.

---

## Phase 2 — Auth Layer (Cognito)

> ~3-5 days · sign-up/sign-in works, and you can articulate authN vs authZ

- [x] Define a Cognito User Pool + App Client in `template.yaml` (2026-07-25)
- [x] Decide how instructors vs clients are distinguished — one pool with `custom:user_role` attribute (2026-07-25)
- [ ] Test sign-up/sign-in via AWS CLI or the Cognito Hosted UI, before touching the frontend
- [x] Wire a Cognito authorizer onto the HTTP API (2026-07-25)
- [x] Cognito answers *who you are*; `authz.py` enforces *what you're allowed to touch* in Lambda code (2026-07-25)

**Done when:** you can sign up, sign in, get a token, and a protected dummy route rejects requests without one.

---

## Phase 3 — Backend API (Lambda + API Gateway)

> ~1-2 weeks · the biggest phase — "What Done Looks Like" becomes real and testable

- [x] Set up the HTTP API in `template.yaml`; attach the Cognito authorizer to protected routes (2026-07-25)
- [x] Write `docs/adr/0003-http-api-over-rest-api.md` (2026-07-25)
- [x] Instructor: create profile (2026-07-25)
- [x] Instructor: get / update own profile (2026-07-25)
- [x] Instructor: search/list instructors (uses the GSI from Phase 1) (2026-07-25)
- [x] Progress: instructor logs an entry for a specific client (2026-07-25)
- [x] Progress: client lists their own history (authz-checked — only their own) (2026-07-25)
- [x] `shared/authz.py` — the ownership check, called at the top of every write handler (2026-07-25)
- [x] `shared/responses.py` — consistent status codes and error shapes across all handlers (2026-07-25)
- [x] Write sample events in `backend/events/`, exercise every handler with `sam local invoke` (2026-07-25)
- [ ] `sam local start-api` — smoke-test every route together, end to end

**Done when:** every bullet in the learning goals doc's "What Done Looks Like" section works via curl/Postman against `sam local start-api`, before a single AWS deploy.

---

## Phase 4 — Frontend

> ~1-1.5 weeks · a usable UI hitting the real API, served from S3

- [x] Scaffold the frontend — React + Vite (2026-07-25)
- [x] Sign-up / sign-in screens wired to Cognito (2026-07-25)
- [x] Instructor: create/edit profile screen (2026-07-25)
- [x] Client: search/browse instructors screen (2026-07-25)
- [x] Instructor: log a progress entry screen (2026-07-25)
- [x] Client: view own progress history screen (2026-07-25)
- [ ] Add the S3 bucket + public-read bucket policy to `template.yaml`
- [ ] Build, sync to S3, confirm the live URL works end to end against the real deployed API

**Done when:** a stranger with the S3 URL can sign up, and both user types can complete their respective flows.

---

## Phase 5 — CI/CD (GitHub Actions)

> ~3-5 days · `git push` deploys everything, no manual console steps again

- [x] Write `.github/workflows/ci.yml` and `.github/workflows/deploy.yml` (2026-07-25)
- [ ] Create a dedicated IAM role/user for the GitHub Actions deploy step, scoped narrowly — never root/admin
- [ ] Store AWS credentials as GitHub Actions secrets
- [x] Pipeline step: sync the frontend build to S3 (in deploy.yml) (2026-07-25)
- [x] Pipeline step: `sam build && sam deploy` (in deploy.yml) (2026-07-25)
- [ ] Set the GitHub Actions spending limit to $0 (Settings -> Billing)
- [ ] Push a trivial change, confirm the pipeline runs green end to end, unattended

**Done when:** a small edit, pushed, deploys itself with the AWS console never opened.

---

## Phase 6 — Testing & Hardening

> ~3-5 days · confidence it actually works, not just that it worked once

- [x] Unit tests for every handler (mock DynamoDB with `moto`) (2026-07-25)
- [ ] Integration tests against `sam local start-api` + DynamoDB Local
- [x] Adversarial pass: Client A tries to read Client B's history → 403 (in test_get_history.py) (2026-07-25)
- [ ] Skim CloudWatch Logs for any Lambda you haven't actually looked at yet
- [ ] Check the real AWS Billing dashboard — confirm $0, confirm the budget alert never fired

**Done when:** the adversarial test above fails the way it should, and Billing shows $0.

---

## Phase 7 — Polish & Interview Prep

> ~3-5 days, ongoing · a stranger understands this project in 5 minutes

- [ ] Architecture diagram in `docs/architecture-diagram.png` (Excalidraw, draw.io, or AWS's own icon set)
- [x] Finish `README.md`: problem statement, diagram, stack, setup steps (2026-07-25)
- [x] Revisit and tighten all three ADRs (2026-07-25)
- [ ] Rehearse explaining, unprompted: why serverless at all, why single-table, why HTTP API over REST API, why SAM (or CDK)
- [ ] Record a short demo (60-90 seconds is plenty) for the README / LinkedIn
- [ ] Screenshot the $0 Billing dashboard — "built and demoed this for free" is a genuinely good interview line

**Done when:** you could hand this repo to a stranger, walk away, and they'd understand what it does and why you built it this way.

---

## Rough total: ~5-8 weeks, part-time

A shape, not a deadline — the checkboxes exist so progress stays visible regardless of exactly how long each phase takes.
