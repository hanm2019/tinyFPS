############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright (C) 1986-2020 Xilinx, Inc. All Rights Reserved.
############################################################
open_project FPS
add_files FPS/src/fps.c
add_files FPS/src/fps.h
add_files FPS/src/point_aux.c
add_files FPS/src/point_aux.h
add_files -tb FPS/test/fps_test.c
add_files -tb FPS/data
open_solution "basic" -flow_target vitis
set_part {xcu200-fsgd2104-2-e}
create_clock -period 10 -name default
#source "./FPS/basic/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
