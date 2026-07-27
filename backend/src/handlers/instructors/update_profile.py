import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.authz import is_resource_owner, is_instructor
from shared.db import get_table, instructor_pk, instructor_sk, gsi1_pk, gsi1_sk
from shared.responses import (
    success_response,
    error_response,
    forbidden_response,
    not_found_response,
    server_error_response,
)


UPDATABLE_FIELDS = ["display_name", "specialty", "location", "bio"]


def handler(event: dict, context) -> dict:
    try:
        instructor_id = event.get("pathParameters", {}).get("id")
        if not instructor_id:
            return error_response("Instructor ID is required")

        if not is_instructor(event):
            return forbidden_response("Only instructors can update profiles")

        if not is_resource_owner(event, instructor_id):
            return forbidden_response("You can only update your own profile")

        body = json.loads(event.get("body") or "{}")
        if not body:
            return error_response("Request body cannot be empty")

        updates = {k: v for k, v in body.items() if k in UPDATABLE_FIELDS and v}
        if not updates:
            return error_response(
                f"No valid fields to update. Updatable: {', '.join(UPDATABLE_FIELDS)}"
            )

        table = get_table()

        existing = table.get_item(
            Key={"PK": instructor_pk(instructor_id), "SK": instructor_sk()}
        )
        if "Item" not in existing:
            return not_found_response("Profile not found")

        item = existing["Item"]
        for key, value in updates.items():
            item[key] = value

        if "specialty" in updates or "location" in updates:
            item["GSI1PK"] = gsi1_pk(item["specialty"])
            item["GSI1SK"] = gsi1_sk(item["location"])

        table.put_item(Item=item)

        return success_response(
            {
                "instructor_id": item["instructor_id"],
                "display_name": item["display_name"],
                "specialty": item["specialty"],
                "location": item["location"],
                "bio": item.get("bio", ""),
            }
        )
    except json.JSONDecodeError:
        return error_response("Invalid JSON in request body")
    except Exception as e:
        print(f"Error updating profile: {e}")
        return server_error_response()
