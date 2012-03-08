_NOTHING = object()

def recursive_getattr(obj, attr, default=_NOTHING):
    for subattr in attr.split("."):
        obj = getattr(obj, subattr, _NOTHING)
        if obj is _NOTHING:
            if default is not _NOTHING:
                return default
            raise AttributeError(attr)
    return obj
