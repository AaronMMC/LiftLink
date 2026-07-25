import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.authz import is_resource_owner, is_client
from shared.db import get_table, progress_pk
from shared.responses import success_response, error_response, forbidden_response, server_error_response

from boto3.dynamodb.conditions import Key


def handler(event: dict, context) -> dict:
    try:
        client_id = event.get("pathParameters", {}).get("id")
        if not client_id:
            return error_response("Client ID is required")

        if not is_client(event):
            return forbidden_response("Only clients can view progress history")

        if not is_resource_owner(event, client_id):
            return forbidden_response("You can only view your own progress history")

        table = get_table()

        result = table.query(
            KeyConditionExpression=Key("PK").eq(progress_pk(client_id))
            & Key("SK").begins_with("ENTRY#"),
            ScanIndexForward=False,
        )

        entries = [
            {
                "entry_id": item["entry_id"],
                "instructor_id": item["instructor_id"],
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
        print(f"Error getting history: {e}")
        return server_error_response()
