import hashlib, base64, math, random
from fastapi import HTTPException, status
import pandas as pd
from datetime import datetime
from typing import Any

from api.auth import JWT


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

def create_id(s1, s2, s3 = None):
    if s3 is None:
        s3 = random.randrange(0, 999)
    hashed1 = hash_with_base64(s1, 16)
    hashed2 = hash_with_base64(s2, 12)
    hashed3 = hash_with_base64(s3, 4)

    id = f"{hashed1}-{hashed2}.{hashed3}=="
    return id

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