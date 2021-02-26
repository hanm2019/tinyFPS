create_project prj -part xcu200-fsgd2104-2-e -force
set_property target_language verilog [current_project]
set vivado_ver [version -short]
set COE_DIR "../../syn/verilog"
source "/home/hanmeng/Documents/tinyFPS/hls/FPS/opt/syn/verilog/farthest_point_sampling_ap_sitodp_0_no_dsp_32_ip.tcl"
if {[regexp -nocase {2015\.3.*} $vivado_ver match] || [regexp -nocase {2016\.1.*} $vivado_ver match]} {
    extract_files -base_dir "./prjsrcs/sources_1/ip" [get_files -all -of [get_ips farthest_point_sampling_ap_sitodp_0_no_dsp_32]]
}
source "/home/hanmeng/Documents/tinyFPS/hls/FPS/opt/syn/verilog/farthest_point_sampling_ap_dadd_1_full_dsp_64_ip.tcl"
if {[regexp -nocase {2015\.3.*} $vivado_ver match] || [regexp -nocase {2016\.1.*} $vivado_ver match]} {
    extract_files -base_dir "./prjsrcs/sources_1/ip" [get_files -all -of [get_ips farthest_point_sampling_ap_dadd_1_full_dsp_64]]
}
