import json
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "handlers")
)

from shared.responses import (
    success_response,
    created_response,
    error_response,
    not_found_response,
    forbidden_response,
    server_error_response,
)


class TestSuccessResponse:
    def test_default_status_code(self):
        result = success_response({"key": "value"})
        assert result["statusCode"] == 200

    def test_custom_status_code(self):
        result = success_response({"key": "value"}, status_code=202)
        assert result["statusCode"] == 202

    def test_body_is_json_string(self):
        result = success_response({"key": "value"})
        body = json.loads(result["body"])
        assert body["key"] == "value"

    def test_cors_headers(self):
        result = success_response({})
        assert result["headers"]["Access-Control-Allow-Origin"] == "*"


class TestCreatedResponse:
    def test_status_code_201(self):
        result = created_response({"id": "123"})
        assert result["statusCode"] == 201


class TestErrorResponse:
    def test_default_400(self):
        result = error_response("bad input")
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "bad input"


class TestNotFoundResponse:
    def test_status_404(self):
        result = not_found_response()
        assert result["statusCode"] == 404


class TestForbiddenResponse:
    def test_status_403(self):
        result = forbidden_response()
        assert result["statusCode"] == 403
        body = json.loads(result["body"])
        assert body["error"] == "Access denied"


class TestServerErrorResponse:
    def test_status_500(self):
        result = server_error_response()
        assert result["statusCode"] == 500
