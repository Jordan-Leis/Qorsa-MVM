"""ML-DSA (FIPS 204) NTT arithmetic. q = 8380417, zeta = 1753.

The NTT is complete (8 layers), so an NTT-domain product is 256 pointwise
multiplications.
"""

from common import N, bitrev, matvec

Q = 8380417
ZETA = 1753
K, L = 6, 5  # ML-DSA-65: A is k x l

# zetas[m] = 1753^BitRev8(m) mod q, m = 0..255 (FIPS 204 Appendix B)
ZETAS = [pow(ZETA, bitrev(m, 8), Q) for m in range(256)]

N_INV = 8347681  # 256^-1 mod 8380417, the final scale in Algorithm 42


def ntt(w):
    """FIPS 204 Algorithm 41."""
    w = list(w)
    m = 0
    length = 128
    while length >= 1:
        for start in range(0, N, 2 * length):
            m += 1
            z = ZETAS[m]
            for j in range(start, start + length):
                t = z * w[j + length] % Q
                w[j + length] = (w[j] - t) % Q
                w[j] = (w[j] + t) % Q
        length //= 2
    return w


def ntt_inv(w):
    """FIPS 204 Algorithm 42."""
    w = list(w)
    m = 256
    length = 1
    while length < N:
        for start in range(0, N, 2 * length):
            m -= 1
            z = -ZETAS[m]
            for j in range(start, start + length):
                t = w[j]
                w[j] = (t + w[j + length]) % Q
                w[j + length] = z * (t - w[j + length]) % Q
        length *= 2
    return [c * N_INV % Q for c in w]


def multiply_ntt(a, b):
    """Pointwise product of two NTT-domain polynomials (FIPS 204 Algorithm 45)."""
    return [x * y % Q for x, y in zip(a, b)]


def matvec_ntt(A, s):
    """A∘s for NTT-domain A (k x l) and s (length l)."""
    return matvec(A, s, multiply_ntt, Q)
