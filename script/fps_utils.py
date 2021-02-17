import random
import torch
import numpy as np
from time import time


def timeit(tag, t):
    print("{}: {}s".format(tag, time() - t))
    return time()


def dist_sq(a, b, dim):
    return sum((a[i] - b[i]) ** 2 for i in range(dim))


def rand_point(dim):
    return [random.uniform(-1, 1) for d in range(dim)]


def rand_sample(size, npoint):
    B, N, _ = size
    arr = np.array(range(N))
    np.random.shuffle(arr)
    arr = torch.from_numpy(arr[:npoint]).to("cuda").repeat([B, 1])
    return arr


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


def point_distance_metric(xyz, index):
    sample_points = index_points(xyz, index)
    return torch.true_divide(
        torch.sum(torch.sum(square_distance(sample_points, sample_points), dim=1), dim=1),
        torch.sum(torch.sum(square_distance(sample_points, xyz), dim=1), dim=1))



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
        dist: sum square distance, [B, N, M]
    """
    B, N, _ = src.shape
    _, M, _ = dst.shape
    dist = -2 * torch.matmul(src, dst.permute(0, 2, 1))
    dist += torch.sum(src ** 2, -1).view(B, N, 1)
    dist += torch.sum(dst ** 2, -1).view(B, 1, M)
    return dist


def point_cover(radius, xyz, new_xyz):
    """
    Input:
        radius: local region radius
        xyz: all points, [B, N, 3]
        new_xyz: query points, [B, S, 3]
    Return:
        group_idx: grouped points index, [B, 1]
    """
    device = xyz.device
    B, N, C = xyz.shape
    _, S, _ = new_xyz.shape
    group_idx = torch.ones(N, dtype=torch.long).to("cuda").view(1, 1, N).repeat([B, S, 1])
    sqrdists = square_distance(new_xyz, xyz)
    group_idx[sqrdists > radius ** 2] = 0
    return torch.sum(torch.max(group_idx, dim=1)[0], dim=1)


def point_cover_sum(radius, xyz, new_xyz):
    """
    Input:
        radius: local region radius
        xyz: all points, [B, N, 3]
        new_xyz: query points, [B, S, 3]
    Return:
        group_idx: grouped points index, [B, 1]
    """
    device = xyz.device
    B, N, C = xyz.shape
    _, S, _ = new_xyz.shape
    group_idx = torch.ones(N, dtype=torch.long).to("cuda").view(1, 1, N).repeat([B, S, 1])
    sqrdists = square_distance(new_xyz, xyz)
    group_idx[sqrdists > radius ** 2] = 0
    return torch.sum(torch.sum(group_idx, dim=1), dim=1)


def farthest_point_sample(xyz: torch.Tensor, npoint: int):
    """
    Input:
        xyz: pointcloud data, [B, N, 3]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [B, npoint]
    """
    device = xyz.device
    B, N, C = xyz.shape
    centroids = torch.zeros(B, npoint, dtype=torch.long).to(device)
    distance = torch.ones(B, N).to(device) * 1e10
    farthest = torch.randint(0, N, (B,), dtype=torch.long).to(device)
    batch_indices = torch.arange(B, dtype=torch.long).to(device)
    for i in range(npoint):
        centroids[:, i] = farthest
        centroid = xyz[batch_indices, farthest, :].view(B, 1, 3)
        dist = torch.sum((xyz - centroid) ** 2, -1)
        mask = dist < distance
        distance[mask] = dist[mask]
        farthest = torch.max(distance, -1)[1]
    return centroids


def cpu_farthest_point_sample(xyz: np.array, npoint: int):
    """
    Input:
        xyz: pointcloud data, [B, N, 3]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [B, npoint]
    """
    batchsize, npts, dim = xyz.shape
    centroids = np.zeros((batchsize, npoint), dtype=np.long)
    distance = np.ones((batchsize, npts))*1e10
    farthest_id = np.random.randint(0, npts, (batchsize,), dtype=np.long)
    batch_index = np.arange(batchsize)
    for i in range(npoint):
        centroids[:, i] = farthest_id
        centro_pt = xyz[batch_index, farthest_id, :].reshape(batchsize, 1, 3)
        dist = np.sum((xyz - centro_pt) ** 2, -1)
        mask = dist < distance
        distance[mask] = dist[mask]
        farthest_id = np.argmax(distance[batch_index])
    return centroids


def point_cover_metrics(xyz: torch.Tensor, index: torch.Tensor, radiu: float):
    _, N, _ = xyz.shape
    sample_points = index_points(xyz, index)
    cover_num = point_cover(radiu, xyz, sample_points)
    cover_num_sum = point_cover_sum(radiu, xyz, sample_points)
    return torch.true_divide(cover_num, N), torch.true_divide(cover_num_sum, N)


