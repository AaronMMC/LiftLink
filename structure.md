# Project Structure & Conventions — Fitness Marketplace

*Companion to `fitness-app-learning-goals.md` (the why) and `DEVELOPMENT_PLAN.md` (the when). This one is the where.*

---

## 1. One decision before you scaffold anything: SAM or CDK

Your learning goals doc already flags this as a "pick one and be able to explain why" item — here's a recommendation with the reasoning behind it, built around **SAM**. CDK swap-notes are included below in case you'd rather go that way.

**Why SAM fits this project:**

- It's purpose-built for exactly this stack — Lambda, HTTP API, DynamoDB, and Cognito all have first-class shorthand in a SAM template, with less abstraction between what you write and what actually gets provisioned. That matters when the explicit goal is *understanding* IAM roles and wiring, not just getting a stack to go green.
- `sam local invoke` and `sam local start-api`, paired with DynamoDB Local in Docker, give you a genuinely free local dev loop — you can build and re-test every handler dozens of times before a single real deploy. That's directly in service of the "zero real spending" posture the whole project is built around.
- Lower ceremony for a project this size. CDK's real payoff — loops, reusable constructs, a general-purpose language driving your infra — shows up on bigger, longer-lived systems. For ~10-15 Lambda functions and one table, it's more machinery than the project needs.

**When CDK would be the better call:** you already know TypeScript well and want "infra as a real programming language" as your interview story, or your Sungka project's doc already commits to CDK and you'd rather run one consistent tool across both portfolio pieces. Structurally, the only thing that changes below is `template.yaml` becomes an `app.py` (or `.ts`) plus stack files under an `infrastructure/` folder — handlers, tests, frontend, and CI/CD stay exactly the same.

Write this decision up properly once you land on it — see § 6 below. It's one of the more interview-worthy calls in the whole build.

---

## 2. Full repository layout

```text
fitness-marketplace/
├── README.md
├── DEVELOPMENT_PLAN.md
├── PROJECT_STRUCTURE.md
├── LICENSE
├── .gitignore
├── .env.example
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── backend/
│   ├── template.yaml
│   ├── samconfig.toml
│   ├── requirements.txt
│   ├── src/
│   │   ├── handlers/
│   │   │   ├── instructors/
│   │   │   │   ├── create_profile.py
│   │   │   │   ├── get_profile.py
│   │   │   │   ├── update_profile.py
│   │   │   │   └── search_instructors.py
│   │   │   ├── clients/
│   │   │   │   └── get_history.py
│   │   │   ├── progress/
│   │   │   │   ├── create_entry.py
│   │   │   │   └── list_entries.py
│   │   │   └── shared/
│   │   │       ├── authz.py
│   │   │       ├── db.py
│   │   │       └── responses.py
│   │   └── layers/
│   │       └── shared-layer/
│   │           └── python/
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── events/
│
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
│
└── docs/
    ├── fitness-app-learning-goals.md
    ├── architecture-diagram.png
    └── adr/
        ├── 0001-sam-over-cdk.md
        ├── 0002-single-table-design.md
        └── 0003-http-api-over-rest-api.md
```

*(Backend assumes Python — the natural pairing with SAM's local tooling and the `moto` testing library. Swapping to Node/TypeScript changes file extensions and `requirements.txt` → `package.json`; nothing else moves.)*

---

## 3. What each piece is for

**`backend/template.yaml`** — every AWS resource, in one file: Lambda functions, the HTTP API and its routes, the Cognito authorizer wiring, the DynamoDB table and GSIs, IAM roles. Single source of truth for "what exists in AWS" — nothing gets created by hand in the console after Phase 0.

**`backend/src/handlers/`** — one file per Lambda function, grouped by domain (`instructors/`, `clients/`, `progress/`) rather than by HTTP verb. This mirrors the "What Done Looks Like" section of your learning goals doc, and it's the layout you'll see in most real serverless codebases — someone skimming this folder should understand the app's two-sided shape without reading a line of logic.

**`backend/src/handlers/shared/`** — where the cross-cutting learning goals live in code:

- `authz.py` — the "does this logged-in user actually own this resource" check, called at the top of every write handler. One shared file means an authorization bug gets fixed once, not five times.
- `db.py` — your single-table key-builder functions. The actual PK/SK schema is Phase 1 work; this file is just where that decision lives once you've made it.
- `responses.py` — consistent HTTP status/body shaping, so every handler fails the same way.

**`backend/src/layers/`** — a Lambda layer for dependencies shared across handlers (a thin boto3 wrapper, say). Not essential at this scale, but a real convention worth having ready — the moment two-plus functions need the same third-party package, this is what stops you from bundling it repeatedly.

**`backend/tests/unit/`** vs **`backend/tests/integration/`** — unit tests mock DynamoDB/Cognito entirely (`pytest` + `moto` is the standard Python pairing) and check handler logic in isolation. Integration tests run against `sam local start-api` + DynamoDB Local — closer to the real thing, slower, fewer of them.

**`backend/events/`** — sample JSON payloads shaped like real API Gateway events, used with `sam local invoke -e events/some_event.json`. Cheap to write, and they double as living documentation of what each endpoint expects.

**`frontend/`** — whatever you're fastest in (React, Vue, plain HTML/CSS/JS with a build step). S3 serves a static build; it has no opinion on how you made it.

**`docs/adr/`** — Architecture Decision Records, covered in § 6.

**Root files:**

- `README.md` — the pitch. First thing a recruiter opens.
- `LICENSE` — MIT is the standard, low-effort choice for a public portfolio repo.
- `DEVELOPMENT_PLAN.md` / `PROJECT_STRUCTURE.md` — process artifacts. Leave them in the repo as evidence of how you work, or delete once internalized — your call.

---

## 4. Git & environment hygiene

**`.gitignore`:**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/

# AWS SAM
.aws-sam/

# Frontend
frontend/node_modules/
frontend/dist/
frontend/build/

# Secrets — never commit real values
.env
.env.local

# OS cruft
.DS_Store
```

**`.env.example`** — commit this with placeholder values only, never a real `.env`:

```shell
# Copy to .env and fill in. Adjust the prefix (VITE_, REACT_APP_, etc.)
# to match whatever your frontend tooling expects.
API_BASE_URL=
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
AWS_REGION=
```

`samconfig.toml` is generally safe to commit — it holds stack name, region, and parameter names, not secrets. If a parameter override ever needs a real secret, that belongs in SSM Parameter Store or a GitHub Actions secret, never in this file.

**Branches & commits** — not load-bearing for a solo project, but worth practicing since it's what a team expects: `main` stays deployable, feature work happens on short-lived branches, commit messages use `feat: / fix: / chore: / docs:` prefixes. Small habit, real payoff.

---

## 5. One-command scaffold

Run once, from wherever the repo should live:

```bash
mkdir -p fitness-marketplace/{backend/src/handlers/{instructors,clients,progress,shared},backend/src/layers/shared-layer/python,backend/tests/unit,backend/tests/integration,backend/events,frontend/public,frontend/src,docs/adr,.github/workflows}

cd fitness-marketplace

touch README.md DEVELOPMENT_PLAN.md PROJECT_STRUCTURE.md LICENSE .gitignore .env.example
touch backend/template.yaml backend/samconfig.toml backend/requirements.txt
touch backend/src/handlers/instructors/{create_profile.py,get_profile.py,update_profile.py,search_instructors.py}
touch backend/src/handlers/clients/get_history.py
touch backend/src/handlers/progress/{create_entry.py,list_entries.py}
touch backend/src/handlers/shared/{authz.py,db.py,responses.py}
touch docs/adr/{0001-sam-over-cdk.md,0002-single-table-design.md,0003-http-api-over-rest-api.md}
touch .github/workflows/deploy.yml

git init
git add .
git commit -m "chore: scaffold project structure"
```

---

## 6. Architecture Decision Records — what and why

An ADR is a short, permanent note capturing a decision, the alternatives you weighed, and why you picked what you picked — written when you make the call, not reconstructed afterward. Standard practice on real infra teams, for the exact reason it'll help you here: "why did you choose X" is the single most common cloud-architecture interview follow-up, and pulling up the note you wrote the day you decided is a much stronger answer than reconstructing your logic on the spot.

Template:

```markdown
# 000X - Title of the decision

**Status:** Accepted
**Date:** YYYY-MM-DD

## Context
What problem were you solving? What were the real options?

## Decision
What did you pick?

## Consequences
What do you gain? What do you give up? What would make you revisit this?
```

Three to write over the course of the build (tracked in `DEVELOPMENT_PLAN.md`):

- `0001-sam-over-cdk.md` — the § 1 decision, in your own words
- `0002-single-table-design.md` — your actual PK/SK/GSI schema, once you've designed it in Phase 1
- `0003-http-api-over-rest-api.md` — shorter, but worth having on record

---

One naming note: `fitness-app-learning-goals.md` keeps its original lowercase-hyphenated name inside `docs/`. Root-level ALL-CAPS files (`README`, this doc, the plan) are the process/meta docs a GitHub visitor expects to find at a glance; content docs — your learning goals doc, the ADRs — live under `docs/` in lowercase-kebab-case. Not an inconsistency, just two different jobs.
