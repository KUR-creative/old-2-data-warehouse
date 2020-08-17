import funcy as F

def modulo_pad(x, m):
    ''' 2a = x + modulo_pad (mod m), where a < x < 2a '''
    return (m - (x % m)) % m

def partition(x, size):
    ''' 
    x => [x0, x1), [x1, x2), ... , [xN-1, x),
    all same sized intervals. 
    '''
    assert x % size == 0
    def multipleseq():
        beg = 0
        max = x + size
        while beg != max:
            yield beg
            beg += size

    parts = list(F.pairwise(multipleseq()))
    return parts if parts else [(0, x)]
