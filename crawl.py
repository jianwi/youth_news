import requests
from lxml import etree
import json
import re

class Crawl:
    def __init__(self, keyword, start_page, end_page):
        self.keyword = keyword
        # 接口中页码是从0开始的
        self.start_page = start_page - 1
        self.end_page = end_page
        # 获取 query 中的 s 字段
        self.s = self.__get_key()

    def run(self):
        for i in range(self.start_page,self.end_page):
            print("第{0}页结果：\n".format(i+1))
            self.search(i)

    # 搜索文章，输入当前页数
    def search(self,current_page):
        url = "http://search.youth.cn/api/customsearch/searchwap?q={0}&p={1}&s={2}".format(self.keyword, current_page, self.s)
        response =  requests.get(url)
        res_obj = json.loads(response.text)
        for item in res_obj['results']:
            # pc 端网页布局不一致，没办法获取，so 爬移动端网页
            # 如果搜索结果中本来就是移动端的，不处理
            if re.search(r"t\.m\.youth\.cn.+htm",item['url']):
                self.get_text_info(item['url'])
            else:
                res = re.search(r'youth\.cn(\/.+htm$)',item['url'])
                if res:
                    # 将pc 端url转为移动端url
                    url = "http://t.m.youth.cn/transfer/index/url/news.youth.cn/"+res.group()
                    self.get_text_info(url)

    # 获取文章内容,输入文章链接
    def get_text_info(self,article_url):
        response = requests.get(article_url)
        # 总有少数奇葩的页面不能抓取。。。
        if response.status_code != 200:
            print("出错了")
            return
        dom = etree.HTML(response.content)
        # 取文章标题
        title = dom.xpath("//h1[@id='title']/text()")[0]

        print("标题："+title)
        # 取文章内容
        article_xpath = dom.xpath("//div[@id='content']")
        # 转成 utf-8
        article = etree.tostring(article_xpath[0], encoding="utf-8", pretty_print=True, method="html").decode('utf-8')
        print("网页内容：\n"+article)

        print("\n- - - - -\n")

    # 获取 s 参数
    @staticmethod
    def __get_key():
        response = requests.get('http://www.youth.cn/')
        body = response.text
        # xpath dom
        dom = etree.HTML(body)
        res = dom.xpath("//input[@name='s']/@value")
        return res[0]


if __name__ == '__main__':
    t = Crawl('香港', 3, 4)
    t.run()
