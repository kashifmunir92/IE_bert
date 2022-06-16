# encoding:utf-8
import json

from elasticsearch import Elasticsearch

es_dev = Elasticsearch("http://es-cn-st21z9y2f003i0ywo.elasticsearch.aliyuncs.com:9200",
                       http_auth=('elastic', 'jygsanBFSmwRl5'),
                       timeout=200)


def create_baike_test_data(data, count):
    with open("/data/zsl/product/product_data/baike/predict_data/%s.json" % str(count), "w") as f:
        for x in data:
            _id = x['_id']
            text = x['_source'][text_name].replace(' ', '')
            if text:
                new_dict = {
                    'id': _id,
                    'text': text
                }
                f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


def create_baidu_test_data(data, count):
    with open("/data/zsl/product/product_data/baidu/predict_data/%s.json" % str(count), "w") as f:
        for x in data:
            _id = x['_id']
            text = x['_source'][text_name]
            if text:
                new_dict = {
                    'id': _id,
                    'text': text.replace('百度快照', '')
                }
                f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


def create_official_web_test_data(data, count):
    with open("/data/zsl/torch_nlp_task/product/product_data/official_web/predict_data/%s.json" % str(count), "w") as f:
        for x in data:
            _id = x['_id']
            text = x['_source'][text_name]
            # print(1111,_id,text)
            if len(text) <= 256:
                # 长度小于512的句子只处理收尾
                new_text_list = []
                cut_sentence = str(text).split('。')

                for index in range(len(cut_sentence)):
                    flag = True
                    if ((index == 0 or index == len(cut_sentence) - 1) and (
                            cut_sentence[index].count(' ') > 1 or cut_sentence[index].count('|') > 1 or cut_sentence[
                        index].count('_') > 1)):
                        flag = False
                    if flag and cut_sentence[index]:
                        new_text_list.append(cut_sentence[index])

                # print(123123,new_text_list)
                if new_text_list:
                    new_dict = {
                        'id': _id,
                        'text': '。'.join(new_text_list)
                    }
                    f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')

            else:
                # 长度大于512的段落进行分组，每组不超过512
                new_sentence_list = []
                cut_sentence = str(text).split('。')
                for index in range(len(cut_sentence)):
                    flag = True
                    cur_sentence = cut_sentence[index]
                    if ((index == 0 or index == len(cut_sentence) - 1) and (
                            cut_sentence[index].count(' ') > 1 or cut_sentence[index].count('|') > 1 or cut_sentence[
                        index].count('_') > 1)):
                        flag = False
                    elif 'copyright' in cut_sentence[index].lower():
                        flag = False
                    else:
                        # 去除无关预测文本
                        for son_sentence in cur_sentence.split(','):
                            if '用于' in son_sentence and '领域' in son_sentence:
                                cur_sentence = cur_sentence.replace(son_sentence, '')
                            if '用于' in son_sentence and '行业' in son_sentence:
                                cur_sentence = cur_sentence.replace(son_sentence, '')

                    cur_sentence = cur_sentence.replace('\t', '').replace('\n', '').replace('\n\t', '')
                    if flag and cur_sentence:
                        new_sentence_list.append(cur_sentence)

                count_length = 0
                temp = []
                while new_sentence_list:
                    cur_text = new_sentence_list.pop(0)
                    cur_length = len(cur_text)
                    if count_length + cur_length < 256:
                        count_length += cur_length
                        temp.append(cur_text)
                    else:
                        new_dict = {
                            'id': _id,
                            'text': '。'.join(temp)
                        }
                        f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')
                        count_length = cur_length
                        temp = [cur_text]
                # print(22222,temp)
                if temp:
                    new_dict = {
                        'id': _id,
                        'text': '。'.join(temp)
                    }
                    f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


def create_official_web_test_data2(data, count):
    with open("/data/zsl/torch_nlp_task/product/product_data/official_web/predict_data/%s.json" % str(count), "w") as f:
        for x in data:
            _id = x['_id']
            text = x['_source'][text_name]

            cut_sentence = list(set(str(text).split('。')))

            for index in range(len(cut_sentence)):
                flag = True
                if ((index == 0 or index == len(cut_sentence) - 1) and (
                        cut_sentence[index].count(' ') > 1 or cut_sentence[index].count('|') > 1 or cut_sentence[
                    index].count('_') > 1)):
                    flag = False

                if flag:
                    new_dict = {
                        'id': _id,
                        'text': cut_sentence[index]
                    }
                    f.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


def get_es_test_data():
    query_body = {
        "query": {
            "bool": {
                "must": [

                ]
            }
        },
        "_source": [text_name],
        "size": size
    }

    queryData0 = es_dev.search(
        index=index_name,
        # doc_type='_doc',
        scroll='10m',
        size=size,
        body=query_body,
    )

    # 处理首页数据

    count = 1
    mdata = queryData0.get("hits").get("hits")
    if not mdata:
        return

    create_data(mdata, count)

    scroll_id = queryData0["_scroll_id"]
    total = queryData0["hits"]["total"]

    page_num = int(total / size)
    print('查询数据量|页数', total, page_num)
    # 处理翻页数据
    while page_num:
        print('剩余页数:', page_num)
        page_data = es_dev.scroll(scroll_id=scroll_id, scroll='5m')["hits"]["hits"]
        count += 1
        create_data(page_data, count)
        page_num -= 1


def get_official_data_by_name(company_name):
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"name": company_name}}
                ]
            }
        },
        "_source": [text_name],
    }

    queryData0 = es_dev.search(
        index=index_name,
        # doc_type='_doc',
        scroll='5m',
        body=query_body,
    )

    # 处理首页数据

    count = 1
    mdata = queryData0.get("hits").get("hits")
    if not mdata:
        return
    print(123123, mdata[0])
    create_official_web_test_data(mdata, 0)


if __name__ == "__main__":
    # baike info
    # size = 10000
    # index_name = 'algo_baike_mainproducts'
    # text_name = 'abstract'
    # create_data = create_baike_test_data

    # baidu info
    # size = 10000
    # index_name = 'algo_baidu_mainproducts_2'
    # text_name = 'abstract'
    # create_data = create_baidu_test_data

    # official_web info
    size = 1000
    index_name = 'algo_official_web_mainproducts'
    text_name = 'brif'

    create_data = create_official_web_test_data
    get_es_test_data()

    # company_name = '攸县凤明生态农业发展有限公司'
    # get_official_data_by_name(company_name)
