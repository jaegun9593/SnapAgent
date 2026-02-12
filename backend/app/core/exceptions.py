"""
Custom exception classes for the application.
"""
from typing import Any, Optional


class AppException(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(message=message, status_code=404, error_code=error_code)


class UnauthorizedError(AppException):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Unauthorized", error_code: str = "UNAUTHORIZED"):
        super().__init__(message=message, status_code=401, error_code=error_code)


class ForbiddenError(AppException):
    """Raised when access is forbidden (403)."""

    def __init__(self, message: str = "Forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(message=message, status_code=403, error_code=error_code)


class ConflictError(AppException):
    """Raised when there's a conflict (409), e.g., duplicate email."""

    def __init__(self, message: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(message=message, status_code=409, error_code=error_code)


class ValidationError(AppException):
    """Raised when validation fails (422)."""

    def __init__(
        self,
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message, status_code=422, error_code=error_code, details=details
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT"):
        super().__init__(message=message, status_code=429, error_code=error_code)


class TokenLimitExceededError(AppException):
    """Raised when token usage limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Token limit exceeded",
        error_code: str = "TOKEN_LIMIT_EXCEEDED",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message, status_code=429, error_code=error_code, details=details
        )


class InternalServerError(AppException):
    """Raised for internal server errors (500)."""

    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message, status_code=500, error_code=error_code, details=details
        )


class ServiceUnavailableError(AppException):
    """Raised when a service is temporarily unavailable (503)."""

    def __init__(
        self, message: str = "Service unavailable", error_code: str = "SERVICE_UNAVAILABLE"
    ):
        super().__init__(message=message, status_code=503, error_code=error_code)
