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
    for i, (spec, loc) in enumerate([("YOGA", "NYC"), ("YOGA", "LA"), ("PILATES", "NYC")]):
        table.put_item(Item={
            "PK": f"INSTRUCTOR#inst-{i}",
            "SK": "PROFILE",
            "GSI1PK": f"SPECIALTY#{spec}",
            "GSI1SK": f"LOCATION#{loc}",
            "instructor_id": f"inst-{i}",
            "display_name": f"Instructor {i}",
            "specialty": spec.lower(),
            "location": loc,
            "bio": "",
            "item_type": "INSTRUCTOR",
        })
    return table


def _make_event(sub: str, role: str, query_params: dict = None) -> dict:
    event = {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {"sub": sub, "custom:user_role": role}
                }
            }
        }
    }
    if query_params:
        event["queryStringParameters"] = query_params
    return event


@mock_aws
class TestSearchInstructors:
    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table_and_seed(self.dynamodb)

    def test_search_by_specialty(self):
        from instructors.search_instructors import handler

        event = _make_event("client-1", "client", query_params={"specialty": "yoga"})
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 2

    def test_search_by_specialty_and_location(self):
        from instructors.search_instructors import handler

        event = _make_event("client-1", "client", query_params={"specialty": "yoga", "location": "NYC"})
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 1

    def test_missing_specialty_returns_400(self):
        from instructors.search_instructors import handler

        event = _make_event("client-1", "client", query_params={})
        result = handler(event, None)
        assert result["statusCode"] == 400

    def test_no_results(self):
        from instructors.search_instructors import handler

        event = _make_event("client-1", "client", query_params={"specialty": "boxing"})
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 0
