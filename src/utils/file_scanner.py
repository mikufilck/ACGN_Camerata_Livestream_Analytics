import os
import re
from typing import List, Dict, TypedDict, Union, Optional


# 定义扫描结果的数据结构
class FileMeta(TypedDict):
    file_path: str  # 文件的绝对路径
    file_name: str  # 文件名 (不含路径)
    file_type: str  # 'log' 或 'csv'
    uid: str  # 提取出的主播UID
    date_str: str  # 日期字符串 ('2025-05-01' 或 '2025-05')
    file_size: int  # 文件大小 (用于后续防重校验)


class FileScanner:
    """
    [工具组件] 文件扫描器
    职责: 扫描指定路径，基于文件名正则提取 UID 和日期，过滤无效文件。
    """

    # -------------------------------------------------------------
    # 正则表达式配置
    # -------------------------------------------------------------

    # Log 匹配模式: 123456_2025-05-01.log
    # Group 1: UID
    # Group 2,3,4: YYYY, MM, DD
    LOG_PATTERN = re.compile(r'^(\d+)_(\d{4})-(\d{1,2})-(\d{1,2})\.log$', re.IGNORECASE)

    # CSV 匹配模式: 123456_2025-5.csv 或 123456_2025-05.csv
    # Group 1: UID
    # Group 2,3: YYYY, MM
    CSV_PATTERN = re.compile(r'^(\d+)_(\d{4})-(\d{1,2})\.csv$', re.IGNORECASE)

    @classmethod
    def scan(cls, target_path: str) -> List[FileMeta]:
        """
        主入口: 扫描目标路径 (支持文件或文件夹)
        返回有效的文件元数据列表。
        """
        results: List[FileMeta] = []

        if not os.path.exists(target_path):
            return []

        # 情况 A: 传入的是单个文件 (通常是 CSV)
        if os.path.isfile(target_path):
            meta = cls._parse_file(target_path)
            if meta:
                results.append(meta)

        # 情况 B: 传入的是目录 (通常是 Log 文件夹)
        elif os.path.isdir(target_path):
            # 递归遍历目录
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    meta = cls._parse_file(full_path)
                    if meta:
                        results.append(meta)

        # 按文件名排序，保证处理顺序 (Log按日期先后)
        results.sort(key=lambda x: x['file_name'])
        return results

    @classmethod
    def _parse_file(cls, file_path: str) -> Optional[FileMeta]:
        """内部逻辑: 解析单个文件名"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # 1. 尝试匹配 Log
        log_match = cls.LOG_PATTERN.match(filename)
        if log_match:
            uid, year, month, day = log_match.groups()
            # 补零格式化: 2025-5-1 -> 2025-05-01
            date_str = f"{year}-{int(month):02d}-{int(day):02d}"
            return {
                "file_path": file_path,
                "file_name": filename,
                "file_type": "log",
                "uid": uid,
                "date_str": date_str,
                "file_size": file_size
            }

        # 2. 尝试匹配 CSV
        csv_match = cls.CSV_PATTERN.match(filename)
        if csv_match:
            uid, year, month = csv_match.groups()
            # 补零格式化: 2025-5 -> 2025-05
            date_str = f"{year}-{int(month):02d}"
            return {
                "file_path": file_path,
                "file_name": filename,
                "file_type": "csv",
                "uid": uid,
                "date_str": date_str,
                "file_size": file_size
            }

        # 3. 都不匹配 (如 .DS_Store, README.txt)
        return None

    @staticmethod
    def group_by_uid(file_list: List[FileMeta]) -> Dict[str, List[FileMeta]]:
        """
        辅助工具: 将扫描结果按 UID 分组
        (方便后续 Parser 批量处理同一个主播的文件)
        """
        grouped = {}
        for item in file_list:
            uid = item['uid']
            if uid not in grouped:
                grouped[uid] = []
            grouped[uid].append(item)
        return grouped