from ModelNetDataLoader import ModelNetDataLoader
import argparse
import numpy as np
import os
import torch
import logging
from tqdm import tqdm


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(FILE_DIR, "../..")

def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('ModelNet40 resample')
    parser.add_argument('--num_point', type=int, default=1024, help='ModelNet40 Point Number [default: 1024]')
    return parser.parse_args()


def main(args):
    def log_string(str):
        logger.info(str)
        print(str)

    '''CREATE DIR'''
    experiment_dir = 'log/resample'
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)

    '''LOG'''
    args = parse_args()
    logger = logging.getLogger("Model")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('%s/eval.txt' % experiment_dir)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    log_string('PARAMETER ...')
    log_string(args)
    log_string('Load dataset ...')


    data_path = BASE_DIR + '/data/modelnet40/modelnet40_normal_resampled/'
    dataset = ModelNetDataLoader(root=data_path, npoint=args.num_point, split='test',
                                          normal_channel=True)
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False,
                                                    num_workers=4)

    for j, data in tqdm(enumerate(data_loader), total=len(data_loader)):
        points, _ = data
        points = points.transpose(2, 1)
        points = (points[0, :3, :] + 1) * 128
        points = points.permute(1, 0).numpy()
        points = np.ceil(points) - 1
        points.astype(np.int)
        np.savetxt(BASE_DIR + '/hls/FPS/data/' + str(j) + '.txt', points, fmt="%d %d %d", delimiter='\n')


if __name__ == '__main__':
    args = parse_args()
    main(args)
