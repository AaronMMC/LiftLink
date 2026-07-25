import json
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.authz import get_user_id, is_instructor
from shared.db import get_table, instructor_pk, instructor_sk, gsi1_pk, gsi1_sk
from shared.responses import created_response, error_response, forbidden_response, server_error_response


REQUIRED_FIELDS = ["display_name", "specialty", "location"]


def handler(event: dict, context) -> dict:
    try:
        if not is_instructor(event):
            return forbidden_response("Only instructors can create profiles")

        user_id = get_user_id(event)
        if not user_id:
            return forbidden_response("Unable to identify user")

        body = json.loads(event.get("body") or "{}")

        missing = [f for f in REQUIRED_FIELDS if not body.get(f)]
        if missing:
            return error_response(f"Missing required fields: {', '.join(missing)}")

        table = get_table()

        existing = table.get_item(
            Key={"PK": instructor_pk(user_id), "SK": instructor_sk()}
        )
        if "Item" in existing:
            return error_response("Profile already exists. Use PUT to update.", 409)

        item = {
            "PK": instructor_pk(user_id),
            "SK": instructor_sk(),
            "GSI1PK": gsi1_pk(body["specialty"]),
            "GSI1SK": gsi1_sk(body["location"]),
            "instructor_id": user_id,
            "display_name": body["display_name"],
            "specialty": body["specialty"],
            "location": body["location"],
            "bio": body.get("bio", ""),
            "item_type": "INSTRUCTOR",
        }

        table.put_item(Item=item)

        return created_response({
            "instructor_id": user_id,
            "display_name": item["display_name"],
            "specialty": item["specialty"],
            "location": item["location"],
            "bio": item["bio"],
        })
    except json.JSONDecodeError:
        return error_response("Invalid JSON in request body")
    except Exception as e:
        print(f"Error creating profile: {e}")
        return server_error_response()
