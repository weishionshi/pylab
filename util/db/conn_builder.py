# 数据库(mysql,oracle) 连接工厂类
# 入参：host, user, password
import pymysql
import cx_Oracle


class PyMysqlFactory:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.database,
                                    charset='utf8')

    def __del__(self):
        self.conn.close()

    def get_connection(self):
        return self.conn


class PyOracleFactory:
    def __init__(self, host, port, user, password, srv_name):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.srv_name = srv_name
        # '用户名/密码@IP:端口号/SERVICE_NAME'
        conn_str = '%s/%s@%s:%s/%s' % (self.user, self.password, self.host, self.port, self.srv_name)
        self.conn = cx_Oracle.connect(conn_str)

    def get_connection(self):
        return self.conn


if __name__ == '__main__':
    # 连接database
    conn = pymysql.connect(host='127.0.0.1', port='3306', user='seepp', password='seepp876', database='seepp',
                           charset='utf8')
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    sql = """
    create table seet_test
    (
        vc_cmd           varchar(500)                        null comment 'execute command',
        vc_host          varchar(20)                         null comment 'host ip'
    )
    """
    # 执行SQL语句
    cursor.execute(sql)
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()
