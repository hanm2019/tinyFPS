'''
the variance for diff dataset,sample_number,random,metric_function

'''

import fps_utils
from data_utils.KITTIDataLoader import KITTIDataLoader
import torch
from tqdm import tqdm
from fps_utils import farthest_point_sample
import matplotlib.pyplot as plt
import os
import numpy as np
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "../")

if __name__ == '__main__':
    def log_string(str):
        logger.info(str)
        print(str)

    '''CREATE DIR'''
    experiment_dir = 'log/fps_metrics/kitti128'
    if not os.path.exists(PROJECT_DIR + experiment_dir):
        os.mkdir(PROJECT_DIR+experiment_dir)
    logger = logging.getLogger("Model")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('%s/eval.txt' % (experiment_dir))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    # KITTI, same sample_number,sum_function,for each frame, sample 10 times
    dataset = 'KITTI'
    DATA_PATH = PROJECT_DIR + 'data/kitti/'
    TEST_DATASET = KITTIDataLoader(root=DATA_PATH, split='testing', item_size=256)
    SAMPLE_LIST = [128,256,512,1024]
    testaccDataLoader = torch.utils.data.DataLoader(TEST_DATASET, batch_size=1, shuffle=False,
                                                    num_workers=4)
    device = torch.device("cuda")
    for num_sampling in SAMPLE_LIST:
        with torch.no_grad():
            metric1_array = np.zeros((len(testaccDataLoader), 10), dtype=np.float64)
            metric2_array = np.zeros((len(testaccDataLoader), 10), dtype=np.float64)
            log_string(("start...dataset:%s,sampling:%d" % (dataset, num_sampling)))
            for j, data in tqdm(enumerate(testaccDataLoader), total=len(testaccDataLoader)):
                points_, _ = data
                points_ = points_.transpose(2, 1)
                points = points_.to(device)
                for i in range(0, 10):
                    result = farthest_point_sample(points, num_sampling).cpu().numpy()[0]
                    sample_points = []
                    for idx in result:
                        sample_points.append(points_[0, :3, idx].numpy().tolist())
                    dis_point = points_[0, :3, :].permute(1, 0).numpy().tolist()
                    metric1_array[j][i] = fps_utils.gpu_fps_metric(dis_point, sample_points, torch.sum)
                    metric2_array[j][i] = fps_utils.gpu_fps_metric(dis_point, sample_points, torch.max)
            log_string(("finish...dataset:%s,sampling:%d" % (dataset, num_sampling)))
            np.savetxt((experiment_dir + "/%s_%d_sum.txt" % (dataset, num_sampling)), metric1_array, encoding='utf-8')
            np.savetxt((experiment_dir + "/%s_%d_max.txt" % (dataset, num_sampling)), metric2_array, encoding='utf-8')
            log_string(("save to file:%s_%d.txt" % (dataset, num_sampling)))
    log_string("finish")
