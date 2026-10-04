# Decisions

Each entry: the choice, the alternatives, and the reason. Status is **Accepted** once Jordan has agreed to it, **Proposed** until then.

---

## D1. Repo and tooling layout (Accepted, 2026-10-03)

- **Choice:** this repo (`Jordan-Leis/Qorsa-MVM`), folders `model/ rtl/ tb/ vivado/ print/ logs/`. Raw tool output lives in `logs/`; Vivado run directories are not committed.
- **Alternatives:** a new `qorsa-agile-mvm` repo.
- **Reason:** the GitHub repo already existed and was empty. The name doesn't matter to the QR code, which points at `jordanleis.com/qorsa`.

## D2. Golden model in plain Python integers (Accepted, 2026-10-03)

- **Choice:** pure Python with built-in integers, following the FIPS 203/204 pseudocode, canonical coefficients in [0, q).
- **Alternatives:** numpy arrays; wrapping pq-crystals C.
- **Reason:** Python integers never overflow, so the model can't silently wrap. Following the FIPS text avoids the Montgomery/signed representation used in pq-crystals (common error 1). numpy is not needed for 256-coefficient polynomials.

## D3. Verilator harness in C++ (Accepted, 2026-10-04)

- **Choice:** one C++ harness per test, reading hex vectors produced by the Python generator, with a valid bit carried through the pipeline and comparison only on valid out.
- **Alternatives:** SystemVerilog testbench with `$readmemh` and classes.
- **Reason:** the exhaustive test is 11M pairs, and C++ keeps it fast. It also avoids Verilator's limits on SV classes and constraints.

## D4. One RTL source for all three PPA builds (Proposed)

- **Choice:** a top-level parameter selecting `KEM`, `DSA` or `AGILE` support, so the single-scheme builds drop the unused Barrett constants and mode logic.
- **Alternatives:** separate RTL per build.
- **Reason:** the comparison is only fair if the three builds differ in nothing except mode support.

## D5. Barrett reduction (Proposed, from the brief; Jordan to confirm)

- **Choice:** Barrett with (q, m, k) = (3329, 5039, 24) and (8380417, 8396807, 46), selected by the mode tag.
- **Alternatives:** Montgomery; special-form reduction.
- **Reason:** values stay in normal representation, so RTL and golden model compare directly. Special-form reduction is future work.
- **Open:** number of conditional subtracts, from Jordan's bound derivation in `LEARNING.md`.

## D6. Lane mapping and gamma hoisting (Proposed, from the brief; Jordan to confirm)

- **Choice:** lane i owns coefficient pair i. ML-KEM: base-case pair i with constant gamma_i. ML-DSA: coefficients 2i and 2i+1. One pipelined agile multiplier per lane. Gamma multiply hoisted to once per row.
- **Correction to the brief:** hoisting needs **three** modular-add accumulators in ML-KEM mode, not two: acc00 = sum(a0 b0), acc11 = sum(a1 b1), acc1 = sum(a0 b1 + a1 b0). At row end c0 = acc00 + gamma_i * acc11, c1 = acc1. ML-DSA mode uses acc00 and acc1 for the even and odd points.
- **Slot order per ML-KEM term:** a0 b0 -> acc00, a1 b1 -> acc11, a0 b1 -> acc1, a1 b0 -> acc1.
- **Open (Jordan): gamma hazard.** The gamma multiply needs the final acc11, which is ready only after the last a1 b1 leaves the multiplier pipeline (latency L). Options: (a) stall about L cycles per row; (b) ping-pong acc11 and issue row r's gamma multiply during row r+1 (hides L if L <= 12); (c) a dedicated gamma multiplier per lane. Suggested: (a) first for a correct baseline, then (b) if time allows, reporting cycles for both.
- **Alternatives:** fully parallel base-case lane (4 to 5 multipliers per lane); Karatsuba for c1.
- **Reason:** to be written by Jordan.

## D7. Mode is a tag on each operation (Proposed)

- **Choice:** the mode bit travels with each operation through every pipeline stage. There is no global mode register.
- **Alternatives:** a global mode register written between transactions.
- **Reason:** with a global register, operations already in flight would be reduced with the wrong constants at a mode switch (common error 8). The mode-switch test (d) checks this.

## D8. Memories and transactions (Accepted in outline, 2026-10-04)

- **Choice:** each lane has two memories (P6 `mem.sv`, reused as is): an A memory and an S memory. A word is one coefficient pair, two 23-bit fields (46 bits); ML-KEM values are zero-extended. Lane i's A memory holds pair i of A[r][j] at address r*COLS + j (A[r][j] is row r, column j, as in FIPS); its S memory holds pair i of s[j] at address j. Memories are loaded through a write port driven by the harness.
- **Transactions** carry {mode, rows, cols}. rows = 1 gives the dot products t^T r and s^T u.
- **Alternatives:** one memory per lane with two read ports; `$readmemh` preload.
- **Reason:** both operands are lane-local, so nothing is broadcast (unlike P6). A write port is how a real host would load it and lets the mode-switch test stream transactions.
- **Open:** exact bit order inside a word and output format; settle when writing the vector generator.

## D9. The engine is a general NTT-domain matrix-vector unit, not a protocol (Accepted, 2026-10-04)

- **Choice:** the engine computes A∘s for whatever is loaded. It does not know whether S holds s, r or y. Noise terms (e, e1, e2) are added, never multiplied, and for u and v only after an inverse NTT, so they are outside the engine.
- **Stretch:** a `transpose` bit in the transaction (read A by column) would cover Encaps' A^T∘r. Address generation only; no datapath change.
- **Reason:** keeps the hardware to the one operation that dominates all of KeyGen, Encaps and Sign.

## D10. What is reused from P6 (Accepted, 2026-10-04)

- `mem.sv`: as is.
- `ctrl.sv`: structure (IDLE/COMPUTE, word and row counters, first/last), extended with a slot counter and the mode tag.
- `accum.sv`: first/last pattern; the add becomes a modular add with a destination select.
- `mvm.sv`: control and address register trees with `dont_touch` replicas. The vector broadcast tree is dropped.
- `dot8.sv`: not reused (8 parallel 8-bit multiplies vs one modular multiply); its input/M/P register pattern carries over.

## D11. modmul_agile interface (Accepted, 2026-10-04)

- **Choice:** one op per cycle, no backpressure; `in_mode` picks q; `in_tag` and `in_mode` travel with the data and come out with the result; `out_valid` marks results. Contract is in the header of `rtl/modmul_agile.sv`.
- **Reason:** the lane needs to know, when a product emerges, which accumulator it belongs to and whether it is first or last. Carrying that in the multiplier pipeline keeps it aligned by construction (common errors 8 and 10).
