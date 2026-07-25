import json
from decimal import Decimal
from typing import Any


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def success_response(body: Any, status_code: int = 200) -> dict:
    """Return a successful HTTP response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }

def created_response(body: Any) -> dict:
    """Return a 201 Created response."""
    return success_response(body, status_code=201)


def error_response(message: str, status_code: int = 400) -> dict:
    """Return an error HTTP response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps({"error": message}),
    }


def not_found_response(message: str = "Resource not found") -> dict:
    """Return a 404 Not Found response."""
    return error_response(message, status_code=404)


def forbidden_response(message: str = "Access denied") -> dict:
    """Return a 403 Forbidden response."""
    return error_response(message, status_code=403)


def server_error_response(message: str = "Internal server error") -> dict:
    """Return a 500 Internal Server Error response."""
    return error_response(message, status_code=500)
