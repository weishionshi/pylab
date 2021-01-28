# -*- encoding=utf8 -*-

"""
数据库连接池操作工具类
PooledDB用于多线程的,如果你的程序频繁地启动和关闭,最好使用这个
PersistentDB用于单线程,如果你的程序只是在单个线程上进行频繁的数据库连接,最好使用这个
使用前：安装
pip3 install pymysql 或者 pip install pymysql
pip3 install DBUtils 或者 pip install DBUtils
"""
import pymysql
import DBUtils.PersistentDB
import DBUtils.PooledDB
import DBUtils.dbconfig.mysqldb_config



# 数据库连接配置信息
config = DBUtils.dbconfig.mysqldb_config

def get_db_pool(is_mult_thread):
    if is_mult_thread:
        poolDB = DBUtils.PooledDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 连接池允许的最大连接数,0和None表示没有限制
            maxconnections=3,
            # 初始化时,连接池至少创建的空闲连接,0表示不创建
            mincached=2,
            # 连接池中空闲的最多连接数,0和None表示没有限制
            maxcached=5,
            # 连接池中最多共享的连接数量,0和None表示全部共享(其实没什么卵用)
            maxshared=3,
            # 连接池中如果没有可用共享连接后,是否阻塞等待,True表示等等,
            # False表示不等待然后报错
            blocking=True,
            # 开始会话前执行的命令列表
            setsession=[],
            # ping Mysql服务器检查服务是否可用
            ping=0,
            **config
        )
    else:
        poolDB = DBUtils.PersistentDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 一个连接最大复用次数,0或者None表示没有限制,默认为0
            maxusage=1000,
            **config
        )
    return poolDB

# 私有方法内部启动测试
if __name__ == '__main__':
    # 以单线程的方式初始化数据库连接池
    db_pool = get_db_pool(False)
    # 从数据库连接池中取出一条连接
    conn = db_pool.connection()
    cursor = conn.cursor()
    # 随便查一下吧
    cursor.execute('select * from uicase')
    # 随便取一条查询结果
    result = cursor.fetchone()
    print(result)
    # 把连接返还给连接池
    conn.close()
