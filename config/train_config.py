import argparse
import os

root_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


args = argparse.ArgumentParser()

# args.task_name = "name_product"
# args.task_name = "main_product"
# args.task_name = "patent_ocr"
args.task_name = "anchor_text"

# 当前使用的卡
os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3'
# os.environ["CUDA_VISIBLE_DEVICES"] = '3'

args.eval_max_seq_length=512
args.per_gpu_eval_batch_size=256
# 通用参数
args.model_type = 'bert'
args.model_name_or_path = root_path+'/pretrain_model'
args.output_dir = root_path+'/model/%s/'%args.task_name
args.overwrite_output_dir = False
args.seed=42
args.local_rank = -1
args.no_cuda = False
args.config_name = ''
args.cache_dir = ''
args.tokenizer_name = ''
args.do_lower_case = True
args.predict_checkpoints = 0
args.markup = 'bios'

# 训练参数
args.data_dir = 'datasets/%s/'%args.task_name
args.do_train = True
args.do_eval = True
args.train_max_seq_length=128
args.per_gpu_train_batch_size=24
args.learning_rate=3e-5
args.num_train_epochs=3
args.logging_steps=448
args.save_steps=448
args.overwrite_output_dir = 1

args.fp16 = False
args.fp16_opt_level = '01'
args.max_steps = -1
args.overwrite_cache=True
args.gradient_accumulation_steps = 1
args.weight_decay = 0.01
args.crf_learning_rate = 5e-5
args.adam_epsilon =1e-8
args.max_grad_norm = 1.0
args.warmup_proportion = 0.1
args.logging_steps = 50





