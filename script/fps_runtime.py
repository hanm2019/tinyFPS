from data_utils.ModelNetDataLoader import ModelNetDataLoader
from data_utils.KITTIDataLoader import KITTIDataLoader
import argparse
import numpy as np
import os
import torch
import logging
from tqdm import tqdm
import sys
import time
from pointnet_util import farthest_point_sample

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('Farthest point sampling ')
    parser.add_argument('--num_point', type=int, default=1024, help='Point Number [default: 1024]')
    parser.add_argument('--num_sampling', type=int, default=256, help='sample Number [default: 256]')
    parser.add_argument('--num_testcase', type=int, default=-1, help='testcase Number [default: -1(All dataset)]')
    parser.add_argument('--normal', action='store_true', default=True,
                        help='Whether to use normal information [default: False]')
    parser.add_argument('--gpu', type=int, default=1, help='enable gpu [default: 1]')
    parser.add_argument('--dataset', type=str, default='modelnet40', help='point cloud dataset [default: modelnet40,KITTI]')
    return parser.parse_args()


def main(args):
    def log_string(str):
        logger.info(str)
        print(str)

    '''CREATE DIR'''
    experiment_dir = 'log/gpu_runtime'

    '''LOG'''
    args = parse_args()
    logger = logging.getLogger("Model")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('%s/%s_eval.txt' % (experiment_dir,args.dataset))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    log_string('PARAMETER ...')
    log_string(args)
    log_string('Load dataset ...')
    if args.dataset == 'modelnet40':
        DATA_PATH = BASE_DIR +'/..' + '/data/modelnet40/modelnet40_normal_resampled/'
        TEST_DATASET = ModelNetDataLoader(root=DATA_PATH, npoint=args.num_point, split='test',
                                          normal_channel=args.normal,item_size = args.num_testcase)
        SAMPLE_LIST = [32,64,128,256,512]
    elif args.dataset == 'KITTI':
        DATA_PATH = BASE_DIR + '/..' +  '/data/kitti/'
        TEST_DATASET = KITTIDataLoader(root=DATA_PATH,  split='testing',item_size = args.num_testcase)
        SAMPLE_LIST = [128,256,512,1024,2048]
    testaccDataLoader = torch.utils.data.DataLoader(TEST_DATASET, batch_size=1, shuffle=False,
                                                    num_workers=4)
    device = torch.device("cuda" if args.gpu else "cpu")

    for num_sampling in SAMPLE_LIST:
        total_time = 0
        i = 0
        with torch.no_grad():
            for j, data in tqdm(enumerate(testaccDataLoader), total=len(testaccDataLoader)):
                points, _ = data
                points = points.transpose(2, 1)
                points = points.to(device)
                start_time = time.time()
                farthest_point_sample(points, num_sampling)
                if args.gpu:
                    torch.cuda.synchronize()
                end_time = time.time()
                total_time = total_time + (end_time - start_time)
                i = i + 1
        log_string("sampling:%d avg_time:%f" % (num_sampling,  total_time / i))

if __name__ == '__main__':
    args = parse_args()
    main(args)
