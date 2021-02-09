import random
from datetime import datetime
import zlib


__all__ = (
    "base36_dumps",
    "base36_loads",
    "unique_id",
    "timestamp_from_id"
)


base36 = '0123456789abcdefghijklmnopqrstuvwxyz'


def base36_dumps(number: int):
    if number < 0:
        return '-' + base36_dumps(-number)

    value = ''

    while number != 0:
        number, index = divmod(number, len(base36))
        value = base36[index] + value

    return value or '0'


def base36_loads(value):
    return int(value, len(base36))


def unique_id():
    """
    Generates a unique id consisting of the the unix timestamp and 8 random bits
    """
    unix_t = int(datetime.utcnow().timestamp() * 1000)
    result = (unix_t << 8) | random.getrandbits(8)
    return base36_dumps(result)


def timestamp_from_id(uid):
    return datetime.utcfromtimestamp((base36_loads(uid) >> 8) / 1000)


def chunk_blob(blob: bytes, size_limit=7000000):
    """
    Chunk bytes into up to 256 chunks with size of up to 'size_limit' bytes
    """
    compressed = bytearray(zlib.compress(blob))
    chunks = []

    chunk_number = 0
    while len(compressed) > size_limit:
        chunk = compressed[:size_limit]
        compressed = compressed[size_limit:]

        chunk.insert(0, chunk_number)
        chunks.append(bytes(chunk))

        chunk_number += 1

    if len(compressed) > 0:
        compressed.insert(0, chunk_number)
        chunks.append(bytes(compressed))

    return chunks


def combine_chunks(chunks):
    sorted_chunks = sorted([bytearray(c) for c in chunks], key=lambda c: c[0])
    result = bytearray()
    for chunk in sorted_chunks:
        result.extend(chunk[1:])

    return zlib.decompress(bytes(result))
