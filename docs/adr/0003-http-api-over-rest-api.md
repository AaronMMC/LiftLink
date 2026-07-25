# 0003 — HTTP API over REST API

**Status:** Accepted
**Date:** 2026-07-25

## Context

API Gateway offers two API types for building RESTful APIs:

1. **HTTP API** — newer, lighter, lower-cost
2. **REST API** — older, feature-rich, more expensive

LiftLink needs: routing, CORS, JWT-based authorization, and Lambda proxy integration.

## Decision

We chose **HTTP API** (`AWS::Serverless::HttpApi`).

## Reasoning

- **Lower cost.** HTTP APIs cost ~70% less than REST APIs ($1.00/million vs $3.50/million requests). For a Free Tier project targeting $0 spend, this matters.

- **Lower latency.** HTTP APIs have measurably lower overhead per request, which improves the user experience for a marketplace with interactive search.

- **Native JWT authorizer.** HTTP API has built-in JWT authorizer support — we point it at our Cognito User Pool and it validates tokens without a custom Lambda authorizer. REST API would require either a Cognito authorizer (which works differently) or a custom Lambda authorizer.

- **Sufficient feature set.** HTTP API supports everything LiftLink needs: path/query parameters, CORS, stage variables, and Lambda proxy integration. The features it lacks (API keys, usage plans, request validation, caching) are not needed for this project.

## Consequences

**Gains:**

- Simpler SAM template — the `Auth` block in `AWS::Serverless::HttpApi` is cleaner than REST API authorizer wiring
- Lower cost per request, contributing to the $0 spend target
- Faster cold-start API responses

**Trade-offs:**

- No built-in request/response validation (we validate in Lambda code instead — arguably better practice anyway)
- No API key or usage plan support (not needed for this app)
- No built-in response caching (could use CloudFront later if needed)
- Fewer integration options (no direct DynamoDB integration — but we want Lambda logic in the middle anyway)

**Revisit if:** we need API key management for third-party consumers, or request throttling/rate limiting at the API Gateway level.
