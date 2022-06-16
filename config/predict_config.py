import argparse
import os

# 手动配置参数
args = argparse.ArgumentParser()
args.model_type = 'bert'
args.model_name_or_path = 'model/bert'
args.task_name = "patent_ocr"
args.eval_max_seq_length = 512
args.per_gpu_eval_batch_size = 128
args.output_dir = 'model/bert'
args.overwrite_output_dir = False
args.seed = 42
args.local_rank = -1
args.no_cuda = False
args.config_name = ''
args.cache_dir = ''
args.tokenizer_name = ''
args.do_lower_case = True
args.predict_checkpoints = 0
args.markup = 'bios'
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

# 通过parse加载参数
# args = get_argparse().parse_args()
# os.environ["CUDA_VISIBLE_DEVICES"] = args.use_device
# os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3'
