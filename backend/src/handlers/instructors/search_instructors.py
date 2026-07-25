import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.db import get_table, gsi1_pk, gsi1_sk, GSI1_NAME
from shared.responses import success_response, error_response, server_error_response

from boto3.dynamodb.conditions import Key


def handler(event: dict, context) -> dict:
    try:
        params = event.get("queryStringParameters") or {}
        specialty = params.get("specialty")
        location = params.get("location")

        if not specialty:
            return error_response("Query parameter 'specialty' is required")

        table = get_table()

        key_condition = Key("GSI1PK").eq(gsi1_pk(specialty))
        if location:
            key_condition = key_condition & Key("GSI1SK").eq(gsi1_sk(location))

        result = table.query(
            IndexName=GSI1_NAME,
            KeyConditionExpression=key_condition,
        )

        instructors = [
            {
                "instructor_id": item["instructor_id"],
                "display_name": item["display_name"],
                "specialty": item["specialty"],
                "location": item["location"],
                "bio": item.get("bio", ""),
            }
            for item in result.get("Items", [])
        ]

        return success_response({
            "instructors": instructors,
            "count": len(instructors),
        })
    except Exception as e:
        print(f"Error searching instructors: {e}")
        return server_error_response()
