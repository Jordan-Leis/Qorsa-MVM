// Behavioral stand-in for modmul_agile, used ONLY to prove the harness works
// before the real multiplier exists. Uses %, so it is not synthesizable
// hardware and is never part of the design.
//
// BUG = 1 corrupts one result (ML-KEM, a = b = 3328) so we can confirm the
// exhaustive test reports it.

module modmul_ref # (
    parameter bit HAS_KEM = 1,
    parameter bit HAS_DSA = 1,
    parameter int W       = 23,
    parameter int TAG_W   = 4,
    parameter int LAT     = 5,
    parameter bit BUG     = 0
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

logic [63:0] q, prod, r;
assign q    = in_mode ? 64'd8380417 : 64'd3329;
assign prod = 64'(a) * 64'(b);
assign r    = (BUG && !in_mode && a == W'(3328) && b == W'(3328)) ? (prod % q) ^ 64'd1 : prod % q;

logic             v_d [LAT];
logic             m_d [LAT];
logic [TAG_W-1:0] t_d [LAT];
logic [W-1:0]     p_d [LAT];

always_ff @(posedge clk) begin
    v_d[0] <= rst ? 1'b0 : in_valid;
    m_d[0] <= in_mode;
    t_d[0] <= in_tag;
    p_d[0] <= r[W-1:0];
    for (int i = 1; i < LAT; i++) begin
        v_d[i] <= rst ? 1'b0 : v_d[i-1];
        m_d[i] <= m_d[i-1];
        t_d[i] <= t_d[i-1];
        p_d[i] <= p_d[i-1];
    end
end

assign out_valid = v_d[LAT-1];
assign out_mode  = m_d[LAT-1];
assign out_tag   = t_d[LAT-1];
assign p         = p_d[LAT-1];

wire unused = &{1'b0, HAS_KEM, HAS_DSA, r[63:W]};

endmodule
