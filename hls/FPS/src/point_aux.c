#include <stdio.h>
#include "point_aux.h"


void pointcloud_read (
		pointcloud_t *in_pointcloud,
		point_dim_t idx
      ) {
   point_dim_t width, length;
   int i;
   FILE        *fp;
   char filename[20];
   point_pix_t tmpx, tmpy, tmpz;

   sprintf(filename, "data/%d.txt", idx);

   fp=fopen(filename,"r");

   width = 3;
   length = 1024;

   in_pointcloud->width  = width;
   in_pointcloud->length = length;

   for (i=0;i<length;i++) {
	   fscanf(fp, "%d %d %d", &tmpx, &tmpy, &tmpz);
       in_pointcloud->points[i].data[0] = tmpx;
       in_pointcloud->points[i].data[1] = tmpy;
       in_pointcloud->points[i].data[2] = tmpz;
   }
   fclose(fp);

}


void pointcloud_write (
      pointcloud_t *out_pointcloud
      ) {
   FILE *fp;
   int i,j;
   point_dim_t width, length;
   point_pix_t tmpx, tmpy, tmpz;

   fp=fopen("data/output.txt","w");

   width = out_pointcloud->width;
   fprintf(fp, "%d\n", width);

   length = out_pointcloud->length;
   fprintf(fp, "%d\n", length);

   for (i=0;i<length;i++) {
      /* Scan-line: */
         tmpx = out_pointcloud->points[i].data[0];
         tmpy = out_pointcloud->points[i].data[1];
         tmpz = out_pointcloud->points[i].data[2];
         fprintf(fp, "%d %d %d\n", tmpx, tmpy, tmpz);
   }
   fclose(fp);
}
