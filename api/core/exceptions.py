class NullValueException(Exception):

    def __init__(self, message: str, invalid: str):
        self.message = message
        self.invalid = invalid

class UnknownValueException(Exception):

    def __init__(self, message: str, invalid: str):
        self.message = message
        self.invalid = invalid

def exception_to_object(e: Exception):
    if hasattr(e, '__dict__'):
        error_info = vars(e).copy()
        error_info["args"] = e.args
        error_info["exception"] = type(e).__name__
    else:
        error_info = {
            "message": str(e),
            "type": type(e).__name__,
            "args": getattr(e, 'args', []),
        }

    return error_info