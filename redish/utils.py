import operator


def maybe_list(value):
    # FIXME
    if not operator.isSequenceType(value):
        return [value]
    return value


def key(names):
    return ":".join(maybe_list(names))
