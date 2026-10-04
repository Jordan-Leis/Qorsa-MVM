# qorsa agile-MVM

A crypto-agile polynomial matrix-vector engine for ML-KEM-768 and ML-DSA-65, in SystemVerilog.

Work in progress. Nothing here has been measured yet. Every number that ends up in this README will link to a log file in `logs/`.

## Layout

| Folder | Contents |
|---|---|
| `model/` | Python golden model (FIPS 203 / FIPS 204, canonical coefficients in [0, q)) and test vector generator |
| `rtl/` | SystemVerilog engine |
| `tb/` | Verilator test harness |
| `vivado/` | Batch Tcl for out-of-context PPA runs |
| `print/` | Scripts for the printed chip |
| `logs/` | Raw tool output that every reported number traces back to |

See `PLAN.md` for the build plan, `DECISIONS.md` for design choices and `LOG.md` for what was run.
