#include <stdio.h>
#include "point_aux.h"


void pointcloud_read (
		pointcloud_t *in_pointcloud,
		point_dim_t idx
      ) {
   point_dim_t width, length;
   int i;
   FILE        *fp;
   char filename[80];
   int tmpx, tmpy, tmpz;

   sprintf(filename, "/home/hanmeng/Documents/tinyFPS/hls/FPS/source/%d.txt", idx);

   fp=fopen(filename,"r");
   if (fp == NULL){
       printf("file open failed\n");
   }

   width = WIDTH;
   length = LENGTH;

   in_pointcloud->width  = width;
   in_pointcloud->length = length;

   for (i=0;i<length;i++) {
	   fscanf(fp, "%d %d %d", &tmpx, &tmpy, &tmpz);
       in_pointcloud->points[i].data[0] = (point_pix_t)tmpx;
       in_pointcloud->points[i].data[1] = (point_pix_t)tmpy;
       in_pointcloud->points[i].data[2] = (point_pix_t)tmpz;
   }
   fclose(fp);

}


void pointcloud_write (
      pointcloud_t *out_pointcloud,
	  point_dim_t idx
      ) {
   FILE *fp;
   int i,j;
   point_dim_t width, length;
   point_pix_t tmpx, tmpy, tmpz;

//   char filename[30];
//sprintf(filename, "result/%d.txt", idx);

   fp=fopen("/home/hanmeng/Documents/tinyFPS/hls/FPS/result/output.txt","w");

   if(fp == NULL){
	   printf("file open failed\n");
   }
   width = out_pointcloud->width;
   fprintf(fp, "%d\n", width);

   length = out_pointcloud->length;
   fprintf(fp, "%d\n", length);

   for (i=0;i<length;i++) {
      /* Scan-line: */
         tmpx = out_pointcloud->points[i].data[0];
         tmpy = out_pointcloud->points[i].data[1];
         tmpz = out_pointcloud->points[i].data[2];
         fprintf(fp, "%d %d %d\n", (int)tmpx, (int)tmpy, (int)tmpz);
   }
   fclose(fp);
}
