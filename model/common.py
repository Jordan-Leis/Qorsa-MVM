"""Helpers shared by the ML-KEM and ML-DSA models.

Coefficients are canonical integers in [0, q) everywhere (FIPS convention).
"""

N = 256


def bitrev(x, bits):
    """Reverse the low `bits` bits of x (BitRev7 / BitRev8 in the FIPS texts)."""
    r = 0
    for _ in range(bits):
        r = (r << 1) | (x & 1)
        x >>= 1
    return r


def schoolbook_negacyclic(f, g, q):
    """f*g in Z_q[X]/(X^256 + 1), computed directly in O(n^2).

    Used only to check the NTT path. X^256 = -1, so terms that wrap past
    degree 255 are subtracted, not added.
    """
    h = [0] * N
    for i in range(N):
        for j in range(N):
            k = i + j
            if k < N:
                h[k] += f[i] * g[j]
            else:
                h[k - N] -= f[i] * g[j]
    return [c % q for c in h]


def poly_add(f, g, q):
    return [(a + b) % q for a, b in zip(f, g)]


def matvec(A, s, mul, q):
    """(A∘s)[i] = sum over j of A[i][j]∘s[j] (FIPS 203 section 2.4.7).

    A is a list of rows, so A[i][j] is row i, column j. `mul` is the
    NTT-domain polynomial product for the scheme.
    """
    out = []
    for row in A:
        acc = [0] * N
        for a_ij, s_j in zip(row, s):
            acc = poly_add(acc, mul(a_ij, s_j), q)
        out.append(acc)
    return out
