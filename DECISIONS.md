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

## D3. Verilator harness in C++ (Proposed)

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

- **Choice:** lane i owns coefficient pair i. ML-KEM: base-case pair i with constant gamma_i. ML-DSA: coefficients 2i and 2i+1. One pipelined agile multiplier per lane, two modular-add accumulators. Gamma multiply hoisted to once per row.
- **Alternatives:** fully parallel base-case lane (4 to 5 multipliers per lane); Karatsuba for c1.
- **Reason:** to be written by Jordan.

## D7. Mode is a tag on each operation (Proposed)

- **Choice:** the mode bit travels with each operation through every pipeline stage. There is no global mode register.
- **Alternatives:** a global mode register written between transactions.
- **Reason:** with a global register, operations already in flight would be reduced with the wrong constants at a mode switch (common error 8). The mode-switch test (d) checks this.

## D8. Matrix and vector conventions (Open)

To be agreed before RTL: row/column order of A, vector file word width and order, per-lane memory addressing.
