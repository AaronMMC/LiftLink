# 0002 — Single-Table DynamoDB Design

**Status:** Accepted
**Date:** 2026-07-25

## Context

LiftLink stores two item types — instructor profiles and progress entries — and needs to support these access patterns efficiently:

1. Get an instructor profile by ID
2. Update an instructor profile (owner only)
3. Search instructors by specialty and optionally location
4. Create a progress entry for a client (instructor writes)
5. List all progress entries by a specific instructor
6. List all progress entries for a specific client (client reads own data only)

DynamoDB charges per table (On-Demand removes capacity planning) but the key design determines query efficiency.

## Decision

**Single-table design** with composite primary keys and one Global Secondary Index (GSI).

### Schema

| Item Type | PK | SK | GSI1PK | GSI1SK |
|---|---|---|---|---|
| Instructor Profile | `INSTRUCTOR#{id}` | `PROFILE` | `SPECIALTY#{specialty}` | `LOCATION#{location}` |
| Progress (client view) | `PROGRESS#{client_id}` | `ENTRY#{timestamp}#{entry_id}` | — | — |
| Progress (instructor view) | `INSTRUCTOR_PROGRESS#{instructor_id}` | `ENTRY#{timestamp}#{entry_id}` | — | — |

### GSI: SpecialtyLocationIndex

- **GSI1PK:** `SPECIALTY#{specialty}` (partition by specialty)
- **GSI1SK:** `LOCATION#{location}` (sort/filter by location)
- **Projection:** ALL

### Access Pattern Mapping

| Access Pattern | Key Used | Operation |
|---|---|---|
| Get instructor profile | PK=`INSTRUCTOR#{id}`, SK=`PROFILE` | `GetItem` |
| Update instructor profile | PK=`INSTRUCTOR#{id}`, SK=`PROFILE` | `PutItem` |
| Search by specialty | GSI1PK=`SPECIALTY#{spec}` | `Query` on GSI1 |
| Search by specialty + location | GSI1PK=`SPECIALTY#{spec}`, GSI1SK=`LOCATION#{loc}` | `Query` on GSI1 |
| Client views own history | PK=`PROGRESS#{client_id}`, SK begins_with `ENTRY#` | `Query` |
| Instructor lists entries | PK=`INSTRUCTOR_PROGRESS#{instructor_id}`, SK begins_with `ENTRY#` | `Query` |
| Create progress entry | Dual-write to client + instructor partitions | 2x `PutItem` (batch) |

### Dual-Write Pattern for Progress Entries

Progress entries are written twice:
1. Under `PROGRESS#{client_id}` — for client history queries
2. Under `INSTRUCTOR_PROGRESS#{instructor_id}` — for instructor listing queries

This avoids a GSI on progress entries and keeps both read paths as efficient single-partition queries.

## Consequences

**Gains:**
- One table, one bill, one set of capacity settings
- Every access pattern resolves to a single `GetItem` or `Query` — no scans, no filters
- Timestamp-based sort keys provide natural chronological ordering
- Specialty + location search is a single GSI query

**Trade-offs:**
- Dual-write for progress entries increases write cost (2 writes per entry) but eliminates the need for a second GSI
- Item type overloading means the table is less self-documenting — the ADR and key-builder code (`db.py`) serve as the schema reference
- Adding a new item type requires careful key design to avoid collisions

**Revisit if:** a new access pattern emerges that can't be served by the existing PK/SK/GSI1 scheme, or if write volume for progress entries becomes high enough that dual-write cost matters.
