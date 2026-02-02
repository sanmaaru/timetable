class AuthorizationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

class RefreshTokenError(AuthorizationError):
    pass
