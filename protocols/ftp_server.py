"""
FTP/FTPS 协议实现
传统文件传输协议
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QLineEdit, QSpinBox, 
                             QCheckBox, QComboBox)

from .base_protocol import BaseProtocol, ProtocolConfig


class FTPConfig(ProtocolConfig):
    """FTP协议配置"""
    
    def __init__(self):
        super().__init__()
        self.port = 21
        self.enabled = False  # FTP默认禁用
        self.passive_mode = True
        self.passive_port_range = "20000-21000"
        self.ftps_enabled = False
        self.ftps_implicit = False
        self.cert_path = ""
        self.anonymous_login = False
        self.max_login_attempts = 3
        self.idle_timeout = 300  # 5分钟
        self.data_timeout = 120  # 2分钟
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'passive_mode': self.passive_mode,
            'passive_port_range': self.passive_port_range,
            'ftps_enabled': self.ftps_enabled,
            'ftps_implicit': self.ftps_implicit,
            'cert_path': self.cert_path,
            'anonymous_login': self.anonymous_login,
            'max_login_attempts': self.max_login_attempts,
            'idle_timeout': self.idle_timeout,
            'data_timeout': self.data_timeout
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        super().from_dict(data)
        self.passive_mode = data.get('passive_mode', True)
        self.passive_port_range = data.get('passive_port_range', "20000-21000")
        self.ftps_enabled = data.get('ftps_enabled', False)
        self.ftps_implicit = data.get('ftps_implicit', False)
        self.cert_path = data.get('cert_path', "")
        self.anonymous_login = data.get('anonymous_login', False)
        self.max_login_attempts = data.get('max_login_attempts', 3)
        self.idle_timeout = data.get('idle_timeout', 300)
        self.data_timeout = data.get('data_timeout', 120)


class FTPConfigWidget(QWidget):
    """FTP协议配置界面"""
    
    def __init__(self, config: FTPConfig, parent=None):
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
        basic_layout.addWidget(QLabel("启用FTP:"), 0, 0)
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
        self.max_connections_spin.setRange(1, 1000)
        basic_layout.addWidget(self.max_connections_spin, 2, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 传输模式组
        mode_group = QGroupBox("传输模式")
        mode_layout = QGridLayout()
        
        # 被动模式
        self.passive_mode_check = QCheckBox("被动模式 (PASV)")
        mode_layout.addWidget(self.passive_mode_check, 0, 0, 1, 2)
        
        # 被动端口范围
        mode_layout.addWidget(QLabel("被动端口范围:"), 1, 0)
        self.passive_port_range_edit = QLineEdit()
        self.passive_port_range_edit.setPlaceholderText("例如: 20000-21000")
        mode_layout.addWidget(self.passive_port_range_edit, 1, 1)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # FTPS设置组
        ftps_group = QGroupBox("FTPS (FTP over SSL/TLS)")
        ftps_layout = QGridLayout()
        
        # 启用FTPS
        self.ftps_enabled_check = QCheckBox("启用FTPS")
        ftps_layout.addWidget(self.ftps_enabled_check, 0, 0)
        
        # 隐式FTPS
        self.ftps_implicit_check = QCheckBox("隐式FTPS")
        ftps_layout.addWidget(self.ftps_implicit_check, 0, 1)
        
        # 证书路径
        ftps_layout.addWidget(QLabel("证书路径:"), 1, 0)
        self.cert_path_edit = QLineEdit()
        ftps_layout.addWidget(self.cert_path_edit, 1, 1)
        
        ftps_group.setLayout(ftps_layout)
        layout.addWidget(ftps_group)
        
        # 安全设置组
        security_group = QGroupBox("安全设置")
        security_layout = QGridLayout()
        
        # 匿名登录
        self.anonymous_login_check = QCheckBox("允许匿名登录")
        security_layout.addWidget(self.anonymous_login_check, 0, 0)
        
        # 最大登录尝试次数
        security_layout.addWidget(QLabel("最大登录尝试:"), 0, 2)
        self.max_login_attempts_spin = QSpinBox()
        self.max_login_attempts_spin.setRange(1, 10)
        security_layout.addWidget(self.max_login_attempts_spin, 0, 3)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # 超时设置组
        timeout_group = QGroupBox("超时设置")
        timeout_layout = QGridLayout()
        
        # 空闲超时
        timeout_layout.addWidget(QLabel("空闲超时(秒):"), 0, 0)
        self.idle_timeout_spin = QSpinBox()
        self.idle_timeout_spin.setRange(30, 3600)
        timeout_layout.addWidget(self.idle_timeout_spin, 0, 1)
        
        # 数据传输超时
        timeout_layout.addWidget(QLabel("数据超时(秒):"), 0, 2)
        self.data_timeout_spin = QSpinBox()
        self.data_timeout_spin.setRange(30, 600)
        timeout_layout.addWidget(self.data_timeout_spin, 0, 3)
        
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_config(self):
        """加载配置到界面"""
        self.enabled_check.setChecked(self.config.enabled)
        self.port_spin.setValue(self.config.port)
        self.bind_address_edit.setText(self.config.bind_address)
        self.max_connections_spin.setValue(self.config.max_connections)
        
        self.passive_mode_check.setChecked(self.config.passive_mode)
        self.passive_port_range_edit.setText(self.config.passive_port_range)
        
        self.ftps_enabled_check.setChecked(self.config.ftps_enabled)
        self.ftps_implicit_check.setChecked(self.config.ftps_implicit)
        self.cert_path_edit.setText(self.config.cert_path)
        
        self.anonymous_login_check.setChecked(self.config.anonymous_login)
        self.max_login_attempts_spin.setValue(self.config.max_login_attempts)
        
        self.idle_timeout_spin.setValue(self.config.idle_timeout)
        self.data_timeout_spin.setValue(self.config.data_timeout)
    
    def save_config(self):
        """保存界面配置"""
        self.config.enabled = self.enabled_check.isChecked()
        self.config.port = self.port_spin.value()
        self.config.bind_address = self.bind_address_edit.text()
        self.config.max_connections = self.max_connections_spin.value()
        
        self.config.passive_mode = self.passive_mode_check.isChecked()
        self.config.passive_port_range = self.passive_port_range_edit.text()
        
        self.config.ftps_enabled = self.ftps_enabled_check.isChecked()
        self.config.ftps_implicit = self.ftps_implicit_check.isChecked()
        self.config.cert_path = self.cert_path_edit.text()
        
        self.config.anonymous_login = self.anonymous_login_check.isChecked()
        self.config.max_login_attempts = self.max_login_attempts_spin.value()
        
        self.config.idle_timeout = self.idle_timeout_spin.value()
        self.config.data_timeout = self.data_timeout_spin.value()


class FTPProtocol(BaseProtocol):
    """FTP/FTPS协议实现"""
    
    def __init__(self):
        super().__init__("ftp")
        self.config = FTPConfig()
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return "FTP/FTPS"
    
    def get_description(self) -> str:
        """获取协议描述"""
        return "传统的文件传输协议，支持 FTP 和加密的 FTPS"
    
    def get_default_port(self) -> int:
        """获取默认端口"""
        return 21
    
    def get_config_widget(self, parent=None) -> QWidget:
        """获取配置界面组件"""
        return FTPConfigWidget(self.config, parent)
    
    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config.enabled:
            return []
        
        args = []
        
        # 启用FTP服务器
        args.append('--ftp')
        
        # FTP端口
        if self.config.port != 21:
            args.extend(['--ftp-port', str(self.config.port)])
        
        # 被动模式端口范围
        if self.config.passive_mode and self.config.passive_port_range:
            args.extend(['--ftp-pasv-range', self.config.passive_port_range])
        
        # FTPS设置
        if self.config.ftps_enabled:
            if self.config.ftps_implicit:
                args.append('--ftps')
            else:
                args.append('--ftps-explicit')
            
            if self.config.cert_path:
                args.extend(['--ftp-cert', self.config.cert_path])
        
        # 匿名登录
        if self.config.anonymous_login:
            args.append('--ftp-anon')
        
        # 超时设置
        if self.config.idle_timeout != 300:
            args.extend(['--ftp-idle-timeout', str(self.config.idle_timeout)])
        
        if self.config.data_timeout != 120:
            args.extend(['--ftp-data-timeout', str(self.config.data_timeout)])
        
        return args
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 检查端口范围
        if not (1 <= self.config.port <= 65535):
            errors.append(f"FTP端口 {self.config.port} 超出有效范围 (1-65535)")
        
        # 检查被动端口范围
        if self.config.passive_mode and self.config.passive_port_range:
            try:
                if '-' in self.config.passive_port_range:
                    start, end = self.config.passive_port_range.split('-')
                    start_port = int(start.strip())
                    end_port = int(end.strip())
                    
                    if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                        errors.append("被动端口范围超出有效范围 (1-65535)")
                    
                    if start_port >= end_port:
                        errors.append("被动端口范围起始端口应小于结束端口")
                else:
                    errors.append("被动端口范围格式错误，应为 'start-end'")
            except ValueError:
                errors.append("被动端口范围包含无效的端口号")
        
        # 检查FTPS证书
        if self.config.ftps_enabled and self.config.cert_path:
            import os
            if not os.path.exists(self.config.cert_path):
                errors.append(f"FTPS证书文件不存在: {self.config.cert_path}")
        
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
            "目录浏览",
            "被动模式传输",
            "主动模式传输",
            "FTPS 加密传输",
            "匿名访问",
            "用户认证",
            "断点续传",
            "多连接传输",
            "目录递归操作",
            "文件权限管理"
        ]
