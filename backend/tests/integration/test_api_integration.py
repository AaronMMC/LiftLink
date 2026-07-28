import json
import os
import sys

import boto3
import pytest
from moto import mock_aws

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers")
)

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


def _make_event(
    sub: str,
    role: str,
    body: dict = None,
    path_params: dict = None,
    query_params: dict = None,
) -> dict:
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
class TestProfileCreateAndRetrieve:
    """Create an instructor profile, then retrieve it — verify round-trip."""

    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_create_then_get_profile(self):
        from instructors import create_profile, get_profile

        user_id = "instructor-001"
        create_event = _make_event(
            sub=user_id,
            role="instructor",
            body={
                "display_name": "Jane Smith",
                "specialty": "yoga",
                "location": "New York",
                "bio": "Certified yoga instructor with 10 years experience.",
            },
        )
        create_res = create_profile.handler(create_event, None)
        assert create_res["statusCode"] == 201
        created = json.loads(create_res["body"])
        assert created["display_name"] == "Jane Smith"
        assert created["instructor_id"] == user_id

        get_event = _make_event(
            sub=user_id,
            role="instructor",
            path_params={"id": user_id},
        )
        get_res = get_profile.handler(get_event, None)
        assert get_res["statusCode"] == 200
        profile = json.loads(get_res["body"])
        assert profile["display_name"] == "Jane Smith"
        assert profile["specialty"] == "yoga"
        assert profile["location"] == "New York"
        assert profile["bio"] == "Certified yoga instructor with 10 years experience."


@mock_aws
class TestProgressEntryAndHistory:
    """Instructor logs a progress entry, client retrieves their own history."""

    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_create_entry_then_get_history(self):
        from clients import get_history
        from progress import create_entry

        instructor_id = "instructor-010"
        client_id = "client-020"

        entry_event = _make_event(
            sub=instructor_id,
            role="instructor",
            body={
                "client_id": client_id,
                "workout_type": "Strength Training",
                "notes": "Bench press 3x10, squats 4x8, deadlift 3x5.",
                "duration_minutes": 75,
            },
        )
        entry_res = create_entry.handler(entry_event, None)
        assert entry_res["statusCode"] == 201
        entry_data = json.loads(entry_res["body"])
        assert entry_data["client_id"] == client_id
        assert entry_data["instructor_id"] == instructor_id

        history_event = _make_event(
            sub=client_id,
            role="client",
            path_params={"id": client_id},
        )
        history_res = get_history.handler(history_event, None)
        assert history_res["statusCode"] == 200
        history = json.loads(history_res["body"])
        assert history["count"] == 1
        assert history["entries"][0]["workout_type"] == "Strength Training"
        assert history["entries"][0]["notes"] == "Bench press 3x10, squats 4x8, deadlift 3x5."
        assert history["entries"][0]["duration_minutes"] == 75


@mock_aws
class TestAdversarialAuthorization:
    """Client B must not read Client A's history — the critical 403 boundary."""

    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_cross_client_access_denied(self):
        from clients import get_history
        from progress import create_entry

        instructor_id = "instructor-adv"
        client_a = "client-A"
        client_b = "client-B"

        create_entry.handler(
            _make_event(
                sub=instructor_id,
                role="instructor",
                body={
                    "client_id": client_a,
                    "workout_type": "Cardio",
                    "notes": "30 min HIIT session.",
                    "duration_minutes": 30,
                },
            ),
            None,
        )

        client_a_event = _make_event(
            sub=client_a,
            role="client",
            path_params={"id": client_a},
        )
        res_a = get_history.handler(client_a_event, None)
        assert res_a["statusCode"] == 200
        assert json.loads(res_a["body"])["count"] == 1

        client_b_event = _make_event(
            sub=client_b,
            role="client",
            path_params={"id": client_a},
        )
        res_b = get_history.handler(client_b_event, None)
        assert res_b["statusCode"] == 403
        assert "own" in json.loads(res_b["body"])["error"].lower()

    def test_instructor_cannot_view_client_history(self):
        from clients import get_history

        instructor_event = _make_event(
            sub="instructor-sneaky",
            role="instructor",
            path_params={"id": "client-target"},
        )
        res = get_history.handler(instructor_event, None)
        assert res["statusCode"] == 403


@mock_aws
class TestInstructorSearch:
    """Create profiles with different specialties, verify search returns correct results."""

    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_search_by_specialty_and_location(self):
        from instructors import create_profile, search_instructors

        profiles = [
            ("inst-s1", "yoga", "New York", "Alice"),
            ("inst-s2", "yoga", "Los Angeles", "Bob"),
            ("inst-s3", "strength", "New York", "Charlie"),
        ]
        for uid, spec, loc, name in profiles:
            create_profile.handler(
                _make_event(
                    sub=uid,
                    role="instructor",
                    body={
                        "display_name": name,
                        "specialty": spec,
                        "location": loc,
                        "bio": f"{name}'s bio",
                    },
                ),
                None,
            )

        yoga_event = _make_event(
            sub="any-user",
            role="client",
            query_params={"specialty": "yoga"},
        )
        yoga_res = search_instructors.handler(yoga_event, None)
        assert yoga_res["statusCode"] == 200
        yoga_data = json.loads(yoga_res["body"])
        assert yoga_data["count"] == 2

        yoga_ny_event = _make_event(
            sub="any-user",
            role="client",
            query_params={"specialty": "yoga", "location": "New York"},
        )
        yoga_ny_res = search_instructors.handler(yoga_ny_event, None)
        assert yoga_ny_res["statusCode"] == 200
        yoga_ny_data = json.loads(yoga_ny_res["body"])
        assert yoga_ny_data["count"] == 1
        assert yoga_ny_data["instructors"][0]["display_name"] == "Alice"


@mock_aws
class TestProfileUpdate:
    """Update an instructor profile and verify the changes persist."""

    def setup_method(self, method=None):
        os.environ["TABLE_NAME"] = TABLE_NAME
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        _create_table(self.dynamodb)

    def test_update_profile_persists(self):
        from instructors import create_profile, get_profile, update_profile

        user_id = "inst-upd"

        create_profile.handler(
            _make_event(
                sub=user_id,
                role="instructor",
                body={
                    "display_name": "Original Name",
                    "specialty": "cardio",
                    "location": "Chicago",
                    "bio": "Original bio.",
                },
            ),
            None,
        )

        update_event = _make_event(
            sub=user_id,
            role="instructor",
            path_params={"id": user_id},
            body={
                "display_name": "Updated Name",
                "specialty": "strength",
                "location": "Austin",
                "bio": "Updated bio with new credentials.",
            },
        )
        update_res = update_profile.handler(update_event, None)
        assert update_res["statusCode"] == 200

        get_event = _make_event(
            sub=user_id,
            role="instructor",
            path_params={"id": user_id},
        )
        get_res = get_profile.handler(get_event, None)
        assert get_res["statusCode"] == 200
        profile = json.loads(get_res["body"])
        assert profile["display_name"] == "Updated Name"
        assert profile["specialty"] == "strength"
        assert profile["location"] == "Austin"
        assert profile["bio"] == "Updated bio with new credentials."

    def test_non_owner_update_rejected(self):
        from instructors import create_profile, update_profile

        owner_id = "inst-owner"
        intruder_id = "inst-intruder"

        create_profile.handler(
            _make_event(
                sub=owner_id,
                role="instructor",
                body={
                    "display_name": "Owner",
                    "specialty": "yoga",
                    "location": "Miami",
                    "bio": "My profile.",
                },
            ),
            None,
        )

        update_event = _make_event(
            sub=intruder_id,
            role="instructor",
            path_params={"id": owner_id},
            body={
                "display_name": "Hacked",
                "specialty": "yoga",
                "location": "Miami",
                "bio": "Intruder bio.",
            },
        )
        update_res = update_profile.handler(update_event, None)
        assert update_res["statusCode"] == 403
