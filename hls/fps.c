#include "fps.h"

// The top-level function
void farthest_point_sampling (
      pointcloud_t *in,
      pointcloud_t *out
      )
{
#ifndef __SYNTHESIS__
	point_distance_array_t *min_distance = (point_distance_array_t *)malloc(sizeof(point_distance_array_t));
	point_t *farthest_point = (point_t *)malloc(sizeof(point_t));

#else // Workaround malloc() calls w/o changing rest of code
	point_distance_array_t _min_distance;
	point_distance_array_t *min_distance = &_min_distance;

	point_t _farthest_point;
	point_t *farthest_point = &_farthest_point;
#endif

	point_dim_t npoint, width, length;
	point_dim_t i,j;
	point_pix_t tmp_data;

	npoint = out->length;
	length = in->length;
	width = in->width;
	init_distance(min_distance);

//random a points -> index:0
	random_select_0:for(i = 0 ;i < WIDTH; i++){
		tmp_data = in->points[0].data[i];
		out->points[0].data[i] = tmp_data;
		farthest_point->data[i] = tmp_data;
	}
	min_distance->distance_mask[0] = 0;

	iteration:for(i= 0; i < SAMPLE_LENGTH - 1; i++){
		distance_max_point(in, farthest_point, min_distance);
		set_farthest_point:for(j = 0; j < WIDTH; j++){
			out->points[i + 1].data[j] = farthest_point->data[j];
		}
#ifndef __SYNTHESIS__
		printf("select point: [%d, %d, %d]\n", farthest_point->data[0], farthest_point->data[1], farthest_point->data[2]);
#endif
	}
}

void init_distance(point_distance_array_t* array){
	point_dim_t i;
	init_distance_label4:for(i = 0; i < LENGTH; i++){
		array->distance_array[i] = MAX_DISTANCE;
		array->distance_mask[i] = 1;
	}
}

void distance_max_point(pointcloud_t* in, point_t* point, point_distance_array_t* array){
	point_pix_t x,y,z;
	point_pix_t xi,yi,zi;
	point_pix_t origin_point_pix[WIDTH];

	point_dim_t i,j, max_index;
	point_distance_t p2p_distance, distance_array[WIDTH], tmp_distance, min_distance;

	point_distance_t max_distance;

	get_origin_point:for(i = 0; i < WIDTH; i++){
		origin_point_pix[i] = point->data[i];
	}
	max_distance = 0;

	calculate_distance:for(i = 0; i < LENGTH; i++){
		if(array->distance_mask[i] == 1){
			xi = in->points[i].data[0];
			yi = in->points[i].data[1];
			zi = in->points[i].data[2];

			p2p_distance = pow(xi - origin_point_pix[0], 2) + pow(yi - origin_point_pix[1], 2) + pow(zi - origin_point_pix[2], 2);

            tmp_distance = array->distance_array[i];
            min_distance = p2p_distance > tmp_distance ? tmp_distance : p2p_distance;
           	array->distance_array[i] = min_distance;
           	if (min_distance > max_distance){
           		point->data[0] = xi;
           		point->data[1] = yi;
           		point->data[2] = zi;
           		max_distance = min_distance;
           		max_index = i;
           	}
		}
	}
	array->distance_mask[max_index] = 0;
	return ;
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


