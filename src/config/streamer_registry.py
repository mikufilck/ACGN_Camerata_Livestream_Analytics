import json
import os
import random
from typing import Dict, Optional, List, TypedDict


# 定义主播配置的数据结构 (Type Hinting)
class StreamerProfile(TypedDict):
    name: str  # 显示名称 (用户可修改)
    uid: str  # 唯一标识 (不可修改)
    color: str  # 图表曲线颜色 (HEX格式)
    created_at: str  # 首次录入时间


class StreamerRegistry:
    """
    [核心组件] 主播户籍管理器
    负责读写 config/streamers.json，管理所有已知主播的元数据。
    """

    def __init__(self):
        # [路径锚定]
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        self.config_root = os.path.join(project_root, "config")
        self.json_path = os.path.join(self.config_root, "streamers.json")

        self._cache: Dict[str, StreamerProfile] = {}

        self._default_colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD",
            "#D4A5A5", "#9B59B6", "#3498DB", "#E67E22", "#2ECC71"
        ]

        self._ensure_config_exists()
        self.reload()

    def _ensure_config_exists(self):
        """确保配置目录和文件存在"""
        if not os.path.exists(self.config_root):
            try:
                os.makedirs(self.config_root)
            except Exception:
                pass

        if not os.path.exists(self.json_path):
            self._save_file({"streamers": []})

    def reload(self):
        """从磁盘重新加载配置 (兼容性增强版)"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # [核心修复] 智能识别两种 JSON 结构

            # 情况 A: 标准格式 {"streamers": [ ... ]}
            if isinstance(raw_data, dict) and "streamers" in raw_data and isinstance(raw_data["streamers"], list):
                self._cache = {s['uid']: s for s in raw_data["streamers"]}

            # 情况 B: 意外保存为纯字典格式 { "uid": { ... } }
            elif isinstance(raw_data, dict) and "streamers" not in raw_data:
                # 尝试判断 values 是否看起来像 profile
                is_profile_dict = True
                for k, v in raw_data.items():
                    if not isinstance(v, dict) or 'uid' not in v:
                        is_profile_dict = False
                        break

                if is_profile_dict:
                    self._cache = raw_data
                else:
                    print("[Registry] 警告: 配置文件格式无法识别，已重置")
                    self._cache = {}

            else:
                self._cache = {}

        except (json.JSONDecodeError, FileNotFoundError):
            self._cache = {}

    def save(self):
        """持久化保存到磁盘 (统一保存为标准格式)"""
        data = {
            "streamers": list(self._cache.values())
        }
        self._save_file(data)

    def _save_file(self, data):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Registry Error] 保存配置失败: {e}")

    # =========================================================
    # 核心业务接口
    # =========================================================

    def get_streamer(self, uid: str) -> Optional[StreamerProfile]:
        return self._cache.get(str(uid))

    def get_or_register(self, uid: str, name: str = None) -> StreamerProfile:
        uid = str(uid)
        if uid in self._cache:
            return self._cache[uid]
        return self.register_new_streamer(uid, name)

    def register_new_streamer(self, uid: str, name: str = None) -> StreamerProfile:
        if not name:
            name = f"主播_{uid}"

        new_profile: StreamerProfile = {
            "name": name,
            "uid": uid,
            "color": self._pick_random_color(uid),
            "created_at": self._get_current_timestamp()
        }

        self._cache[uid] = new_profile
        self.save()
        return new_profile

    def update_streamer_info(self, uid: str, name: str = None, color: str = None):
        uid = str(uid)
        if uid not in self._cache:
            return

        changed = False
        if name:
            self._cache[uid]['name'] = name
            changed = True
        if color:
            self._cache[uid]['color'] = color
            changed = True

        if changed:
            self.save()

    def get_all_streamers(self) -> List[StreamerProfile]:
        return list(self._cache.values())

    # =========================================================
    # 工具方法
    # =========================================================

    def _pick_random_color(self, uid: str) -> str:
        hash_val = sum(ord(c) for c in uid)
        return self._default_colors[hash_val % len(self._default_colors)]

    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 单例模式 (可选，方便全局调用)
# registry = StreamerRegistry()