import torch
import numpy as np
import approximate_kdtree
import math
import fps_utils


def rand_sample(size, npoint):
    B, N, _ = size
    arr = np.array(range(N))
    np.random.shuffle(arr)
    arr = torch.from_numpy(arr[:npoint]).to("cuda").repeat([B, 1])
    return arr


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
    distance = np.ones((batchsize, npts)) * 1e10
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


def mult_farthest_point_sample(xyz: torch.Tensor, npoint: int):
    B, _, D = xyz.shape
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, np.ceil(np.log2(npoint)))
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    _, N, M, _ = tree.shape
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    bucket_list = rand_sample((1, N, D), npoint)
    for i, bucket_idx in enumerate(bucket_list[0]):
        for j in range(B):
            random_high = int(size[j][bucket_idx].item())
            random_idx = np.random.randint(0, random_high)
            sample_points[j][i][:] = tree[j][bucket_idx][random_idx][:]
    return sample_points


def mult_batch_farthest_point_sample(xyz: torch.Tensor, npoint: int, batch: int):
    B, _, D = xyz.shape
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, np.ceil(np.log2(npoint / batch)))
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    _, N, M, _ = tree.shape
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    already_sample = 0
    for batch_idx in range(batch):
        if already_sample == 0:
            frame_size = math.ceil(npoint / batch)
            bucket_list = rand_sample((1, N, D), frame_size)
            for i, bucket_idx in enumerate(bucket_list[0]):
                for j in range(B):
                    random_high = int(size[j][bucket_idx].item())
                    random_idx = np.random.randint(0, random_high)
                    sample_points[j][i][:] = tree[j][bucket_idx][random_idx][:]
            already_sample = already_sample + frame_size
        else:
            frame_size = min(math.ceil(npoint / batch), npoint - already_sample)
            bucket_list = rand_sample((1, N, D), frame_size)
            S = sample_points[:, :already_sample, :]
            #print("already_sample", already_sample,"S:",S.shape)  # wanted: B, already_sample , 3
            for i, bucket_idx in enumerate(bucket_list[0]):
                for j in range(B):
                    random_high = int(size[j][bucket_idx].item())
                    P = tree[j][bucket_idx][:random_high][:]  # wanted:random_high, 3
                    bucket_point_idx = fps_utils.farthest_square_distance_index(P, S[j, :, :])
                    sample_points[j, already_sample + i, :] = P[bucket_point_idx, :]
            already_sample = already_sample + frame_size
    return sample_points
