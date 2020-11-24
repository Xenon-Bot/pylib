import random
from datetime import datetime, timedelta


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


def datetime_to_string(dt: datetime):
    return dt.strftime("%d. %b %Y - %H:%M")


def timedelta_to_string(td: timedelta):
    seconds = td.total_seconds()
    if seconds == 0:
        return "0s"

    units = (
        ("w", 7 * 24 * 60 * 60),
        ("d", 24 * 60 * 60),
        ("h", 60 * 60),
        ("m", 60),
        ("s", 1)
    )

    result = ""
    for unit, mp in units:
        count, seconds = divmod(seconds, mp)
        if count > 0:
            result += f" {int(count)}{unit}"

    return result.strip()
