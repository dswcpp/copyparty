#!/usr/bin/env python3
"""
CopyParty 完整界面组件 - 严格遵循源码
基于 copyparty/__main__.py 中的所有配置选项
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import List, Dict, Any
import os

from copyparty_complete_config import (
    CopyPartyCompleteConfig, GeneralConfig, NetworkConfig, TLSConfig, CertConfig,
    AuthConfig, PasswordChangeConfig, QRConfig, ZeroconfConfig, MDNSConfig, SSDPConfig,
    FilesystemConfig, ShareConfig, UploadConfig, DatabaseConfig, ThumbnailConfig,
    TranscodingConfig, ProtocolConfig, SecurityConfig, UIConfig, LoggingConfig
)


class GeneralConfigWidget(QWidget):
    """通用配置界面 - 对应 add_general()"""
    
    def __init__(self, config: CopyPartyCompleteConfig):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 基本选项组
        basic_group = QGroupBox("基本选项")
        basic_layout = QFormLayout()
        
        # 配置文件
        config_files_layout = QVBoxLayout()
        self.config_files_list = QListWidget()
        config_files_btn_layout = QHBoxLayout()
        self.add_config_btn = QPushButton("添加配置文件")
        self.remove_config_btn = QPushButton("移除配置文件")
        self.add_config_btn.clicked.connect(self.add_config_file)
        self.remove_config_btn.clicked.connect(self.remove_config_file)
        config_files_btn_layout.addWidget(self.add_config_btn)
        config_files_btn_layout.addWidget(self.remove_config_btn)
        config_files_btn_layout.addStretch()
        config_files_layout.addWidget(self.config_files_list)
        config_files_layout.addLayout(config_files_btn_layout)
        basic_layout.addRow("配置文件 (-c):", config_files_layout)
        
        # 最大客户端数
        self.max_clients_spin = QSpinBox()
        self.max_clients_spin.setRange(1, 65535)
        self.max_clients_spin.setValue(1024)
        basic_layout.addRow("最大客户端数 (-nc):", self.max_clients_spin)
        
        # CPU 核心数
        self.cpu_cores_spin = QSpinBox()
        self.cpu_cores_spin.setRange(1, 64)
        self.cpu_cores_spin.setValue(1)
        basic_layout.addRow("CPU 核心数 (-j):", self.cpu_cores_spin)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 账户和卷组
        accounts_group = QGroupBox("账户和卷")
        accounts_layout = QFormLayout()
        
        # 账户列表
        accounts_list_layout = QVBoxLayout()
        self.accounts_list = QListWidget()
        accounts_btn_layout = QHBoxLayout()
        self.add_account_btn = QPushButton("添加账户")
        self.remove_account_btn = QPushButton("移除账户")
        self.add_account_btn.clicked.connect(self.add_account)
        self.remove_account_btn.clicked.connect(self.remove_account)
        accounts_btn_layout.addWidget(self.add_account_btn)
        accounts_btn_layout.addWidget(self.remove_account_btn)
        accounts_btn_layout.addStretch()
        accounts_list_layout.addWidget(self.accounts_list)
        accounts_list_layout.addLayout(accounts_btn_layout)
        accounts_layout.addRow("账户 (-a):", accounts_list_layout)
        
        # 卷列表
        volumes_list_layout = QVBoxLayout()
        self.volumes_list = QListWidget()
        volumes_btn_layout = QHBoxLayout()
        self.add_volume_btn = QPushButton("添加卷")
        self.remove_volume_btn = QPushButton("移除卷")
        self.add_volume_btn.clicked.connect(self.add_volume)
        self.remove_volume_btn.clicked.connect(self.remove_volume)
        volumes_btn_layout.addWidget(self.add_volume_btn)
        volumes_btn_layout.addWidget(self.remove_volume_btn)
        volumes_btn_layout.addStretch()
        volumes_list_layout.addWidget(self.volumes_list)
        volumes_list_layout.addLayout(volumes_btn_layout)
        accounts_layout.addRow("卷 (-v):", volumes_list_layout)
        
        # 组列表
        groups_list_layout = QVBoxLayout()
        self.groups_list = QListWidget()
        groups_btn_layout = QHBoxLayout()
        self.add_group_btn = QPushButton("添加组")
        self.remove_group_btn = QPushButton("移除组")
        self.add_group_btn.clicked.connect(self.add_group)
        self.remove_group_btn.clicked.connect(self.remove_group)
        groups_btn_layout.addWidget(self.add_group_btn)
        groups_btn_layout.addWidget(self.remove_group_btn)
        groups_btn_layout.addStretch()
        groups_list_layout.addWidget(self.groups_list)
        groups_list_layout.addLayout(groups_btn_layout)
        accounts_layout.addRow("组 (--grp):", groups_list_layout)
        
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)
        
        # 功能选项组
        features_group = QGroupBox("功能选项")
        features_layout = QFormLayout()
        
        # 启用点文件
        self.enable_dots_cb = QCheckBox("启用点文件显示 (-ed)")
        features_layout.addRow("", self.enable_dots_cb)
        
        # URL 格式
        self.urlform_edit = QLineEdit()
        self.urlform_edit.setText("print,xm")
        features_layout.addRow("URL 格式 (--urlform):", self.urlform_edit)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 显示设置组
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout()
        
        # 窗口标题
        self.window_title_edit = QLineEdit()
        self.window_title_edit.setText("cpp @ $pub")
        display_layout.addRow("窗口标题 (--wintitle):", self.window_title_edit)
        
        # 服务器名称
        self.server_name_edit = QLineEdit()
        self.server_name_edit.setText("copyparty")
        display_layout.addRow("服务器名称 (--name):", self.server_name_edit)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # MIME 类型组
        mime_group = QGroupBox("MIME 类型")
        mime_layout = QFormLayout()
        
        # MIME 映射
        mime_list_layout = QVBoxLayout()
        self.mime_list = QListWidget()
        mime_btn_layout = QHBoxLayout()
        self.add_mime_btn = QPushButton("添加 MIME 映射")
        self.remove_mime_btn = QPushButton("移除 MIME 映射")
        self.add_mime_btn.clicked.connect(self.add_mime_mapping)
        self.remove_mime_btn.clicked.connect(self.remove_mime_mapping)
        mime_btn_layout.addWidget(self.add_mime_btn)
        mime_btn_layout.addWidget(self.remove_mime_btn)
        mime_btn_layout.addStretch()
        mime_list_layout.addWidget(self.mime_list)
        mime_list_layout.addLayout(mime_btn_layout)
        mime_layout.addRow("MIME 映射 (--mime):", mime_list_layout)
        
        # MIME 选项
        self.list_mimes_cb = QCheckBox("列出所有 MIME 类型 (--mimes)")
        mime_layout.addRow("", self.list_mimes_cb)
        
        self.expensive_mime_cb = QCheckBox("启用昂贵的 MIME 检测 (--rmagic)")
        mime_layout.addRow("", self.expensive_mime_cb)
        
        mime_group.setLayout(mime_layout)
        layout.addWidget(mime_group)
        
        # 信息选项组
        info_group = QGroupBox("信息选项")
        info_layout = QFormLayout()
        
        self.show_license_cb = QCheckBox("显示许可证 (--license)")
        info_layout.addRow("", self.show_license_cb)
        
        self.show_version_cb = QCheckBox("显示版本 (--version)")
        info_layout.addRow("", self.show_version_cb)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_config_file(self):
        """添加配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "配置文件 (*.conf *.cfg *.ini);;所有文件 (*)"
        )
        if file_path:
            self.config_files_list.addItem(file_path)
    
    def remove_config_file(self):
        """移除配置文件"""
        current_row = self.config_files_list.currentRow()
        if current_row >= 0:
            self.config_files_list.takeItem(current_row)
    
    def add_account(self):
        """添加账户"""
        account, ok = QInputDialog.getText(self, "添加账户", "账户格式 (username:password):")
        if ok and account.strip():
            self.accounts_list.addItem(account.strip())
    
    def remove_account(self):
        """移除账户"""
        current_row = self.accounts_list.currentRow()
        if current_row >= 0:
            self.accounts_list.takeItem(current_row)
    
    def add_volume(self):
        """添加卷"""
        volume, ok = QInputDialog.getText(self, "添加卷", "卷格式 (path:alias:permissions):")
        if ok and volume.strip():
            self.volumes_list.addItem(volume.strip())
    
    def remove_volume(self):
        """移除卷"""
        current_row = self.volumes_list.currentRow()
        if current_row >= 0:
            self.volumes_list.takeItem(current_row)
    
    def add_group(self):
        """添加组"""
        group, ok = QInputDialog.getText(self, "添加组", "组格式 (groupname:members):")
        if ok and group.strip():
            self.groups_list.addItem(group.strip())
    
    def remove_group(self):
        """移除组"""
        current_row = self.groups_list.currentRow()
        if current_row >= 0:
            self.groups_list.takeItem(current_row)
    
    def add_mime_mapping(self):
        """添加 MIME 映射"""
        mapping, ok = QInputDialog.getText(self, "添加 MIME 映射", "映射格式 (extension:mime/type):")
        if ok and mapping.strip():
            self.mime_list.addItem(mapping.strip())
    
    def remove_mime_mapping(self):
        """移除 MIME 映射"""
        current_row = self.mime_list.currentRow()
        if current_row >= 0:
            self.mime_list.takeItem(current_row)
    
    def load_config(self):
        """加载配置"""
        general = self.config.general
        
        # 加载配置文件列表
        self.config_files_list.clear()
        for config_file in general.config_files:
            self.config_files_list.addItem(config_file)
        
        # 加载基本选项
        self.max_clients_spin.setValue(general.max_clients)
        self.cpu_cores_spin.setValue(general.cpu_cores)
        
        # 加载账户列表
        self.accounts_list.clear()
        for account in general.accounts:
            self.accounts_list.addItem(account)
        
        # 加载卷列表
        self.volumes_list.clear()
        for volume in general.volumes:
            self.volumes_list.addItem(volume)
        
        # 加载组列表
        self.groups_list.clear()
        for group in general.groups:
            self.groups_list.addItem(group)
        
        # 加载功能选项
        self.enable_dots_cb.setChecked(general.enable_dots)
        self.urlform_edit.setText(general.urlform)
        
        # 加载显示设置
        self.window_title_edit.setText(general.window_title)
        self.server_name_edit.setText(general.server_name)
        
        # 加载 MIME 映射
        self.mime_list.clear()
        for mime_mapping in general.mime_mappings:
            self.mime_list.addItem(mime_mapping)
        
        # 加载 MIME 选项
        self.list_mimes_cb.setChecked(general.list_mimes)
        self.expensive_mime_cb.setChecked(general.expensive_mime)
        
        # 加载信息选项
        self.show_license_cb.setChecked(general.show_license)
        self.show_version_cb.setChecked(general.show_version)
    
    def save_config(self):
        """保存配置"""
        general = self.config.general
        
        # 保存配置文件列表
        general.config_files = []
        for i in range(self.config_files_list.count()):
            item = self.config_files_list.item(i)
            if item:
                general.config_files.append(item.text())
        
        # 保存基本选项
        general.max_clients = self.max_clients_spin.value()
        general.cpu_cores = self.cpu_cores_spin.value()
        
        # 保存账户列表
        general.accounts = []
        for i in range(self.accounts_list.count()):
            item = self.accounts_list.item(i)
            if item:
                general.accounts.append(item.text())
        
        # 保存卷列表
        general.volumes = []
        for i in range(self.volumes_list.count()):
            item = self.volumes_list.item(i)
            if item:
                general.volumes.append(item.text())
        
        # 保存组列表
        general.groups = []
        for i in range(self.groups_list.count()):
            item = self.groups_list.item(i)
            if item:
                general.groups.append(item.text())
        
        # 保存功能选项
        general.enable_dots = self.enable_dots_cb.isChecked()
        general.urlform = self.urlform_edit.text().strip()
        
        # 保存显示设置
        general.window_title = self.window_title_edit.text().strip()
        general.server_name = self.server_name_edit.text().strip()
        
        # 保存 MIME 映射
        general.mime_mappings = []
        for i in range(self.mime_list.count()):
            item = self.mime_list.item(i)
            if item:
                general.mime_mappings.append(item.text())
        
        # 保存 MIME 选项
        general.list_mimes = self.list_mimes_cb.isChecked()
        general.expensive_mime = self.expensive_mime_cb.isChecked()
        
        # 保存信息选项
        general.show_license = self.show_license_cb.isChecked()
        general.show_version = self.show_version_cb.isChecked()


class CompleteNetworkConfigWidget(QWidget):
    """完整网络配置界面 - 对应 add_network()"""

    def __init__(self, config: CopyPartyCompleteConfig):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 基本网络设置组
        basic_group = QGroupBox("基本网络设置")
        basic_layout = QFormLayout()

        # 监听 IP
        self.listen_ips_edit = QLineEdit()
        self.listen_ips_edit.setText("::")
        self.listen_ips_edit.setPlaceholderText("例如: ::, 0.0.0.0, 192.168.1.100")
        basic_layout.addRow("监听 IP (-i):", self.listen_ips_edit)

        # 监听端口
        self.listen_ports_edit = QLineEdit()
        self.listen_ports_edit.setText("3923")
        self.listen_ports_edit.setPlaceholderText("例如: 3923, 8080-8090")
        basic_layout.addRow("监听端口 (-p):", self.listen_ports_edit)

        # 包含链路本地地址
        self.include_link_local_cb = QCheckBox("包含链路本地地址 (--ll)")
        basic_layout.addRow("", self.include_link_local_cb)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # 反向代理设置组
        proxy_group = QGroupBox("反向代理设置")
        proxy_layout = QFormLayout()

        # 反向代理深度
        self.reverse_proxy_depth_spin = QSpinBox()
        self.reverse_proxy_depth_spin.setRange(0, 10)
        self.reverse_proxy_depth_spin.setValue(1)
        proxy_layout.addRow("反向代理深度 (--rproxy):", self.reverse_proxy_depth_spin)

        # XFF 头名称
        self.xff_header_edit = QLineEdit()
        self.xff_header_edit.setText("x-forwarded-for")
        proxy_layout.addRow("XFF 头名称 (--xff-hdr):", self.xff_header_edit)

        # XFF 源
        self.xff_sources_edit = QLineEdit()
        self.xff_sources_edit.setText("127.0.0.0/8, ::1/128")
        self.xff_sources_edit.setPlaceholderText("可信代理源，逗号分隔")
        proxy_layout.addRow("XFF 源 (--xff-src):", self.xff_sources_edit)

        # IP 白名单
        self.ip_allowlist_edit = QLineEdit()
        self.ip_allowlist_edit.setPlaceholderText("IP 白名单，逗号分隔")
        proxy_layout.addRow("IP 白名单 (--ipa):", self.ip_allowlist_edit)

        # 反向代理位置
        self.reverse_proxy_location_edit = QLineEdit()
        self.reverse_proxy_location_edit.setPlaceholderText("例如: /copyparty")
        proxy_layout.addRow("反向代理位置 (--rp-loc):", self.reverse_proxy_location_edit)

        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # 系统选项组
        system_group = QGroupBox("系统选项")
        system_layout = QFormLayout()

        # 重用地址 (Windows)
        self.reuseaddr_cb = QCheckBox("重用地址 - Windows (--reuseaddr)")
        system_layout.addRow("", self.reuseaddr_cb)

        # 自由绑定 (Linux)
        self.freebind_cb = QCheckBox("自由绑定 - Linux (--freebind)")
        system_layout.addRow("", self.freebind_cb)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # 文件输出组
        output_group = QGroupBox("文件输出")
        output_layout = QFormLayout()

        # 写入端点
        self.write_endpoints_edit = QLineEdit()
        self.write_endpoints_edit.setPlaceholderText("端点文件路径")
        output_layout.addRow("写入端点 (--wr-h-eps):", self.write_endpoints_edit)

        # 写入可访问
        self.write_accessible_edit = QLineEdit()
        self.write_accessible_edit.setPlaceholderText("可访问文件路径")
        output_layout.addRow("写入可访问 (--wr-h-aon):", self.write_accessible_edit)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 超时设置组
        timeout_group = QGroupBox("超时设置")
        timeout_layout = QFormLayout()

        # 套接字头部超时
        self.socket_timeout_header_spin = QSpinBox()
        self.socket_timeout_header_spin.setRange(1, 3600)
        self.socket_timeout_header_spin.setValue(120)
        self.socket_timeout_header_spin.setSuffix(" 秒")
        timeout_layout.addRow("套接字头部超时 (--s-thead):", self.socket_timeout_header_spin)

        # 套接字主体超时
        self.socket_timeout_body_spin = QDoubleSpinBox()
        self.socket_timeout_body_spin.setRange(1.0, 3600.0)
        self.socket_timeout_body_spin.setValue(128.0)
        self.socket_timeout_body_spin.setSuffix(" 秒")
        timeout_layout.addRow("套接字主体超时 (--s-tbody):", self.socket_timeout_body_spin)

        # 套接字读取大小
        self.socket_read_size_spin = QSpinBox()
        self.socket_read_size_spin.setRange(1024, 10485760)  # 1KB - 10MB
        self.socket_read_size_spin.setValue(256 * 1024)
        self.socket_read_size_spin.setSuffix(" 字节")
        timeout_layout.addRow("套接字读取大小 (--s-rd-sz):", self.socket_read_size_spin)

        # 套接字写入大小
        self.socket_write_size_spin = QSpinBox()
        self.socket_write_size_spin.setRange(1024, 10485760)  # 1KB - 10MB
        self.socket_write_size_spin.setValue(256 * 1024)
        self.socket_write_size_spin.setSuffix(" 字节")
        timeout_layout.addRow("套接字写入大小 (--s-wr-sz):", self.socket_write_size_spin)

        # 套接字写入休眠
        self.socket_write_sleep_spin = QDoubleSpinBox()
        self.socket_write_sleep_spin.setRange(0.0, 10.0)
        self.socket_write_sleep_spin.setValue(0.0)
        self.socket_write_sleep_spin.setSuffix(" 秒")
        self.socket_write_sleep_spin.setDecimals(3)
        timeout_layout.addRow("套接字写入休眠 (--s-wr-slp):", self.socket_write_sleep_spin)

        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)

        # 调试选项组
        debug_group = QGroupBox("调试选项")
        debug_layout = QFormLayout()

        # 响应休眠
        self.response_sleep_spin = QDoubleSpinBox()
        self.response_sleep_spin.setRange(0.0, 10.0)
        self.response_sleep_spin.setValue(0.0)
        self.response_sleep_spin.setSuffix(" 秒")
        self.response_sleep_spin.setDecimals(3)
        debug_layout.addRow("响应休眠 (--rsp-slp):", self.response_sleep_spin)

        # 响应抖动
        self.response_jitter_spin = QDoubleSpinBox()
        self.response_jitter_spin.setRange(0.0, 10.0)
        self.response_jitter_spin.setValue(0.0)
        self.response_jitter_spin.setSuffix(" 秒")
        self.response_jitter_spin.setDecimals(3)
        debug_layout.addRow("响应抖动 (--rsp-jtr):", self.response_jitter_spin)

        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        layout.addStretch()
        self.setLayout(layout)

    def load_config(self):
        """加载配置"""
        network = self.config.network

        self.listen_ips_edit.setText(network.listen_ips)
        self.listen_ports_edit.setText(network.listen_ports)
        self.include_link_local_cb.setChecked(network.include_link_local)

        self.reverse_proxy_depth_spin.setValue(network.reverse_proxy_depth)
        self.xff_header_edit.setText(network.xff_header)
        self.xff_sources_edit.setText(network.xff_sources)
        self.ip_allowlist_edit.setText(network.ip_allowlist)
        self.reverse_proxy_location_edit.setText(network.reverse_proxy_location)

        self.reuseaddr_cb.setChecked(network.reuseaddr)
        self.freebind_cb.setChecked(network.freebind)

        self.write_endpoints_edit.setText(network.write_endpoints)
        self.write_accessible_edit.setText(network.write_accessible)

        self.socket_timeout_header_spin.setValue(network.socket_timeout_header)
        self.socket_timeout_body_spin.setValue(network.socket_timeout_body)
        self.socket_read_size_spin.setValue(network.socket_read_size)
        self.socket_write_size_spin.setValue(network.socket_write_size)
        self.socket_write_sleep_spin.setValue(network.socket_write_sleep)

        self.response_sleep_spin.setValue(network.response_sleep)
        self.response_jitter_spin.setValue(network.response_jitter)

    def save_config(self):
        """保存配置"""
        network = self.config.network

        network.listen_ips = self.listen_ips_edit.text().strip()
        network.listen_ports = self.listen_ports_edit.text().strip()
        network.include_link_local = self.include_link_local_cb.isChecked()

        network.reverse_proxy_depth = self.reverse_proxy_depth_spin.value()
        network.xff_header = self.xff_header_edit.text().strip()
        network.xff_sources = self.xff_sources_edit.text().strip()
        network.ip_allowlist = self.ip_allowlist_edit.text().strip()
        network.reverse_proxy_location = self.reverse_proxy_location_edit.text().strip()

        network.reuseaddr = self.reuseaddr_cb.isChecked()
        network.freebind = self.freebind_cb.isChecked()

        network.write_endpoints = self.write_endpoints_edit.text().strip()
        network.write_accessible = self.write_accessible_edit.text().strip()

        network.socket_timeout_header = self.socket_timeout_header_spin.value()
        network.socket_timeout_body = self.socket_timeout_body_spin.value()
        network.socket_read_size = self.socket_read_size_spin.value()
        network.socket_write_size = self.socket_write_size_spin.value()
        network.socket_write_sleep = self.socket_write_sleep_spin.value()

        network.response_sleep = self.response_sleep_spin.value()
        network.response_jitter = self.response_jitter_spin.value()
