# Log

Commands run, tool versions, results. Newest at the bottom.

## 2026-10-03 (Sat): S0 setup

**Machine:** Ubuntu 24.04.4 LTS on WSL2 (kernel 6.18.40.1), x86_64. Python 3.12.3, git 2.43.0, gh 2.96.0.

- Repo skeleton created: `model/ rtl/ tb/ vivado/ print/ logs/`, plus `PLAN.md`, `DECISIONS.md`, `LEARNING.md`.
- Toolchain install (needs sudo, about 121 MB download):
  `sudo apt install -y verilator openscad python3-venv python3-pip`
  Result: pending.
- Verilator smoke test: `tb/smoke/run.sh`, output to `logs/s0_verilator_smoke.log`. Result: pending.
- Vivado smoke test on eceubuntu (brief section 13). Result: pending.

## 2026-10-04 (Sun, early): M1 golden model

- Model in `model/` (plain Python 3.12.3, standard library only): `mlkem.py` (FIPS 203 Alg. 9 to 12), `mldsa.py` (FIPS 204 Alg. 41, 42, 45), `common.py` (BitRev, schoolbook negacyclic product, A∘s).
- `python3 -m unittest discover -s model -v`: **12 tests, all pass** in 0.65 s. Output: `logs/m1_model_tests.log`.
  - Root checks: 17^128 ≡ -1 (mod 3329); 1753^256 ≡ -1 (mod 8380417); 512 does not divide 3328.
  - Scale factors: 128^-1 mod 3329 = 3303, 256^-1 mod 8380417 = 8347681.
  - gamma table: 128 distinct roots of X^128 + 1, paired as +/- each other.
  - inverse NTT(NTT(f)) == f, 20 random polynomials per scheme.
  - NTT-domain product == schoolbook negacyclic product: 16 edge pairs plus 20 random pairs per scheme.
  - A∘s == schoolbook A*s for random non-symmetric A: ML-KEM-768 (3x3), ML-DSA-65 (6x5).
  - Hoisted-gamma schedule equals the direct base-case product (ML-KEM-768).
- Mutation check (did the tests have teeth?):
  - gamma = 17^i instead of 17^(2*BitRev7(i)+1): 3 failures, all ML-KEM (gamma table, product, matvec). ML-DSA tests still pass.
  - cyclic instead of negacyclic schoolbook: 4 failures (product and matvec, both schemes).
- Not yet done: optional cross-check against pq-crystals reference C.

## 2026-10-04 (Sun): tools, harness

- Thank-you email sent (Jordan). Golden model reviewed by Jordan.
- Installed by Jordan: Verilator 5.020 (Debian 5.020-1), OpenSCAD 2021.01, python3-venv, python3-pip. g++ 13.3.0, GNU Make 4.3.
- `tb/smoke/run.sh`: **pass**, prints "hello from verilator". `logs/s0_verilator_smoke.log`.
- Vivado on eceubuntu: assumed available (Jordan, 2026-10-04); smoke test still to be run before M4.
- modmul harness (`tb/modmul/`), self-tested against a behavioral `%` stand-in (`selftest/modmul_ref.sv`, latency 5):
  - `make all DUT=modmul_ref`: kem_exhaustive 11,082,241 checked, 0 mismatches (0.79 s); dsa_random 1,000,256 checked, 0 mismatches; mixed 1,000,000 checked, 0 mismatches. `logs/harness_selftest_*.log`.
  - `make kem DUT=modmul_ref PARAMS="-GBUG=1"`: **fails as intended**, 1 mismatch reported at a=3328 b=3328, make exits nonzero. `logs/harness_selftest_BUG1_kem_exhaustive.log`.
