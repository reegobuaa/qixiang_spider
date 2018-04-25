# -*- coding: utf-8 -*-
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
import json
import pymysql
import os

#保存为txt文件
class TxtPipeline(object):
    def process_item(self, item, spider):
        #获取当前工作目录
        base_dir = os.getcwd()
        file = base_dir + '/exp_气候_大气研究.txt'
        with open(file, 'a+') as f:
            f.write(item['name'] + '\t')
            f.write(item['url'] + '\t')
            for i in item['exp']:
                f.write(i)
            f.write('\n\n')
        return item


#保存为json文件
class JsonPipeline(object):

    def __init__(self):
        self.filename = open("exp_org_only.json", "wb+")

    def process_item(self, item, spider):
        text = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.filename.write(text.encode("utf-8"))
        return item

    def close_spider(self, spider):
        self.filename.close()


#保存到数据库
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'reego941122',
    'db': 'qixiang',
    'charset': 'utf8'
}
class MysqlPipeline(object):
    # 获取数据库连接和游标
    def __init__(self):
        self.connection = pymysql.connect(**db_config)
        self.cursor = self.connection.cursor()
    # Pipeline必须实现的方法，对收集好的item进行一系列处理

    def process_item(self, item, spider):
        # 存储的SQL语句
        sql = 'update scholar_qixiang set `experience` = %s, `resource_url` = %s where `id` = %s '
        try:
            self.cursor.execute(sql, (
                                      item['exp'].encode('utf-8'),
                                      item['url'].encode('utf-8'),
                                      item['id'].encode('utf-8'),
                                      )
                                )
            self.connection.commit()
        except pymysql.Error as e:
            # 若存在异常则抛出
            print(e.args)
        return item