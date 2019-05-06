from django.test import TestCase
import datetime
from .models import SpiderCollect, HdfsClusterinfo, HdfsNodeinfo, YarnClusterinfo, SpiderCollectHistory
from django.db.models import Q

# Create your tests here.
date_time = "2019-01:2019-02"
if date_time:
    # 通过搜索框删选时间
    start_time = max(date_time.split(":"))
    end_time = min(date_time.split(":"))
    print(start_time, end_time)
    # 按照节点名称分组, 取最新的数据, 得到字典的结果
    hdfs_node_dic = HdfsClusterinfo.objects.exec_js('db.HdfsClusterinfo.find({"$and": [{cluster_id:"hadoop1"}, {t_time:{"$gte":"2019-01"}}, {t_time:{"$lte": "2019-02"}}]})')
    hdfs_node_obj = []
    for hdfs_node in hdfs_node_dic["_batch"]:
        hdfs_node_obj.append(HdfsNodeinfo.objects.filter(_id=hdfs_node["firstSalesDate"]["_id"]).first())

