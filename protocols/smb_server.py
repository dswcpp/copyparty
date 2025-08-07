"""
SMB/CIFS 协议实现
Windows 网络共享协议
"""

import os
from typing import List, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QLineEdit, QSpinBox, 
                             QCheckBox, QComboBox, QTextEdit)

from .base_protocol import BaseProtocol, ProtocolConfig


class SMBConfig(ProtocolConfig):
    """SMB协议配置"""
    
    def __init__(self):
        super().__init__()
        self.port = 445
        self.enabled = False  # SMB默认禁用
        self.netbios_port = 139
        self.server_name = "COPYPARTY"
        self.workgroup = "WORKGROUP"
        self.server_string = "CopyParty SMB Server"
        self.enable_netbios = True
        self.enable_smb1 = False
        self.enable_smb2 = True
        self.enable_smb3 = True
        self.guest_access = False
        self.require_encryption = False
        self.max_protocol = "SMB3"
        self.min_protocol = "SMB2"
        self.shares = []  # 共享配置列表
        self.log_level = 1
        self.enable_oplocks = True
        self.enable_notify = True
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'netbios_port': self.netbios_port,
            'server_name': self.server_name,
            'workgroup': self.workgroup,
            'server_string': self.server_string,
            'enable_netbios': self.enable_netbios,
            'enable_smb1': self.enable_smb1,
            'enable_smb2': self.enable_smb2,
            'enable_smb3': self.enable_smb3,
            'guest_access': self.guest_access,
            'require_encryption': self.require_encryption,
            'max_protocol': self.max_protocol,
            'min_protocol': self.min_protocol,
            'shares': self.shares,
            'log_level': self.log_level,
            'enable_oplocks': self.enable_oplocks,
            'enable_notify': self.enable_notify
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        super().from_dict(data)
        self.netbios_port = data.get('netbios_port', 139)
        self.server_name = data.get('server_name', "COPYPARTY")
        self.workgroup = data.get('workgroup', "WORKGROUP")
        self.server_string = data.get('server_string', "CopyParty SMB Server")
        self.enable_netbios = data.get('enable_netbios', True)
        self.enable_smb1 = data.get('enable_smb1', False)
        self.enable_smb2 = data.get('enable_smb2', True)
        self.enable_smb3 = data.get('enable_smb3', True)
        self.guest_access = data.get('guest_access', False)
        self.require_encryption = data.get('require_encryption', False)
        self.max_protocol = data.get('max_protocol', "SMB3")
        self.min_protocol = data.get('min_protocol', "SMB2")
        self.shares = data.get('shares', [])
        self.log_level = data.get('log_level', 1)
        self.enable_oplocks = data.get('enable_oplocks', True)
        self.enable_notify = data.get('enable_notify', True)


class SMBConfigWidget(QWidget):
    """SMB协议配置界面"""
    
    def __init__(self, config: SMBConfig, parent=None):
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
        basic_layout.addWidget(QLabel("启用SMB:"), 0, 0)
        self.enabled_check = QCheckBox()
        basic_layout.addWidget(self.enabled_check, 0, 1)
        
        # SMB端口
        basic_layout.addWidget(QLabel("SMB端口:"), 0, 2)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        basic_layout.addWidget(self.port_spin, 0, 3)
        
        # NetBIOS端口
        basic_layout.addWidget(QLabel("NetBIOS端口:"), 1, 0)
        self.netbios_port_spin = QSpinBox()
        self.netbios_port_spin.setRange(1, 65535)
        basic_layout.addWidget(self.netbios_port_spin, 1, 1)
        
        # 启用NetBIOS
        self.enable_netbios_check = QCheckBox("启用NetBIOS")
        basic_layout.addWidget(self.enable_netbios_check, 1, 2, 1, 2)
        
        # 绑定地址
        basic_layout.addWidget(QLabel("绑定地址:"), 2, 0)
        self.bind_address_edit = QLineEdit()
        basic_layout.addWidget(self.bind_address_edit, 2, 1, 1, 3)
        
        # 最大连接数
        basic_layout.addWidget(QLabel("最大连接:"), 3, 0)
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 1000)
        basic_layout.addWidget(self.max_connections_spin, 3, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 服务器标识组
        identity_group = QGroupBox("服务器标识")
        identity_layout = QGridLayout()
        
        # 服务器名称
        identity_layout.addWidget(QLabel("服务器名称:"), 0, 0)
        self.server_name_edit = QLineEdit()
        self.server_name_edit.setPlaceholderText("COPYPARTY")
        identity_layout.addWidget(self.server_name_edit, 0, 1)
        
        # 工作组
        identity_layout.addWidget(QLabel("工作组:"), 0, 2)
        self.workgroup_edit = QLineEdit()
        self.workgroup_edit.setPlaceholderText("WORKGROUP")
        identity_layout.addWidget(self.workgroup_edit, 0, 3)
        
        # 服务器描述
        identity_layout.addWidget(QLabel("服务器描述:"), 1, 0)
        self.server_string_edit = QLineEdit()
        self.server_string_edit.setPlaceholderText("CopyParty SMB Server")
        identity_layout.addWidget(self.server_string_edit, 1, 1, 1, 3)
        
        identity_group.setLayout(identity_layout)
        layout.addWidget(identity_group)
        
        # 协议版本组
        protocol_group = QGroupBox("协议版本")
        protocol_layout = QGridLayout()
        
        # SMB版本支持
        self.enable_smb1_check = QCheckBox("SMB 1.0 (不推荐)")
        protocol_layout.addWidget(self.enable_smb1_check, 0, 0)
        
        self.enable_smb2_check = QCheckBox("SMB 2.0")
        protocol_layout.addWidget(self.enable_smb2_check, 0, 1)
        
        self.enable_smb3_check = QCheckBox("SMB 3.0")
        protocol_layout.addWidget(self.enable_smb3_check, 0, 2)
        
        # 协议范围
        protocol_layout.addWidget(QLabel("最小协议:"), 1, 0)
        self.min_protocol_combo = QComboBox()
        self.min_protocol_combo.addItems(["SMB1", "SMB2", "SMB3"])
        protocol_layout.addWidget(self.min_protocol_combo, 1, 1)
        
        protocol_layout.addWidget(QLabel("最大协议:"), 1, 2)
        self.max_protocol_combo = QComboBox()
        self.max_protocol_combo.addItems(["SMB1", "SMB2", "SMB3"])
        protocol_layout.addWidget(self.max_protocol_combo, 1, 3)
        
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        # 安全设置组
        security_group = QGroupBox("安全设置")
        security_layout = QGridLayout()
        
        # 访客访问
        self.guest_access_check = QCheckBox("允许访客访问")
        security_layout.addWidget(self.guest_access_check, 0, 0)
        
        # 要求加密
        self.require_encryption_check = QCheckBox("要求加密传输")
        security_layout.addWidget(self.require_encryption_check, 0, 1)
        
        # 日志级别
        security_layout.addWidget(QLabel("日志级别:"), 1, 0)
        self.log_level_spin = QSpinBox()
        self.log_level_spin.setRange(0, 10)
        security_layout.addWidget(self.log_level_spin, 1, 1)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QGridLayout()
        
        # 机会锁
        self.enable_oplocks_check = QCheckBox("启用机会锁 (Oplocks)")
        advanced_layout.addWidget(self.enable_oplocks_check, 0, 0)
        
        # 变更通知
        self.enable_notify_check = QCheckBox("启用变更通知")
        advanced_layout.addWidget(self.enable_notify_check, 0, 1)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # 共享配置组
        shares_group = QGroupBox("共享配置")
        shares_layout = QVBoxLayout()
        
        shares_layout.addWidget(QLabel("共享列表 (格式: 名称:路径:权限):"))
        self.shares_edit = QTextEdit()
        self.shares_edit.setMaximumHeight(100)
        self.shares_edit.setPlaceholderText("例如:\nshare1:/path/to/share1:rw\nshare2:/path/to/share2:r")
        shares_layout.addWidget(self.shares_edit)
        
        shares_group.setLayout(shares_layout)
        layout.addWidget(shares_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_config(self):
        """加载配置到界面"""
        self.enabled_check.setChecked(self.config.enabled)
        self.port_spin.setValue(self.config.port)
        self.netbios_port_spin.setValue(self.config.netbios_port)
        self.bind_address_edit.setText(self.config.bind_address)
        self.max_connections_spin.setValue(self.config.max_connections)
        
        self.server_name_edit.setText(self.config.server_name)
        self.workgroup_edit.setText(self.config.workgroup)
        self.server_string_edit.setText(self.config.server_string)
        self.enable_netbios_check.setChecked(self.config.enable_netbios)
        
        self.enable_smb1_check.setChecked(self.config.enable_smb1)
        self.enable_smb2_check.setChecked(self.config.enable_smb2)
        self.enable_smb3_check.setChecked(self.config.enable_smb3)
        self.min_protocol_combo.setCurrentText(self.config.min_protocol)
        self.max_protocol_combo.setCurrentText(self.config.max_protocol)
        
        self.guest_access_check.setChecked(self.config.guest_access)
        self.require_encryption_check.setChecked(self.config.require_encryption)
        self.log_level_spin.setValue(self.config.log_level)
        
        self.enable_oplocks_check.setChecked(self.config.enable_oplocks)
        self.enable_notify_check.setChecked(self.config.enable_notify)
        
        # 加载共享配置
        shares_text = '\n'.join([f"{share['name']}:{share['path']}:{share['permissions']}" 
                                for share in self.config.shares])
        self.shares_edit.setPlainText(shares_text)
    
    def save_config(self):
        """保存界面配置"""
        self.config.enabled = self.enabled_check.isChecked()
        self.config.port = self.port_spin.value()
        self.config.netbios_port = self.netbios_port_spin.value()
        self.config.bind_address = self.bind_address_edit.text()
        self.config.max_connections = self.max_connections_spin.value()
        
        self.config.server_name = self.server_name_edit.text()
        self.config.workgroup = self.workgroup_edit.text()
        self.config.server_string = self.server_string_edit.text()
        self.config.enable_netbios = self.enable_netbios_check.isChecked()
        
        self.config.enable_smb1 = self.enable_smb1_check.isChecked()
        self.config.enable_smb2 = self.enable_smb2_check.isChecked()
        self.config.enable_smb3 = self.enable_smb3_check.isChecked()
        self.config.min_protocol = self.min_protocol_combo.currentText()
        self.config.max_protocol = self.max_protocol_combo.currentText()
        
        self.config.guest_access = self.guest_access_check.isChecked()
        self.config.require_encryption = self.require_encryption_check.isChecked()
        self.config.log_level = self.log_level_spin.value()
        
        self.config.enable_oplocks = self.enable_oplocks_check.isChecked()
        self.config.enable_notify = self.enable_notify_check.isChecked()
        
        # 解析共享配置
        shares_text = self.shares_edit.toPlainText().strip()
        shares = []
        if shares_text:
            for line in shares_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        shares.append({
                            'name': parts[0],
                            'path': parts[1],
                            'permissions': parts[2]
                        })
        self.config.shares = shares


class SMBProtocol(BaseProtocol):
    """SMB/CIFS协议实现"""
    
    def __init__(self):
        super().__init__("smb")
        self.config = SMBConfig()
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return "SMB/CIFS"
    
    def get_description(self) -> str:
        """获取协议描述"""
        return "Windows 网络共享协议，支持文件和打印机共享"
    
    def get_default_port(self) -> int:
        """获取默认端口"""
        return 445
    
    def get_config_widget(self, parent=None) -> QWidget:
        """获取配置界面组件"""
        return SMBConfigWidget(self.config, parent)
    
    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config.enabled:
            return []
        
        args = []
        
        # 启用SMB服务器
        args.append('--smb')
        
        # SMB端口
        if self.config.port != 445:
            args.extend(['--smb-port', str(self.config.port)])
        
        # NetBIOS设置
        if self.config.enable_netbios:
            args.append('--smb-netbios')
            if self.config.netbios_port != 139:
                args.extend(['--smb-netbios-port', str(self.config.netbios_port)])
        
        # 服务器标识
        if self.config.server_name != "COPYPARTY":
            args.extend(['--smb-server-name', self.config.server_name])
        
        if self.config.workgroup != "WORKGROUP":
            args.extend(['--smb-workgroup', self.config.workgroup])
        
        if self.config.server_string != "CopyParty SMB Server":
            args.extend(['--smb-server-string', self.config.server_string])
        
        # 协议版本
        if not self.config.enable_smb1:
            args.append('--smb-no-smb1')
        
        if not self.config.enable_smb2:
            args.append('--smb-no-smb2')
        
        if not self.config.enable_smb3:
            args.append('--smb-no-smb3')
        
        if self.config.min_protocol != "SMB2":
            args.extend(['--smb-min-protocol', self.config.min_protocol])
        
        if self.config.max_protocol != "SMB3":
            args.extend(['--smb-max-protocol', self.config.max_protocol])
        
        # 安全设置
        if self.config.guest_access:
            args.append('--smb-guest')
        
        if self.config.require_encryption:
            args.append('--smb-encrypt')
        
        if self.config.log_level != 1:
            args.extend(['--smb-log-level', str(self.config.log_level)])
        
        # 高级设置
        if not self.config.enable_oplocks:
            args.append('--smb-no-oplocks')
        
        if not self.config.enable_notify:
            args.append('--smb-no-notify')
        
        # 共享配置
        for share in self.config.shares:
            share_spec = f"{share['name']}:{share['path']}:{share['permissions']}"
            args.extend(['--smb-share', share_spec])
        
        return args
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        
        # 检查端口范围
        if not (1 <= self.config.port <= 65535):
            errors.append(f"SMB端口 {self.config.port} 超出有效范围 (1-65535)")
        
        if not (1 <= self.config.netbios_port <= 65535):
            errors.append(f"NetBIOS端口 {self.config.netbios_port} 超出有效范围 (1-65535)")
        
        # 检查服务器名称
        if not self.config.server_name or len(self.config.server_name) > 15:
            errors.append("服务器名称不能为空且不能超过15个字符")
        
        # 检查工作组名称
        if not self.config.workgroup or len(self.config.workgroup) > 15:
            errors.append("工作组名称不能为空且不能超过15个字符")
        
        # 检查协议版本一致性
        if self.config.min_protocol == "SMB3" and not self.config.enable_smb3:
            errors.append("最小协议设置为SMB3但SMB3未启用")
        
        if self.config.max_protocol == "SMB1" and not self.config.enable_smb1:
            errors.append("最大协议设置为SMB1但SMB1未启用")
        
        # 检查共享配置
        for i, share in enumerate(self.config.shares):
            if not share.get('name'):
                errors.append(f"共享 {i+1} 缺少名称")
            
            if not share.get('path'):
                errors.append(f"共享 {i+1} 缺少路径")
            
            path = share.get('path', '')
            if path and not os.path.exists(path):
                errors.append(f"共享 {i+1} 路径不存在: {path}")
            
            permissions = share.get('permissions', '')
            if permissions and permissions not in ['r', 'rw', 'rwm', 'rwmd']:
                errors.append(f"共享 {i+1} 权限无效: {permissions}")
        
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
            "文件共享",
            "目录浏览",
            "文件上传下载",
            "Windows 网络邻居",
            "NetBIOS 名称解析",
            "SMB 1.0/2.0/3.0 协议",
            "访客访问",
            "用户认证",
            "加密传输",
            "机会锁 (Oplocks)",
            "变更通知",
            "多共享支持",
            "权限控制"
        ]
