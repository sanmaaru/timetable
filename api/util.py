import hashlib, base64

def hash_with_base64(data, length: int):
    if length % 4 != 0:
        raise ValueError('Invalid lenght')

    hash_len = length // 4 * 3

    hasher = hashlib.shake_256()
    hasher.update(data)
    hashed_byte = hasher.digest(hash_len)

    hashed_b64 = base64.b64decode(hashed_byte).decode('ascii')

    return hashed_b64 