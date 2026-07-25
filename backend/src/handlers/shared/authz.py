from typing import Optional


def get_user_id(event: dict) -> Optional[str]:
    """Extract the authenticated user's sub (ID) from the API Gateway event."""
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except (KeyError, TypeError):
        return None


def get_user_role(event: dict) -> Optional[str]:
    """Extract the user's role (instructor/client) from JWT claims."""
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]["custom:user_role"]
    except (KeyError, TypeError):
        return None


def is_resource_owner(event: dict, resource_owner_id: str) -> bool:
    """Check if the authenticated user owns the specified resource."""
    user_id = get_user_id(event)
    if user_id is None:
        return False
    return user_id == resource_owner_id


def is_instructor(event: dict) -> bool:
    """Check if the authenticated user has the instructor role."""
    return get_user_role(event) == "instructor"


def is_client(event: dict) -> bool:
    """Check if the authenticated user has the client role."""
    return get_user_role(event) == "client"
