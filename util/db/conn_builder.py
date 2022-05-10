# 数据库(mysql,oracle) 连接工厂类
# 入参：host, user, password
import pymysql
import cx_Oracle
from dbutils.persistent_db import PersistentDB


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

# TODO:connection pool


class PersistentDBPoolFactory:
    """
    PersistentDB ：提供线程专用的数据库连接，线程终止时才真正关闭链接
    为每个线程创建一个连接，通过thread.local实现
    """

    def __init__(self, host, port, user, password, database, charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.__pool = PersistentDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=1,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested,
            # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            closeable=False,
            # 如果为False时， conn.close() 实际上被忽略，连接不会被关闭，只有线程关闭时，才会自动关闭链接。
            # 如果为True时， conn.close()则关闭连接，那么再次调用pool.connection时就会报错，因为已经真的关闭了连接（pool.steady_connection()可以获取一个新的链接）
            threadlocal=None,  # 本线程独享值得对象，用于保存链接对象，如果链接对象被重置
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset
        )

    def get_pool(self):
        return self.__pool



def test_pymysql():
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

def test_pool():
    pool = PersistentDBPoolFactory(host='127.0.0.1', port=3306, user='root', password='Caifu123rt', database='stdtcs_513',
                           charset='utf8').get_pool()
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("select t.VC_VALUE from tc_tsysparameter t where t.vc_tenant_id ='10000' and t.VC_ITEM = 'SYSDATE' ")
    result = cursor.fetchall()
    print(str(result))
    cursor.close()
    conn.close()  # 不是真的关闭连接,只是把连接还给了连接池。


if __name__ == '__main__':
    test_pool()