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
    table.put_item(Item={
        "PK": "INSTRUCTOR#inst-1",
        "SK": "PROFILE",
        "GSI1PK": "SPECIALTY#YOGA",
        "GSI1SK": "LOCATION#NYC",
        "instructor_id": "inst-1",
        "display_name": "Jane",
        "specialty": "yoga",
        "location": "NYC",
        "bio": "Yoga expert",
        "item_type": "INSTRUCTOR",
    })
    return table


def _make_event(sub: str, role: str, body: dict = None, path_params: dict = None) -> dict:
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {"sub": sub, "custom:user_role": role}
                }
            }
        }
    }
    if body:
        event["body"] = json.dumps(body)
    if path_params:
        event["pathParameters"] = path_params
    return event


@mock_aws
class TestUpdateProfile:
    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table_and_seed(self.dynamodb)

    def test_updates_own_profile(self):
        from instructors.update_profile import handler

        event = _make_event("inst-1", "instructor", body={"bio": "Updated bio"}, path_params={"id": "inst-1"})
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["bio"] == "Updated bio"

    def test_rejects_non_owner(self):
        from instructors.update_profile import handler

        event = _make_event("inst-2", "instructor", body={"bio": "Hacked"}, path_params={"id": "inst-1"})
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_rejects_client_role(self):
        from instructors.update_profile import handler

        event = _make_event("inst-1", "client", body={"bio": "Nope"}, path_params={"id": "inst-1"})
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_rejects_empty_body(self):
        from instructors.update_profile import handler

        event = _make_event("inst-1", "instructor", body={}, path_params={"id": "inst-1"})
        result = handler(event, None)
        assert result["statusCode"] == 400
