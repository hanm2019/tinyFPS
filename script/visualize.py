from plyfile import PlyData, PlyElement
import torch
import numpy as np
from open3d import *
import argparse

color_list = [[0, 0, 0], [0, 255, 0], [0, 0, 255], [255, 106, 106]]

dt = 0.01


def ply_point(points, color, dt=0):
    N, C = points.shape
    point_list = [
        (points[j, 0] + dt, points[j, 1] + dt, points[j, 2] + dt, color_list[color][0], color_list[color][1], color_list[color][2]) for
        j in range(N)]
    return point_list


def write_ply(save_path, points: torch.Tensor, sample_points: torch.Tensor):
    B, N, _ = points.shape
    for i in range(B):
        np_point = points[i].cpu().numpy()
        np_sample_point = sample_points[i].cpu().numpy()
        ply_points_list = ply_point(np_point, 0, 0)
        ply_sample_points_list = ply_point(np_sample_point, 1, dt)
        vertex_list = ply_points_list + ply_sample_points_list
        vertex = np.array(vertex_list,
                          dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
        el = PlyElement.describe(vertex, 'vertex', comments=['vertices'])
        PlyData([el], text=True).write(save_path + str(i) + '.ply')


def visualize(file_path):
    cloud = read_point_cloud(file_path)
    draw_geometries([cloud])


def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('Farthest point sampling visualize')
    parser.add_argument('--file', type=str, default='log/ply/point0_0.ply',
                        help='ply file name [default: point0_0.ply]')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    visualize(args.file)
