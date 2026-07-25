import json
import sys
import os

import boto3
from moto import mock_aws

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers"))

TABLE_NAME = "LiftLinkTable"


def _create_table_and_seed(dynamodb):
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "SpecialtyLocationIndex",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    for i in range(3):
        table.put_item(Item={
            "PK": "INSTRUCTOR_PROGRESS#inst-1",
            "SK": f"ENTRY#2026-07-{25-i}T10:00:00#entry-{i}",
            "entry_id": f"entry-{i}",
            "instructor_id": "inst-1",
            "client_id": f"client-{i}",
            "workout_type": "Strength",
            "notes": f"Session {i}",
            "duration_minutes": 60,
            "created_at": f"2026-07-{25-i}T10:00:00",
            "item_type": "PROGRESS_ENTRY",
        })
    return table


def _make_event(sub: str, role: str) -> dict:
    return {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {"sub": sub, "custom:user_role": role}
                }
            }
        }
    }


@mock_aws
class TestListEntries:
    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table_and_seed(self.dynamodb)

    def test_lists_instructor_entries(self):
        from progress.list_entries import handler

        event = _make_event("inst-1", "instructor")
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 3

    def test_rejects_non_instructor(self):
        from progress.list_entries import handler

        event = _make_event("client-1", "client")
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_empty_for_new_instructor(self):
        from progress.list_entries import handler

        event = _make_event("inst-new", "instructor")
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 0
