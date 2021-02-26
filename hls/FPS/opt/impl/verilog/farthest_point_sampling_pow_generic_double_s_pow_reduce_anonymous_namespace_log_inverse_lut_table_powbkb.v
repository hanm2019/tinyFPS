// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2020.1 (64-bit)
// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// ==============================================================
`timescale 1 ns / 1 ps
(* rom_style = "distributed" *) module farthest_point_sampling_pow_generic_double_s_pow_reduce_anonymous_namespace_log_inverse_lut_table_powbkb_rom (
addr0, ce0, q0, clk);

parameter DWIDTH = 6;
parameter AWIDTH = 6;
parameter MEM_SIZE = 64;

input[AWIDTH-1:0] addr0;
input ce0;
output reg[DWIDTH-1:0] q0;
input clk;

(* ram_style = "distributed" *)reg [DWIDTH-1:0] ram[0:MEM_SIZE-1];

initial begin
    $readmemh("./farthest_point_sampling_pow_generic_double_s_pow_reduce_anonymous_namespace_log_inverse_lut_table_powbkb_rom.dat", ram);
end



always @(posedge clk)  
begin 
    if (ce0) 
    begin
        q0 <= ram[addr0];
    end
end



endmodule

`timescale 1 ns / 1 ps
module farthest_point_sampling_pow_generic_double_s_pow_reduce_anonymous_namespace_log_inverse_lut_table_powbkb(
    reset,
    clk,
    address0,
    ce0,
    q0);

parameter DataWidth = 32'd6;
parameter AddressRange = 32'd64;
parameter AddressWidth = 32'd6;
input reset;
input clk;
input[AddressWidth - 1:0] address0;
input ce0;
output[DataWidth - 1:0] q0;



farthest_point_sampling_pow_generic_double_s_pow_reduce_anonymous_namespace_log_inverse_lut_table_powbkb_rom farthest_point_sampling_pow_generic_double_s_pow_reduce_anonymous_namespace_log_inverse_lut_table_powbkb_rom_U(
    .clk( clk ),
    .addr0( address0 ),
    .ce0( ce0 ),
    .q0( q0 ));

endmodule
