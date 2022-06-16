# encoding:utf-8
import datetime
import json
import os

from elasticsearch import Elasticsearch, helpers

es_dev = Elasticsearch("http://es-cn-st21z9y2f003i0ywo.elasticsearch.aliyuncs.com:9200",
                       http_auth=('elastic', 'jygsanBFSmwRl5'),
                       timeout=200)


def search_dirty_word(_source_from):
    predict_file = []
    path = '/data/zsl/torch_nlp_task/product/product_data/%s/predict_result/' % _source_from
    for root_path, dirs, files in os.walk(path):
        predict_file = files
        # print(123123,predict_file)

    predict_file = sorted(predict_file, key=lambda x: int(x.split('.')[0]))
    # print(11111,predict_file)
    flag = False
    for file_name in predict_file:
        print(2222, file_name)
        with open(path + file_name) as f:
            company_dict = {}
            for line in f.readlines():
                line_data = json.loads(line)
                # print(3333,b)

                _id = line_data['id']
                if _id == 'WsQhInwBMumHQQ3Yhhs_':
                    # print(222,file_name)
                    print(3333, line_data)
                    flag = True
                elif flag:
                    return


def update_baidu_baike_es_data(predict_path_name, index_name, update_field_name):
    predict_file = []
    path = '/data/zsl/product/product_data/%s/predict_result/' % predict_path_name
    for root_path, dirs, files in os.walk(path):
        predict_file = files

    predict_file = sorted(predict_file, key=lambda x: int(x.split('.')[0]))
    # print(11111,predict_file)
    for file_name in predict_file:
        # print(2222,file_name)
        # 组合
        time1 = datetime.datetime.now()
        with open(path + file_name) as f:

            output_data = []
            for line in f.readlines():
                line_data = json.loads(line)
                try:
                    _id = line_data['id']
                    product_list = list(line_data['label']['product'].keys())
                    action = {
                        "_index": index_name,
                        "_type": "doc",
                        "_id": _id,
                        "_op_type": "update",
                        "doc": {
                            update_field_name: product_list,
                            update_field_name + '_version': 1
                        }
                    }
                    # print(456456,_id,product_list)
                    output_data.append(action)

                except Exception as e:
                    # print('not exist',e)
                    continue

            time2 = datetime.datetime.now()
            print('组装数据耗时', time2 - time1)
            print(123123, len(output_data))
            helpers.bulk(es_dev, output_data)
            time3 = datetime.datetime.now()
            print('更新数据耗时', time3 - time2)
            print('%s|更新完成' % file_name)


def update_baidu_es_data():
    def get_ellipsis_position(text):
        i = 0
        position_list = []
        while i <= len(text) - 3:
            if text[i:i + 3] == '...':
                position_list.append(i)
                i += 3
            else:
                i += 1
        return position_list

    predict_file = []
    path = '/data/zsl/torch_nlp_task/product/product_data/baidu/predict_result/'
    for root_path, dirs, files in os.walk(path):
        predict_file = files

    predict_file = sorted(predict_file, key=lambda x: int(x.split('.')[0]))
    # print(11111,predict_file)
    for file_name in predict_file:
        # print(2222,file_name)
        # 组合
        time1 = datetime.datetime.now()
        with open(path + file_name) as f:

            output_data = []
            for line in f.readlines():
                line_data = json.loads(line)
                try:
                    _id = line_data['id']
                    text = line_data['text']
                    ellipsis_position = get_ellipsis_position(text)
                    product_data = line_data['label']['product']
                    valid_product_list = []
                    # print(11111,text)
                    # 过滤掉省略号的产品词
                    for key in product_data:
                        if '...' not in key:
                            flag = False
                            for _index_info in product_data[key]:
                                # print(123123,_index_info)
                                if _index_info[1] + 1 not in ellipsis_position:
                                    flag = True
                                    break
                            if flag:
                                valid_product_list.append(key)
                        # else:
                        #     print('22222',key)
                    # print(33333,valid_product_list)

                    # product_list = list(line_data['label']['product'].keys())

                    action = {
                        "_index": 'algo_baidu_mainproducts_2',
                        "_type": "doc",
                        "_id": _id,
                        "_op_type": "update",
                        "doc": {
                            'baidu_product_list': valid_product_list,
                            'baidu_product_list_version': 2
                        }
                    }
                    # print(456456,_id,product_list)
                    output_data.append(action)

                except Exception as e:
                    # print('not exist',e)
                    continue

            time2 = datetime.datetime.now()
            print('组装数据耗时', time2 - time1)
            print(123123, len(output_data))
            helpers.bulk(es_dev, output_data)
            time3 = datetime.datetime.now()
            print('更新数据耗时', time3 - time2)
            print('%s|更新完成' % file_name)


if __name__ == "__main__":
    '''
    寻找脏数据
    '''

    _source_from = 'official_web'
    search_dirty_word(_source_from)
