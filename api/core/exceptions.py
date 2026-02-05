class NullValueException(Exception):

    def __init__(self, message: str, invalid: str):
        self.message = message
        self.invalid = invalid

def exception_to_object(e: Exception):
    error_info = vars(e).copy()
    error_info["args"] = e.args
    error_info["exception"] = type(e).__name__

    return error_info