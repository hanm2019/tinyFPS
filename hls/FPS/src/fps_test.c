#include <stdio.h>
#include <stdlib.h>
#include "fps.h"

int main () {
   // Dynamically allocate pointcloud buffers as they are rather large
   // and stack overflow may occur if statically allocated
   pointcloud_t *origin_points = (pointcloud_t *)malloc(sizeof(pointcloud_t));
   pointcloud_t *sample_points = (pointcloud_t *)malloc(sizeof(pointcloud_t));

   // Read input pointclouds
   pointcloud_read(origin_points, 0);
   sample_points->length = 32;
   sample_points->width = 3;

   farthest_point_sampling(origin_points, sample_points);

   // Save output pointclouds
   pointcloud_write(sample_points);

   // Compare results
   int ret = system("diff --brief -w data/output.txt data/output.golden.txt");

   if (ret != 0) {
      printf("Test failed!!!\n");
      return 1;
   } else {
      printf("Test passed!\n");
      return 0;
   }
}

