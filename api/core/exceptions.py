class NullValueException(Exception):

    def __init__(self, message: str, invalid: str):
        self.message = message
        self.invalid = invalid