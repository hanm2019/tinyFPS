############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright (C) 1986-2020 Xilinx, Inc. All Rights Reserved.
############################################################
open_project FPS
set_top farthest_point_sampling
add_files fps.c
add_files fps.h
add_files point_aux.c
add_files point_aux.h
add_files -tb fps_test.c -cflags "-Wno-unknown-pragmas" -csimflags "-Wno-unknown-pragmas"
open_solution "basic" -flow_target vitis
set_part {xcu200-fsgd2104-2-e}
create_clock -period 10 -name default
config_interface -default_slave_interface s_axilite -m_axi_alignment_byte_size 64 -m_axi_latency 64 -m_axi_max_widen_bitwidth 512
config_rtl -register_reset_num 3
source "./FPS/basic/directives.tcl"
csim_design
csynth_design
cosim_design -trace_level all
export_design -format ip_catalog
