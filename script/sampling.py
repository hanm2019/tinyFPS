import torch
import numpy as np
import math
import fps_utils
import cuda.fps_stack_cuda as origin_fps

def rand_sample(size, npoint):
    B, N, _ = size
    arr = np.array(range(N))
    np.random.shuffle(arr)
    arr = torch.from_numpy(arr[:npoint]).to("cuda").repeat([B, 1])
    return arr




def farthest_point_sample_cuda(xyz: torch.Tensor, npoint: int):
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
    origin_fps.furthest_point_sampling_wrapper(B, N, npoint, xyz, temp, output)
    return output




def farthest_point_sample_pytorch(xyz: torch.Tensor, npoint: int, first=-1):
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


def farthest_point_sample(xyz: torch.Tensor, npoint: int, first=-1, cuda=True):
    if cuda == False:
        return farthest_point_sample_pytorch(xyz, npoint, first)
    else:
        return farthest_point_sample_cuda(xyz, npoint).long()



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


