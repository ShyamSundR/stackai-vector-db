"""
Exception classes for StackAI SDK
"""


class StackAIException(Exception):
    """Base exception for all StackAI SDK errors"""
    pass


class APIException(StackAIException):
    """Exception raised when API returns an error response"""
    
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")


class ValidationException(StackAIException):
    """Exception raised for client-side validation errors"""
    pass


class ConnectionException(StackAIException):
    """Exception raised when unable to connect to the API"""
    pass


class TimeoutException(StackAIException):
    """Exception raised when API request times out"""
    pass 