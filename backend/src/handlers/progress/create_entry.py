import json
import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.authz import get_user_id, is_instructor
from shared.db import get_table, progress_pk, progress_sk, instructor_progress_pk, instructor_progress_sk
from shared.responses import created_response, error_response, forbidden_response, server_error_response


REQUIRED_FIELDS = ["client_id", "workout_type", "notes"]


def handler(event: dict, context) -> dict:
    try:
        if not is_instructor(event):
            return forbidden_response("Only instructors can log progress entries")

        instructor_id = get_user_id(event)
        if not instructor_id:
            return forbidden_response("Unable to identify user")

        body = json.loads(event.get("body") or "{}")

        missing = [f for f in REQUIRED_FIELDS if not body.get(f)]
        if missing:
            return error_response(f"Missing required fields: {', '.join(missing)}")

        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        client_id = body["client_id"]

        client_item = {
            "PK": progress_pk(client_id),
            "SK": progress_sk(timestamp, entry_id),
            "entry_id": entry_id,
            "instructor_id": instructor_id,
            "client_id": client_id,
            "workout_type": body["workout_type"],
            "notes": body["notes"],
            "duration_minutes": body.get("duration_minutes", 0),
            "created_at": timestamp,
            "item_type": "PROGRESS_ENTRY",
        }

        instructor_item = {
            "PK": instructor_progress_pk(instructor_id),
            "SK": instructor_progress_sk(timestamp, entry_id),
            "entry_id": entry_id,
            "instructor_id": instructor_id,
            "client_id": client_id,
            "workout_type": body["workout_type"],
            "notes": body["notes"],
            "duration_minutes": body.get("duration_minutes", 0),
            "created_at": timestamp,
            "item_type": "PROGRESS_ENTRY",
        }

        table = get_table()
        with table.batch_writer() as batch:
            batch.put_item(Item=client_item)
            batch.put_item(Item=instructor_item)

        return created_response({
            "entry_id": entry_id,
            "instructor_id": instructor_id,
            "client_id": client_id,
            "workout_type": body["workout_type"],
            "notes": body["notes"],
            "duration_minutes": body.get("duration_minutes", 0),
            "created_at": timestamp,
        })
    except json.JSONDecodeError:
        return error_response("Invalid JSON in request body")
    except Exception as e:
        print(f"Error creating progress entry: {e}")
        return server_error_response()
