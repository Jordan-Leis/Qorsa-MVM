// Toolchain smoke test: proves Verilator can build and run a SystemVerilog model.
module hello;
  initial begin
    $display("hello from verilator");
    $finish;
  end
endmodule
