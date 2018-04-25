#!/usr/bin/python
# -*- coding:utf-8 -*-
import pymysql
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from complete_exp.items import CompleteExpItem


class Scholar(object):
    def __init__(self, id, name, org):
        self.id = id
        self.name = name
        self.org = org

    def __str__(self):
        return '(%s,%s,%s)' % (self.id, self.name, self.org)


config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'reego941122',
    'db': 'qixiang',
    'charset': 'utf8'
}
con = pymysql.connect(**config)
cur = con.cursor()
# 选择所有经历为空的学者姓名和机构
sql = "select `id`, `name`, `organization` from scholar_qixiang where experience IS NULL"
cur.execute(sql)
results = cur.fetchall()
scholars = []
for result in results:
    scholars.append(Scholar(result[0], result[1], result[2]))


class CompleteSpider(Spider):
    name = "exp"
    allowed_domains = ["baike.baidu.com"]
    start_urls = ["https://baike.baidu.com/item/"]

    def parse(self, response):
        for scholar in scholars:
            name = scholar.name
            full_url = "https://baike.baidu.com/item/"+str(name)
            yield scrapy.Request(full_url, callback=self.parse_sel, meta={"scholar": scholar})

    def parse_sel(self, response):
        sel = Selector(response)
        scholar = response.meta['scholar']
        #判断百度百科上是否有这个名字
        if response.url != "https://baike.baidu.com/error.html":
            #获取该姓名的所有人物
            persons = sel.xpath('//ul[@class="polysemantList-wrapper cmn-clearfix"]/li/a/@href').extract()
            #如果该名字对应多个人物
            if persons:
                current_url = response.url
                yield scrapy.Request(current_url, callback=self.parse_exp, meta={"scholar": scholar})
                for person in persons:
                    current_url = "https://baike.baidu.com"+str(person)
                    yield scrapy.Request(current_url, callback=self.parse_exp, meta={"scholar": scholar})

            #如果该人名只对应一个人物
            else:
                current_url = response.url
                yield scrapy.Request(current_url, callback=self.parse_exp, meta={"scholar": scholar})

    #确定爬取页面
    def parse_exp(self, response):

        sel = Selector(response)
        scholar = response.meta['scholar']
        id = scholar.id
        org = scholar.org
        name = scholar.name
        exp = "".join(sel.xpath('//div[@class="main-content"]/div[@class="para"]/text()|'
                                '//div[@class="main-content"]/div[@class="para"]//a[@href]/text()').extract())
        # 匹配与气象有关的关键词
        ''''
        flag = 0
        if "气象" in exp or "气候" in exp or "大气研究" in exp:
            flag=1
        if flag:
        '''
        if org in exp:
            item = CompleteExpItem()
            item['id'] = id
            item['name'] = name
            item['org'] = org
            item['url'] = response.url
            item['exp'] = exp
            yield item
