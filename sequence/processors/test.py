# encoding:utf-8
import datetime
import json
import os

from elasticsearch import Elasticsearch, helpers

es_dev = Elasticsearch("http://es-cn-st21z9y2f003i0ywo.elasticsearch.aliyuncs.com:9200",
                       http_auth=('elastic', 'jygsanBFSmwRl5'),
                       timeout=200)

post_name_list = []
with open('/data/zsl/torch_nlp_task/product/product_data/dict/post_name_list.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        value = line.strip()
        if value not in post_name_list:
            post_name_list.append(value)
post_name_list = set(post_name_list)


def repair_product_info(text, product_info, _type):
    '''
    _type:1官网，2百度，3百科
    '''
    product_list = []
    for x in product_info:
        # 后续增加白名单数据不处理
        # if x in white_word_list:
        #     pass

        for y in product_info[x]:
            # print(123123,x,y)
            change_name = x
            if _type == 2 and text[y[1] + 1:y[1] + 4] == '...':
                # print('wrong product',text[y[0]:y[1]+4])
                continue

            if x[-2:] not in post_name_list and text[y[1] + 1:y[1] + 3] not in post_name_list:
                # 当前识别产品词尾缀不在后缀列表且产品词后续两位也不在尾缀列表时，判断是否拼接
                for post_name in post_name_list:
                    # print(11111,post_name)
                    new_name = str(text[y[0]:y[1] + 2])
                    if new_name != x and new_name.endswith(post_name):
                        change_name = text[y[0]:y[1] + 2]
                        print(123123, x, change_name)
                        break
            # else:
            #     print(22222,x,text[y[0]:y[1]+3])

            product_list.append(change_name)

    return product_list


def update_official_web_es_data():
    predict_file = []
    path = '/data/zsl/torch_nlp_task/product/product_data/official_web/predict_result/'
    for root_path, dirs, files in os.walk(path):
        predict_file = files
        # print(123123,predict_file)

    predict_file = sorted(predict_file, key=lambda x: int(x.split('.')[0]))
    # print(11111,predict_file)
    for file_name in predict_file:
        print('########', file_name)
        # 组合
        time1 = datetime.datetime.now()
        with open(path + file_name) as f:
            company_dict = {}
            for line in f.readlines():
                line_data = json.loads(line)
                # print(3333,b)
                _id = line_data['id']
                text = line_data['text']
                try:
                    product_info = line_data['label']['product']
                    # print(1111,list(line_data['label']['product'].keys()))
                    product_list = repair_product_info(text, product_info, 1)
                except Exception as e:
                    # print('error',e)
                    product_list = []
                    # print(22222,product_list)
                if _id not in company_dict:
                    company_dict[_id] = product_list
                else:
                    company_dict[_id] += product_list

        # 更新es库数据
        output_data = []
        for key in company_dict:
            action = {
                "_index": "algo_official_web_mainproducts",
                "_type": "_doc",
                "_id": key,
                "_op_type": "update",
                "doc": {
                    'company_product_list_2': list(set(company_dict[key])),
                    'company_product_list_version': 5
                }
            }

            output_data.append(action)
        time2 = datetime.datetime.now()
        print('组装数据耗时', time2 - time1)
        # print(123123,len(output_data))
        helpers.bulk(es_dev, output_data)
        time3 = datetime.datetime.now()
        print('更新数据耗时', time3 - time2)
        print('%s|更新完成' % file_name)


def update_baike_es_data():
    predict_file = []
    path = '/data/zsl/torch_nlp_task/product/product_data/baike/predict_result/'
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
                _id = line_data['id']
                text = line_data['text']
                try:
                    product_info = line_data['label']['product']
                    product_list = repair_product_info(text, product_info, 3)
                except Exception as e:
                    # print('error',e)
                    product_list = []
                action = {
                    "_index": 'algo_baike_mainproducts',
                    "_type": "doc",
                    "_id": _id,
                    "_op_type": "update",
                    "doc": {
                        'baike_product_list': product_list,
                        'baike_product_list_version': 3
                    }
                }
                output_data.append(action)

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
        print('file name', file_name)
        # 组合
        time1 = datetime.datetime.now()
        with open(path + file_name) as f:
            output_data = []
            for line in f.readlines():
                line_data = json.loads(line)

                _id = line_data['id']
                text = line_data['text']
                # ellipsis_position = get_ellipsis_position(text)
                try:
                    product_info = line_data['label']['product']
                    product_list = repair_product_info(text, product_info, 2)
                    product_list = list(set(product_list))
                except Exception as e:
                    # print('error',e)
                    product_list = []

                action = {
                    "_index": 'algo_baidu_mainproducts_2',
                    "_type": "doc",
                    "_id": _id,
                    "_op_type": "update",
                    "doc": {
                        'baidu_product_list': product_list,
                        'baidu_product_list_version': 2
                    }
                }
                output_data.append(action)

            time2 = datetime.datetime.now()
            print('组装数据耗时', time2 - time1)
            print(123123, len(output_data))
            helpers.bulk(es_dev, output_data)
            time3 = datetime.datetime.now()
            print('更新数据耗时', time3 - time2)
            print('%s|更新完成' % file_name)


if __name__ == "__main__":
    # 更新官网数据
    update_official_web_es_data()

    # 更新百度数据
    # update_baidu_es_data()

    # 更新百科数据
    # update_baike_es_data()
