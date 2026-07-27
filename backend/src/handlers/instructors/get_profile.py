import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.db import get_table, instructor_pk, instructor_sk
from shared.responses import success_response, not_found_response, server_error_response


def handler(event: dict, context) -> dict:
    try:
        instructor_id = event.get("pathParameters", {}).get("id")
        if not instructor_id:
            return not_found_response("Instructor ID is required")

        table = get_table()
        result = table.get_item(
            Key={"PK": instructor_pk(instructor_id), "SK": instructor_sk()}
        )

        item = result.get("Item")
        if not item:
            return not_found_response("Instructor not found")

        return success_response(
            {
                "instructor_id": item["instructor_id"],
                "display_name": item["display_name"],
                "specialty": item["specialty"],
                "location": item["location"],
                "bio": item.get("bio", ""),
            }
        )
    except Exception as e:
        print(f"Error getting profile: {e}")
        return server_error_response()
