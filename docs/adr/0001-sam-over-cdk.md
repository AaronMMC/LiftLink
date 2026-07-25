# 0001 — SAM over CDK

**Status:** Accepted
**Date:** 2026-07-25

## Context

LiftLink needs Infrastructure as Code (IaC) to define and deploy its serverless stack: Lambda functions, API Gateway HTTP API, DynamoDB table, and Cognito User Pool. The main candidates are:

1. **AWS SAM** — a CloudFormation superset purpose-built for serverless
2. **AWS CDK** — general-purpose IaC using a real programming language (TypeScript/Python)
3. **Terraform** — cloud-agnostic IaC with HCL

## Decision

We chose **AWS SAM**.

## Reasoning

- **Purpose-built for this stack.** Lambda, HTTP API, DynamoDB, and Cognito all have first-class shorthand in SAM templates (`AWS::Serverless::Function`, `AWS::Serverless::HttpApi`). Less abstraction between what you write and what actually gets provisioned — which matters when the explicit goal is understanding IAM roles and resource wiring, not just getting a stack to deploy.

- **Free local development loop.** `sam local invoke` and `sam local start-api`, paired with DynamoDB Local in Docker, provide a genuinely zero-cost local dev experience. Every handler can be tested dozens of times before a single real AWS deploy. This directly supports the zero-spend posture.

- **Lower ceremony for project scale.** CDK's real payoff — loops, reusable constructs, a general-purpose language driving infra — shows up on bigger, longer-lived systems. For ~7 Lambda functions and one table, CDK would add machinery the project doesn't need.

- **Terraform** was ruled out because the project is AWS-only and doesn't benefit from cloud-agnostic abstractions. SAM's CloudFormation native integration is simpler for this use case.

## Consequences

**Gains:**
- Single `template.yaml` captures the full stack — easy to audit, diff, and review
- SAM CLI's local tooling reduces iteration time and cloud costs to zero during development
- Lower learning curve for someone new to serverless IaC

**Trade-offs:**
- YAML over a real language — no loops, conditionals, or type-checking in the template
- If the project grew to 50+ functions, CDK constructs would provide better organization

**Revisit if:** the project grows beyond ~15 Lambda functions, or if multi-account/multi-region deployment becomes a requirement.
