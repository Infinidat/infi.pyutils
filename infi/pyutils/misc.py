import itertools

def renumerate(seq):
    """Like enumerate(), only in reverse order. Useful for filtering a list in place"""
    if isinstance(seq, list) or isinstance(seq, tuple):
        return _renumerate_lazy(seq)
    return _renumerate_strict(seq)

def _renumerate_lazy(seq):
    for index in xrange(len(seq)-1, -1, -1):
        yield index, seq[index]
def _renumerate_strict(seq):
    return reversed(list(enumerate(seq)))
