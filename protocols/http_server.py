"""
HTTP/HTTPS 协议实现
CopyParty 的主要协议
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QLineEdit, QSpinBox, 
                             QCheckBox, QComboBox)

from .base_protocol import BaseProtocol, ProtocolConfig


class HTTPConfig(ProtocolConfig):
    """HTTP协议配置"""
    
    def __init__(self):
        super().__init__()
        self.port = 3923
        self.https_only = False
        self.http_only = False
        self.cert_path = ""
        self.ssl_versions = ""
        self.ciphers = ""
        self.compression = True
        self.keep_alive = True
        self.max_request_size = 100 * 1024 * 1024  # 100MB
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'https_only': self.https_only,
            'http_only': self.http_only,
            'cert_path': self.cert_path,
            'ssl_versions': self.ssl_versions,
            'ciphers': self.ciphers,
            'compression': self.compression,
            'keep_alive': self.keep_alive,
            'max_request_size': self.max_request_size
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        super().from_dict(data)
        self.https_only = data.get('https_only', False)
        self.http_only = data.get('http_only', False)
        self.cert_path = data.get('cert_path', "")
        self.ssl_versions = data.get('ssl_versions', "")
        self.ciphers = data.get('ciphers', "")
        self.compression = data.get('compression', True)
        self.keep_alive = data.get('keep_alive', True)
        self.max_request_size = data.get('max_request_size', 100 * 1024 * 1024)


class HTTPConfigWidget(QWidget):
    """HTTP协议配置界面"""
    
    def __init__(self, config: HTTPConfig, parent=None):
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
        basic_layout.addWidget(QLabel("启用HTTP:"), 0, 0)
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
        
        # 最大连接数
        basic_layout.addWidget(QLabel("最大连接:"), 2, 0)
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 10000)
        basic_layout.addWidget(self.max_connections_spin, 2, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # SSL/TLS设置组
        ssl_group = QGroupBox("SSL/TLS 设置")
        ssl_layout = QGridLayout()
        
        # HTTP/HTTPS模式
        self.http_only_check = QCheckBox("仅HTTP")
        ssl_layout.addWidget(self.http_only_check, 0, 0)
        
        self.https_only_check = QCheckBox("仅HTTPS")
        ssl_layout.addWidget(self.https_only_check, 0, 1)
        
        # 证书路径
        ssl_layout.addWidget(QLabel("证书路径:"), 1, 0)
        self.cert_path_edit = QLineEdit()
        ssl_layout.addWidget(self.cert_path_edit, 1, 1, 1, 2)
        
        # SSL版本
        ssl_layout.addWidget(QLabel("SSL版本:"), 2, 0)
        self.ssl_versions_edit = QLineEdit()
        ssl_layout.addWidget(self.ssl_versions_edit, 2, 1, 1, 2)
        
        # 密码套件
        ssl_layout.addWidget(QLabel("密码套件:"), 3, 0)
        self.ciphers_edit = QLineEdit()
        ssl_layout.addWidget(self.ciphers_edit, 3, 1, 1, 2)
        
        ssl_group.setLayout(ssl_layout)
        layout.addWidget(ssl_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QGridLayout()
        
        # 压缩
        self.compression_check = QCheckBox("启用压缩")
        advanced_layout.addWidget(self.compression_check, 0, 0)
        
        # Keep-Alive
        self.keep_alive_check = QCheckBox("Keep-Alive")
        advanced_layout.addWidget(self.keep_alive_check, 0, 1)
        
        # 最大请求大小
        advanced_layout.addWidget(QLabel("最大请求(MB):"), 1, 0)
        self.max_request_spin = QSpinBox()
        self.max_request_spin.setRange(1, 1024)
        advanced_layout.addWidget(self.max_request_spin, 1, 1)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_config(self):
        """加载配置到界面"""
        self.enabled_check.setChecked(self.config.enabled)
        self.port_spin.setValue(self.config.port)
        self.bind_address_edit.setText(self.config.bind_address)
        self.max_connections_spin.setValue(self.config.max_connections)
        
        self.http_only_check.setChecked(self.config.http_only)
        self.https_only_check.setChecked(self.config.https_only)
        self.cert_path_edit.setText(self.config.cert_path)
        self.ssl_versions_edit.setText(self.config.ssl_versions)
        self.ciphers_edit.setText(self.config.ciphers)
        
        self.compression_check.setChecked(self.config.compression)
        self.keep_alive_check.setChecked(self.config.keep_alive)
        self.max_request_spin.setValue(self.config.max_request_size // (1024 * 1024))
    
    def save_config(self):
        """保存界面配置"""
        self.config.enabled = self.enabled_check.isChecked()
        self.config.port = self.port_spin.value()
        self.config.bind_address = self.bind_address_edit.text()
        self.config.max_connections = self.max_connections_spin.value()
        
        self.config.http_only = self.http_only_check.isChecked()
        self.config.https_only = self.https_only_check.isChecked()
        self.config.cert_path = self.cert_path_edit.text()
        self.config.ssl_versions = self.ssl_versions_edit.text()
        self.config.ciphers = self.ciphers_edit.text()
        
        self.config.compression = self.compression_check.isChecked()
        self.config.keep_alive = self.keep_alive_check.isChecked()
        self.config.max_request_size = self.max_request_spin.value() * 1024 * 1024


class HTTPProtocol(BaseProtocol):
    """HTTP/HTTPS协议实现"""
    
    def __init__(self):
        super().__init__("http")
        self.config = HTTPConfig()
        self.config.enabled = True  # HTTP是默认启用的
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return "HTTP/HTTPS"
    
    def get_description(self) -> str:
        """获取协议描述"""
        return "CopyParty 的主要 Web 协议，支持文件上传下载和 Web 界面访问"
    
    def get_default_port(self) -> int:
        """获取默认端口"""
        return 3923
    
    def get_config_widget(self, parent=None) -> QWidget:
        """获取配置界面组件"""
        return HTTPConfigWidget(self.config, parent)
    
    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config.enabled:
            return []
        
        args = []
        
        # 端口设置
        if self.config.port != 3923:
            args.extend(['-p', str(self.config.port)])
        
        # 绑定地址
        if self.config.bind_address != "0.0.0.0":
            args.extend(['-i', self.config.bind_address])
        
        # 最大连接数
        if self.config.max_connections != 100:
            args.extend(['-nc', str(self.config.max_connections)])
        
        # HTTP/HTTPS模式
        if self.config.http_only:
            args.append('--http-only')
        elif self.config.https_only:
            args.append('--https-only')
        
        # SSL证书
        if self.config.cert_path:
            args.extend(['--cert', self.config.cert_path])
        
        # SSL版本
        if self.config.ssl_versions:
            args.extend(['--ssl-ver', self.config.ssl_versions])
        
        # 密码套件
        if self.config.ciphers:
            args.extend(['--ciphers', self.config.ciphers])
        
        return args
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 检查端口范围
        if not (1 <= self.config.port <= 65535):
            errors.append(f"端口 {self.config.port} 超出有效范围 (1-65535)")
        
        # 检查互斥选项
        if self.config.http_only and self.config.https_only:
            errors.append("HTTP-only 和 HTTPS-only 不能同时启用")
        
        # 检查证书文件
        if self.config.https_only and not self.config.cert_path:
            errors.append("HTTPS-only 模式需要指定证书文件")
        
        if self.config.cert_path:
            import os
            if not os.path.exists(self.config.cert_path):
                errors.append(f"证书文件不存在: {self.config.cert_path}")
        
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
            "文件上传下载",
            "Web 界面",
            "REST API",
            "WebSocket",
            "HTTP/2",
            "SSL/TLS 加密",
            "压缩传输",
            "断点续传",
            "多线程下载",
            "目录浏览",
            "文件预览",
            "用户认证",
            "权限控制"
        ]
