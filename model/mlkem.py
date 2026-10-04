"""ML-KEM (FIPS 203) NTT arithmetic. q = 3329, zeta = 17.

The NTT stops one layer early (7 layers), so an NTT-domain product is 128
degree-1 base-case products modulo (X^2 - gamma_i).
"""

from common import N, bitrev, matvec

Q = 3329
ZETA = 17
K = 3  # ML-KEM-768

# zetas[i] = 17^BitRev7(i) mod q, i = 0..127 (FIPS 203 Appendix A, first table)
ZETAS = [pow(ZETA, bitrev(i, 7), Q) for i in range(128)]

# gammas[i] = 17^(2*BitRev7(i)+1) mod q, i = 0..127 (FIPS 203 Appendix A, second table)
GAMMAS = [pow(ZETA, 2 * bitrev(i, 7) + 1, Q) for i in range(128)]

N_INV = 3303  # 128^-1 mod 3329, the final scale in Algorithm 10


def ntt(f):
    """FIPS 203 Algorithm 9."""
    f = list(f)
    i = 1
    length = 128
    while length >= 2:
        for start in range(0, N, 2 * length):
            zeta = ZETAS[i]
            i += 1
            for j in range(start, start + length):
                t = zeta * f[j + length] % Q
                f[j + length] = (f[j] - t) % Q
                f[j] = (f[j] + t) % Q
        length //= 2
    return f


def ntt_inv(f):
    """FIPS 203 Algorithm 10."""
    f = list(f)
    i = 127
    length = 2
    while length <= 128:
        for start in range(0, N, 2 * length):
            zeta = ZETAS[i]
            i -= 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % Q
                f[j + length] = zeta * (f[j + length] - t) % Q
        length *= 2
    return [c * N_INV % Q for c in f]


def base_case_multiply(a0, a1, b0, b1, gamma):
    """FIPS 203 Algorithm 12: (a0 + a1 X)(b0 + b1 X) mod (X^2 - gamma)."""
    c0 = (a0 * b0 + a1 * b1 * gamma) % Q
    c1 = (a0 * b1 + a1 * b0) % Q
    return c0, c1


def multiply_ntts(f, g):
    """FIPS 203 Algorithm 11."""
    h = [0] * N
    for i in range(128):
        h[2 * i], h[2 * i + 1] = base_case_multiply(
            f[2 * i], f[2 * i + 1], g[2 * i], g[2 * i + 1], GAMMAS[i])
    return h


def matvec_ntt(A, s):
    """A∘s for NTT-domain A (k x k) and s (length k)."""
    return matvec(A, s, multiply_ntts, Q)
