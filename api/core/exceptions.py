from flask import Flask, jsonify


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ApiError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ConflictError(ApiError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, 409)


class UnauthorizedError(ApiError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify({"error": err.message}), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(_err: Exception):
        return jsonify({"error": "Internal server error"}), 500
