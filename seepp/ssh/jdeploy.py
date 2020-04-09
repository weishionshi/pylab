import sys
from seepp.ssh.jenkins_deploy import JenkinsDeployer

if __name__ == '__main__':
    if sys.argv[1] == '' :
        print('请指定环境信息，例如jdeploy fintcs-tcs-service')
        exit()
    else:
        # init deployer obj
        obj = JenkinsDeployer(sys.argv[1])
        # start deploy
        obj.deploy()