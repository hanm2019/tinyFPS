
/opt/Xilinx/Vivado/2020.1/bin/xelab xil_defaultlib.apatb_farthest_point_sampling_top glbl -prj farthest_point_sampling.prj -L smartconnect_v1_0 -L axi_protocol_checker_v1_1_12 -L axi_protocol_checker_v1_1_13 -L axis_protocol_checker_v1_1_11 -L axis_protocol_checker_v1_1_12 -L xil_defaultlib -L unisims_ver -L xpm  --lib "ieee_proposed=./ieee_proposed" -s farthest_point_sampling -debug wave
/opt/Xilinx/Vivado/2020.1/bin/xsim --noieeewarnings farthest_point_sampling -tclbatch farthest_point_sampling.tcl
