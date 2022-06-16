**cdsw指南:**
https://cf.qizhidao.com/pages/viewpage.action?pageId=85930575

**访问混合云:**
需要配置dns
首选: 172.18.32.7
备选：114.114.114.114

**demo:**
尝试直接运行 predict.py 中的demo_single() 来看效果。
如果要起model, 可以用predict.py 中的predict_single() 来起服务。

**project:**
所有项目用public模式起。合作者配在project 里面。这样团队内可以互相学习。
项目名要有足够描述性。
项目建议直接用git保存在gitlab中。方便共享，方便合作。

**模型存储：**
大文件不应该存在项目中，模板项目维护了gitignore 文件。
所有模型文件以及很大的样本数据应该存在hdfs：
可以使用utils/hdfs_sl.py 脚本上传或者下载模型文件和训练样本。

hdfs 目录结构：
/dtb-dev/102/是开发环境下算法部门的目录，下面按组分开。
每个人可以考虑用项目名或者自己的账号名做目录名。

模型文件：/dtb-dev/102/dev_Algo_Enterprise/models/model_name

预训练模型文件存在：/dtb-dev/102/dev_Algo_Enterprise/models/pretrain/bert
数据集：
/dtb-dev/102/dev_Algo_Enterprise/datasets/data_name

**更多数据读写：**
hive: utils/hive_reader.py
es: es_client.py
更多: https://cf.qizhidao.com/pages/viewpage.action?pageId=85927160

**训练流程：**
从hdfs 上下载预训练模型：
import utils.hdfs_sl
utils.hdfs_sl.load_pretrain_model()
然后运行 run_train.sh

**预测流程：**
从hdfs上下载训练好的模型：
import utils.hdfs_sl
utils.hdfs_sl.load_model()
然后运行predict.py

**gpu相关：**
包很大的话最好直接放在我们自己的pypi上面，速度会很快。参考requirements.txt
cdsw 里面目前要使用显卡，需要先运行ldconfig. 参考predict.py 中的示例。

**model:**
model用来提供模型验证，以及实时调用。
建议每个项目留一个低资源，cpu版本的model用作测试和实验。这个服务可以配置免密。
model 本身可以要很多资源，并且内置了网关和负载均衡.
model启动前会自动运行cdsw-build.sh， 所以把环境搭建写在里面即可。

**job:**
这个功能用来跑批。提供多种定时方式。
job并不会执行cdsw-build.sh， 和session差不多.
所以需要创建合适的session kernel，基于其创建job。