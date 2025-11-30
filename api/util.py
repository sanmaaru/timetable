import hashlib, base64, math
import pandas as pd
from datetime import datetime
from typing import Any

def hash_with_base64(data, length: int):
    if length % 4 != 0:
        raise ValueError('Invalid lenght')
    data = str(data).encode('utf-8')
    hash_len = length // 4 * 3

    hasher = hashlib.shake_256()
    hasher.update(data)
    hashed_byte = hasher.digest(hash_len)

    hashed_b64 = base64.b64encode(hashed_byte).decode('ascii')

    return hashed_b64 

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