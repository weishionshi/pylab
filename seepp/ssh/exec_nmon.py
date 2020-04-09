from util.ssh.SSHThread import ParamikoThreading

if __name__ == '__main__':
    # from settings import hosts  # 调用配置文件配置文件为settings.py
    hosts = [dict(host="192.168.1.108", username="root", password="caifu@123"),
             dict(host="192.168.1.108", username="root", password="caifu@123"),
             dict(host="192.168.1.108", username="root", password="bbqqll")]

    command = "date -s \"20191107 17:25:00\""

    t_pool = []
    for host in hosts:
        t = ParamikoThreading(
            host=host.get("host", "localhost"),
            username=host.get("username", "root"),
            password=host.get("password", "123"),
            command=command
        )
        t_pool.append(t)
    for t in t_pool:
        t.start()
    for t in t_pool:
        t.join()
