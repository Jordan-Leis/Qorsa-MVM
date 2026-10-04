# Learning

Jordan's notes, in his own words. The agent may quiz and point out gaps but does not write answers here.

## Primer

1. Why post-quantum cryptography exists
2. Module-LWE in one paragraph
3. Why the NTT (and why ML-KEM's NTT is incomplete)
4. Where matrix-vector products dominate
5. Crypto agility and why hardware makes it hard
6. Barrett reduction, including the bound on r and how many conditional subtracts are needed

## Design

- Why lane i owns pair i
- Why gamma can be hoisted out of the loop

## Hand calculations

- One ML-KEM base-case multiply, small chosen values
- One Barrett reduction for q = 3329, step by step
- DSP-per-lane estimate for each build (ML-KEM-only, ML-DSA-only, agile)

## Predictions (write before measuring)

| Quantity | Prediction | Measured | Log |
|---|---|---|---|
| DSPs per lane, ML-KEM-only | | | |
| DSPs per lane, ML-DSA-only | | | |
| DSPs per lane, agile | | | |
| Fmax, each build | | | |
| Cycles per ML-KEM-768 matrix | | | |
| Cycles per ML-DSA-65 matrix | | | |

## Likely questions

- Why is ML-KEM's NTT incomplete, and what does that do to the multiply?
- Why Barrett over Montgomery in this design?
- What does agility cost here, and where does the cost come from?
- Is this constant-time or side-channel safe?
- How does this differ from the P6 engine?
- What would you do with another week?
- How would an EDA tool help or hurt this design?
