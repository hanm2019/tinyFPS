import random


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


def fps_metric(points, sample_points, distance_func=sum_function):
    sample_result = 0
    for sample_point in sample_points:
        sample_result = sample_result + distance_func(sample_point, points)
    return sample_result


def point_metric(points, distance_func=sum_function):
    total_result = 0
    for point in points:
        total_result = total_result + distance_func(point, points)
    return total_result


