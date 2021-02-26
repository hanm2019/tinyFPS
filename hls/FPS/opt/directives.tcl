############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright (C) 1986-2020 Xilinx, Inc. All Rights Reserved.
############################################################
set_directive_top -name farthest_point_sampling "farthest_point_sampling"
set_directive_array_partition -dim 1 -factor 64 -type cyclic "farthest_point_sampling" in->points
set_directive_array_partition -dim 1 -factor 64 -type cyclic "farthest_point_sampling" out->points
set_directive_inline "init_distance"
set_directive_dataflow "distance/distance_label1"
set_directive_unroll -factor 4 "distance_max_idx/distance_max_idx_label3"
set_directive_array_partition -type cyclic -factor 16 -dim 1 "distance_max_idx" in->points
set_directive_array_partition -type cyclic -factor 16 -dim 1 "distance_max_idx" out->points
set_directive_array_partition -type cyclic -factor 16 -dim 1 "distance_max_idx" array->distance_array
set_directive_array_partition -type cyclic -factor 16 -dim 1 "distance_max_idx" array->distance_mask
set_directive_array_partition -dim 1 -factor 64 -type cyclic "farthest_point_sampling" _min_distance.distance_mask
set_directive_array_partition -dim 1 -factor 64 -type cyclic "farthest_point_sampling" _min_distance.distance_array
set_directive_unroll -factor 64 "init_distance/init_distance_label4"
set_directive_array_partition -dim 1 -factor 64 -type cyclic "init_distance" array->distance_array
set_directive_array_partition -dim 1 -factor 64 -type cyclic "init_distance" array->distance_mask
set_directive_array_partition -type complete -dim 1 "farthest_point_sampling" _farthest_point
set_directive_array_partition -type block -factor 3 -dim 1 "farthest_point_sampling" in->points
set_directive_array_partition -type block -factor 3 -dim 1 "farthest_point_sampling" out->points
set_directive_unroll "farthest_point_sampling/random_select_0"
set_directive_pipeline -II 2 "distance_max_point/calculate_distance"
set_directive_unroll "farthest_point_sampling/set_farthest_point"
set_directive_array_partition -type complete -dim 1 "distance_max_point" origin_point_pix
set_directive_array_partition -type complete -dim 1 "distance_max_point" distance_array
set_directive_unroll "distance_max_point/get_origin_point"
set_directive_unroll "distance_max_point/calculate_one_dim"
set_directive_pipeline "distance_max_point/calculate_one_dim"
