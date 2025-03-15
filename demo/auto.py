import json
import subprocess
import hashlib
import argparse
from pathlib import Path
import os

# ANSI 转义码
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"


def enable_ansi_escape_codes():
    """
    启用 Windows 命令行中的 ANSI 转义码支持。
    """
    if os.name == 'nt':
        os.system('chcp 65001 >nul')
        os.system('')


def create_config(directory, exclude_names):
    """
    创建配置文件，包含目录中所有文件的 MD5 校验值。

    :param directory: 目标目录
    :param exclude_names: 如果名称在该参数中，就排除不计入
    :return: 配置字典
    """
    config = {
        "presets": []
    }
    for filepath in directory.glob('*'):
        if filepath.is_file() and filepath.name not in exclude_names:
            file_md5 = calculate_md5(filepath)
            config['presets'].append({
                "filename": filepath.name,
                "data_md5": file_md5
            })
    return config


def calculate_md5(file_path):
    """
    计算文件的 MD5 校验值。

    :param file_path: 文件路径
    :return: MD5 校验值
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192 * 10), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def build_exe(directory, bat_file):
    """
    创建配置文件并调用批处理脚本打包目录。

    :param directory: 目标目录
    :param bat_file: 批处理脚本路径
    """
    app_name = '游戏仓鼠(文件完整性校验)'
    # 如果已生成的exe，需要排除不计算 md5，否则会有问题
    config = create_config(directory, [f"{app_name}.exe"])
    presets_path = directory / 'presets.json'
    try:
        # 写入配置文件
        with open(presets_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        # 调用批处理脚本，命令格式如下：
        # bat文件路径 json路径 输出目录 执行后是否暂停 输出的程序名称
        subprocess.call([str(bat_file), str(presets_path.resolve()), str(directory.resolve()), 'no', app_name])
    except Exception as e:
        # 删除配置文件
        if presets_path.exists():
            presets_path.unlink()
        print(f'{RED}* 打包过程中出现错误: {e}{RESET}')
        return False
    else:
        # 删除配置文件
        if presets_path.exists():
            presets_path.unlink()
        return True


def main():
    """
    主函数，解析命令行参数并打包目录。
    """
    enable_ansi_escape_codes()

    parser = argparse.ArgumentParser(description='批量创建游戏仓鼠程序')
    parser.add_argument('bat_file', type=str, help='bat 文件的路径')
    args = parser.parse_args()
    bat_file = Path(args.bat_file).resolve()

    if not bat_file.exists():
        print(f'{RED}* 批处理文件 {bat_file} 不存在，请检查路径。{RESET}')
        return None

    directories = [d for d in Path('./').glob("*") if d.is_dir() and not d.name.startswith('.')]
    dir_count = len(directories)
    success_count = 0
    failure_dirs = []
    print(f'{BLUE}* 待打包目录共计：{dir_count} 个{RESET}')
    print(f'{BLUE}* 使用的批处理文件：{bat_file}{RESET}')

    for index, directory in enumerate(directories):
        print(f'{YELLOW}* [{index + 1}/{dir_count}] 即将打包：{directory}{RESET}')
        result = build_exe(directory, bat_file)
        if result:
            success_count += 1
            print(f'{GREEN}* 打包完成: {str(directory)}，可执行程序已输出到该目录{RESET}\n')
        else:
            failure_dirs.append(directory)

    print(f'{BLUE}* 脚本运行结束，预计打包 {dir_count} 个，实际成功 {success_count} 个{RESET}')
    if failure_dirs:
        print(f'{RED}* 打包失败的目录如下：{RESET}')
    for i, f_dir in enumerate(failure_dirs):
        print(f'{BLUE}{i}{RESET}: {str(f_dir)}')


if __name__ == "__main__":
    main()
