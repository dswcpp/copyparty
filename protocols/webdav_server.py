"""
WebDAV 协议实现
基于HTTP的分布式创作和版本控制协议
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QLineEdit, QSpinBox, 
                             QCheckBox, QComboBox, QTextEdit)

from .base_protocol import BaseProtocol, ProtocolConfig


class WebDAVConfig(ProtocolConfig):
    """WebDAV协议配置"""
    
    def __init__(self):
        super().__init__()
        self.port = 8080
        self.enabled = False  # WebDAV默认禁用
        self.path_prefix = "/webdav"
        self.enable_locks = True
        self.lock_timeout = 3600  # 1小时
        self.enable_versioning = False
        self.max_depth = 10
        self.enable_properties = True
        self.custom_properties = []
        self.enable_quota = False
        self.quota_size = 1024 * 1024 * 1024  # 1GB
        self.enable_compression = True
        self.compression_level = 6
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'path_prefix': self.path_prefix,
            'enable_locks': self.enable_locks,
            'lock_timeout': self.lock_timeout,
            'enable_versioning': self.enable_versioning,
            'max_depth': self.max_depth,
            'enable_properties': self.enable_properties,
            'custom_properties': self.custom_properties,
            'enable_quota': self.enable_quota,
            'quota_size': self.quota_size,
            'enable_compression': self.enable_compression,
            'compression_level': self.compression_level
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        super().from_dict(data)
        self.path_prefix = data.get('path_prefix', "/webdav")
        self.enable_locks = data.get('enable_locks', True)
        self.lock_timeout = data.get('lock_timeout', 3600)
        self.enable_versioning = data.get('enable_versioning', False)
        self.max_depth = data.get('max_depth', 10)
        self.enable_properties = data.get('enable_properties', True)
        self.custom_properties = data.get('custom_properties', [])
        self.enable_quota = data.get('enable_quota', False)
        self.quota_size = data.get('quota_size', 1024 * 1024 * 1024)
        self.enable_compression = data.get('enable_compression', True)
        self.compression_level = data.get('compression_level', 6)


class WebDAVConfigWidget(QWidget):
    """WebDAV协议配置界面"""
    
    def __init__(self, config: WebDAVConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QGridLayout()
        
        # 启用协议
        basic_layout.addWidget(QLabel("启用WebDAV:"), 0, 0)
        self.enabled_check = QCheckBox()
        basic_layout.addWidget(self.enabled_check, 0, 1)
        
        # 端口设置
        basic_layout.addWidget(QLabel("端口:"), 0, 2)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        basic_layout.addWidget(self.port_spin, 0, 3)
        
        # 绑定地址
        basic_layout.addWidget(QLabel("绑定地址:"), 1, 0)
        self.bind_address_edit = QLineEdit()
        basic_layout.addWidget(self.bind_address_edit, 1, 1, 1, 3)
        
        # 路径前缀
        basic_layout.addWidget(QLabel("路径前缀:"), 2, 0)
        self.path_prefix_edit = QLineEdit()
        self.path_prefix_edit.setPlaceholderText("/webdav")
        basic_layout.addWidget(self.path_prefix_edit, 2, 1, 1, 3)
        
        # 最大连接数
        basic_layout.addWidget(QLabel("最大连接:"), 3, 0)
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 1000)
        basic_layout.addWidget(self.max_connections_spin, 3, 1)
        
        # 最大深度
        basic_layout.addWidget(QLabel("最大深度:"), 3, 2)
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 100)
        basic_layout.addWidget(self.max_depth_spin, 3, 3)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 功能设置组
        features_group = QGroupBox("功能设置")
        features_layout = QGridLayout()
        
        # 启用锁定
        self.enable_locks_check = QCheckBox("启用文件锁定")
        features_layout.addWidget(self.enable_locks_check, 0, 0)
        
        # 锁定超时
        features_layout.addWidget(QLabel("锁定超时(秒):"), 0, 2)
        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(60, 86400)
        features_layout.addWidget(self.lock_timeout_spin, 0, 3)
        
        # 启用版本控制
        self.enable_versioning_check = QCheckBox("启用版本控制")
        features_layout.addWidget(self.enable_versioning_check, 1, 0)
        
        # 启用属性
        self.enable_properties_check = QCheckBox("启用自定义属性")
        features_layout.addWidget(self.enable_properties_check, 1, 1)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 配额设置组
        quota_group = QGroupBox("配额设置")
        quota_layout = QGridLayout()
        
        # 启用配额
        self.enable_quota_check = QCheckBox("启用存储配额")
        quota_layout.addWidget(self.enable_quota_check, 0, 0)
        
        # 配额大小
        quota_layout.addWidget(QLabel("配额大小(MB):"), 0, 2)
        self.quota_size_spin = QSpinBox()
        self.quota_size_spin.setRange(1, 1024 * 1024)  # 1MB - 1TB
        quota_layout.addWidget(self.quota_size_spin, 0, 3)
        
        quota_group.setLayout(quota_layout)
        layout.addWidget(quota_group)
        
        # 压缩设置组
        compression_group = QGroupBox("压缩设置")
        compression_layout = QGridLayout()
        
        # 启用压缩
        self.enable_compression_check = QCheckBox("启用压缩")
        compression_layout.addWidget(self.enable_compression_check, 0, 0)
        
        # 压缩级别
        compression_layout.addWidget(QLabel("压缩级别:"), 0, 2)
        self.compression_level_spin = QSpinBox()
        self.compression_level_spin.setRange(1, 9)
        compression_layout.addWidget(self.compression_level_spin, 0, 3)
        
        compression_group.setLayout(compression_layout)
        layout.addWidget(compression_group)
        
        # 自定义属性组
        properties_group = QGroupBox("自定义属性")
        properties_layout = QVBoxLayout()
        
        properties_layout.addWidget(QLabel("自定义属性列表 (每行一个):"))
        self.custom_properties_edit = QTextEdit()
        self.custom_properties_edit.setMaximumHeight(80)
        self.custom_properties_edit.setPlaceholderText("例如:\nauthor\ncreated_by\nproject")
        properties_layout.addWidget(self.custom_properties_edit)
        
        properties_group.setLayout(properties_layout)
        layout.addWidget(properties_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_config(self):
        """加载配置到界面"""
        self.enabled_check.setChecked(self.config.enabled)
        self.port_spin.setValue(self.config.port)
        self.bind_address_edit.setText(self.config.bind_address)
        self.path_prefix_edit.setText(self.config.path_prefix)
        self.max_connections_spin.setValue(self.config.max_connections)
        self.max_depth_spin.setValue(self.config.max_depth)
        
        self.enable_locks_check.setChecked(self.config.enable_locks)
        self.lock_timeout_spin.setValue(self.config.lock_timeout)
        self.enable_versioning_check.setChecked(self.config.enable_versioning)
        self.enable_properties_check.setChecked(self.config.enable_properties)
        
        self.enable_quota_check.setChecked(self.config.enable_quota)
        self.quota_size_spin.setValue(self.config.quota_size // (1024 * 1024))
        
        self.enable_compression_check.setChecked(self.config.enable_compression)
        self.compression_level_spin.setValue(self.config.compression_level)
        
        self.custom_properties_edit.setPlainText('\n'.join(self.config.custom_properties))
    
    def save_config(self):
        """保存界面配置"""
        self.config.enabled = self.enabled_check.isChecked()
        self.config.port = self.port_spin.value()
        self.config.bind_address = self.bind_address_edit.text()
        self.config.path_prefix = self.path_prefix_edit.text()
        self.config.max_connections = self.max_connections_spin.value()
        self.config.max_depth = self.max_depth_spin.value()
        
        self.config.enable_locks = self.enable_locks_check.isChecked()
        self.config.lock_timeout = self.lock_timeout_spin.value()
        self.config.enable_versioning = self.enable_versioning_check.isChecked()
        self.config.enable_properties = self.enable_properties_check.isChecked()
        
        self.config.enable_quota = self.enable_quota_check.isChecked()
        self.config.quota_size = self.quota_size_spin.value() * 1024 * 1024
        
        self.config.enable_compression = self.enable_compression_check.isChecked()
        self.config.compression_level = self.compression_level_spin.value()
        
        # 解析自定义属性
        properties_text = self.custom_properties_edit.toPlainText().strip()
        if properties_text:
            self.config.custom_properties = [
                prop.strip() for prop in properties_text.split('\n') 
                if prop.strip()
            ]
        else:
            self.config.custom_properties = []


class WebDAVProtocol(BaseProtocol):
    """WebDAV协议实现"""
    
    def __init__(self):
        super().__init__("webdav")
        self.config = WebDAVConfig()
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return "WebDAV"
    
    def get_description(self) -> str:
        """获取协议描述"""
        return "基于HTTP的分布式创作和版本控制协议，支持远程文件编辑和协作"
    
    def get_default_port(self) -> int:
        """获取默认端口"""
        return 8080
    
    def get_config_widget(self, parent=None) -> QWidget:
        """获取配置界面组件"""
        return WebDAVConfigWidget(self.config, parent)
    
    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config.enabled:
            return []
        
        args = []
        
        # 启用WebDAV服务器
        args.append('--webdav')
        
        # WebDAV端口
        if self.config.port != 8080:
            args.extend(['--webdav-port', str(self.config.port)])
        
        # 路径前缀
        if self.config.path_prefix != "/webdav":
            args.extend(['--webdav-prefix', self.config.path_prefix])
        
        # 最大深度
        if self.config.max_depth != 10:
            args.extend(['--webdav-max-depth', str(self.config.max_depth)])
        
        # 锁定设置
        if not self.config.enable_locks:
            args.append('--webdav-no-locks')
        elif self.config.lock_timeout != 3600:
            args.extend(['--webdav-lock-timeout', str(self.config.lock_timeout)])
        
        # 版本控制
        if self.config.enable_versioning:
            args.append('--webdav-versioning')
        
        # 自定义属性
        if not self.config.enable_properties:
            args.append('--webdav-no-props')
        
        for prop in self.config.custom_properties:
            args.extend(['--webdav-prop', prop])
        
        # 配额设置
        if self.config.enable_quota:
            args.extend(['--webdav-quota', str(self.config.quota_size)])
        
        # 压缩设置
        if not self.config.enable_compression:
            args.append('--webdav-no-compression')
        elif self.config.compression_level != 6:
            args.extend(['--webdav-compression-level', str(self.config.compression_level)])
        
        return args
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 检查端口范围
        if not (1 <= self.config.port <= 65535):
            errors.append(f"WebDAV端口 {self.config.port} 超出有效范围 (1-65535)")
        
        # 检查路径前缀
        if not self.config.path_prefix.startswith('/'):
            errors.append("路径前缀必须以 '/' 开头")
        
        # 检查锁定超时
        if self.config.enable_locks and self.config.lock_timeout < 60:
            errors.append("锁定超时时间不能少于60秒")
        
        # 检查最大深度
        if self.config.max_depth < 1:
            errors.append("最大深度必须大于0")
        
        # 检查配额大小
        if self.config.enable_quota and self.config.quota_size < 1024 * 1024:
            errors.append("配额大小不能少于1MB")
        
        # 检查压缩级别
        if self.config.enable_compression and not (1 <= self.config.compression_level <= 9):
            errors.append("压缩级别必须在1-9之间")
        
        # 检查绑定地址
        if self.config.bind_address:
            try:
                import ipaddress
                ipaddress.ip_address(self.config.bind_address)
            except ValueError:
                if self.config.bind_address not in ["::", "0.0.0.0"]:
                    errors.append(f"无效的绑定地址: {self.config.bind_address}")
        
        return len(errors) == 0, errors
    
    def get_supported_features(self) -> List[str]:
        """获取支持的功能特性"""
        return [
            "远程文件编辑",
            "文件锁定机制",
            "版本控制",
            "自定义属性",
            "目录浏览",
            "文件上传下载",
            "批量操作",
            "存储配额管理",
            "压缩传输",
            "用户认证",
            "权限控制",
            "协作编辑支持"
        ]
