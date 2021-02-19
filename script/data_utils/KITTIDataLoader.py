import numpy as np
import warnings
import os
from torch.utils.data import Dataset
warnings.filterwarnings('ignore')


class KITTIDataLoader(Dataset):
    def __init__(self, root,  split='testing',  cache_size=150, item_size = -1):
        self.root = root + '/' + split + '/velodyne/'
        self.item_size = item_size

        # list of (shape_name, shape_txt_file_path) tuple
        self.datapath = len([lists for lists in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, lists))])

        print('The size of %s data is %d'%(split,self.datapath))
        point_set = np.fromfile(self.root + '000000.bin', dtype=np.float32).reshape(-1, 4)
        print('data shape:',point_set.shape)
        self.cache_size = cache_size  # how many data points to cache in memory
        self.cache = {}  # from index to (point_set, cls) tuple

    def __len__(self):
        if self.item_size == -1:
            return self.datapath
        else:
            return min(self.item_size,self.datapath)

    def _get_item(self, index):
        if index in self.cache:
            point_set = self.cache[index]
        else:
            index_str = ("%06d.bin") % index
            fn = self.root + index_str
            point_set = np.fromfile(fn, dtype=np.float32).reshape(-1,4)
            point_set= point_set[:,:3]
            #mal the point_set
            #point_set = (point_set - point_set.min()) / (point_set.max() - point_set.min())
            #point_set = point_set.reshape(-1,3)
            cls = np.array([1,1,1,1]).astype(np.int32)
            if len(self.cache) < self.cache_size:
                self.cache[index] = (point_set,cls)

        return point_set,cls

    def __getitem__(self, index):
        return self._get_item(index)

