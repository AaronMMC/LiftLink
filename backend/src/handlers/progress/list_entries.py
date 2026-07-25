import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.authz import get_user_id, is_instructor
from shared.db import get_table, instructor_progress_pk
from shared.responses import success_response, forbidden_response, server_error_response

from boto3.dynamodb.conditions import Key


def handler(event: dict, context) -> dict:
    try:
        if not is_instructor(event):
            return forbidden_response("Only instructors can list their progress entries")

        instructor_id = get_user_id(event)
        if not instructor_id:
            return forbidden_response("Unable to identify user")

        table = get_table()

        result = table.query(
            KeyConditionExpression=Key("PK").eq(instructor_progress_pk(instructor_id))
            & Key("SK").begins_with("ENTRY#"),
            ScanIndexForward=False,
        )

        entries = [
            {
                "entry_id": item["entry_id"],
                "client_id": item["client_id"],
                "workout_type": item["workout_type"],
                "notes": item["notes"],
                "duration_minutes": item.get("duration_minutes", 0),
                "created_at": item["created_at"],
            }
            for item in result.get("Items", [])
        ]

        return success_response({
            "entries": entries,
            "count": len(entries),
        })
    except Exception as e:
        print(f"Error listing entries: {e}")
        return server_error_response()
