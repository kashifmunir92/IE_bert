from hdfs.ext.kerberos import KerberosClient
import os


proj_pretrain_model_path = 'pretrain/bert'
remote_proj_model_path = 'anchor_text/bert'
proj_sample_name = 'anchor_text'

prefix = '/dtb-dev/102/dev_Algo_Enterprise'
model_prefix='models'
sample_prefix='samples'

client = KerberosClient('http://cdp03-s05b0407.prd.qizhidao.com:9870;cdp04-s04b0408.prd.qizhidao.com:9870')

def save_model(local_model_path = 'model/bert'):
    hdfs_abs_model_path = prefix+'/'+model_prefix+'/'+remote_proj_model_path+'/pytorch_model.bin'
    client.upload(hdfs_abs_model_path, local_model_path, cleanup=True)

def load_model(local_model_path = 'model/bert/'):
    hdfs_abs_model_path = prefix+'/'+model_prefix+'/'+remote_proj_model_path+'/pytorch_model.bin'
    client.download(hdfs_abs_model_path, local_model_path)

def load_pretrain_model(local_pretrain_model_path = 'pretrain_model/'):
    if not os.path.exists(local_pretrain_model_path):
        os.makedirs(local_pretrain_model_path, exist_ok=True)
    hdfs_abs_model_path = prefix+'/'+model_prefix+'/'+proj_pretrain_model_path
    client.download(hdfs_abs_model_path, local_pretrain_model_path)

def load_samples(local_sample_path = 'datasets/'):
    if not os.path.exists(local_sample_path):
        os.makedirs(local_sample_path, exist_ok=True)    
    hdfs_abs_sample_path = prefix+'/'+sample_prefix+'/'+proj_sample_name
    client.download(hdfs_abs_sample_path, local_sample_path)

client.list(prefix)