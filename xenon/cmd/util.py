__all__ = (
    "list_get",
)


def list_get(iterable, **keys):
    for thing in iterable:
        for key, value in keys.items():
            if getattr(thing, key) != value:
                break

        else:
            return thing
