def wer(r, h):
    """
    Calculation of WER with Levenshtein distance.
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list

    Returns
    -------
    int

    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    >>> wer("".split(), "who is there".split())
    3
    """
    # initialisation
    import numpy

    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.int32)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    backtrack = numpy.zeros((len(r)+1, len(h)+1), dtype=numpy.int32)
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                backtrack[0][j] = 2
            elif j == 0:
                backtrack[i][0] = 3

    inserts = 0
    deletes = 0
    substitutes = 0

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
                backtrack[i,j] = 0
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

                if d[i][j] == substitution:
                    backtrack[i,j] = 1
                elif d[i][j] == insertion:
                    backtrack[i,j] = 2
                else:
                    backtrack[i,j] = 3

    # Backtrack solution
    i,j = len(r), len(h)
    while i > 0 or j > 0:
        if backtrack[i,j] == 0:
            i,j = i-1, j-1
        elif backtrack[i,j] == 1:
            i,j = i - 1, j - 1
            substitutes += 1
        elif backtrack[i, j] == 2:
            i,j = [i, j - 1]
            inserts += 1
        else:
            i,j = [i - 1, j]
            deletes += 1

    return 100.0 * d[len(r)][len(h)] / len(r), inserts, deletes, substitutes, len(r)

def compute_wer_from_file(r, h):
    with open(r, "r") as f:
        rs = f.read().strip().lower().replace("\n", " ").split(" ")
    with open(h, "r") as f:
        hs = f.read().strip().lower().replace("\n", " ").split(" ")
    return wer(rs, hs)