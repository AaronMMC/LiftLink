import json
import sys
import os

import boto3
import pytest
from moto import mock_aws

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers"))


TABLE_NAME = "LiftLinkTable"


def _create_table(dynamodb):
    dynamodb.create_table(
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


def _make_event(sub: str, role: str, body: dict = None, path_params: dict = None, query_params: dict = None) -> dict:
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": sub,
                        "custom:user_role": role,
                    }
                }
            }
        },
    }
    if body:
        event["body"] = json.dumps(body)
    if path_params:
        event["pathParameters"] = path_params
    if query_params:
        event["queryStringParameters"] = query_params
    return event


@mock_aws
class TestCreateProfile:
    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_creates_profile_successfully(self):
        from instructors.create_profile import handler

        event = _make_event("inst-1", "instructor", body={
            "display_name": "Jane",
            "specialty": "yoga",
            "location": "NYC",
        })
        result = handler(event, None)
        assert result["statusCode"] == 201
        body = json.loads(result["body"])
        assert body["instructor_id"] == "inst-1"
        assert body["display_name"] == "Jane"

    def test_rejects_non_instructor(self):
        from instructors.create_profile import handler

        event = _make_event("client-1", "client", body={
            "display_name": "Jane",
            "specialty": "yoga",
            "location": "NYC",
        })
        result = handler(event, None)
        assert result["statusCode"] == 403

    def test_rejects_missing_fields(self):
        from instructors.create_profile import handler

        event = _make_event("inst-1", "instructor", body={"display_name": "Jane"})
        result = handler(event, None)
        assert result["statusCode"] == 400

    def test_rejects_duplicate_profile(self):
        from instructors.create_profile import handler

        event = _make_event("inst-1", "instructor", body={
            "display_name": "Jane",
            "specialty": "yoga",
            "location": "NYC",
        })
        handler(event, None)
        result = handler(event, None)
        assert result["statusCode"] == 409
