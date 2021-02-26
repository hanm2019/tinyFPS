#include <stdio.h>
#include <stdlib.h>
#include "fps.h"

int main () {
   // Dynamically allocate pointcloud buffers as they are rather large
   // and stack overflow may occur if statically allocated
	char command[160];
	point_dim_t idx;
    pointcloud_t *origin_points = (pointcloud_t *)malloc(sizeof(pointcloud_t));
    pointcloud_t *sample_points = (pointcloud_t *)malloc(sizeof(pointcloud_t));

   // Read input pointclouds
   pointcloud_read(origin_points, idx);
   sample_points->length = SAMPLE_LENGTH;
   sample_points->width = 3;

   farthest_point_sampling(origin_points, sample_points);

   // Save output pointclouds
   pointcloud_write(sample_points, idx);

   // Compare results
   sprintf(command, "diff --brief -w /home/hanmeng/Documents/tinyFPS/hls/FPS/result/output.txt /home/hanmeng/Documents/tinyFPS/hls/FPS/ref/%d.txt",(int)idx);
   int ret = system(command);

   if (ret != 0) {
      printf("Test failed!!!\n");
      return 1;
   } else {
      printf("Test passed!\n");
      return 0;
   }
}

