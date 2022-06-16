from elasticsearch import Elasticsearch
 
# 登录
es = Elasticsearch([{'host':'10.10.13.12','port':9200}],
        http_auth=('xiao', '123456'),
        timeout=60,
        max_retries=3,
        retry_on_timeout=True,
        )
 
# 查询分页
es.indices.get_alias().keys()
 
# 查询所有数据
## 1
es.search(index="index_name", doc_type="type_name")
## 2
body = {
    "query":{
        "match_all":{}
    }
}
es.search(index="index_name", doc_type="type_name", body=body)