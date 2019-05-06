"""dsj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from pachong.views import *

urlpatterns = [
    path('', RootView.as_view()),
    path('index/', IndexView.as_view()),
    # 爬虫实时展示
    path('spider/list/', SpiderCollectView.as_view()),
    re_path('^spider_data/(\w+)/$', SpiderDataView.as_view()),
    re_path('broken_data/', BrokenDataView.as_view()),

    # hdfs集群实时状态
    path('hdfs_cluster/list/', HdfsClusterView.as_view()),
    re_path('^hdfs_cluster_data/(?P<cluster_id>\w+)/$', HdfsClusterDataView.as_view()),
    path('hdfs_cluster_history/', HdfsClusterHistoryView.as_view()),

    # hdfs节点实时状态
    path('hdfs_node/list/', HdfsNodeView.as_view()),
    re_path('^hdfs_node_data/(?P<node_name>\w+)/$', HdfsNodeDataView.as_view()),
    path('hdfs_node_history/', HdfsNodeHistoryView.as_view()),

    # yarn 集群实时状态
    path('yarn_cluster/list/', YarnClusterView.as_view()),
    re_path('^yarn_cluster_data/(?P<cluster_id>\w+)/$', YarnClusterDataView.as_view()),
    path('yarn_cluster_history/', YarnClusterHistoryView.as_view()),
]
