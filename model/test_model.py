"""Independent validation of the golden model (PLAN.md, M1).

Nothing here trusts the NTT code: products are checked against the O(n^2)
schoolbook negacyclic product, and constants against number theory.

Run from the repo root:  python3 -m unittest discover -s model -v
"""

import random
import unittest

import mldsa
import mlkem
from common import N, poly_add, schoolbook_negacyclic

TRIALS = 20


def rand_poly(rng, q):
    return [rng.randrange(q) for _ in range(N)]


class RootsAndConstants(unittest.TestCase):

    def test_mlkem_zeta_is_primitive_256th_root(self):
        q = mlkem.Q
        self.assertEqual(pow(17, 128, q), q - 1)  # 17^128 = -1, so order is exactly 256

    def test_mlkem_has_no_512th_root(self):
        # The group Z_q* has order q-1 = 3328 = 2^8 * 13, so no element has order 512.
        # That is why ML-KEM's NTT stops at 7 layers.
        self.assertNotEqual((mlkem.Q - 1) % 512, 0)

    def test_mldsa_zeta_is_primitive_512th_root(self):
        q = mldsa.Q
        self.assertEqual(pow(1753, 256, q), q - 1)

    def test_inverse_scale_factors(self):
        self.assertEqual(pow(128, -1, mlkem.Q), mlkem.N_INV)
        self.assertEqual(pow(256, -1, mldsa.Q), mldsa.N_INV)

    def test_mlkem_gamma_table(self):
        q, g = mlkem.Q, mlkem.GAMMAS
        self.assertEqual(len(set(g)), 128)
        for i in range(128):
            self.assertEqual(pow(g[i], 128, q), q - 1)  # each gamma is a root of X^128 + 1
        for i in range(64):
            self.assertEqual((g[2 * i] + g[2 * i + 1]) % q, 0)  # pairs are +/- each other


class TransformRoundTrip(unittest.TestCase):

    def check(self, scheme, seed):
        rng = random.Random(seed)
        for _ in range(TRIALS):
            f = rand_poly(rng, scheme.Q)
            self.assertEqual(scheme.ntt_inv(scheme.ntt(f)), f)

    def test_mlkem(self):
        self.check(mlkem, 1)

    def test_mldsa(self):
        self.check(mldsa, 2)


class ProductMatchesSchoolbook(unittest.TestCase):

    def check(self, scheme, mul, seed):
        rng = random.Random(seed)
        q = scheme.Q
        edge = [[q - 1] * N, [0] * N, [1] + [0] * (N - 1), [0] * (N - 1) + [1]]
        cases = [(a, b) for a in edge for b in edge]
        cases += [(rand_poly(rng, q), rand_poly(rng, q)) for _ in range(TRIALS)]
        for f, g in cases:
            got = scheme.ntt_inv(mul(scheme.ntt(f), scheme.ntt(g)))
            self.assertEqual(got, schoolbook_negacyclic(f, g, q))

    def test_mlkem(self):
        self.check(mlkem, mlkem.multiply_ntts, 3)

    def test_mldsa(self):
        self.check(mldsa, mldsa.multiply_ntt, 4)


class MatvecMatchesSchoolbook(unittest.TestCase):
    """A∘s in the NTT domain equals the schoolbook A*s, row by row.

    A is random, so it is not symmetric: swapping rows and columns would fail.
    """

    def check(self, scheme, rows, cols, seed):
        rng = random.Random(seed)
        q = scheme.Q
        A = [[rand_poly(rng, q) for _ in range(cols)] for _ in range(rows)]
        s = [rand_poly(rng, q) for _ in range(cols)]
        A_hat = [[scheme.ntt(a) for a in row] for row in A]
        s_hat = [scheme.ntt(x) for x in s]
        got = [scheme.ntt_inv(t) for t in scheme.matvec_ntt(A_hat, s_hat)]
        for i in range(rows):
            want = [0] * N
            for j in range(cols):
                want = poly_add(want, schoolbook_negacyclic(A[i][j], s[j], q), q)
            self.assertEqual(got[i], want, f"row {i}")

    def test_mlkem768(self):
        self.check(mlkem, mlkem.K, mlkem.K, 5)

    def test_mldsa65(self):
        self.check(mldsa, mldsa.K, mldsa.L, 6)


class GammaHoisting(unittest.TestCase):
    """The hardware schedule: c0 = sum(a0 b0) + gamma_i * sum(a1 b1), one gamma multiply per row."""

    def test_hoisted_equals_direct(self):
        rng = random.Random(7)
        q, k = mlkem.Q, mlkem.K
        A_hat = [[rand_poly(rng, q) for _ in range(k)] for _ in range(k)]
        s_hat = [rand_poly(rng, q) for _ in range(k)]
        want = mlkem.matvec_ntt(A_hat, s_hat)
        for r in range(k):
            for i in range(128):
                s00 = s11 = c1 = 0
                for j in range(k):
                    a0, a1 = A_hat[r][j][2 * i], A_hat[r][j][2 * i + 1]
                    b0, b1 = s_hat[j][2 * i], s_hat[j][2 * i + 1]
                    s00 = (s00 + a0 * b0) % q
                    s11 = (s11 + a1 * b1) % q
                    c1 = (c1 + a0 * b1 + a1 * b0) % q
                c0 = (s00 + mlkem.GAMMAS[i] * s11) % q
                self.assertEqual((c0, c1), (want[r][2 * i], want[r][2 * i + 1]))


if __name__ == "__main__":
    unittest.main()
