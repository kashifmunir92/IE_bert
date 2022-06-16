import json

new_file = open("/data/zsl/torch_nlp_task/product/product_data/official_web/predict_data/0.json", "w")
with open('/data/zsl/torch_nlp_task/product/product_data/official_web/predict_data/1124.json') as f:
    count = 1
    for line in f.readlines():
        b = json.loads(line)
        new_dict = {
            'id': b['id'] + ':' + str(count),
            'text': b['text']
        }
        count += 1
        new_file.write(json.dumps(new_dict, ensure_ascii=False) + '\n')
        print(new_dict)
new_file.close()
