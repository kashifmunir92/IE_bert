CURRENT_DIR=`pwd`
export BERT_BASE_DIR=$CURRENT_DIR/pretrain_model/
export GLUE_DIR=$CURRENT_DIR/datasets/
export OUTPUR_DIR=$CURRENT_DIR/model/

# TASK_NAME="cluener"
# TASK_NAME="patent_ocr"
# TASK_NAME="main_product"
TASK_NAME="patent_names"


python bert_crf_train.py \
  --model_type=bert \
  --model_name_or_path=$BERT_BASE_DIR \
  --task_name=$TASK_NAME \
  --do_train \
  --do_eval \
  --do_lower_case \
  --data_dir=$GLUE_DIR/${TASK_NAME}/ \
  --train_max_seq_length=128 \
  --eval_max_seq_length=512 \
  --per_gpu_train_batch_size=8 \
  --per_gpu_eval_batch_size=24 \
  --learning_rate=3e-5 \
  --num_train_epochs=1.0 \
  --logging_steps=448 \
  --save_steps=448 \
  --output_dir=$OUTPUR_DIR/${TASK_NAME}/ \
  --overwrite_output_dir \
  --seed=42
