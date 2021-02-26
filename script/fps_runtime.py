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
from sampling import farthest_point_sample, cpu_farthest_point_sample

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('Farthest point sampling ')
    parser.add_argument('--num_point', type=int, default=1024, help='ModelNet40 Point Number [default: 1024]')
    parser.add_argument('--num_testcase', type=int, default=-1, help='testcase Number [default: -1(All dataset)]')
    parser.add_argument('--gpu',type=int, default=1, help='GPU [default: 1]')
    parser.add_argument('--dataset', type=str, default='modelnet40', help='point cloud dataset [default: modelnet40],[option:modelnet40,KITTI]')
    return parser.parse_args()


def main(args):
    def log_string(str):
        logger.info(str)
        print(str)

    '''CREATE DIR'''
    experiment_dir = 'log/runtime'
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)

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
        data_path = BASE_DIR + '/..' + '/data/modelnet40/modelnet40_normal_resampled/'
        test_dataset = ModelNetDataLoader(root=data_path, npoint=args.num_point, split='test',
                                          normal_channel=True, item_size = args.num_testcase)
        sample_list = [32,64,128,256]
    elif args.dataset == 'KITTI':
        data_path = BASE_DIR + '/..' + '/data/kitti/'
        if args.num_testcase == -1:
            item_size = 256
        else:
            item_size = args.num_testcase
        test_dataset = KITTIDataLoader(root=data_path,  split='testing',item_size = item_size)
        sample_list = [512, 1024, 2048, 4096]
    test_data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False,
                                                    num_workers=4)
    device = torch.device("cuda")

    for num_sampling in sample_list:
        total_time = 0
        i = 0
        with torch.no_grad():
            for j, data in tqdm(enumerate(test_data_loader), total=len(test_data_loader)):
                points, _ = data
                points = points.transpose(2, 1)
                if args.gpu:
                    points = points.to(device)
                    points = points[:, :3, :]
                    points = points.permute(0, 2, 1).contiguous()
                    start_time = time.time()
                    idx = farthest_point_sample(points, num_sampling)
                    torch.cuda.synchronize()
                    end_time = time.time()
                    total_time = total_time + (end_time - start_time)
                else:
                    points = points[:, :3, :]
                    points = points.permute(0, 2, 1).numpy()
                    start_time = time.time()
                    cpu_farthest_point_sample(points, num_sampling)
                    end_time = time.time()
                    total_time = total_time + (end_time - start_time)
                i = i + 1
        log_string("sampling:%d avg_time:%f" % (num_sampling,  total_time / i))


if __name__ == '__main__':
    args = parse_args()
    main(args)
