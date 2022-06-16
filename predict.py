from utils.exception_handler import catch_exception

import json
import os

import glob
import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, SequentialSampler, TensorDataset
from torch.utils.data.distributed import DistributedSampler

from config.predict_config import args
from sequence.models.albert_for_ner import AlbertCrfForNer
from sequence.models.bert_for_ner import BertCrfForNer
from sequence.models.transformers import WEIGHTS_NAME, BertConfig, AlbertConfig
from sequence.processors.ner_seq import InputExample
from sequence.processors.ner_seq import collate_fn
from sequence.processors.ner_seq import convert_examples_to_features
from sequence.processors.ner_seq import ner_processors as processors
from sequence.processors.utils_ner import CNerTokenizer, get_entities
from utils.common import seed_everything
from utils.exception_handler import catch_exception
from utils.timer import time_cost

import subprocess
try:
    subprocess.run(["ldconfig"])
except:
    pass

if not os.path.exists(args.model_name_or_path+'/pytorch_model.bin'):
    from utils import hdfs_sl
    print('no model file. downloading...')
    hdfs_sl.load_model()
    print('model downloaded')


MODEL_CLASSES = {
    # bert ernie bert_wwm bert_wwwm_ext
    'bert': (BertConfig, BertCrfForNer, CNerTokenizer),
    'albert': (AlbertConfig, AlbertCrfForNer, CNerTokenizer)
}

# 使用的设备
args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")

# Set seed:设置种子数 使得每次结果是确定的
seed_everything(args.seed)
# Prepare NER task
args.task_name = args.task_name.lower()
if args.task_name not in processors:
    raise ValueError("Task not found: %s" % (args.task_name))

processor = processors[args.task_name]()

# get the train labels
label_list = processor.get_labels()
args.id2label = {i: label for i, label in enumerate(label_list)}
args.label2id = {label: i for i, label in enumerate(label_list)}
num_labels = len(label_list)

# 加载配置
args.model_type = args.model_type.lower()
config_class, model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
config = config_class.from_pretrained(args.config_name if args.config_name else args.model_name_or_path,
                                      num_labels=num_labels, cache_dir=args.cache_dir if args.cache_dir else None, )

# 加载模型
tokenizer = tokenizer_class.from_pretrained(args.output_dir, do_lower_case=args.do_lower_case)
checkpoints = [args.output_dir]
if args.predict_checkpoints > 0:
    checkpoints = list(
        os.path.dirname(c) for c in sorted(glob.glob(args.output_dir + '/**/' + WEIGHTS_NAME, recursive=True)))
    # logging.getLogger("transformers.modeling_utils").setLevel(logging.WARN)  # Reduce logging
    checkpoints = [x for x in checkpoints if x.split('-')[-1] == str(args.predict_checkpoints)]
# logger.info("Predict the following checkpoints: %s", checkpoints)
checkpoint = checkpoints[-1]

prefix = checkpoint.split('/')[-1] if checkpoint.find('checkpoint') != -1 else ""

model = model_class.from_pretrained(checkpoint, config=config)
model.to(args.device)


def _read_json(input_data):
    lines = []
    for line in input_data:
        # line = json.loads(line.strip())
        text = line['text']
        label_entities = line.get('label', None)
        words = list(text)
        labels = ['O'] * len(words)
        if label_entities is not None:
            for key, value in label_entities.items():
                for sub_name, sub_index in value.items():
                    for start_index, end_index in sub_index:
                        assert ''.join(words[start_index:end_index + 1]) == sub_name
                        if start_index == end_index:
                            labels[start_index] = 'S-' + key
                        else:
                            labels[start_index] = 'B-' + key
                            labels[start_index + 1:end_index + 1] = ['I-' + key] * (len(sub_name) - 1)
        lines.append({"words": words, "labels": labels})
    return lines


def _create_examples(lines, set_type):
    """Creates examples for the training and dev sets."""
    examples = []
    for (i, line) in enumerate(lines):
        guid = "%s-%s" % (set_type, i)
        text_a = line['words']
        # BIOS
        labels = line['labels']
        examples.append(InputExample(guid=guid, text_a=text_a, labels=labels))
    return examples


def load_test_data(args, task, tokenizer, test_data):
    processor = processors[task]()
    # Load data features from cache or dataset file

    # logger.info("Creating features from dataset file at %s", args.predict_data_dir)
    label_list = processor.get_labels()

    examples = _create_examples(test_data, 'test')
    features = convert_examples_to_features(examples=examples,
                                            tokenizer=tokenizer,
                                            label_list=label_list,
                                            max_seq_length=args.eval_max_seq_length,
                                            cls_token_at_end=bool(args.model_type in ["xlnet"]),
                                            pad_on_left=bool(args.model_type in ['xlnet']),
                                            cls_token=tokenizer.cls_token,
                                            cls_token_segment_id=2 if args.model_type in ["xlnet"] else 0,
                                            sep_token=tokenizer.sep_token,
                                            # pad on the left for xlnet
                                            pad_token=tokenizer.convert_tokens_to_ids([tokenizer.pad_token])[0],
                                            pad_token_segment_id=4 if args.model_type in ['xlnet'] else 0,
                                            )

    # Convert to Tensors and build dataset
    all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
    all_label_ids = torch.tensor([f.label_ids for f in features], dtype=torch.long)
    all_lens = torch.tensor([f.input_len for f in features], dtype=torch.long)
    dataset = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_lens, all_label_ids)
    return dataset


def predict(args, model, tokenizer, test_text, prefix=""):
    test_data = _read_json(test_text)
    test_dataset = load_test_data(args, args.task_name, tokenizer, test_data)
    # Note that DistributedSampler samples randomly
    test_sampler = SequentialSampler(test_dataset) if args.local_rank == -1 else DistributedSampler(test_dataset)
    # args.eval_batch_size = args.per_gpu_eval_batch_size * max(1, args.n_gpu)
    test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=args.per_gpu_eval_batch_size,
                                 collate_fn=collate_fn)

    results = []
    if isinstance(model, nn.DataParallel):
        model = model.module

    for step, batch in enumerate(test_dataloader):
        model.eval()
        batch = tuple(t.to(args.device) for t in batch)
        with torch.no_grad():
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": None, 'input_lens': batch[4]}
            if args.model_type != "distilbert":
                # XLM and RoBERTa don"t use segment_ids
                inputs["token_type_ids"] = (batch[2] if args.model_type in ["bert", "xlnet"] else None)
            outputs = model(**inputs)
            logits = outputs[0]
            tags = model.crf.decode(logits, inputs['attention_mask'])
            tags = tags.squeeze(0).cpu().numpy().tolist()

            # 解析当前batch标签
            for tag_info in tags:
                preds = tag_info[1:-1]  # [CLS]XXXX[SEP]
                label_entities = get_entities(preds, args.id2label, args.markup)
                json_d = dict()
                json_d['tag_seq'] = " ".join([args.id2label[x] for x in preds])
                json_d['entities'] = label_entities
                results.append(json_d)

    test_submit = []
    for x, y in zip(test_text, results):
        json_d = {'id': x['id'], 'text': x['text'], 'label': {}}
        entities = y['entities']
        words = list(x['text'])
        if len(entities) != 0:
            for subject in entities:
                tag = subject[0]
                start = subject[1]
                end = subject[2]
                word = "".join(words[start:end + 1])
                if tag in json_d['label']:
                    if word in json_d['label'][tag]:
                        json_d['label'][tag][word].append([start, end])
                    else:
                        json_d['label'][tag][word] = [[start, end]]
                else:
                    json_d['label'][tag] = {}
                    json_d['label'][tag][word] = [[start, end]]
        test_submit.append(json_d)

    return test_submit

@time_cost
@catch_exception
def predict_data(data):
    return predict(args, model, tokenizer, data, prefix=prefix)

def predict_single(args):
    """
    input: '{"id": id_str, "text": text}'
    """
    res = predict_data([args])
    return res

def demo_single():
    inp = {"id": "CN123456789A", "text": "该出口9.7在配给腔9的较高区域中开设，其形式为从配给腔9出来的通路。在本实施方式中，示例性地示出了两个出口，在图中一个在左侧，一个在右侧。 在第一实施方式中，出口9.7可以用作进入主流6中的浓盐溶液11的配给部位9.8"}
    ner_info = predict_single(inp)
    print(ner_info)


demo_single()