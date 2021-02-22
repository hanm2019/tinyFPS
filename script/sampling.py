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
    distance = torch.ones(B, N).to(device) * 1e20
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


def kdt_random(xyz: torch.Tensor, npoint: int):
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


def kdt_m_batch_fps(xyz: torch.Tensor, npoint: int, batch: int):
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
            # print("already_sample", already_sample,"S:",S.shape)  # wanted: B, already_sample , 3
            for i, bucket_idx in enumerate(bucket_list[0]):
                for j in range(B):
                    random_high = int(size[j][bucket_idx].item())
                    P = tree[j][bucket_idx][:random_high][:]  # wanted:random_high, 3
                    bucket_point_idx = fps_utils.farthest_square_distance_index(P, S[j, :, :])
                    sample_points[j, already_sample + i, :] = P[bucket_point_idx, :]
            already_sample = already_sample + frame_size
    return sample_points


def m_kdt_fps_cm(xyz: torch.Tensor, npoint: int, batch: int):
    B, _, D = xyz.shape
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, np.ceil(np.log2(npoint * batch)))
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    bucket_idxs = farthest_point_sample(cm, npoint)
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    for batch_idx in range(B):
        for i, bucket_idx in enumerate(bucket_idxs[batch_idx]):
            bucket_size = int(size[batch_idx][bucket_idx].item())
            cm_point = cm[batch_idx][bucket_idx].reshape(1, 1, D)
            bucket_points = tree[batch_idx, bucket_idx, :bucket_size, :].reshape(1, -1, D)
            bucket_cm_point_index = torch.min(fps_utils.square_distance(cm_point, bucket_points), -1)[1]
            sample_points[batch_idx, i, :] = tree[batch_idx, bucket_idx, bucket_cm_point_index, :]
    return sample_points


def kdt_batch_log_fps(xyz: torch.Tensor, npoint: int, dim=False):
    B, _, D = xyz.shape
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, np.ceil(np.log2(npoint)), dim)
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    order, batch_lists = fps_utils.batch_travel_order(pow(2, int(np.ceil(np.log2(npoint)))))
    random_high = int(torch.min(size[:, npoint - 1], 0)[0])
    sample_points[:, 0, :] = tree[:, npoint - 1, np.random.randint(0, random_high), :]
    already_sample = 1
    for i, batch_list in enumerate(batch_lists):
        S = sample_points[:, :already_sample, :]
        for batch_idx in batch_list:
            bucket_size = int(torch.min(size, 0)[0][batch_idx])
            P = tree[:, batch_idx, :bucket_size, :].reshape(B, -1, D)
            bucket_point_idx = fps_utils.farthest_square_distance_index_batch(P, S).reshape(B, -1)
            if i == 0:
                sample_points[:, 0, :] = fps_utils.index_points(P, bucket_point_idx)[:, 0, :]
            else:
                sample_points[:, already_sample, :] = fps_utils.index_points(P, bucket_point_idx)[:, 0, :]
                already_sample = already_sample + 1
            if already_sample == npoint:
                break
    return sample_points


def kdt_m_batch_log_fps(xyz: torch.Tensor, npoint: int, batch: int, dim=False):
    B, _, D = xyz.shape
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, np.ceil(np.log2(npoint / batch)), dim)
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    order, batch_lists = fps_utils.batch_travel_order(pow(2, int(np.ceil(np.log2(npoint / batch)))))
    random_high = int(torch.min(size[:, int(np.ceil(npoint / batch)) - 1], 0)[0])
    sample_points[:, 0, :] = tree[:, int(np.ceil(npoint / batch)) - 1, np.random.randint(0, random_high), :]
    already_sample = 1
    for b in range(batch):
        for i, batch_list in enumerate(batch_lists):
            S = sample_points[:, :already_sample, :]
            for batch_idx in batch_list:
                bucket_size = int(torch.min(size, 0)[0][batch_idx])
                P = tree[:, batch_idx, :bucket_size, :].reshape(B, -1, D)
                bucket_point_idx = fps_utils.farthest_square_distance_index_batch(P, S).reshape(B, -1)
                if i == 0 and b == 0:
                    sample_points[:, 0, :] = fps_utils.index_points(P, bucket_point_idx)[:, 0, :]
                else:
                    sample_points[:, already_sample, :] = fps_utils.index_points(P, bucket_point_idx)[:, 0, :]
                    already_sample = already_sample + 1
                if already_sample == npoint:
                    break
    return sample_points


def kdt_m_batch_mean_fps(xyz: torch.Tensor, npoint: int, batch: int, dim=False, random=False, random_divide = 1):
    B, _, D = xyz.shape
    approximate_kdtree_high = int(np.ceil(np.log2(npoint / batch)))
    bucket_size = int(pow(2, approximate_kdtree_high))
    approximate_tree = approximate_kdtree.approximate_kdtree(xyz, approximate_kdtree_high, dim)
    tree, cm, size = approximate_tree.make_approximate_kdtree()
    sample_points = torch.zeros((B, npoint, D), dtype=torch.float).to("cuda")
    min_bucket_distance = np.ones((B, bucket_size))*1e10
    min_distance = np.min(min_bucket_distance, axis=1)
    if not random:
        b_idx = farthest_point_sample(xyz, bucket_size)
        sample_points[:, :bucket_size, :] = fps_utils.index_points(xyz, b_idx)
    else:
        bucket_list = rand_sample((1, bucket_size, D), int(bucket_size / random_divide))
        for b in range(B):
            for i in bucket_list[0]:
                sample_points[b, i, :] = tree[b, i, int(np.random.randint(0, int(size[b, i].cpu()[0]))), :]
    batch_count = 0
    for b in range(B):
        already_sample = int(bucket_size / random_divide)
        while already_sample != npoint:
            S = sample_points[b, :already_sample, :].reshape(1, -1, D)
            for i in range(bucket_size):
                P = tree[b, i, :int(size[b, i]), :].reshape(1, -1, D)
                min_dist = torch.min(fps_utils.square_distance(P, S), -1)[0]
                max_min_dist, max_min_dist_idx = torch.max(min_dist, -1)
                max_min_dist = max_min_dist.reshape(1).cpu().numpy()
                max_min_dist_idx = max_min_dist_idx.reshape(1)
                if max_min_dist > min_distance[b]:
                    point = P[0, max_min_dist_idx, :]
                    sample_points[b, already_sample, :] = point
                    already_sample = already_sample + 1
                    if already_sample == npoint:
                        break
                    point_dist = fps_utils.square_distance(P, point.reshape(1,1,D)).reshape(1, -1)
                    min_bucket_distance[b][i] = torch.max(torch.min(min_dist, point_dist), -1)[0]
                else:
                    min_bucket_distance[b][i] = min(min_bucket_distance[b][i], max_min_dist)
            min_distance = np.mean(min_bucket_distance, axis=1)
            batch_count = batch_count + 1
    return sample_points, batch_count