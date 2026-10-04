# Build and run the modmul_agile tests. Results are teed into logs/.
#
#   make kem            test a: exhaustive, ML-KEM mode
#   make dsa            test b: edges plus 10^6 random, ML-DSA mode
#   make mixed          random mode per op, idle gaps (checks the mode tag)
#   make all            all three
#
#   make kem PARAMS="-GHAS_DSA=0"    build only the ML-KEM path
#   make all DUT=modmul_ref          harness self-test against a behavioral model
#   make kem DUT=modmul_ref PARAMS="-GBUG=1"   self-test: harness must FAIL

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

DUT    ?= modmul_agile
PARAMS ?=
N      ?= 1000000
SEED   ?= 1

ROOT := ../..
ifeq ($(DUT),modmul_agile)
  SRC    := $(ROOT)/rtl/modmul_agile.sv
  LOGPFX := modmul
else
  SRC    := selftest/$(DUT).sv
  LOGPFX := harness_selftest
endif

# One build directory per DUT + parameter set, so changing PARAMS rebuilds.
TAG := $(subst $() $(),,$(subst -G,_,$(subst =,,$(PARAMS))))
OBJ := obj_$(DUT)$(TAG)
BIN := $(OBJ)/V$(DUT)
LOGSFX := $(TAG)

VFLAGS := --cc --exe --build -j 0 -O3 -Wall -Wno-fatal \
          --x-assign unique --x-initial unique \
          --top-module $(DUT) $(PARAMS) \
          -CFLAGS "-O2 -DVDUT=V$(DUT) -DVDUT_H='\"V$(DUT).h\"'"

.PHONY: all kem dsa mixed build clean
all: kem dsa mixed

build: $(BIN)

$(BIN): $(SRC) tb_modmul.cpp
	verilator $(VFLAGS) --Mdir $(OBJ) $(SRC) tb_modmul.cpp 2>&1 | tee $(ROOT)/logs/$(LOGPFX)$(LOGSFX)_build.log

kem: $(BIN)
	( verilator --version; echo "DUT=$(DUT) PARAMS=$(PARAMS)"; time ./$(BIN) kem_exhaustive ) 2>&1 | tee $(ROOT)/logs/$(LOGPFX)$(LOGSFX)_kem_exhaustive.log

dsa: $(BIN)
	( verilator --version; echo "DUT=$(DUT) PARAMS=$(PARAMS)"; time ./$(BIN) dsa_random $(N) $(SEED) ) 2>&1 | tee $(ROOT)/logs/$(LOGPFX)$(LOGSFX)_dsa_random.log

mixed: $(BIN)
	( verilator --version; echo "DUT=$(DUT) PARAMS=$(PARAMS)"; time ./$(BIN) mixed $(N) $(SEED) ) 2>&1 | tee $(ROOT)/logs/$(LOGPFX)$(LOGSFX)_mixed.log

clean:
	rm -rf obj_*
