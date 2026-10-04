# Plan

Schedule: Saturday 2026-10-03 night to Tuesday 2026-10-06 noon.

Ownership: Jordan writes, or reviews line by line, the modular multiplier, the lane and the controller. Scaffolding (test harness, vector generators, Tcl, build scripts, print scripts) can be written by the agent and is reviewed by Jordan.

## S0: setup (Sat night)

- [x] Verilator 5 installed, hello-world builds
- [x] Python venv (not needed so far: the model uses only the standard library)
- [x] Repo skeleton, `DECISIONS.md`, `LOG.md`, `LEARNING.md`
- [x] First commit pushed
- [ ] Vivado smoke test on eceubuntu: version prints, `get_parts xck26*` finds the K26 part

## M1: golden model (Sun)

- [x] Plain Python, no crypto libraries, following FIPS 203/204 pseudocode
- [x] zeta tables, NTT, inverse NTT, BaseCaseMultiply, MultiplyNTTs, pointwise multiply, A∘s for both schemes
- [ ] Validation, independent of the model itself:
  - [x] NTT-domain product equals schoolbook negacyclic product, both schemes, random inputs
  - [x] inverse NTT(NTT(f)) == f; scale factors 3303 and 8347681 equal 128^-1 and 256^-1
  - [ ] scale factors and zeta tables compared against the FIPS 203/204 PDF text and appendices
  - [x] 17^128 ≡ -1 (mod 3329), 1753^256 ≡ -1 (mod 8380417)
  - [x] gamma table unit test
- [x] Memory layout agreed in `DECISIONS.md` (D8); exact word bit order still open
- [ ] Vector generator: per-lane operand memories and expected outputs, several seeds, alternating-mode stream
- [ ] Jordan: `LEARNING.md` primer items 1 to 6, hand calculations, DSP-per-lane predictions
- [ ] Jordan: first draft of `modmul_agile.sv`
- [x] Verilator C++ harness plus tests (a) and (b) ready for the multiplier (self-tested, `tb/modmul/`)
- [ ] Chip generator and `/qorsa` redirect page drafted; small test tile printed

## M2+M3: RTL and verification (Mon)

- [ ] Full chip print started in the morning
- [ ] `modmul_agile.sv` passes (a) and (b)
- [ ] `lane.sv`, controller, `agile_mvm.sv` with `LANES` parameter
- [ ] (c) A∘s matches golden vectors, ML-KEM-768 and ML-DSA-65, at least 5 seeds each, cycle counts logged
- [ ] (d) alternating-mode stream, no idle gap, bit-exact
- [ ] One OOC Vivado run of `modmul_agile` (LANES=1) to prove the Tcl flow and DSP inference
- [ ] Three deliberate-break experiments recorded in `LOG.md`
- [ ] Predictions for Fmax, DSPs and cycles written down before the PPA runs

## M4: PPA (Tue morning)

- [ ] Builds: ML-KEM-only, ML-DSA-only, agile; LANES=1 and 8 (or 16); 128 if runtime allows
- [ ] `report_utilization` and `report_timing_summary` saved per build in `logs/`
- [ ] "Price of agility" table in README, each number labelled with build, LANES, stage, part and Vivado version

## Tests

| ID | Unit | What |
|---|---|---|
| a | `modmul_agile`, ML-KEM | exhaustive: all 3329 x 3329 = 11,082,241 pairs, latency-aligned scoreboard |
| b | `modmul_agile`, ML-DSA | at least 10^6 random pairs plus edges (0, 1, q-1, values just under 2^23) |
| c | `agile_mvm` | A∘s vs golden vectors, both schemes, at least 5 seeds each |
| d | `agile_mvm` | ML-KEM and ML-DSA transactions alternating back to back |

## Out of scope

NTT or inverse NTT in hardware, SHAKE and sampling, the full KEM or signature, constant-time or side-channel hardening, running on a board, ASIC flow, formal proofs.
