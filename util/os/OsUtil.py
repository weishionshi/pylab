import os


def get_all_files_in_local_dir(local_dir):
    # 保存所有文件的列表
    all_files = list()

    # 获取当前指定目录下的所有目录及文件，包含属性值
    files = os.listdir(local_dir)
    for x in files:
        # local_dir目录中每一个文件或目录的完整路径
        filename = os.path.join(local_dir, x)
        # 如果是目录，则递归处理该目录
        if os.path.isdir(x):
            all_files.extend(get_all_files_in_local_dir(filename))
        else:
            all_files.append(filename)
    return all_files