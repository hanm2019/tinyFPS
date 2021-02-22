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
    parser.add_argument('--solution', type=int, default=1,
                        help='solution [1:fps,default,2:random,3:k_random, 4:k/m_batch, 5:k*m_fps_cm, 6: k_batch]')
    parser.add_argument('--batch_size', type=int, default=2, help='batch_size [default: 2')
    parser.add_argument('--dataset', type=str, default='modelnet40',
                        help='point cloud dataset [default: modelnet40],[option:modelnet40,KITTI]')
    parser.add_argument('--metrics', type=str, default='cover',
                        help='metrics list [default: cover], [option: cover,distance,minradiu]')
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
    metric_base_list = ['cover', 'distance', 'minradiu']
    for metric_str in metric_str_list:
        if metric_str in metric_base_list:
            metric_list.append(metric_str)

    if args.dataset == 'modelnet40':
        data_path = BASE_DIR + '/..' + '/data/modelnet40/modelnet40_normal_resampled/'
        test_dataset = ModelNetDataLoader(root=data_path, npoint=1024, split='test',
                                          normal_channel=True, item_size=args.num_testcase)
        min_radiu = 0.1
        max_radiu = 1.0
        mult_kdtree_batch = 4
        mult_kdtree_batch2 = 4
        radiu_list = [0.05, 0.1, 0.2, 0.4]
    elif args.dataset == 'KITTI':
        data_path = BASE_DIR + '/..' + '/data/kitti/'
        if args.num_testcase == -1:
            item_size = 256
        else:
            item_size = args.num_testcase
        test_dataset = KITTIDataLoader(root=data_path, split='testing', item_size=item_size)
        min_radiu = 0.5
        max_radiu = 4.0
        mult_kdtree_batch = 16
        mult_kdtree_batch2 = 4
        radiu_list = [0.25, 0.5, 1, 2]
    test_data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False,
                                                   num_workers=4)
    device = torch.device("cuda")

    for num_sampling in sample_list:
        cover_total_rate_list = [torch.zeros((args.batch_size, 1)).to('cuda') for i in range(4)]
        cover_total_sum_rate_list = [torch.zeros((args.batch_size, 1)).to('cuda') for i in range(4)]
        distance_total_rate = torch.zeros((args.batch_size, 1)).to('cuda')
        min_radiu_total = torch.zeros((args.batch_size, 1)).to('cuda')
        batch_count_total = 0
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
                elif args.solution == 3:  # k random
                    sample_points = sampling.kdt_random(points, num_sampling)
                elif args.solution == 4:  # k/m batch
                    sample_points = sampling.kdt_m_batch_fps(points, num_sampling, mult_kdtree_batch)
                elif args.solution == 5:  # k*m fps_cm
                    sample_points = sampling.m_kdt_fps_cm(points, num_sampling, mult_kdtree_batch2)
                elif args.solution == 6:  # k batch log
                    sample_points = sampling.kdt_batch_log_fps(points, num_sampling)
                elif args.solution == 7:  # k batch log dim
                    sample_points = sampling.kdt_batch_log_fps(points, num_sampling, dim=True)
                elif args.solution == 8:  # k/m batch log
                    sample_points = sampling.kdt_m_batch_log_fps(points, num_sampling, mult_kdtree_batch)
                elif args.solution == 9:  # k/m batch log dim
                    sample_points = sampling.kdt_m_batch_log_fps(points, num_sampling, mult_kdtree_batch, dim=True)
                elif args.solution == 10:  # fps_k/m batch mean
                    sample_points, batch_count = sampling.kdt_m_batch_mean_fps(points, num_sampling, mult_kdtree_batch, dim=False)
                    batch_count_total =  batch_count_total + batch_count
                elif args.solution == 11:  # random k/m batch mean
                    sample_points, batch_count = sampling.kdt_m_batch_mean_fps(points, num_sampling, mult_kdtree_batch, dim=False, random=True)
                    batch_count_total =  batch_count_total + batch_count
                if 'cover' in metric_list:
                    for i, radiu in enumerate(radiu_list):
                        cover_rate, cover_sum_rate = fps_utils.point_cover_metrics(points, sample_points, radiu)
                        cover_total_rate_list[i] = cover_total_rate_list[i] + cover_rate
                        cover_total_sum_rate_list[i] = cover_total_sum_rate_list[i] + cover_sum_rate
                if 'distance' in metric_list:
                    distance_rate = fps_utils.point_distance_metric(points, sample_points)
                    distance_total_rate = distance_total_rate + distance_rate
                if 'minradiu' in metric_list:
                    min_radiu_metric = fps_utils.point_min_radiu_cover_metrics(points, sample_points, 0.95, min_radiu,
                                                                               max_radiu)
                    min_radiu_total = min_radiu_total + min_radiu_metric

        log_string("[DataSet: %s, Sample:%d, solution: %d]" % (args.dataset, num_sampling, args.solution))
        if 'cover' in metric_list:
            log_string("\t|radiu\t\t|cover_rate\t|cover_sum\t|")
            for i, radiu in enumerate(radiu_list):
                log_string("\t|%f\t|%f\t|%f\t|" % (radiu, (torch.mean(cover_total_rate_list[i]) / len(test_data_loader)).item(), (torch.mean(cover_total_sum_rate_list[i]) / len(test_data_loader)).item()))
        if 'distance' in metric_list:
            log_string("\tdistance:%f" % ((torch.mean(distance_total_rate) / len(test_data_loader)).item()))
        if 'minradiu' in metric_list:
            log_string("\tminradiu:%f" % ((torch.mean(min_radiu_total) / len(test_data_loader)).item()))
        if args.solution in [10, 11]:
            log_string("\tbatch_count:%f" % ((batch_count_total / len(test_data_loader) / args.batch_size)))
        log_string("finish")
        torch.cuda.empty_cache()


if __name__ == '__main__':
    args = parse_args()
    main(args)
