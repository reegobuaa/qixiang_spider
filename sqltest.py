import pymysql


class Scholar(object):
    def __init__(self, id, name, org):
        self.id = id
        self.name = name
        self.org = org


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
sql = "select `id`, `name`, `organization` from scholar_qixiang where experience IS NULL limit 100"
cur.execute(sql)
results = cur.fetchall()

for result in results:
    scholar = Scholar(result[0], result[1], result[2])
    print(scholar.id)
    print(scholar.name)
    print(scholar.org)


