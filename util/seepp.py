from util.ReadConfig import get_config_parser
from util.ssh.SSHThread import ParamikoThreading
import logging
import os
from util.ssh.ssh_client import SSHClient
from util.os.os_util import get_all_files_in_local_dir

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
sections_map = get_config_parser("local_config_puyin.ini")


# ------获取本地指定目录及其子目录下的所有文件------
def __get_all_files_in_local_dir(local_dir):
    # 保存所有文件的列表
    all_files = list()

    # 获取当前指定目录下的所有目录及文件，包含属性值
    files = os.listdir(local_dir)
    for x in files:
        # local_dir目录中每一个文件或目录的完整路径
        filename = os.path.join(local_dir, x)
        # 如果是目录，则递归处理该目录
        if os.path.isdir(x):
            all_files.extend(__get_all_files_in_local_dir(filename))
        else:
            all_files.append(filename)
    return all_files


def deploy(service_name):
    # get connfig based on service_name
    items = sections_map[service_name]
    local_path = items['local_dir']
    start_shell = items['start_shell']
    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)

    # upload local file to remote
    logger.info("STEP:begin to upload jar/war file")
    deploy_path = items['deploy_path'] + r'/springboot/application'
    client.sftp_put_dir(local_path, deploy_path)

    # get the name of jar file
    jar_name = os.path.split(get_all_files_in_local_dir(local_path)[0])[-1]
    logger.info("jar name:" + jar_name)

    # edit the start shell script in remote
    logger.info("STEP:begin to edit boot shell")
    cmd = r'sed -i "s/application\/fintcs-query-service.*\.jar$/application\/' + jar_name + '/g" ' + items[
        'deploy_path'] + r'/springboot/' + start_shell
    logger.debug("cmd:" + cmd)
    client.exec_cmd(cmd)


def deploy_all():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to deploy:" + ','.join(service_list))
    for service in service_list:
        deploy(service)


if __name__ == '__main__':
    deploy_all()
