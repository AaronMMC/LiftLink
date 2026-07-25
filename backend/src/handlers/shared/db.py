import os

import boto3


TABLE_NAME_ENV = "TABLE_NAME"
GSI1_NAME = "SpecialtyLocationIndex"


def get_table_name() -> str:
    """Return the DynamoDB table name from environment."""
    return os.environ.get(TABLE_NAME_ENV, "LiftLinkTable")


def get_dynamodb_resource():
    """Return a boto3 DynamoDB resource."""
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
    if endpoint_url:
        return boto3.resource("dynamodb", endpoint_url=endpoint_url)
    return boto3.resource("dynamodb")


def get_table():
    """Return the DynamoDB table object."""
    return get_dynamodb_resource().Table(get_table_name())


def instructor_pk(instructor_id: str) -> str:
    """Build PK for an instructor profile."""
    return f"INSTRUCTOR#{instructor_id}"


def instructor_sk() -> str:
    """Build SK for an instructor profile."""
    return "PROFILE"


def progress_pk(client_id: str) -> str:
    """Build PK for progress entries scoped to a client."""
    return f"PROGRESS#{client_id}"


def progress_sk(timestamp: str, entry_id: str) -> str:
    """Build SK for a specific progress entry."""
    return f"ENTRY#{timestamp}#{entry_id}"


def instructor_progress_pk(instructor_id: str) -> str:
    """Build PK for progress entries scoped to an instructor."""
    return f"INSTRUCTOR_PROGRESS#{instructor_id}"


def instructor_progress_sk(timestamp: str, entry_id: str) -> str:
    """Build SK for an instructor's progress entry."""
    return f"ENTRY#{timestamp}#{entry_id}"


def gsi1_pk(specialty: str) -> str:
    """Build GSI1 PK for instructor search by specialty."""
    return f"SPECIALTY#{specialty.upper()}"


def gsi1_sk(location: str) -> str:
    """Build GSI1 SK for instructor search by location."""
    return f"LOCATION#{location.upper()}"
