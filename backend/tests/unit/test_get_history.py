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
            "PK": "PROGRESS#client-A",
            "SK": f"ENTRY#2026-07-{25-i}T10:00:00#entry-{i}",
            "entry_id": f"entry-{i}",
            "instructor_id": "inst-1",
            "client_id": "client-A",
            "workout_type": "Cardio",
            "notes": f"Session {i}",
            "duration_minutes": 45,
            "created_at": f"2026-07-{25-i}T10:00:00",
            "item_type": "PROGRESS_ENTRY",
        })
    table.put_item(Item={
        "PK": "PROGRESS#client-B",
        "SK": "ENTRY#2026-07-25T10:00:00#entry-B",
        "entry_id": "entry-B",
        "instructor_id": "inst-1",
        "client_id": "client-B",
        "workout_type": "Strength",
        "notes": "Client B only",
        "duration_minutes": 60,
        "created_at": "2026-07-25T10:00:00",
        "item_type": "PROGRESS_ENTRY",
    })
    return table


def _make_event(sub: str, role: str, path_id: str) -> dict:
    return {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {"sub": sub, "custom:user_role": role}
                }
            }
        },
        "pathParameters": {"id": path_id},
    }


@mock_aws
class TestGetHistory:
    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table_and_seed(self.dynamodb)

    def test_client_sees_own_history(self):
        from clients.get_history import handler

        event = _make_event("client-A", "client", "client-A")
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 3

    def test_adversarial_cross_client_access_denied(self):
        """Client A tries to read Client B's history — MUST be rejected with 403."""
        from clients.get_history import handler

        event = _make_event("client-A", "client", "client-B")
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_instructor_cannot_read_client_history(self):
        from clients.get_history import handler

        event = _make_event("inst-1", "instructor", "client-A")
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_client_b_sees_own_history(self):
        from clients.get_history import handler

        event = _make_event("client-B", "client", "client-B")
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 1
        assert body["entries"][0]["notes"] == "Client B only"
