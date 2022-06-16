# encoding:utf-8
import json
import os

import pandas as pd

hook_keyword = ['包括', '包含', '例如', '比如', ':']


def get_cooccur_data(text, line_product_list):
    '''
    获取共现关系
    '''
    sentence_list = str(text).split('。')
    end_index = 0
    i = 0
    j = 0
    cooccur_data = []
    temp = []
    # 双指针匹配方式，O(n+m)
    while i < len(sentence_list):
        end_index += len(sentence_list[i]) + 1
        while j < len(line_product_list):
            if line_product_list[j][1] <= end_index:
                cur_word = line_product_list[j][2]
                if cur_word not in temp:
                    temp.append(cur_word)
                j += 1
            else:
                if temp:
                    cooccur_data.append(temp)
                temp = []
                break
        i += 1

    if temp:
        cooccur_data.append(temp)

    return cooccur_data


def get_relation_data(text, line_product_list):
    i = 0
    flag = False
    while i < len(text):
        if text[i:i + 2] in hook_keyword:
            line_product_list.append([i, i + 2, text[i:i + 2], 0])
            i += 2
            flag = True
        else:
            if text[i] in hook_keyword:
                line_product_list.append([i, i + 1, text[i], 0])
                flag = True
            elif text[i] in ['；', ';']:
                line_product_list.append([i, i + 1, text[i], -1])

            i += 1

    line_product_list = sorted(line_product_list, key=lambda x: x[0])
    # print('new_product_list', line_product_list)

    # 删除冲突数据，遇到冲突保留类型1
    index = 1
    while index < len(line_product_list):
        if line_product_list[index][0] < line_product_list[index - 1][1]:
            if line_product_list[index][3] == 1:
                # print('删除元素1',line_product_list[index-1])
                line_product_list.pop(index - 1)
            else:
                # print('删除元素2', line_product_list[index])
                line_product_list.pop(index)
        else:
            index += 1

    all_relation_info = []
    if flag:
        j = 0
        son_state = [0, ] * len(line_product_list)
        father_node = None
        hook = None
        temp = []
        while j < len(line_product_list):
            if line_product_list[j][3] == 0:
                if son_state[j - 1] == 0 and j > 0 and j < len(line_product_list) - 1 and line_product_list[j - 1][
                    3] == 1:
                    if (j - 2 >= 0 and line_product_list[j - 1][0] - line_product_list[j - 2][1] > 2) or j - 2 < 0:
                        father_node = line_product_list[j - 1]
                        hook = line_product_list[j][2]

            elif line_product_list[j][3] == 1:
                # 间隔不大于10,存在上下位关系
                if line_product_list[j][0] - line_product_list[j - 1][1] <= 10 and father_node:
                    cur_product = line_product_list[j]
                    if cur_product[2] != father_node[2]:
                        temp.append(cur_product)
                    son_state[j] = 1
                else:
                    if father_node and temp and (temp[0][0] - father_node[1] <= 10):
                        # print(1111,father_node,hook,temp)
                        all_relation_info.append([father_node, hook, temp])
                        temp = []
                        father_node = None
                        hook = None
            else:
                # type = -1 被句子级分隔符中断，重新获取father_node，hook and temp
                if father_node and temp and (temp[0][0] - father_node[1] <= 10):
                    # print(22222,father_node,hook,temp)
                    all_relation_info.append([father_node, hook, temp])
                temp = []
                father_node = None
                hook = None

            j += 1
        if father_node and temp and (temp[0][0] - father_node[1] <= 10):
            all_relation_info.append([father_node, hook, temp])

    return all_relation_info


def main():
    predict_file = []
    path = '/data/zsl/torch_nlp_task/product/product_data/official_web/predict_result/'
    output_path = '/data/zsl/torch_nlp_task/product/product_data/official_web/relation_result/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for root_path, dirs, files in os.walk(path):
        predict_file = files
        # print(123123,predict_file)

    predict_file = sorted(predict_file, key=lambda x: int(x.split('.')[0]))

    extract_relation_data = []

    for file_name in predict_file:
        print(111, file_name)
        # output_file = open(output_path+file_name,"w")

        with open(path + file_name) as f:
            for line in f.readlines():
                line_data = json.loads(line)
                try:
                    product_info = line_data['label']['product']
                except Exception as e:
                    continue

                # print(11111,list(product_info.keys()))
                # 重组产品词及其位置数据
                line_product_list = []
                for key in product_info:
                    for _index_info in product_info[key]:
                        # print([_index_info,key])
                        line_product_list.append([_index_info[0], _index_info[1], key, 1])

                line_product_list = sorted(line_product_list, key=lambda x: x[0])
                # print(line_product_list)
                text = line_data['text']

                cooccur_data = []
                # cooccur_data = get_cooccur_data(text,line_product_list)
                # print(11111,cooccur_data)
                relation_data = get_relation_data(text, line_product_list)
                # print(22222,relation_data)

                # if cooccur_data or relation_data:
                #     new_dict = {
                #         # 'id':line_data['id'],
                #         'text':str(text).replace('\n','').replace('\t',''),
                #         # 'cooccur_data':cooccur_data,
                #         'relation_data':relation_data
                #     }

                #     extract_relation_data.append(new_dict)
                # output_file.write(json.dumps(new_dict,ensure_ascii=False)+'\n')

                if relation_data:
                    for x in relation_data:
                        value1 = {
                            '原文': str(text).replace('\t\n', '').replace('\n\t', '').replace('\n', '').replace('\t', ''),
                            '父节点': x[0][2],
                            '子节点': ''
                        }
                        extract_relation_data.append(value1)
                        for y in x[2]:
                            value2 = {
                                '原文': '',
                                '父节点': '',
                                '子节点': y[2]
                            }
                            extract_relation_data.append(value2)

        # output_file.close()

    output_data = pd.DataFrame(extract_relation_data)
    output_data.to_csv(output_path + '产品词关系抽取测试2.csv', index=False)


if __name__ == "__main__":
    main()
