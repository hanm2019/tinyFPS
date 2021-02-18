from data_utils.ModelNetDataLoader import ModelNetDataLoader
from data_utils.KITTIDataLoader import KITTIDataLoader
import argparse
import os
import torch
import logging
from tqdm import tqdm
import fps_utils
import sampling
import visualize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('Farthest point sampling metrics')
    parser.add_argument('--num_sampling', type=str, default='256', help='sample Number [default: 256]')
    parser.add_argument('--num_testcase', type=int, default=-1, help='testcase Number [default: -1(All dataset)]')
    parser.add_argument('--solution', type=int, default=1, help='solution [1:fps,default,2:random,3:mult, 4:mult_batch]')
    parser.add_argument('--radiu', type=float, default=0.05, help='point cover radiu [default: 0.05')
    parser.add_argument('--batch_size', type=int, default=2, help='batch_size [default: 2')
    parser.add_argument('--dataset', type=str, default='modelnet40',
                        help='point cloud dataset [default: modelnet40],[option:modelnet40,KITTI]')
    parser.add_argument('--metrics', type=str, default='cover',
                        help='metrics list [default: cover], [option: cover,distance]')
    return parser.parse_args()


def main(args):
    def log_string(str):
        logger.info(str)
        print(str)

    '''CREATE DIR'''
    experiment_dir = 'log/metrics'
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)

    '''LOG'''
    args = parse_args()
    logger = logging.getLogger("Model")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('%s/%s_eval.txt' % (experiment_dir, args.dataset))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    log_string('PARAMETER ...')
    log_string(args)
    sampling_str_list = args.num_sampling.split(',')
    sample_list = []
    for sampling_str in sampling_str_list:
        sample_list.append(int(sampling_str))

    metric_str_list = args.metrics.split(',')
    metric_list = []
    metric_base_list = ['cover', 'distance']
    for metric_str in metric_str_list:
        if metric_str in metric_base_list:
            metric_list.append(metric_str)

    if args.dataset == 'modelnet40':
        data_path = BASE_DIR + '/..' + '/data/modelnet40/modelnet40_normal_resampled/'
        test_dataset = ModelNetDataLoader(root=data_path, npoint=1024, split='test',
                                          normal_channel=True, item_size=args.num_testcase)
        # sample_list = [32,64,128,256]
    elif args.dataset == 'KITTI':
        data_path = BASE_DIR + '/..' + '/data/kitti/'
        test_dataset = KITTIDataLoader(root=data_path, split='testing', item_size=min(args.num_testcase, 256))
        # sample_list = [2048, 4096, 8192, 16384]
    test_data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False,
                                                   num_workers=4)
    device = torch.device("cuda")

    for num_sampling in sample_list:
        cover_total_rate = torch.zeros((args.batch_size, 1)).to('cuda')
        cover_total_sum_rate = torch.zeros((args.batch_size, 1)).to('cuda')
        distance_total_rate = torch.zeros((args.batch_size, 1)).to('cuda')

        with torch.no_grad():
            for j, data in tqdm(enumerate(test_data_loader), total=len(test_data_loader)):
                points, _ = data
                points = points.transpose(2, 1)
                points = points.to(device)
                points = points[:, :3, :]
                points = points.permute(0, 2, 1).contiguous()
                if args.solution == 1:  # fps
                    idx = sampling.farthest_point_sample(points, num_sampling)
                    sample_points = fps_utils.index_points(points, idx)
                elif args.solution == 2:  # random
                    idx = sampling.rand_sample(points.shape, num_sampling)
                    sample_points = fps_utils.index_points(points, idx)
                elif args.solution == 3:  # mult-kdtree random
                    sample_points = sampling.mult_farthest_point_sample(points, num_sampling)
                elif args.solution == 4:  # mult-kdtree batch
                    sample_points = sampling.mult_batch_farthest_point_sample(points, num_sampling, 2)
                if 'cover' in metric_list:
                    cover_rate, cover_sum_rate = fps_utils.point_cover_metrics(points, sample_points, args.radiu)
                    cover_total_rate = cover_total_rate + cover_rate
                    cover_total_sum_rate = cover_total_sum_rate + cover_sum_rate
                if 'distance' in metric_list:
                    distance_rate = fps_utils.point_distance_metric(points, sample_points)
                    distance_total_rate = distance_total_rate + distance_rate

        rate, sum_rate, distance_rate = torch.mean(cover_total_rate), torch.mean(cover_total_sum_rate), torch.mean(
            distance_total_rate)
        log_string("cover:%f, sum_cover:%f,distance:%f" % ((rate / len(test_data_loader)).item(),
                                                      (sum_rate / len(test_data_loader)).item(),
                                                      (distance_rate / len(test_data_loader)).item()))
        log_string("finish")


if __name__ == '__main__':
    args = parse_args()
    main(args)
