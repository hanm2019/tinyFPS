import random
import torch
import numpy as np
from time import time
import fps_stack_src.fps_stack_cuda as fps


def timeit(tag, t):
    print("{}: {}s".format(tag, time() - t))
    return time()


def dist_sq(a, b, dim):
    return sum((a[i] - b[i]) ** 2 for i in range(dim))


def rand_point(dim):
    return [random.uniform(-1, 1) for d in range(dim)]


def max_function(point, dest_points):
    max_result = 0
    for dest_point in dest_points:
        max_result = max(max_result, dist_sq(point, dest_point, 3))
    return max_result


def sum_function(point, dest_points):
    result = 0
    for dest_point in dest_points:
        result = result + dist_sq(point, dest_point, 3)
    return result


def gpu_fps_metric(points, sample_points, distance_func=torch.sum):
    sample_result = np.float64(0)
    tensor_dest_points = torch.Tensor(points).to("cuda")
    for sample_point in sample_points:
        tensor_point = torch.Tensor(sample_point).to("cuda")
        sample_result = sample_result + distance_func((tensor_dest_points - tensor_point) ** 2).cpu().numpy()
    return sample_result


def fps_metric(points, sample_points, distance_func=sum_function):
    sample_result = 0
    for sample_point in sample_points:
        sample_result = sample_result + distance_func(sample_point, points)
    return sample_result


def index_points(points, idx):
    """
    Input:
        points: input points data, [B, N, C]
        idx: sample index data, [B, S]
    Return:
        new_points:, indexed points data, [B, S, C]
    """
    device = points.device
    B = points.shape[0]
    view_shape = list(idx.shape)
    view_shape[1:] = [1] * (len(view_shape) - 1)
    repeat_shape = list(idx.shape)
    repeat_shape[0] = 1
    batch_indices = torch.arange(B, dtype=torch.long).to(device).view(view_shape).repeat(repeat_shape)
    new_points = points[batch_indices, idx, :]
    return new_points


def square_distance(src, dst):
    """
    Calculate Euclid distance between each two points.
    src^T * dst = xn * xm + yn * ym + zn * zm；
    sum(src^2, dim=-1) = xn*xn + yn*yn + zn*zn;
    sum(dst^2, dim=-1) = xm*xm + ym*ym + zm*zm;
    dist = (xn - xm)^2 + (yn - ym)^2 + (zn - zm)^2
         = sum(src**2,dim=-1)+sum(dst**2,dim=-1)-2*src^T*dst
    Input:
        src: source points, [B, N, C]
        dst: target points, [B, M, C]
    Output:
        dist: sum square distance, [B, 1]
    """
    B, N, _ = src.shape
    _, M, _ = dst.shape
    dist = -2 * torch.matmul(src, dst.permute(0, 2, 1))
    dist += torch.sum(src ** 2, -1).view(B, N, 1)
    dist += torch.sum(dst ** 2, -1).view(B, 1, M)
    return dist.sum(dim=1).sum(dim=1)


def farthest_point_sample(xyz: torch.Tensor, npoint: int):
    """
    Input:
        xyz: pointcloud data, [B, N, 3]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [B, npoint]
    """
    assert xyz.is_contiguous()

    B, N, _ = xyz.size()
    output = torch.cuda.IntTensor(B, npoint)
    temp = torch.cuda.FloatTensor(B, N).fill_(1e10)
    fps.furthest_point_sampling_wrapper(B, N, npoint, xyz, temp, output)
    return output



