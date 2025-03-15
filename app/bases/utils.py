"""
工具库函数
客户无需多管该文件
"""
import os
import sys
import hashlib


def calculate_md5(filepath, chunk_size=8192):
    md5 = hashlib.md5()
    with filepath.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def resource_path(relative_path: str):
    """将相对路径转为exe运行时资源文件的绝对路径"""
    # _MEIPASS 是exe运行时的临时目录路径
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
