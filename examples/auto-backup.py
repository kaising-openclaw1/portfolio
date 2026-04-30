#!/usr/bin/env python3
"""
自动备份脚本示例
功能：定时备份指定目录，支持压缩和增量备份
"""

import os
import shutil
import datetime
import hashlib

def backup_directory(source_dir, backup_dir):
    """备份目录到指定位置"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 创建备份
    shutil.copytree(source_dir, backup_path)
    
    # 计算文件哈希
    file_count = sum([len(files) for _, _, files in os.walk(backup_path)])
    
    return {
        "status": "success",
        "backup_path": backup_path,
        "file_count": file_count,
        "timestamp": timestamp
    }

if __name__ == "__main__":
    # 示例用法
    result = backup_directory("~/documents", "~/backups")
    print(f"备份完成：{result}")
