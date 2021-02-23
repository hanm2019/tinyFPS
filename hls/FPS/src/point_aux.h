#ifndef POINT_AUX_H_
#define POINT_AUX_H_

#ifdef BIT_ACCURATE
#include "autopilot_tech.h"

typedef uint8  point_pix_t;
typedef uint10 point_dim_t;

#else // Use native C types

typedef unsigned char  point_pix_t;
typedef unsigned short point_dim_t;

#endif // ifdef BIT_ACCURATE

#define WIDTH 3
#define LENGTH 1024

typedef struct {
   point_pix_t data[WIDTH];
} point_t;

typedef struct {
   point_t points[LENGTH];
   point_dim_t width;
   point_dim_t length;
} pointcloud_t;

void pointcloud_read(pointcloud_t *in_pointcloud, point_dim_t idx);

void pointcloud_write(pointcloud_t *out_pointcloud);

#endif
