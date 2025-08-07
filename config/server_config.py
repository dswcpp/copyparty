"""
服务器配置模块
迁移自 copyparty_complete_config.py 中的 GeneralConfig
"""

import os
from typing import List, Dict, Any, Optional
from .base_config import BaseConfig, ValidationResult


class ServerConfig(BaseConfig):
    """服务器配置 - 迁移自 GeneralConfig"""
    
    def __init__(self):
        super().__init__()
        
        # 基本选项
        self.config_files: List[str] = []  # -c
        self.max_clients: int = 1024  # -nc
        self.cpu_cores: int = 1  # -j
        self.accounts: List[str] = []  # -a
        self.volumes: List[str] = [f"{os.getcwd()}::rw"]  # -v 默认添加当前目录作为读写卷
        self.groups: List[str] = []  # --grp
        
        # 工作目录
        self.working_directory: str = os.getcwd()
        
        # 功能开关
        self.enable_dots: bool = False  # -ed
        self.urlform: str = "print,xm"  # --urlform
        
        # 显示设置
        self.window_title: str = "cpp @ $pub"  # --wintitle
        self.server_name: str = "copyparty"  # --name
        
        # MIME 类型
        self.mime_mappings: List[str] = []  # --mime
        self.list_mimes: bool = False  # --mimes
        self.expensive_mime: bool = False  # --rmagic
        
        # 信息选项
        self.show_license: bool = False  # --license
        self.show_version: bool = False  # --version
        
        # 设置验证规则
        self._required_fields = ['working_directory']
        self._type_rules = {
            'max_clients': int,
            'cpu_cores': int,
            'accounts': list,
            'volumes': list,
            'groups': list,
            'enable_dots': bool,
            'urlform': str,
            'window_title': str,
            'server_name': str,
            'mime_mappings': list,
            'list_mimes': bool,
            'expensive_mime': bool,
            'show_license': bool,
            'show_version': bool
        }
        self._value_rules = {
            'max_clients': {'min': 1, 'max': 65535},
            'cpu_cores': {'min': 1, 'max': 64}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'config_files': self.config_files,
            'max_clients': self.max_clients,
            'cpu_cores': self.cpu_cores,
            'accounts': self.accounts,
            'volumes': self.volumes,
            'groups': self.groups,
            'working_directory': self.working_directory,
            'enable_dots': self.enable_dots,
            'urlform': self.urlform,
            'window_title': self.window_title,
            'server_name': self.server_name,
            'mime_mappings': self.mime_mappings,
            'list_mimes': self.list_mimes,
            'expensive_mime': self.expensive_mime,
            'show_license': self.show_license,
            'show_version': self.show_version
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.config_files = data.get('config_files', [])
        self.max_clients = data.get('max_clients', 1024)
        self.cpu_cores = data.get('cpu_cores', 1)
        self.accounts = data.get('accounts', [])
        self.volumes = data.get('volumes', [])
        self.groups = data.get('groups', [])
        self.working_directory = data.get('working_directory', os.getcwd())
        self.enable_dots = data.get('enable_dots', False)
        self.urlform = data.get('urlform', "print,xm")
        self.window_title = data.get('window_title', "cpp @ $pub")
        self.server_name = data.get('server_name', "copyparty")
        self.mime_mappings = data.get('mime_mappings', [])
        self.list_mimes = data.get('list_mimes', False)
        self.expensive_mime = data.get('expensive_mime', False)
        self.show_license = data.get('show_license', False)
        self.show_version = data.get('show_version', False)
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # 配置文件
        for config_file in self.config_files:
            args.extend(['-c', config_file])
        
        # 最大客户端数
        if self.max_clients != 1024:
            args.extend(['-nc', str(self.max_clients)])
        
        # CPU 核心数
        if self.cpu_cores != 1:
            args.extend(['-j', str(self.cpu_cores)])
        
        # 账户
        for account in self.accounts:
            args.extend(['-a', account])
        
        # 卷
        for volume in self.volumes:
            args.extend(['-v', volume])
        
        # 组
        for group in self.groups:
            args.extend(['--grp', group])
        
        # 功能开关
        if self.enable_dots:
            args.append('-ed')
        
        # URL 表单
        if self.urlform != "print,xm":
            args.extend(['--urlform', self.urlform])
        
        # 窗口标题
        if self.window_title != "cpp @ $pub":
            args.extend(['--wintitle', self.window_title])
        
        # 服务器名称
        if self.server_name != "copyparty":
            args.extend(['--name', self.server_name])
        
        # MIME 映射
        for mime_mapping in self.mime_mappings:
            args.extend(['--mime', mime_mapping])
        
        # MIME 选项
        if self.list_mimes:
            args.append('--mimes')
        
        if self.expensive_mime:
            args.append('--rmagic')
        
        # 信息选项
        if self.show_license:
            args.append('--license')
        
        if self.show_version:
            args.append('--version')
        
        return args
    
    def _custom_validation(self, result: ValidationResult):
        """自定义验证"""
        # 验证工作目录
        if self.working_directory and not os.path.exists(self.working_directory):
            result.add_error(f"工作目录不存在: {self.working_directory}")
        
        # 验证账户格式
        for account in self.accounts:
            if ':' not in account:
                result.add_warning(f"账户格式可能不正确: {account} (应为 username:password)")
        
        # 验证卷格式
        for volume in self.volumes:
            parts = volume.split(':')
            if len(parts) < 1:
                result.add_error(f"卷格式错误: {volume}")
            else:
                volume_path = parts[0]
                if volume_path and not os.path.exists(volume_path):
                    result.add_warning(f"卷路径不存在: {volume_path}")
        
        # 验证配置文件
        for config_file in self.config_files:
            if not os.path.exists(config_file):
                result.add_warning(f"配置文件不存在: {config_file}")
    
    def add_account(self, username: str, password: str, permissions: str = ""):
        """添加账户"""
        if permissions:
            account = f"{username}:{password}:{permissions}"
        else:
            account = f"{username}:{password}"
        
        # 检查是否已存在
        for existing_account in self.accounts:
            if existing_account.startswith(f"{username}:"):
                # 更新现有账户
                index = self.accounts.index(existing_account)
                self.accounts[index] = account
                self.mark_changed()
                return
        
        # 添加新账户
        self.accounts.append(account)
        self.mark_changed()
    
    def remove_account(self, username: str):
        """删除账户"""
        for account in self.accounts[:]:  # 创建副本以安全删除
            if account.startswith(f"{username}:"):
                self.accounts.remove(account)
                self.mark_changed()
                break
    
    def add_volume(self, path: str, alias: str = "", permissions: str = "r"):
        """添加卷"""
        if alias:
            volume = f"{path}:{alias}:{permissions}"
        else:
            volume = f"{path}::{permissions}"
        
        if volume not in self.volumes:
            self.volumes.append(volume)
            self.mark_changed()
    
    def remove_volume(self, path: str):
        """删除卷"""
        for volume in self.volumes[:]:  # 创建副本以安全删除
            if volume.startswith(f"{path}:"):
                self.volumes.remove(volume)
                self.mark_changed()
                break
    
    def get_volume_info(self, volume: str) -> Dict[str, str]:
        """解析卷信息"""
        parts = volume.split(':')
        
        if len(parts) >= 3:
            return {
                'path': parts[0],
                'alias': parts[1],
                'permissions': parts[2]
            }
        elif len(parts) == 2:
            return {
                'path': parts[0],
                'alias': '',
                'permissions': parts[1]
            }
        else:
            return {
                'path': parts[0],
                'alias': '',
                'permissions': 'r'
            }
    
    def get_account_info(self, account: str) -> Dict[str, str]:
        """解析账户信息"""
        parts = account.split(':')
        
        if len(parts) >= 3:
            return {
                'username': parts[0],
                'password': parts[1],
                'permissions': parts[2]
            }
        elif len(parts) == 2:
            return {
                'username': parts[0],
                'password': parts[1],
                'permissions': ''
            }
        else:
            return {
                'username': parts[0],
                'password': '',
                'permissions': ''
            }


class UploadConfig(BaseConfig):
    """上传配置 - 迁移自原有的上传相关配置"""
    
    def __init__(self):
        super().__init__()
        
        # 上传限制
        self.max_file_size: int = 0  # 0 表示无限制
        self.max_files_per_upload: int = 0  # 0 表示无限制
        self.allowed_extensions: List[str] = []  # 允许的文件扩展名
        self.blocked_extensions: List[str] = []  # 禁止的文件扩展名
        
        # 上传行为
        self.overwrite_existing: bool = False  # 是否覆盖现有文件
        self.create_directories: bool = True  # 是否创建目录
        
        # 设置验证规则
        self._type_rules = {
            'max_file_size': int,
            'max_files_per_upload': int,
            'allowed_extensions': list,
            'blocked_extensions': list,
            'overwrite_existing': bool,
            'create_directories': bool
        }
        self._value_rules = {
            'max_file_size': {'min': 0},
            'max_files_per_upload': {'min': 0}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'max_file_size': self.max_file_size,
            'max_files_per_upload': self.max_files_per_upload,
            'allowed_extensions': self.allowed_extensions,
            'blocked_extensions': self.blocked_extensions,
            'overwrite_existing': self.overwrite_existing,
            'create_directories': self.create_directories
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.max_file_size = data.get('max_file_size', 0)
        self.max_files_per_upload = data.get('max_files_per_upload', 0)
        self.allowed_extensions = data.get('allowed_extensions', [])
        self.blocked_extensions = data.get('blocked_extensions', [])
        self.overwrite_existing = data.get('overwrite_existing', False)
        self.create_directories = data.get('create_directories', True)
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # TODO: 根据 CopyParty 的实际参数添加上传相关的命令行参数
        
        return args
