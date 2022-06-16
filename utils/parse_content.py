# encoding:utf-8
from utils.timer import time_cost
from utils.exception_handler import catch_exception

alpha_word = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

split_word = ['、', '和', '与', '及', '或']
# ,' ' 空格作为连接符时锚点识别失败
other_word = ["'", '-', '.', '(', ')']
#
chinese_word = ["‘", "’", "（", "）"]

# combine_word = ['~','至','到']
combine_word = []

valid_word = split_word + other_word + combine_word

black_words = ['步骤', '实施例', '技术方案']


def is_valid_symbol(symbol):
    '''
    是否有效字符
    :param symbol:
    :return:
    '''
    symbol = str(symbol)
    if symbol.isdigit():
        return True
    # if symbol.isalpha():
    if symbol.lower() in alpha_word:
        return True
    if symbol in valid_word:
        return True

    return False


def is_valid_number(value):
    '''
    是否有效编号
    :param value:
    :return:
    '''
    if value and str(value)[0] in ["'", '-', '.']:
        return False

    for i in value:
        if str(i).isdigit():
            return True
    return False


@catch_exception
def get_valid_numer_tag(sentence):
    '''
    获取所有锚点字符串
    :param sentence:
    :return:
    '''
    i = 0
    numer_tag_list = []
    while i < len(sentence):
        temp = []
        # print(11111,sentence[i],is_valid_symbol(sentence[i]))
        if is_valid_symbol(sentence[i]):
            temp.append(i)
            i += 1
            while i < len(sentence) and is_valid_symbol(sentence[i]):
                i += 1
            temp.append(i)
        # if temp:
        #     print(123123,sentence[temp[0]:temp[1]])
        if temp and is_valid_number(sentence[temp[0]:temp[1]]):
            cur_value = sentence[temp[0]:temp[1]]

            # 前后首词为分隔符的词
            if str(cur_value)[-1] in split_word+['-', '.'] \
                    or (str(cur_value)[-1] == '(') \
                    or (str(cur_value)[-1] == ')' and (str(cur_value).count('(')!=str(cur_value).count(')'))):
                temp[1] -= 1
                cur_value = cur_value[:-1]

            if str(cur_value)[0] in split_word+["'", '-', '.'] \
                    or (str(cur_value)[0] == ')') \
                    or (str(cur_value)[-1] == '(' and (str(cur_value).count('(') != str(cur_value).count(')'))):
                temp[0] += 1
                cur_value = cur_value[1:]

            temp.append(cur_value)
            numer_tag_list.append(temp)
        i += 1
    return numer_tag_list

def get_ner_label_info(label):
    '''
    预测实体转字典
    :param label:
    :return:
    '''
    all_position_tag = {}
    if 'product' in label:
        for x in label['product']:
            if x in black_words:
                # 删除黑名单实体词
                continue
            for y in label['product'][x]:
                all_position_tag[tuple(y)] = x

    return all_position_tag


def update_map_result(map_result,cur_sentence,all_position_tag,number_tag_list):
    '''
    更新映射关系字典
    :param map_result:
    :param cur_sentence:
    :param all_position_tag:
    :param number_tag_list:
    :return:
    '''
    for key in all_position_tag:
        flag = False
        cur_number = ''
        # 通过位置关系判断当前编号有否对应项
        # print(3333,key,all_position_tag[key])
        for number_tag in number_tag_list:
            cur_number = number_tag[2]
            if key[1] + 1 == number_tag[0]:
                #锚点词与编号拼接的情况
                # 激光电视2 - 1
                flag = True
                break
            # ,' '
            if cur_sentence[key[0] - 1] in [':', '-', '：','、','.'] and key[0] - 1 == number_tag[1]:
                #锚点词与编号词通过停顿词连接
                # 1-电冰箱；2-电热水器；5-电磁炉
                flag = True
                break

            # if key[1] + 2 < len(cur_sentence) and cur_sentence[key[1] + 1] in ['(', '（'] and key[1] + 2 == \
            #         number_tag[0]:
            #     # 电视机(3)
            #     flag = True
            #     break

        if flag:
            # 匹配成功的锚点词先切割，再进行更新
            cur_number_list = cur_number.replace('和', '、').replace('与', '、').replace('及', '、').replace('或','、').split('、')
            # print(123123,cur_number,cur_number_list)
            for new_number in cur_number_list:
                if new_number not in map_result:
                    map_result[new_number] = {all_position_tag[key]: 1}
                else:
                    if all_position_tag[key] not in map_result[new_number]:
                        map_result[new_number][all_position_tag[key]] = 1
                    else:
                        map_result[new_number][all_position_tag[key]] += 1



@catch_exception
def parse_text(ner_info):
    '''
    文本解析入口
    :param ner_info:
    :return:
    '''
    map_result = {}
    for elem in ner_info:
        # cur_sentence = elem['text'].replace("’","'").replace("‘","'").replace("（","(").replace("）",")")
        cur_sentence = elem['text'].replace(chr(8216), "'").replace(chr(8217), "'").replace("（", "(").replace("）", ")")
        label = elem['label']

        #获取所有有效编号
        number_tag_list = get_valid_numer_tag(cur_sentence)
        # print(11111, number_tag_list)

        #所有预测的实体字典
        all_position_tag = get_ner_label_info(label)
        # print(2222, all_position_tag)

        # 更新实体与编号的映射关系
        update_map_result(map_result,cur_sentence,all_position_tag,number_tag_list)

    anchor_result = {}
    #精选锚点词
    for key in map_result:
        if not key:
            continue
        data = sorted(map_result[key].items(), key=lambda x: x[1], reverse=True)
        temp = data[0][0]
        for i in range(1, len(data)):
            if temp in data[i][0]:
                temp = data[i][0]
            else:
                break
        anchor_result[key] = temp

    return anchor_result


@time_cost
@catch_exception
def parse_anchor_text_info(predict_data):
    patent_dict = {}
    for elem in predict_data:
        if elem['id'] not in patent_dict:
            patent_dict[elem['id']] = [elem]
        else:
            patent_dict[elem['id']].append(elem)

    output_data = {}
    for out_num in patent_dict:
        ner_predict_info = patent_dict[out_num]
        anchor_info = parse_text(ner_predict_info)
        output_data[out_num] = anchor_info

    return output_data


if __name__ == "__main__":
    # data = [{'id': 'CN123456789A', 'text': '激光电视14包括投影13，光源16，光束112。', 'label': {'product': {'激光电视': [[0, 3]], '投影': [[8, 9]], '光源': [[13, 14]], '光束': [[18, 19]]}}}, {'id': 'CN123456789A', 'text': '我们生产的矿泉水16包含矿物质成分11。', 'label': {'product': {'矿泉水': [[5, 7]], '矿物质成分': [[12, 16]]}}}, {'id': 'CN123456789A', 'text': '卡环3的环槽内箍有弹簧2。弹簧2可使内锥套10、卡环3成一体不会散落', 'label': {'product': {'卡环': [[0, 1], [24, 25]], '弹簧': [[9, 10], [13, 14]], '内锥套': [[18, 20]]}}}, {'id': 'CN123456789B', 'text': '本发明主要由支架1、弹簧2、卡环3、滚动轴承4、螺母5、支承轴6、外锥套7、调节螺母8、衬套9、内锥套10、百分表12、表座13、检测环14组成', 'label': {'product': {'支架': [[6, 7]], '弹簧': [[10, 11]], '卡环': [[14, 15]], '滚动轴承': [[18, 21]], '螺母': [[24, 25]], '支承轴': [[28, 30]], '外锥套': [[33, 35]], '调节螺母': [[38, 41]], '衬套': [[44, 45]], '内锥套': [[48, 50]], '百分表': [[54, 56]], '表座': [[60, 61]], '检测环': [[65, 67]]}}}, {'id': 'CN123456789B', 'text': '接着可以使用本装置对链轮进行检测：将链轮15的安装孔套在内锥套10的外圆上', 'label': {'product': {'链轮': [[18, 19]], '内锥套': [[28, 30]]}}}, {'id': 'CN123456789B', 'text': '支承轴6上套装有滚动轴承4', 'label': {'product': {'支承轴': [[0, 2]], '滚动轴承': [[8, 11]]}}}, {'id': 'CN123456789C', 'text': '在链轮15检测过程中使用', 'label': {'product': {'链轮': [[1, 2]]}}}, {'id': 'CN123456789C', 'text': '这样才能保证套在内锥套外圆上的链轮在紧贴定位台阶端面时处于与内锥套轴线同轴位置。[]本发明的优点是：1、能方便检测链轮齿根圆径向和链轮端面跳动', 'label': {}}, {'id': 'CN123456789C', 'text': '且检测精度高2、有效控制链轮质量', 'label': {}}]

    data = [
    {
        "id": 1,
        "label": {
            "product": {
                "层": [
                    [
                        0,
                        0
                    ],
                    [
                        11,
                        11
                    ],
                    [
                        25,
                        25
                    ],
                    [
                        36,
                        36
                    ],
                    [
                        50,
                        50
                    ],
                    [
                        74,
                        74
                    ]
                ],
                "显示系统": [
                    [
                        105,
                        108
                    ],
                    [
                        122,
                        125
                    ]
                ]
            }
        },
        "text": "层102(m)被称为在层102(1)底部或下方，而层102(1)被称为在层102(m)上方或顶部。 层102可以被配置成实现各种功能，诸如过滤由另一层102(激光电视)发出的光，提供对其他层的擦伤的保护，提供对显示系统100的损坏的保护，感应对显示系统100（色彩亮度）的触摸或其他输入"
    }
]

    print(parse_anchor_text_info(data))
    # print(ord('‘'))
    # print(ord('’'))
    # print(chr(8216))
    # print(chr(8217))
