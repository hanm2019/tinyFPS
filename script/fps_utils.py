import random
import torch
import numpy as np

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



