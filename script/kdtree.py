"""
A super short KD-Tree for points...
so concise that you can copypasta into your homework without arousing suspicion.


Usage:
1. Use make_kd_tree to create the kd
2. You can then use `get_knn` for k nearest neighbors or 
   `get_nearest` for the nearest neighbor

points are be a array of points: [[0, 1, 2], [12.3, 4.5, 2.3], ...]

"""
import numpy as np
from fps_utils import dist_sq
from fps_utils import rand_point

dim = 3
debug = False


def dist_sq_dim(a, b):
    return dist_sq(a, b, dim)


def sub_make_kd_tree(points, dim, i=0):
    if len(points) > 1:
        points.sort(key=lambda x: x[i])
        i = (i + 1) % dim
        half = len(points) >> 1
        return [
            sub_make_kd_tree(points[: half], dim, i),
            sub_make_kd_tree(points[half + 1:], dim, i),
            points[half]
        ]
    elif len(points) == 1:
        return [None, None, points[0]]


# Makes the KD-Tree for fast lookup

def numpy_make_kd_tree(points, dim, i=0):
    # change np.array to list
    points_array = points.tolist()
    return sub_make_kd_tree(points_array, dim, i)


def make_kd_tree(points, dim, i=0):
    return sub_make_kd_tree(points, dim, i)


# Adds a point to the kd-tree
def add_point(kd_node, point, dim, i=0):
    if kd_node is not None:
        dx = kd_node[2][i] - point[i]
        i = (i + 1) % dim
        for j, c in ((0, dx >= 0), (1, dx < 0)):
            if c and kd_node[j] is None:
                kd_node[j] = [None, None, point]
            elif c:
                add_point(kd_node[j], point, dim, i)


# k nearest neighbors
'''
kd_node: the root of tree
point: the goal point
k : k-nearest neighbors
dim: the total dim number
dist_func: dist function,default is (x-y)**2
return_distances: wheather return the distance
i: first dim index
heap: a heap for result

'''


def get_knn(kd_node, point, k, dim, dist_func=dist_sq_dim, return_distances=False, i=0, heap=None):
    import heapq
    is_root = not heap
    if is_root:
        heap = []
    if kd_node is not None:
        dist = dist_func(point, kd_node[2])
        dx = kd_node[2][i] - point[i]
        if len(heap) < k:
            heapq.heappush(heap, (-dist, kd_node[2]))
        elif dist < -heap[0][0]:
            heapq.heappushpop(heap, (-dist, kd_node[2]))
        i = (i + 1) % dim
        # Goes into the left branch, and then the right branch if needed
        get_knn(kd_node[dx < 0], point, k, dim, dist_func, return_distances, i, heap)
        if dx * dx < -heap[0][0] or len(heap) < k:
            get_knn(kd_node[dx >= 0], point, k, dim, dist_func, return_distances, i, heap)
    if is_root:
        neighbors = sorted((-h[0], h[1]) for h in heap)
        return neighbors if return_distances else [n[1] for n in neighbors]


''' For the closest neighbor
kd_node: the root of tree
point: the goal point
dim: the total dim number
dist_func: dist function,default is (x-y)**2
return_distances: wheather return the distance
i: first dim index
best: a heap for result

'''


def get_nearest(kd_node, point, dim, dist_func=dist_sq_dim, return_distances=False, i=0, best=None):
    if kd_node is not None:
        dist = dist_func(point, kd_node[2])
        dx = kd_node[2][i] - point[i]
        if not best:
            best = [dist, kd_node[2]]
        elif dist < best[0]:
            best[0], best[1] = dist, kd_node[2]
        i = (i + 1) % dim
        # Goes into the left branch, and then the right branch if needed
        get_nearest(kd_node[dx < 0], point, dim, dist_func, return_distances, i, best)
        if dx * dx < best[0]:
            get_nearest(kd_node[dx >= 0], point, dim, dist_func, return_distances, i, best)
    return best if return_distances else best[1]


'''
kd_node: the root of tree
point: the goal point
k : k-nearest neighbors
dim: the total dim number
radiu: the dist limit
upperK: the length of result, -1 means no limit
dist_func: dist function,default is (x-y)**2
return_distances: wheather return the distance
i: first dim index
heap: a heap for result
is_root: the root flag

'''


def get_ball_query(kd_node, point, dim, radiu, upperK=-1, dist_func=dist_sq_dim, return_distances=False, i=0,
                   heap=None, is_root=True):
    import heapq
    if is_root:
        heap = []
    if kd_node is not None:
        dist = dist_func(point, kd_node[2])
        dx = kd_node[2][i] - point[i]
        if dist <= radiu:
            if upperK == -1 or len(heap) < upperK:
                if debug:
                    print("push a node:", kd_node[2], "len(heap):", len(heap))
                heapq.heappush(heap, (-dist, kd_node[2]))
            elif dist < -heap[0][0]:
                if debug:
                    print("push pop a node:", kd_node[2], " len(heap):", len(heap))
                heapq.heappushpop(heap, (-dist, kd_node[2]))
        i = (i + 1) % dim
        # Goes into the left branch, and then the right branch if needed
        get_ball_query(kd_node[dx < 0], point, dim, radiu, upperK, dist_func, return_distances, i, heap, False)
        if (upperK == -1 and dx * dx <= radiu) or \
                (upperK != -1 and len(heap) < upperK and dx * dx <= radiu) or \
                (upperK != -1 and len(heap) == upperK and dx * dx < -heap[0][0]):
            get_ball_query(kd_node[dx >= 0], point, dim, radiu, upperK, dist_func, return_distances, i, heap, False)
    if is_root:
        neighbors = sorted((-h[0], h[1]) for h in heap)
        return neighbors if return_distances else [n[1] for n in neighbors]


"""
Below is all the testing code
"""

import random


def puts(l):
    for x in l:
        print(x)


if __name__ == '__main__':
    points = np.array([rand_point(dim) for x in range(10000)])

    test = [rand_point(dim) for x in range(10)]

    kd_tree = numpy_make_kd_tree(points, dim)

    print(get_nearest(kd_tree, test[0], dim, dist_sq_dim))
    print(get_ball_query(kd_tree, test[0], dim, 0.1, 5, dist_sq_dim))  # limit of 5
    print(get_ball_query(kd_tree, test[0], dim, 0.1, -1, dist_sq_dim))  # no limit
    print("")
    for t in test:
        print(get_knn(kd_tree, t, 8, dim, dist_sq_dim))

"""
You can also define the distance function inline, like:

print get_nearest(kd_tree, [0] * dim, dim, lambda a,b: dist_sq(a, b, dim))
print get_nearest(kd_tree, [0] * dim, dim, lambda a,b: sum((a[i] - b[i]) ** 2 for i in range(dim)))
"""
