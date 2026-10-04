// Verilator harness for modmul_agile (PLAN.md tests a and b).
//
// Usage:
//   tb kem_exhaustive            all 3329 x 3329 pairs, ML-KEM mode
//   tb dsa_random <n> <seed>     edge pairs plus n random pairs, ML-DSA mode
//   tb mixed <n> <seed>          n random ops, random mode per op, random idle gaps
//
// The expected value is (a*b) % q computed here in C++, independent of the
// RTL and of the Python model. Each op is pushed on a scoreboard when it
// enters; every out_valid pops one and compares p, mode and tag. Exit code is
// 0 only if every op came out, in order, correct, with no extra outputs.

#include <verilated.h>
#include VDUT_H

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <random>
#include <vector>

static const uint64_t Q[2] = {3329, 8380417};
static const int TAG_W = 4;
static const int MAX_REPORT = 10;

struct Op {
    uint32_t a, b, tag;
    int mode;
    uint64_t cycle_in;
};

class Bench {
public:
    explicit Bench(uint32_t seed) : rng(seed) {
        dut = new VDUT;
        dut->clk = 0;
        dut->rst = 1;
        dut->in_valid = 0;
        for (int i = 0; i < 4; i++) tick();
        dut->rst = 0;
    }
    ~Bench() { dut->final(); delete dut; }

    void push(uint32_t a, uint32_t b, int mode) {
        Op op{a, b, (uint32_t)(rng() & ((1u << TAG_W) - 1)), mode, cycle};
        dut->in_valid = 1;
        dut->in_mode = mode;
        dut->in_tag = op.tag;
        dut->a = a;
        dut->b = b;
        sb.push_back(op);
        pushed++;
        tick();
    }

    // Idle cycle with junk on the data inputs, so a DUT that ignores in_valid fails.
    void idle() {
        dut->in_valid = 0;
        dut->in_mode = rng() & 1;
        dut->in_tag = rng() & ((1u << TAG_W) - 1);
        dut->a = rng() & 0x7fffff;
        dut->b = rng() & 0x7fffff;
        tick();
    }

    bool finish(const char* name) {
        for (int i = 0; i < 256 && !sb.empty(); i++) idle();
        for (int i = 0; i < 16; i++) idle();  // catch late extra outputs
        if (!sb.empty()) {
            fail_line("%zu ops never produced an output (first: a=%u b=%u mode=%d, entered cycle %llu)",
                      sb.size(), sb.front().a, sb.front().b, sb.front().mode,
                      (unsigned long long)sb.front().cycle_in);
        }
        printf("%s %s: %llu ops in, %llu results checked, %llu mismatches, %llu cycles, latency %lld\n",
               failures ? "FAIL" : "PASS", name,
               (unsigned long long)pushed, (unsigned long long)checked,
               (unsigned long long)failures, (unsigned long long)cycle, (long long)latency);
        return failures == 0;
    }

    std::mt19937_64 rng;

private:
    VDUT* dut;
    uint64_t cycle = 0, pushed = 0, checked = 0, failures = 0;
    long long latency = -1;
    std::deque<Op> sb;

    template <typename... Args>
    void fail_line(const char* fmt, Args... args) {
        if (failures < MAX_REPORT) {
            printf("  MISMATCH: ");
            printf(fmt, args...);
            printf("\n");
        }
        failures++;
    }

    void tick() {
        dut->clk = 1;
        dut->eval();
        cycle++;
        check();
        dut->clk = 0;
        dut->eval();
    }

    void check() {
        if (dut->rst || !dut->out_valid) return;
        if (sb.empty()) {
            fail_line("cycle %llu: out_valid with no op in flight (p=%u)",
                      (unsigned long long)cycle, (unsigned)dut->p);
            return;
        }
        Op op = sb.front();
        sb.pop_front();
        long long lat = (long long)(cycle - op.cycle_in);
        if (latency < 0) latency = lat;
        uint32_t want = (uint32_t)((uint64_t)op.a * op.b % Q[op.mode]);
        checked++;
        if (dut->p != want || dut->out_mode != op.mode || dut->out_tag != op.tag || lat != latency) {
            fail_line("cycle %llu: mode=%d a=%u b=%u expected p=%u got p=%u"
                      " (out_mode=%d out_tag=%u want tag=%u, latency %lld vs %lld)",
                      (unsigned long long)cycle, op.mode, op.a, op.b, want, (unsigned)dut->p,
                      (int)dut->out_mode, (unsigned)dut->out_tag, op.tag, lat, latency);
        }
    }
};

static bool kem_exhaustive() {
    Bench tb(1);
    for (uint32_t a = 0; a < Q[0]; a++)
        for (uint32_t b = 0; b < Q[0]; b++)
            tb.push(a, b, 0);
    return tb.finish("kem_exhaustive");
}

static bool dsa_random(uint64_t n, uint32_t seed) {
    Bench tb(seed);
    const uint32_t q = (uint32_t)Q[1];
    // Largest legal input is q-1 = 8380416, just under 2^23 = 8388608.
    std::vector<uint32_t> edge = {0, 1, 2, 3, q - 1, q - 2, q / 2, q / 2 + 1,
                                  1u << 22, (1u << 22) - 1, 1u << 13, (1u << 13) - 1,
                                  (1u << 13) + 1, 1753, 4096, 8191};
    for (uint32_t a : edge)
        for (uint32_t b : edge)
            tb.push(a, b, 1);
    std::uniform_int_distribution<uint32_t> d(0, q - 1);
    for (uint64_t i = 0; i < n; i++) tb.push(d(tb.rng), d(tb.rng), 1);
    return tb.finish("dsa_random");
}

static bool mixed(uint64_t n, uint32_t seed) {
    Bench tb(seed);
    for (uint64_t i = 0; i < n; i++) {
        int mode = tb.rng() & 1;
        std::uniform_int_distribution<uint32_t> d(0, (uint32_t)Q[mode] - 1);
        uint32_t a = d(tb.rng), b = d(tb.rng);
        tb.push(a, b, mode);
        if ((tb.rng() & 7) == 0) tb.idle();
    }
    return tb.finish("mixed");
}

int main(int argc, char** argv) {
    Verilated::randReset(2);  // randomize uninitialized state
    Verilated::commandArgs(argc, argv);
    if (argc < 2) {
        fprintf(stderr, "usage: %s kem_exhaustive | dsa_random <n> <seed> | mixed <n> <seed>\n", argv[0]);
        return 2;
    }
    const char* t = argv[1];
    uint64_t n = argc > 2 ? strtoull(argv[2], nullptr, 10) : 1000000;
    uint32_t seed = argc > 3 ? (uint32_t)strtoul(argv[3], nullptr, 10) : 1;
    bool ok;
    if (!strcmp(t, "kem_exhaustive")) ok = kem_exhaustive();
    else if (!strcmp(t, "dsa_random")) ok = dsa_random(n, seed);
    else if (!strcmp(t, "mixed")) ok = mixed(n, seed);
    else { fprintf(stderr, "unknown test %s\n", t); return 2; }
    return ok ? 0 : 1;
}
