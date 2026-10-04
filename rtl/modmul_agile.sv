/***************************************************/
/* Agile Modular Multiplier                        */
/* p = a*b mod q, Barrett reduction, pipelined     */
/* q selected per operation by in_mode             */
/***************************************************/
//
// Contract (the Verilator harness in tb/modmul relies on this):
//
//   - Accepts one operation per cycle when in_valid = 1. No backpressure.
//   - in_mode = 0: ML-KEM, q = 3329.     Barrett m = 5039,    k = 24.
//     in_mode = 1: ML-DSA, q = 8380417.  Barrett m = 8396807, k = 46.
//   - Inputs are canonical: a, b < q of the selected mode. In ML-KEM mode
//     the upper bits of a and b are zero.
//   - Output p is canonical: p < q.
//   - out_valid, out_mode and out_tag are in_valid, in_mode and in_tag
//     delayed by exactly the pipeline latency. The harness checks results
//     only where out_valid = 1, so any fixed latency works.
//   - in_tag is not used by the multiplier. It carries the lane's control
//     bits (which accumulator, first, last) alongside the data.
//   - HAS_KEM / HAS_DSA select which moduli are built, for the PPA runs
//     (KEM-only, DSA-only, agile). With only one enabled, in_mode is ignored.
//   - rst is synchronous and should only reset control (valid). Leave data
//     registers unreset so Vivado can pack them into the DSP48E2.

module modmul_agile # (
    parameter bit HAS_KEM = 1,
    parameter bit HAS_DSA = 1,
    parameter int W       = 23,   // coefficient width, enough for q = 8380417
    parameter int TAG_W   = 4
)(
    input  logic             clk,
    input  logic             rst,
    input  logic             in_valid,
    input  logic             in_mode,
    input  logic [TAG_W-1:0] in_tag,
    input  logic [W-1:0]     a,
    input  logic [W-1:0]     b,
    output logic             out_valid,
    output logic             out_mode,
    output logic [TAG_W-1:0] out_tag,
    output logic [W-1:0]     p
);

/******* Your code starts here *******/


/******* Your code ends here ********/

endmodule
