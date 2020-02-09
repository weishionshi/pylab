import configparser
import os
import logging


def get_config_parser(file_name):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # 获取当前文件所在目录的上两级目录
    root_dir = os.path.dirname(os.path.abspath('..'))
    sectionsMap = {}
    logger.debug("root dir:" + root_dir)
    logger.info("config file: "+root_dir + "/config/" + file_name)
    cf = configparser.ConfigParser()
    # 拼接得到local_config.ini文件的路径，直接使用
    cf.read(root_dir + "/config/" + file_name)
    sections = cf.sections()

    for i in range(len(sections)):
        items = cf.items(sections[i])
        itemsMap = {}
        for j in range(len(items)):
            itemsMap[items[j][0]] = items[j][1]
        sectionsMap[sections[i]] = itemsMap
    return sectionsMap
'''
    secs = cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，每个section由[]包裹，即[section])，并以列表的形式返回
    print("sections: ")
    print(secs)

    options = cf.options("fintcs-query-service")  # 获取某个section名为fintcs-query-service所对应的键
    print("options:")
    print(options)

    items = cf.items("fintcs-query-service")  # 获取section名为fintcs-query-service所对应的全部键值对
    print("items")
    print(items)

    host = cf.get("fintcs-query-service", "host")  # 获取[fintcs-query-service]中host对应的值
    print("host:\n"+host)
'''