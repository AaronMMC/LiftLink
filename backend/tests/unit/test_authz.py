import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers"))

from shared.authz import get_user_id, get_user_role, is_resource_owner, is_instructor, is_client


def _make_event(sub: str = "user-123", role: str = "instructor") -> dict:
    return {
        "requestContext": {
            "authorizer": {
                "jwt": {
                    "claims": {
                        "sub": sub,
                        "custom:user_role": role,
                    }
                }
            }
        }
    }


class TestGetUserId:
    def test_extracts_sub(self):
        assert get_user_id(_make_event(sub="abc")) == "abc"

    def test_returns_none_for_missing_claims(self):
        assert get_user_id({}) is None

    def test_returns_none_for_malformed_event(self):
        assert get_user_id({"requestContext": {}}) is None


class TestGetUserRole:
    def test_extracts_role(self):
        assert get_user_role(_make_event(role="client")) == "client"

    def test_returns_none_for_missing(self):
        assert get_user_role({}) is None


class TestIsResourceOwner:
    def test_owner_matches(self):
        assert is_resource_owner(_make_event(sub="user-1"), "user-1") is True

    def test_owner_mismatch(self):
        assert is_resource_owner(_make_event(sub="user-1"), "user-2") is False

    def test_missing_sub(self):
        assert is_resource_owner({}, "user-1") is False


class TestIsInstructor:
    def test_instructor_role(self):
        assert is_instructor(_make_event(role="instructor")) is True

    def test_client_role(self):
        assert is_instructor(_make_event(role="client")) is False


class TestIsClient:
    def test_client_role(self):
        assert is_client(_make_event(role="client")) is True

    def test_instructor_role(self):
        assert is_client(_make_event(role="instructor")) is False
