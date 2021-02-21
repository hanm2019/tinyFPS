import torch
import fps_utils
import math
import numpy as np

class approximate_kdtree:

    def __init__(self, xyz: torch.Tensor, high: int, dim = False):
        assert high > 0
        assert xyz.shape[1] > pow(2, high)
        self.B, self.N, self.D = xyz.shape
        self.high = high
        self.dim = dim
        self.b_xyz = xyz.cpu().numpy().tolist()
        self.kdtree = torch.zeros((1, 1, math.ceil(self.N / pow(2, self.high)), self.D), dtype=torch.float).to(
            "cuda").repeat(
            [self.B, int(pow(2, self.high )), 1, 1])
        self.kdtree_cm = torch.zeros((1, 1, self.D), dtype=torch.float).to("cuda").repeat(
            [self.B, int(pow(2, self.high )), 1])
        self.kdtree_bucket_size = torch.zeros((1, 1, 1), dtype=torch.float).to("cuda").repeat(
            [self.B, int(pow(2, self.high )), 1])

    def sub_make_approximate_kdtree(self, xyz: list, batch_idx: int, i: int, level: int, index: int):
        if level != 0:
            xyz.sort(key=lambda x: x[i])
            i = (i + 1) % self.D
            half = len(xyz) >> 1
            self.sub_make_approximate_kdtree(xyz[:half], batch_idx, i, level - 1, index * 2)
            self.sub_make_approximate_kdtree(xyz[half:], batch_idx, i, level - 1, index * 2 + 1),
        else:
            xyz = torch.Tensor(xyz)
            self.kdtree[batch_idx][index][:][:xyz.shape[0]] = xyz
            self.kdtree_bucket_size[batch_idx][index] = xyz.shape[0]
            self.kdtree_cm[batch_idx][index][:] = torch.mean(xyz, dim=0)

    def sub_make_approximate_dim_kdtree(self, xyz: list, batch_idx: int, level: int, index: int):
        if level != 0:
            xyz_np = np.array(xyz)
            dim = np.argmax(xyz_np.max(axis=0) - xyz_np.min(axis=0))
            xyz.sort(key=lambda x: x[dim])
            half = len(xyz) >> 1
            self.sub_make_approximate_dim_kdtree(xyz[:half], batch_idx,  level - 1, index * 2)
            self.sub_make_approximate_dim_kdtree(xyz[half:], batch_idx,  level - 1, index * 2 + 1),
        else:
            xyz = torch.Tensor(xyz)
            self.kdtree[batch_idx][index][:][:xyz.shape[0]] = xyz
            self.kdtree_bucket_size[batch_idx][index] = xyz.shape[0]
            self.kdtree_cm[batch_idx][index][:] = torch.mean(xyz, dim=0)


    def make_approximate_kdtree(self):
        for batch_idx, xyz in enumerate(self.b_xyz):
            if self.dim:
                self.sub_make_approximate_dim_kdtree(xyz, batch_idx, self.high, 0)
            else:
                self.sub_make_approximate_kdtree(xyz, batch_idx, 0, self.high, 0)
        return self.kdtree, self.kdtree_cm, self.kdtree_bucket_size

    def getkdtree(self):
        return self.kdtree

    def getkdtree_cm(self):
        return self.kdtree_cm

    def getkdtree_bucket_size(self):
        return self.kdtree_bucket_size


if __name__ == "__main__":
    testcase = torch.Tensor([fps_utils.rand_point(3) for x in range(1001)]).repeat([1, 1, 1])
    akdtree = approximate_kdtree(testcase, 7, dim=True)
    tree, cm, bucket_size = akdtree.make_approximate_kdtree()
    # print(tree.shape)
    # print(cm)
    # print(bucket_size)
