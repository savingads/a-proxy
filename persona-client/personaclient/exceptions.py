"""
Exception classes for the Persona API Client
"""


class PersonaClientError(Exception):
    """Base exception for all client errors"""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class PersonaNotFoundError(PersonaClientError):
    """Raised when a persona is not found"""

    def __init__(self, persona_id, status_code=404, response=None):
        message = f"Persona with ID {persona_id} not found"
        super().__init__(message, status_code, response)
        self.persona_id = persona_id


class PersonaValidationError(PersonaClientError):
    """Raised when there's a validation error with persona data"""

    def __init__(self, message, errors=None, status_code=400, response=None):
        super().__init__(message, status_code, response)
        self.errors = errors or {}

    def __str__(self):
        if self.errors:
            error_str = ", ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in self.errors.items()
            )
            return f"{self.message}: {error_str}"
        return self.message


class PersonaAPIError(PersonaClientError):
    """Raised when there's an error from the API"""

    def __init__(self, message, status_code=500, response=None):
        super().__init__(message, status_code, response)
