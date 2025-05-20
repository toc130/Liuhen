"""
数据管理器模块 - 统一管理截图记录的存储和检索
"""

import os
import json
import datetime
import time
from typing import List, Dict, Any, Optional, Tuple

from src.config import DATA_DIR

# 数据库文件路径
DB_FILE = os.path.join(DATA_DIR, "records.json")

# 单例实例
_instance = None

class DataManager:
    """数据管理器类，负责记录的增删改查"""
    
    def __new__(cls):
        """实现单例模式"""
        global _instance
        if _instance is None:
            _instance = super(DataManager, cls).__new__(cls)
            _instance._initialized = False
        return _instance
    
    def __init__(self):
        """初始化数据管理器"""
        # 如果已经初始化过，则跳过
        if getattr(self, '_initialized', False):
            return
            
        print(f"初始化DataManager，数据文件路径：{DB_FILE}")
        self.records = []
        self._load_records()
        self._initialized = True
    
    def _load_records(self) -> None:
        """从文件加载记录"""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                    # 打印加载信息，调试使用
                    print(f"成功加载了 {len(self.records)} 条记录")
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载记录文件失败: {e}")
                self.records = []
        else:
            print(f"记录文件不存在，将创建新文件: {DB_FILE}")
            self.records = []
            
            # 确保目录存在
            os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
            
            # 创建空记录文件
            try:
                with open(DB_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                print(f"已创建空记录文件: {DB_FILE}")
            except Exception as e:
                print(f"创建空记录文件失败: {e}")
    
    def _save_records(self) -> None:
        """保存记录到文件"""
        try:
            os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(self.records)} 条记录到 {DB_FILE}")
        except Exception as e:
            print(f"保存记录失败: {e}")
    
    def add_record(self, task_name: str, image_path: str, notes: str = "") -> int:
        """添加新记录
        
        Args:
            task_name: 任务/项目名称
            image_path: 图片文件路径
            notes: 附加说明
            
        Returns:
            int: 新记录的ID
        """
        # 生成新记录ID
        record_id = len(self.records) + 1
        if self.records and 'id' in self.records[-1]:
            record_id = self.records[-1]['id'] + 1
        
        # 标准化路径格式（使用正斜杠）
        normalized_path = os.path.abspath(image_path).replace('\\', '/')
        
        # 输出调试信息
        print(f"添加记录 - 原始路径: {image_path}")
        print(f"添加记录 - 标准化路径: {normalized_path}")
        
        # 创建记录
        record = {
            'id': record_id,
            'task_name': task_name,
            'image_path': normalized_path,
            'notes': notes,
            'timestamp': datetime.datetime.now().isoformat(),
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        self.records.append(record)
        self._save_records()
        return record_id
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """获取所有记录
        
        Returns:
            List[Dict[str, Any]]: 记录列表
        """
        return self.records
    
    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[Dict[str, Any]]: 找到的记录或None
        """
        for record in self.records:
            if record['id'] == record_id:
                return record
        return None
    
    def search_records(self, keyword: str = "", date_from: str = "", date_to: str = "") -> List[Dict[str, Any]]:
        """搜索记录
        
        Args:
            keyword: 关键词搜索
            date_from: 开始日期
            date_to: 结束日期
            
        Returns:
            List[Dict[str, Any]]: 符合条件的记录列表
        """
        results = []
        
        # 转换日期字符串为datetime对象
        try:
            if date_from:
                from_date = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            else:
                from_date = None
                
            if date_to:
                to_date = datetime.datetime.strptime(date_to, "%Y-%m-%d")
                # 设置结束日期为当天的23:59:59
                to_date = to_date.replace(hour=23, minute=59, second=59)
            else:
                to_date = None
        except ValueError:
            return []
        
        for record in self.records:
            # 创建时间检查
            if 'timestamp' in record:
                try:
                    record_date = datetime.datetime.fromisoformat(record['timestamp'])
                    
                    # 日期范围过滤
                    if from_date and record_date < from_date:
                        continue
                    if to_date and record_date > to_date:
                        continue
                except (ValueError, TypeError):
                    pass
            
            # 关键词搜索
            if keyword:
                task_name = record.get('task_name', '').lower()
                notes = record.get('notes', '').lower()
                if keyword.lower() not in task_name and keyword.lower() not in notes:
                    continue
            
            results.append(record)
        
        return results
    
    def update_record(self, record_id: int, task_name: str = None, notes: str = None) -> bool:
        """更新记录
        
        Args:
            record_id: 记录ID
            task_name: 新的任务/项目名称
            notes: 新的附加说明
            
        Returns:
            bool: 更新是否成功
        """
        for i, record in enumerate(self.records):
            if record['id'] == record_id:
                if task_name is not None:
                    self.records[i]['task_name'] = task_name
                if notes is not None:
                    self.records[i]['notes'] = notes
                self.records[i]['updated_at'] = datetime.datetime.now().isoformat()
                self._save_records()
                return True
        return False
    
    def delete_record(self, record_id: int) -> Tuple[bool, str]:
        """删除记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 图片路径或错误消息)
        """
        for i, record in enumerate(self.records):
            if record['id'] == record_id:
                image_path = record.get('image_path', '')
                del self.records[i]
                self._save_records()
                return True, image_path
        return False, "记录不存在" 