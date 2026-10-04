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
