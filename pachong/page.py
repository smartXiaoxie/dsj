class Pagination(object):
    def __init__(self, current_page_num, all_count, request, per_page_num=5, pager_count=11):
        """
        封装分页相关数据
        :param current_page_num: 当前访问页的数字
        :param all_count:    分页数据中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param pager_count:  最多显示的页码个数
        """
        # 将传入的字符/数字, 转换成int类型
        # 出现任何错误, 默认显示第一页
        try:
            current_page_num = int(current_page_num)
        except Exception as e:
            current_page_num = 1

        # 当前访问页数小于1, 默认显示第一页
        if current_page_num < 1:
            current_page_num = 1

        # 当前访问页的数字; 数据总条数; 每页显示的条数
        self.current_page_num = current_page_num
        self.all_count = all_count
        self.per_page_num = per_page_num

        # all_pager 实际总页码
        # divmod(x, y)分别取商和余数
        all_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_pager += 1
        self.all_pager = all_pager

        # 最多显示的页码数 11 ; 左右两边的页码数(中间看: 左边5个右边5个)
        self.pager_count = pager_count
        self.pager_count_half = int((pager_count - 1) / 2)  # 5

        # 保存搜索条件 ★★★
        # QueryDict 只读; 可以拷贝; 拷贝之后可以更改
        import copy
        self.params = copy.deepcopy(request.GET)

    # ,每页显示的条数, 从第几条开始, 到哪一条结束
    @property
    def start(self):
        return (self.current_page_num - 1) * self.per_page_num

    @property
    def end(self):
        return self.current_page_num * self.per_page_num

    def page_html(self):
        # 如果总页码 < 11
        # 左闭右开, 所有右边+1
        if self.all_pager <= self.pager_count:
            pager_start = 1
            pager_end = self.all_pager + 1

        # 总页码 > 11
        else:
            # 页码翻到开头
            # 当前页码数如果 <= 左右两边的页码数 5
            if self.current_page_num <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1
            # 当前页码数大于5
            else:
                # 页码翻到最后
                if (self.current_page_num + self.pager_count_half) > self.all_pager:
                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1
                # 页码中间
                else:
                    pager_start = self.current_page_num - self.pager_count_half
                    pager_end = self.current_page_num + self.pager_count_half + 1

        page_html_list = []

        # 首页
        first_page = '<li><a href="?page=%s">首页</a></li>' % (1,)
        page_html_list.append(first_page)

        # 上一页
        # 如果当前页码数 <= 1, 将上一页置为disabled
        if self.current_page_num <= 1:
            prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            prev_page = '<li><a href="?page=%s">上一页</a></li>' % (self.current_page_num - 1,)

        page_html_list.append(prev_page)

        # 中间页码
        for i in range(pager_start, pager_end):
            # params, 拷贝的数据
            self.params["page"] = i
            if i == self.current_page_num:
                # self.params.unlencode() 将QueryDict再组成字符串编码格式
                temp = '<li class="active"><a href="?%s">%s</a></li>' % (self.params.urlencode(), i)
            else:
                temp = '<li><a href="?%s">%s</a></li>' % (self.params.urlencode(), i)
            page_html_list.append(temp)

        # 下一页
        # 如果当前页码大于总页码, 将下一页,置为disabled
        if self.current_page_num >= self.all_pager:
            next_page = '<li class="disabled"><a href="#">下一页</a></li>'
        else:
            next_page = '<li><a href="?page=%s">下一页</a></li>' % (self.current_page_num + 1,)
        page_html_list.append(next_page)

        # 尾页
        last_page = '<li><a href="?page=%s">尾页</a></li>' % (self.all_pager,)
        page_html_list.append(last_page)

        return ''.join(page_html_list)