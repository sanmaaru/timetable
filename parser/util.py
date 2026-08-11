import hashlib
import math
from datetime import datetime
from typing import Any
import pandas as pd

def is_empty(value: Any) -> bool:
    # None
    if value is None:
        return True

    # pandas/NumPy NaN
    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        pass

    # pandas.isna (np.nan, pd.NA 등)
    try:
        if pd.isna(value):
            return True
    except TypeError:
        pass

    # 문자열 처리
    if isinstance(value, str):
        if value.strip() == "":
            return True
        if value.strip().lower() == "nan":
            return True

    return False


def get_generation(grade: int):
    return (datetime.now().year - 1983) - (grade-1)


def get_grade(generation: int):
    return datetime.now().year - 1983 - generation + 1


def generate_identity_id(number: int, generation: int, name: str):
    num_str = str(number % 10)
    gen_str = f"{generation:02d}"[-2:]

    hashed_bytes = hashlib.sha256(name.encode("utf-8")).hexdigest()
    hashed_name = hashed_bytes[:12]

    result = f"{num_str}{gen_str}-{hashed_name}"
    return result
