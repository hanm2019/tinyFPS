#include "fps.h"

// The top-level function
void farthest_point_sampling (
      pointcloud_t *in,
      pointcloud_t *out
      )
{
#ifndef __SYNTHESIS__
	point_distance_array_t *min_distance = (point_distance_array_t *)malloc(sizeof(point_distance_array_t));

#else // Workaround malloc() calls w/o changing rest of code
	point_distance_array_t _min_distance;
	point_distance_array_t *min_distance = &_min_distance;
#endif

	point_dim_t npoint, width, length;
	point_dim_t i,j;
	point_dim_t out_idx, min_point_idx;

	npoint = out->length;
	length = in->length;
	width = in->width;
	init_distance(min_distance);

//random a points -> index:0
	out->points[0].data[0] = in->points[0].data[0];
	out->points[0].data[1] = in->points[0].data[1];
	out->points[0].data[2] = in->points[0].data[2];
//
	out_idx = 0;
	min_distance->distance_mask[0] = 0;

	for(i= 0; i < npoint - 1; i++){
		distance(in, out_idx, min_distance);
		min_point_idx = max_idx(min_distance);
		out->points[i + 1].data[0] = in->points[min_point_idx].data[0];
		out->points[i + 1].data[1] = in->points[min_point_idx].data[1];
		out->points[i + 1].data[2] = in->points[min_point_idx].data[2];
		min_distance->distance_mask[min_point_idx] = 0;
		out_idx = min_point_idx;
	}
}

void init_distance(point_distance_array_t* array){
	point_dim_t i;
	for(i = 0; i < LENGTH; i++){
		array->distance_array[i] = MAX_DISTANCE;
		array->distance_mask[i] = 1;
	}
}

void distance(pointcloud_t* in, point_dim_t idx, point_distance_array_t* array){
	point_pix_t x,y,z;
	point_pix_t xi,yi,zi;

	point_dim_t i;
	point_distance_t p2p_distance;
	x = in->points[idx].data[0];
	y = in->points[idx].data[1];
	z = in->points[idx].data[2];

	for(i = 0; i < LENGTH; i++){
		if(array->distance_mask[i] == 1){
			xi = in->points[i].data[0];
			yi = in->points[i].data[1];
			zi = in->points[i].data[2];
#ifndef __SYNTHESIS__
			p2p_distance = (x - xi)*(x - xi) + (y - yi) * (y - yi) + (z - zi) * (z - zi);
#else
            p2p_distance = pow(x - xi, 2) + pow(y - yi, 2) + pow(z - zi, 2);
#endif
			array->distance_array[i] = array->distance_array[i] >  p2p_distance ? p2p_distance : array->distance_array[i];
		}
	}
}

point_dim_t max_idx(point_distance_array_t* array){
	point_dim_t i, max_index;
	point_distance_t max_distance;
	max_distance = 0;
	for(i = 0 ;i < LENGTH;i++){
		if(array->distance_mask[i] == 1){
			if(array->distance_array[i] > max_distance){
				max_distance = array->distance_array[i];
				max_index = i;
			}
		}
	}
	return max_index;
}


