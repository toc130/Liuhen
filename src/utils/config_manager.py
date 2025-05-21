"""
配置管理器 - 管理用户配置
"""

import os
import json
import sys
import copy

# 导入默认配置
from src.config import (
    DEFAULT_REMINDER_TIME, REMINDER_MESSAGE, REMINDER_SOUND_ENABLED,
    INTERVAL_REMINDER_MINUTES, INTERVAL_REMINDER_MESSAGE,
    SCREENSHOT_DIR
)

class ConfigManager:
    """配置管理器类，管理用户配置"""
    
    _instance = None  # 单例模式实例
    
    @classmethod
    def get_instance(cls):
        """获取ConfigManager单例实例"""
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if ConfigManager._instance is not None:
            raise Exception("ConfigManager是单例类，请使用get_instance()方法获取实例")
        
        # 默认配置
        self.default_config = {
            "reminder": {
                "default_time": DEFAULT_REMINDER_TIME,
                "message": REMINDER_MESSAGE,
                "sound_enabled": REMINDER_SOUND_ENABLED,
                "interval_minutes": INTERVAL_REMINDER_MINUTES,
                "interval_message": INTERVAL_REMINDER_MESSAGE
            },
            "ui": {
                "startup_maximized": True,
                "confirm_on_exit": True,
                "auto_save": False,
                "screenshot_quality": 90
            },
            "files": {
                "screenshot_save_path": SCREENSHOT_DIR,
                "use_custom_path": False
            },
            "advanced": {
                "debug_mode": False,
                "save_logs": True
            }
        }
        
        # 当前配置
        self.config = {}  # 创建新的空字典，而不是使用引用
        
        # 深拷贝默认配置到当前配置
        self.config = copy.deepcopy(self.default_config)
        
        # 加载用户配置
        self.load_config()
    
    def get_user_config_path(self):
        """获取用户配置文件路径"""
        # 获取用户配置目录
        if hasattr(sys, "_MEIPASS"):  # PyInstaller打包环境
            config_dir = os.path.join(os.path.expanduser("~"), ".liuhen")
            print(f"打包环境 - 用户配置目录: {config_dir}")
        else:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            print(f"开发环境 - 用户配置目录: {config_dir}")
        
        # 确保目录存在
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
                print(f"已创建配置目录: {config_dir}")
            except Exception as e:
                print(f"创建配置目录失败，尝试使用备选目录: {e}")
                # 如果首选目录创建失败，尝试使用桌面
                config_dir = os.path.join(os.path.expanduser("~"), "Desktop", ".liuhen")
                os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "user_config.json")
    
    def load_config(self):
        """加载用户配置"""
        config_path = self.get_user_config_path()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # 递归更新配置
                    self.update_nested_dict(self.config, user_config)
                    
                # 验证保存路径的有效性
                if "files" in self.config and "screenshot_save_path" in self.config["files"]:
                    save_path = self.config["files"]["screenshot_save_path"]
                    # 确保路径是字符串且存在
                    if not isinstance(save_path, str) or not save_path:
                        print("保存路径无效，重置为默认")
                        from src.config import SCREENSHOT_DIR
                        self.config["files"]["screenshot_save_path"] = SCREENSHOT_DIR
                        
                print(f"已加载用户配置: {config_path}")
            except Exception as e:
                print(f"加载用户配置失败: {e}")
                # 文件可能损坏，创建备份并使用默认配置
                if os.path.exists(config_path):
                    try:
                        backup_path = f"{config_path}.bak"
                        import shutil
                        shutil.copy2(config_path, backup_path)
                        print(f"已创建配置文件备份: {backup_path}")
                    except Exception as backup_error:
                        print(f"备份配置文件失败: {backup_error}")
        else:
            print("未找到用户配置文件，使用默认配置")
    
    def update_nested_dict(self, d, u):
        """递归更新嵌套字典
        
        Args:
            d: 目标字典
            u: 更新字典
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self.update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def save_config(self, new_config=None):
        """保存用户配置
        
        Args:
            new_config: 新的配置字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            print("ConfigManager - 开始保存配置")
            if new_config:
                # 更新配置
                print("ConfigManager - 更新配置字典")
                self.update_nested_dict(self.config, new_config)
            else:
                print("ConfigManager - 没有提供新配置，使用当前配置")
            
            # 验证保存路径格式
            if "files" in self.config and "screenshot_save_path" in self.config["files"]:
                save_path = self.config["files"]["screenshot_save_path"]
                if isinstance(save_path, str):
                    # 标准化路径
                    self.config["files"]["screenshot_save_path"] = os.path.normpath(save_path)
                    print(f"ConfigManager - 标准化保存路径: {self.config['files']['screenshot_save_path']}")
            
            # 保存到文件
            config_path = self.get_user_config_path()
            print(f"ConfigManager - 准备保存到: {config_path}")
            
            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                print(f"ConfigManager - 创建配置目录: {config_dir}")
                os.makedirs(config_dir, exist_ok=True)
            
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                print(f"ConfigManager - 已成功保存用户配置: {config_path}")
                return True
            except Exception as e:
                print(f"ConfigManager - 保存用户配置失败: {e}")
                # 尝试保存到备选位置
                try:
                    backup_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                    backup_path = os.path.join(backup_dir, "liuhen_config.json")
                    print(f"ConfigManager - 尝试保存到备选位置: {backup_path}")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        json.dump(self.config, f, ensure_ascii=False, indent=2)
                    print(f"ConfigManager - 已保存用户配置到备选位置: {backup_path}")
                    return True
                except Exception as backup_error:
                    print(f"ConfigManager - 保存到备选位置也失败: {backup_error}")
                    return False
        except Exception as e:
            print(f"ConfigManager - 保存配置过程中发生未预期错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_value(self, section, key, default=None):
        """获取配置值
        
        Args:
            section: 配置区域
            key: 配置键名
            default: 默认值
        
        Returns:
            配置值
        """
        try:
            return self.config[section][key]
        except (KeyError, TypeError):
            return default
    
    def set_value(self, section, key, value):
        """设置配置值
        
        Args:
            section: 配置区域
            key: 配置键名
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def apply_config(self, app_instance):
        """将配置应用到应用实例
        
        Args:
            app_instance: 应用实例
        """
        # 应用提醒设置
        if hasattr(app_instance, 'reminder_entry'):
            app_instance.reminder_entry.delete(0, 'end')
            app_instance.reminder_entry.insert(0, self.get_value('reminder', 'default_time', DEFAULT_REMINDER_TIME))
        
        # 应用文件路径设置
        if hasattr(app_instance, 'save_screenshot'):
            # 路径设置会在保存时应用，无需额外处理
            pass
        
        return True

# 创建默认实例
default_config_manager = ConfigManager.get_instance() 