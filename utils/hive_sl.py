from impala.dbapi import connect
from impala.util import as_pandas
"""
专利相关信息在https://cf.qizhidao.com/pages/viewpage.action?pageId=85924197
专利数据表见：https://cf.qizhidao.com/download/attachments/85924197/ads%E5%9B%BD%E7%9F%A5%E5%B1%80%E4%B8%93%E5%88%A9%E6%95%B0%E6%8D%AE%E5%AD%97%E5%85%B8.xlsx?api=v2
"""
 
hive_conf = {
  #  "host":'172.18.0.230',
    "host":'vip-address.prd.qizhidao.com', #
    "port":10099,
    "auth_mechanism":"GSSAPI",  #"PLAIN"
    "kerberos_service_name":'hive',
}

conn = connect(**hive_conf)
cursor = conn.cursor()
 
# # 执行查询
# # cursor.description
# cursor.execute('show databases')
 
# cursor.execute('use default')
# cursor.execute('SHOW TABLES')
# tables = as_pandas(cursor)
# print(tables)
 
# print(cursor.fetchall())
 
# hsql = """
# SELECT f.appid_original,f.claim_claimtext,f.description,d.brief FROM
# bigdata_application_dev.dwd_qxb_intellectual_propertyt_patents_new d
# right JOIN bigdata_application_dev.fulltext_final f on d.request_num_standard=f.appid_original limit 10
# """

patent_sql = """
SELECT out_num,app_num_standard,out_type,category_num_ipc,ipc_section,fulltext_imgs,patent_img,patent_brief,claims,claim_first,claims_independ,instruction 
FROM bigdata_application_dev.ads_patent_wide limit 10
"""

cursor.execute(patent_sql)
 
df = as_pandas(cursor)
# print(cursor.fetchall())
df.head()


# 写入
sql = """create external table ods_user_datasct (
    id STRING , 
    name STRING , 
    sex STRING , 
    city STRING , 
    occupation STRING , 
    mobile_phone_num STRING ,
    fix_phone_num STRING , 
    bank_name STRING ,
    address STRING ,
    marriage STRING ,
    child_num INT
    )
row format delimited fields terminated by ','
STORED AS TEXTFILE
LOCATION
'hdfs://nameservice1:8020/tmp/datasct/'"""
cursor.execute(sql)
 
# 写入确认一下
cursor.execute('select * from ods_user_datasct')
ods_user = as_pandas(cursor)
ods_user