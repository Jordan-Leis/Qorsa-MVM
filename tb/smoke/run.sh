#!/usr/bin/env bash
# Build and run the Verilator smoke test. Output goes to logs/s0_verilator_smoke.log.
set -euo pipefail
cd "$(dirname "$0")"
root=../..
{
  verilator --version
  verilator --binary -Wall --Mdir obj_dir hello.sv
  ./obj_dir/Vhello
} 2>&1 | tee "$root/logs/s0_verilator_smoke.log"
