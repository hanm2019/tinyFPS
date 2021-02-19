import random
import torch
from time import time


def timeit(tag, t):
    print("{}: {}s".format(tag, time() - t))
    return time()


def dist_sq(a, b, dim):
    return sum((a[i] - b[i]) ** 2 for i in range(dim))


def rand_point(dim):
    return [random.uniform(-1, 1) for d in range(dim)]


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


def farthest_square_distance_index(src, dst):
    """
    Calculate Euclid distance between each two points.
    src^T * dst = xn * xm + yn * ym + zn * zm；
    sum(src^2, dim=-1) = xn*xn + yn*yn + zn*zn;
    sum(dst^2, dim=-1) = xm*xm + ym*ym + zm*zm;
    dist = (xn - xm)^2 + (yn - ym)^2 + (zn - zm)^2
         = sum(src**2,dim=-1)+sum(dst**2,dim=-1)-2*src^T*dst
    Input:
        src: source points, [N, C]
        dst: target points, [M, C]
    Output:
        dist: sum square distance, [1]
    """
    N, _ = src.shape
    M, _ = dst.shape
    dist = -2 * torch.matmul(src, dst.permute(1, 0))
    dist += torch.sum(src ** 2, -1).view(N, 1)
    dist += torch.sum(dst ** 2, -1).view(1, M)
    s = torch.max(torch.min(dist, -1)[0], -1)[1]
    return s


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


def point_cover_metrics(xyz: torch.Tensor, sample_points: torch.Tensor, radiu: float):
    _, N, _ = xyz.shape
    cover_num = point_cover(radiu, xyz, sample_points)
    cover_num_sum = point_cover_sum(radiu, xyz, sample_points)
    return torch.true_divide(cover_num, N), torch.true_divide(cover_num_sum, N)


def point_min_radiu_cover_metrics(xyz: torch.Tensor, sample_points: torch.Tensor, threshold: float, min_radiu: float, max_radiu: float):
    B, N, _ = xyz.shape
    # find the min radiu,where cover > threshold
    result1 =torch.zeros((B, 1)).to("cuda")
    for b in range(B):
        left_radiu = min_radiu
        right_radiu = max_radiu
        while True:
            radiu = (right_radiu + left_radiu) / 2
            cover_num = torch.true_divide(point_cover(radiu, xyz[b].unsqueeze(0), sample_points[b].unsqueeze(0)), N).item()
            if cover_num > threshold:
                right_radiu = radiu
            else:
                left_radiu = radiu
            if abs(right_radiu - left_radiu) < 0.01:
                break
        result1[b] = left_radiu
    return result1


def point_distance_metric(xyz, sample_points):
    return torch.true_divide(
        torch.sum(torch.sum(square_distance(sample_points, sample_points), dim=1), dim=1),
        torch.sum(torch.sum(square_distance(sample_points, xyz), dim=1), dim=1))

