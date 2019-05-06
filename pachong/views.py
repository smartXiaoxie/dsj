import datetime

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import View
from django.db.models import Max

from .models import SpiderCollect, HdfsClusterinfo, HdfsNodeinfo, YarnClusterinfo, SpiderCollectHistory, BigdataDeplay
from .page import Pagination


# Create your views here.
# 首页（暂时没有内容）
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


# 重定向
class RootView(View):
    def get(self, request):
        return redirect('/index/')


# 实时展示详情页的数据
class SpiderCollectView(View):
    def get(self, request):
        val = request.GET.get("pro")
        if val:
            spider_obj = SpiderCollect.objects.filter(spider_name__contains=val)
        else:
            spider_obj = SpiderCollect.objects.all()

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, spider_obj.count(), request)
        spider_obj = spider_obj[pagination.start: pagination.end]
        return render(request, 'spider_list.html', {"spider_obj": spider_obj, "pagination": pagination})


# 项目的数据-扇形图
class SpiderDataView(View):
    def get(self, request, pid):
        ########################################
        # 扇形图-request_stats的数据
        spider_obj = SpiderCollect.objects.filter(pk=pid).first()
        # 项目名(为了从另一个集合里取数据, 下面构建折线图时会用到)
        spider_name = spider_obj.spider_name
        # request_status的数据
        request_stats = spider_obj.request_stats
        """
        # request_stats数据格式如下
        "request_stats": {
            "downloader/response_status_count/912": 3599,
            "request_failed": 10167,                            # 去掉这条数据
            "downloader/response_status_count/503": 64,
            "downloader/exception_type_count/twisted_internet_error_TimeoutError": 139,
            "downloader/response_status_count/403": 6331,
            "request_total": 17563,
            "downloader/response_status_count/302": 1
	    },
        """

        sector_series_data = []
        sector_legend_data = []
        # 数据处理
        # 1.循环文档里的数据,构建扇形图上series需要的数据格式
        for k, y in request_stats.items():
            if not "request_failed" == k and not "request_total" == k:
                sector_series_data.append({"value": y, "name": k})

        # 2.计算200的数据,并添加到sector_series_data
        downloader_200 = request_stats["request_total"]
        for i in sector_series_data:
            downloader_200 = int(downloader_200) - int(i["value"])
        sector_series_data.append({"value": downloader_200, "name": "downloader_200"})

        # 3.扇形图legend上的数据
        sector_legend_data = [i["name"] for i in sector_series_data]

        ########################################
        # 扇形图-data_stats的数据
        data_stats = spider_obj.data_stats
        series_data = []
        legend_data = []
        # 1.循环文档里的数据,构建扇形图上series需要的数据格式
        for k, y in data_stats.items():
            series_data.append({"value": y, "name": k})

        # 2.扇形图legend上的数据
        legend_data = [i["name"] for i in series_data]

        return render(request, 'spider_history.html', locals())


# 项目的历史数据-折线图（数据来自spiderCollectHistory）
class BrokenDataView(View):
    def get(self, request):
        spider_name = request.GET.get("spider_name")
        now = datetime.datetime.now()
        val = int(request.GET.get("id"))
        if val:
            date = now - datetime.timedelta(weeks=val)
        else:
            # 默认显示一周的内容
            date = now - datetime.timedelta(weeks=1)
        # history_data = SpiderCollectHistory.objects.filter(spider_name=spider_name, start_time__gte=date)

        # 由于时间是字符串类型的,所以先把所有的数据取出来, 按照时间倒序排序, 再处理
        history_data = SpiderCollectHistory.objects.filter(spider_name=spider_name).order_by("-start_time")
        history_data_obj = []
        for i in history_data:
            # 将时间大于date的放到hdfs_cluster_obj_lst里
            if datetime.datetime.strptime(i.start_time, "%Y-%m-%d %H:%M:%S") > date:
                history_data_obj.append(i)

            # 当等于需要的天数时,退出
            if len(history_data_obj) == val * 7:
                break

        # 主项图上的配置项和数据---总cpu
        # 折线图上的数据
        # 1.先取数据,然后对数据排序
        history_list = []
        for obj in history_data_obj:
            history_list.append({"date": str(datetime.datetime.strptime(obj.start_time, "%Y-%m-%d %H:%M:%S")), "total": obj.request_stats.get("request_total")})
        history_list = sorted(history_list, key=lambda el: el["date"])

        # 2.折线图的数据
        broken_x_data = []
        broken_series_data = []
        for obj in history_list:
            broken_x_data.append(obj.get("date"))
            broken_series_data.append(obj.get("total"))

        return JsonResponse((broken_x_data, broken_series_data), safe=False)


# hdfs 集群实时状态
class HdfsClusterView(View):
    def get(self, request):
        # 按照cluster_id分组, 取最新的数据, 得到字典的结果
        # hdfs_cluster_dic = HdfsClusterinfo.objects.exec_js('db.HdfsClusterinfo.aggregate([{$sort: {t_time: -1}},{$group:{_id:"$cluster_id", firstSalesDate: {$first: "$$ROOT"}}}])')
        hdfs_cluster_obj = BigdataDeplay.objects.filter(table_name="HdfsClusterinfo")
        # hdfs_cluster_obj = []
        # for hdfs_node in hdfs_cluster_dic["_batch"]:
        #     hdfs_cluster_obj.append(HdfsClusterinfo.objects.filter(_id=hdfs_node["firstSalesDate"]["_id"]).first())

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, len(hdfs_cluster_obj), request)
        hdfs_cluster_obj = hdfs_cluster_obj[pagination.start: pagination.end]
        return render(request, 'hdfs_cluster_list.html', {"hdfs_cluster_obj": hdfs_cluster_obj, "pagination": pagination})


# hdfs 集群柱形图数据
def hdfs_data(request, cluster_id=None, val=None):
    if request.GET.get("date_time") == str(0):
        cluster_id = request.GET.get("cluster_id")
        val = int(request.GET.get("id"))
        date_time = None
    else:
        cluster_id = request.GET.get("cluster_id")
        val = int(request.GET.get("id"))
        date_time = request.GET.get("date_time")

    if date_time:
        # 通过搜索框删选时间
        max_time = max(date_time.split(":"))
        min_time = min(date_time.split(":"))
        # 按照节点名称分组, 取最新的数据, 得到字典的结果
        hdfs_cluster_obj_lst = HdfsClusterinfo.objects.filter(cluster_id=cluster_id, t_time__gte=min_time, t_time__lte=max_time).order_by("-t_time")
    else:
        # 通过按钮点击的
        now = datetime.datetime.now()
        if val:
            date = now - datetime.timedelta(weeks=val)
        else:
            # 默认显示一周的内容
            val = 1
            date = now - datetime.timedelta(weeks=val)
        # hdfs_cluster_obj = HdfsClusterinfo.objects.filter(cluster_id=cluster_id, t_time__gte=date)
        # 由于时间是字符串类型的,所以先把所有的数据取出来, 按照时间倒序排序, 再处理
        hdfs_cluster_obj = HdfsClusterinfo.objects.filter(cluster_id=cluster_id).order_by("-t_time")
        hdfs_cluster_obj_lst = []
        for i in hdfs_cluster_obj:
            # 将时间大于date的放到hdfs_cluster_obj_lst里
            if datetime.datetime.strptime(i.t_time, "%Y-%m-%d %H:%M:%S") > date:
                hdfs_cluster_obj_lst.append(i)

            # 当等于需要的天数时,退出
            if len(hdfs_cluster_obj_lst) == val * 7:
                break

    # 主项图上的配置项和数据---总大小
    hdfs_total_data = []
    for i in reversed(hdfs_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.hdfs_total)
        hdfs_total_data.append(lis)

    # 主项图上的配置项和数据---使用空间
    hdfs_used_data = []
    for i in reversed(hdfs_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.hdfs_used)
        hdfs_used_data.append(lis)

    # 主项图上的配置项和数据---文件总数
    file_total_data = []
    for i in reversed(hdfs_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.file_total)
        file_total_data.append(lis)

    return {"hdfs_total": hdfs_total_data,
            "hdfs_used": hdfs_used_data,
            "file_total": file_total_data
            }


# hdfs 集群(默认显示1周的数据)
class HdfsClusterDataView(View):
    def get(self, request, cluster_id):
        return render(request, "hdfs_cluster_history.html", locals())


# hdfs 集群(点击最近1/2/3/4周触发)
class HdfsClusterHistoryView(View):
    def get(self, request):
        chart_data = hdfs_data(request)
        return JsonResponse(chart_data)


# hdfs节点实时状态
class HdfsNodeView(View):
    def get(self, request):
        # 按照节点名称分组, 取最新的数据, 得到字典的结果
        # hdfs_node_dic = HdfsNodeinfo.objects.exec_js('db.HdfsNodeinfo.aggregate([{$sort: {t_time: -1}},{$group:{_id:"$node_name", firstSalesDate: {$first: "$$ROOT"}}}])')
        # hdfs_node_obj = []
        hdfs_node_obj = BigdataDeplay.objects.filter(table_name="HdfsNodeinfo")
        # for hdfs_node in hdfs_node_dic["_batch"]:
        #     hdfs_node_obj.append(HdfsNodeinfo.objects.filter(_id=hdfs_node["firstSalesDate"]["_id"]).first())

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, len(hdfs_node_obj), request)
        hdfs_node_obj = hdfs_node_obj[pagination.start: pagination.end]
        return render(request, 'hdfs_node_list.html', {"hdfs_node_obj": hdfs_node_obj, "pagination": pagination})


# hdfs 节点柱形图数据
def hdfs_node_data(request, node_name=None, val=None):
    if request.GET.get("date_time") == str(0):
        node_name = request.GET.get("node_name")
        val = int(request.GET.get("id"))
        date_time = None
    else:
        node_name = request.GET.get("node_name")
        val = int(request.GET.get("id"))
        date_time = request.GET.get("date_time")

    if date_time:
        # 通过搜索框删选时间
        max_time = max(date_time.split(":"))
        min_time = min(date_time.split(":"))
        # 按照节点名称分组, 取最新的数据, 得到字典的结果
        hdfs_node_obj_lst = HdfsNodeinfo.objects.filter(node_name=node_name, t_time__gte=min_time, t_time__lte=max_time).order_by("-t_time")
    else:
        # 通过按钮点击
        now = datetime.datetime.now()
        if val:
            date = now - datetime.timedelta(weeks=val)
        else:
            # 默认显示一周的内容
            val = 1
            date = now - datetime.timedelta(weeks=val)
        # hdfs_cluster_obj = HdfsClusterinfo.objects.filter(cluster_id=cluster_id, t_time__gte=date)
        # 由于时间是字符串类型的,所以先把所有的数据取出来, 按照时间倒序排序, 再处理
        hdfs_node_obj = HdfsNodeinfo.objects.filter(node_name=node_name).order_by("-t_time")
        hdfs_node_obj_lst = []
        for i in hdfs_node_obj:
            # 将时间大于date的放到hdfs_cluster_obj_lst里
            if datetime.datetime.strptime(i.t_time, "%Y-%m-%d %H:%M:%S") > date:
                hdfs_node_obj_lst.append(i)

            # 当等于需要的天数时,退出
            if len(hdfs_node_obj_lst) == val * 7:
                break

    # 主项图上的配置项和数据---总大小
    node_size_total_data = []
    for i in reversed(hdfs_node_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.node_size_total)
        node_size_total_data.append(lis)

    # 主项图上的配置项和数据---使用空间
    node_size_used_data = []
    for i in reversed(hdfs_node_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.node_size_used)
        node_size_used_data.append(lis)

    return {"node_size_total": node_size_total_data,
            "node_size_used": node_size_used_data
            }


# hdfs 节点(默认显示1周的数据)
class HdfsNodeDataView(View):
    def get(self, request, node_name):
        return render(request, "hdfs_node_history.html", locals())


# hdfs 节点(点击最近1/2/3/4周触发)
class HdfsNodeHistoryView(View):
    def get(self, request):
        chart_data = hdfs_node_data(request)
        return JsonResponse(chart_data)


# yarn 集群实时状态
class YarnClusterView(View):
    def get(self, request):
        # 按照cluster_id分组, 取最新的数据, 得到字典的结果
        # yarn_cluster_dic = YarnClusterinfo.objects.exec_js('db.YarnClusterinfo.aggregate([{$sort: {t_time: -1}},{$group:{_id:"$cluster_id", firstSalesDate: {$first: "$$ROOT"}}}])')
        # yarn_cluster_obj = []
        yarn_cluster_obj = BigdataDeplay.objects.filter(table_name="YarnClusterinfo")
        # for hdfs_node in yarn_cluster_dic["_batch"]:
        #     yarn_cluster_obj.append(YarnClusterinfo.objects.filter(_id=hdfs_node["firstSalesDate"]["_id"]).first())

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, len(yarn_cluster_obj), request)
        yarn_cluster_obj = yarn_cluster_obj[pagination.start: pagination.end]
        return render(request, 'yarn_cluster_list.html', {"yarn_cluster_obj": yarn_cluster_obj, "pagination": pagination})


# yarn 集群柱形图数据
def yarn_cluster_data(request, cluster_id=None, val=None):
    if request.GET.get("date_time") == str(0):
        cluster_id = request.GET.get("cluster_id")
        val = int(request.GET.get("id"))
        date_time = None
    else:
        cluster_id = request.GET.get("cluster_id")
        val = int(request.GET.get("id"))
        date_time = request.GET.get("date_time")

    if date_time:
        # 通过搜索框删选时间
        max_time = max(date_time.split(":"))
        min_time = min(date_time.split(":"))
        # 按照节点名称分组, 取最新的数据, 得到字典的结果
        yarn_cluster_obj_lst = YarnClusterinfo.objects.filter(cluster_id=cluster_id, t_time__gte=min_time, t_time__lte=max_time).order_by("-t_time")
    else:
        # 通过按钮点击的
        now = datetime.datetime.now()
        if val:
            date = now - datetime.timedelta(weeks=val)
        else:
            # 默认显示一周的内容
            val = 1
            date = now - datetime.timedelta(weeks=val)

        # 由于时间是字符串类型的,所以先把所有的数据取出来, 按照时间倒序排序, 再处理
        yarn_cluster_obj = YarnClusterinfo.objects.filter(cluster_id=cluster_id).order_by("-t_time")
        yarn_cluster_obj_lst = []
        for i in yarn_cluster_obj:
            # 将时间大于date的放到hdfs_cluster_obj_lst里
            if datetime.datetime.strptime(i.t_time, "%Y-%m-%d %H:%M:%S") > date:
                yarn_cluster_obj_lst.append(i)

            # 当等于需要的天数时,退出
            if len(yarn_cluster_obj_lst) == val * 7:
                break

    # 主项图上的配置项和数据---总cpu
    total_cpu_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.total_cpu)
        total_cpu_data.append(lis)

    # 主项图上的配置项和数据---总内存
    total_mem_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.total_mem)
        total_mem_data.append(lis)

    # 主项图上的配置项和数据---总内存
    used_cpu_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.used_cpu)
        used_cpu_data.append(lis)

    # 主项图上的配置项和数据---used_mem
    used_mem_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.used_mem)
        used_mem_data.append(lis)

    # 主项图上的配置项和数据---appsRuning
    apps_runing_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.appsRuning)
        apps_runing_data.append(lis)

    # 主项图上的配置项和数据---appsPending
    apps_pending_data = []
    for i in reversed(yarn_cluster_obj_lst):
        lis = []
        lis.append(i.t_time)
        lis.append(i.appsPending)
        apps_pending_data.append(lis)

    return {"total_cpu_data": total_cpu_data,
            "total_mem_data": total_mem_data,
            "used_cpu_data": used_cpu_data,
            "used_mem_data": used_mem_data,
            "apps_runing_data": apps_runing_data,
            "apps_pending_data": apps_pending_data,
            }

# yarn 集群(默认显示1周的数据)
class YarnClusterDataView(View):
    def get(self, request, cluster_id):
        return render(request, "yarn_cluster_history.html", locals())

# yarn 集群(点击最近1/2/3/4周触发)
class YarnClusterHistoryView(View):
    def get(self, request):
        chart_data = yarn_cluster_data(request)
        return JsonResponse(chart_data)