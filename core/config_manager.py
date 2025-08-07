"""
配置管理器
统一管理所有配置模块
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加配置模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.base_config import BaseConfig, ValidationResult, ConfigGroup
from config.server_config import ServerConfig, UploadConfig
from config.network_config import NetworkConfig
from config.security_config import SecurityConfig


class ConfigManager(ConfigGroup):
    """统一配置管理器"""

    def __init__(self):
        super().__init__()

        # 初始化各种配置
        self.server_config = ServerConfig()
        self.network_config = NetworkConfig()
        self.security_config = SecurityConfig()
        self.upload_config = UploadConfig()

        # 添加到配置组
        self.add_config('server', self.server_config)
        self.add_config('network', self.network_config)
        self.add_config('security', self.security_config)
        self.add_config('upload', self.upload_config)

        # 配置文件路径
        self.config_file_path: Optional[str] = None

        # 自动保存设置
        self.auto_save_enabled: bool = True
        self.auto_save_interval: int = 30  # 秒

    def load_config(self, file_path: str):
        """加载配置文件"""
        try:
            self.load_from_file(file_path)
            self.config_file_path = file_path
            print(f"配置已从 {file_path} 加载")
        except Exception as e:
            print(f"加载配置失败: {e}")
            raise

    def save_config(self, file_path: Optional[str] = None):
        """保存配置文件"""
        if file_path is None:
            file_path = self.config_file_path

        if file_path is None:
            raise ValueError("未指定配置文件路径")

        try:
            self.save_to_file(file_path)
            self.config_file_path = file_path
            print(f"配置已保存到 {file_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
            raise

    def load_from_legacy(self, legacy_config):
        """从旧配置迁移"""
        try:
            # 迁移服务器配置
            if hasattr(legacy_config, 'general'):
                general = legacy_config.general

                # 基本设置
                self.server_config.working_directory = getattr(general, 'working_directory', os.getcwd())
                self.server_config.max_clients = getattr(general, 'max_clients', 1024)
                self.server_config.cpu_cores = getattr(general, 'cpu_cores', 1)
                self.server_config.accounts = getattr(general, 'accounts', [])
                self.server_config.volumes = getattr(general, 'volumes', [])
                self.server_config.groups = getattr(general, 'groups', [])

                # 功能设置
                self.server_config.enable_dots = getattr(general, 'enable_dots', False)
                self.server_config.urlform = getattr(general, 'urlform', "print,xm")
                self.server_config.window_title = getattr(general, 'window_title', "cpp @ $pub")
                self.server_config.server_name = getattr(general, 'server_name', "copyparty")

                # MIME 设置
                self.server_config.mime_mappings = getattr(general, 'mime_mappings', [])
                self.server_config.list_mimes = getattr(general, 'list_mimes', False)
                self.server_config.expensive_mime = getattr(general, 'expensive_mime', False)

            # 迁移网络配置
            if hasattr(legacy_config, 'network'):
                network = legacy_config.network

                self.network_config.listen_ips = getattr(network, 'listen_ips', "::")
                self.network_config.listen_ports = getattr(network, 'listen_ports', "3923")
                self.network_config.include_link_local = getattr(network, 'include_link_local', False)
                self.network_config.reverse_proxy_depth = getattr(network, 'reverse_proxy_depth', 1)
                self.network_config.xff_header = getattr(network, 'xff_header', "x-forwarded-for")
                self.network_config.xff_sources = getattr(network, 'xff_sources', "127.0.0.0/8, ::1/128")

                # 超时设置
                self.network_config.socket_timeout_header = getattr(network, 'socket_timeout_header', 120)
                self.network_config.socket_timeout_body = getattr(network, 'socket_timeout_body', 128.0)
                self.network_config.socket_read_size = getattr(network, 'socket_read_size', 256 * 1024)
                self.network_config.socket_write_size = getattr(network, 'socket_write_size', 256 * 1024)

            # 迁移TLS配置
            if hasattr(legacy_config, 'tls'):
                tls = legacy_config.tls

                self.security_config.tls.http_only = getattr(tls, 'http_only', False)
                self.security_config.tls.https_only = getattr(tls, 'https_only', False)
                self.security_config.tls.cert_path = getattr(tls, 'cert_path', "")
                self.security_config.tls.ssl_versions = getattr(tls, 'ssl_versions', "")
                self.security_config.tls.ciphers = getattr(tls, 'ciphers', "")

            # 迁移上传配置
            if hasattr(legacy_config, 'upload'):
                upload = legacy_config.upload

                self.upload_config.max_file_size = getattr(upload, 'max_file_size', 0)
                self.upload_config.max_files_per_upload = getattr(upload, 'max_files_per_upload', 0)
                self.upload_config.overwrite_existing = getattr(upload, 'overwrite_existing', False)
                self.upload_config.create_directories = getattr(upload, 'create_directories', True)

            # 标记所有配置为已更改
            self.server_config.mark_changed()
            self.network_config.mark_changed()
            self.security_config.mark_changed()
            self.upload_config.mark_changed()

            print("旧配置迁移完成")

        except Exception as e:
            print(f"旧配置迁移失败: {e}")
            raise

    def generate_copyparty_args(self) -> List[str]:
        """生成 CopyParty 命令行参数"""
        args = []

        # 添加各模块的参数
        args.extend(self.server_config.get_command_args())
        args.extend(self.network_config.get_command_args())
        args.extend(self.security_config.get_command_args())
        args.extend(self.upload_config.get_command_args())

        return args

    def validate_all(self) -> ValidationResult:
        """验证所有配置"""
        return self.validate()

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            'server': {
                'working_directory': self.server_config.working_directory,
                'max_clients': self.server_config.max_clients,
                'accounts_count': len(self.server_config.accounts),
                'volumes_count': len(self.server_config.volumes)
            },
            'network': {
                'listen_ips': self.network_config.listen_ips,
                'listen_ports': self.network_config.listen_ports,
                'reverse_proxy_depth': self.network_config.reverse_proxy_depth
            },
            'security': {
                'https_only': self.security_config.tls.https_only,
                'authentication_enabled': self.security_config.authentication.enable_authentication,
                'cert_configured': bool(self.security_config.tls.cert_path)
            },
            'upload': {
                'max_file_size': self.upload_config.max_file_size,
                'max_files_per_upload': self.upload_config.max_files_per_upload
            }
        }

    def reset_to_defaults(self):
        """重置为默认配置"""
        self.server_config = ServerConfig()
        self.network_config = NetworkConfig()
        self.security_config = SecurityConfig()
        self.upload_config = UploadConfig()

        # 重新添加到配置组
        self._configs.clear()
        self.add_config('server', self.server_config)
        self.add_config('network', self.network_config)
        self.add_config('security', self.security_config)
        self.add_config('upload', self.upload_config)

        print("配置已重置为默认值")

    def export_config(self, format: str = 'json') -> str:
        """导出配置"""
        if format.lower() == 'json':
            return self.to_json()
        elif format.lower() == 'yaml':
            return self.to_yaml()
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def import_config(self, content: str, format: str = 'json'):
        """导入配置"""
        if format.lower() == 'json':
            self.from_json(content)
        elif format.lower() == 'yaml':
            self.from_yaml(content)
        else:
            raise ValueError(f"不支持的导入格式: {format}")

    def get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 在用户主目录下创建配置目录
        config_dir = Path.home() / '.copyparty_desktop'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')

    def auto_save_if_needed(self):
        """如果需要则自动保存"""
        if self.auto_save_enabled and self.changed and self.config_file_path:
            try:
                self.save_config()
                print("配置已自动保存")
            except Exception as e:
                print(f"自动保存失败: {e}")
