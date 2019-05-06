from django.db import models
import mongoengine

# Create your models here.
class SpiderCollect(mongoengine.Document):
    spider_name = mongoengine.StringField()
    start_time = mongoengine.StringField()
    request_stats = mongoengine.StringField()
    rate_avg = mongoengine.IntField()
    operating = mongoengine.IntField()
    uuid = mongoengine.StringField()
    finish_time = mongoengine.StringField()
    data_stats = mongoengine.StringField()
    stopped = mongoengine.IntField()
    time_total = mongoengine.IntField()

    meta = {"collection": 'spiderCollect'}

    def __str__(self):
        return self.spider_name

class SpiderCollectHistory(mongoengine.Document):
    spider_name = mongoengine.StringField()
    start_time = mongoengine.StringField()
    request_stats = mongoengine.StringField()
    rate_avg = mongoengine.IntField()
    operating = mongoengine.IntField()
    uuid = mongoengine.StringField()
    finish_time = mongoengine.StringField()
    data_stats = mongoengine.StringField()
    stopped = mongoengine.IntField()
    time_total = mongoengine.IntField()

    meta = {"collection": 'spiderCollectHistory'}

    def __str__(self):
        return self.spider_name

# hdfs 集群
class HdfsClusterinfo(mongoengine.Document):
    _id = mongoengine.ObjectIdField()
    file_total = mongoengine.IntField()
    hdfs_total = mongoengine.StringField()
    t_time = mongoengine.StringField()
    hdfs_remaining = mongoengine.StringField()
    miss_block = mongoengine.IntField()
    active_name = mongoengine.StringField()
    version = mongoengine.StringField()
    live_node = mongoengine.IntField()
    blocks_total = mongoengine.IntField()
    dead_node = mongoengine.IntField()
    cluster_id = mongoengine.StringField()
    hdfs_used = mongoengine.StringField()
    cluster_status = mongoengine.StringField()

    meta = {"collection": 'HdfsClusterinfo'}

    def __str__(self):
        return self.cluster_id

# hdfs 节点
class HdfsNodeinfo(mongoengine.Document):
    _id = mongoengine.ObjectIdField()
    node_size_total = mongoengine.IntField()
    node_size_remaining = mongoengine.IntField()
    t_time = mongoengine.StringField()
    node_ip = mongoengine.StringField()
    non_dfs_used = mongoengine.IntField()
    node_size_used = mongoengine.IntField()
    node_name = mongoengine.StringField()
    node_state = mongoengine.StringField()
    cluster_id = mongoengine.StringField()
    block_num = mongoengine.IntField()

    meta = {"collection": 'HdfsNodeinfo'}

    def __str__(self):
        return self.node_name

# yarn 集群
class YarnClusterinfo(mongoengine.Document):
    _id = mongoengine.ObjectIdField()
    total_cpu = mongoengine.IntField()
    cluster_state = mongoengine.StringField()
    t_time = mongoengine.StringField()
    used_cpu = mongoengine.IntField()
    appsPending = mongoengine.IntField()
    appsRuning = mongoengine.IntField()
    total_mem = mongoengine.IntField()
    total_live = mongoengine.IntField()
    used_mem = mongoengine.IntField()
    cluster_id = mongoengine.StringField()
    active_name = mongoengine.StringField()
    unhealthyNodes = mongoengine.IntField()

    meta = {"collection": 'YarnClusterinfo'}

    def __str__(self):
        return self.cluster_id

class BigdataDeplay(mongoengine.Document):
    _id = mongoengine.ObjectIdField()
    file_total = mongoengine.IntField()
    hdfs_total = mongoengine.StringField()
    t_time = mongoengine.StringField()
    hdfs_remaining = mongoengine.StringField()
    miss_block = mongoengine.IntField()
    active_name = mongoengine.StringField()
    version = mongoengine.StringField()
    live_node = mongoengine.IntField()
    blocks_total = mongoengine.IntField()
    dead_node = mongoengine.IntField()
    cluster_id = mongoengine.StringField()
    hdfs_used = mongoengine.StringField()
    cluster_status = mongoengine.StringField()
    node_size_total = mongoengine.IntField()
    node_size_remaining = mongoengine.IntField()
    node_ip = mongoengine.StringField()
    non_dfs_used = mongoengine.IntField()
    node_size_used = mongoengine.IntField()
    node_name = mongoengine.StringField()
    node_state = mongoengine.StringField()
    block_num = mongoengine.IntField()
    total_cpu = mongoengine.IntField()
    cluster_state = mongoengine.StringField()
    used_cpu = mongoengine.IntField()
    appsPending = mongoengine.IntField()
    appsRuning = mongoengine.IntField()
    total_mem = mongoengine.IntField()
    total_live = mongoengine.IntField()
    used_mem = mongoengine.IntField()
    unhealthyNodes = mongoengine.IntField()
    table_name = mongoengine.StringField()

    meta = {"collection": 'Bigdata_deplay'}

    def __str__(self):
        return self._id