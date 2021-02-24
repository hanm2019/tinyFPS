#ifndef FPS_H_
#define FPS_H_
//#include <ap_cint.h>
#include <math.h>
#include <stdbool.h>

#ifdef BIT_ACCURATE
#include "autopilot_tech.h"

typedef uint18  point_distance_t;
typedef uint1 point_mask_t;

#else // Use native C types
#include "stdlib.h"

typedef unsigned int point_distance_t;
typedef bool point_mask_t;
#endif
#define MAX_DISTANCE (point_distance_t)(1 << 17)
#include "point_aux.h"

#define CLIP(x) (((x)>255) ? 255 : (((x)<0) ? 0 : (x)))

typedef struct{
	point_distance_t distance_array[LENGTH];
	point_mask_t distance_mask[LENGTH];
} point_distance_array_t;


void farthest_point_sampling(pointcloud_t*, pointcloud_t*);

void init_distance(point_distance_array_t*);

void distance(pointcloud_t*, point_dim_t, point_distance_array_t*);

point_dim_t max_idx(point_distance_array_t*);


#endif
