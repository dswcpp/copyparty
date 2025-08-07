"""
配置编辑器组件
迁移自 copyparty_complete_widgets.py 中的配置组件
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QTabWidget, QGroupBox, QLabel, QLineEdit, 
                             QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                             QPushButton, QListWidget, QTextEdit, QFileDialog,
                             QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class ConfigEditorWidget(QWidget):
    """配置编辑器组件 - 迁移配置组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        
        self.init_ui()
        self.load_config_to_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 服务器配置标签
        self.create_server_tab()
        
        # 网络配置标签
        self.create_network_tab()
        
        # 安全配置标签
        self.create_security_tab()
        
        # 上传配置标签
        self.create_upload_tab()

        # 协议配置标签
        self.create_protocol_tab()

        # 文件索引标签
        self.create_file_index_tab()

        # 账户和卷管理标签
        self.create_account_volume_tab()

        # 高级配置标签
        self.create_advanced_tab()
        
        layout.addWidget(self.tabs)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("应用")
        self.apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_btn)
        
        self.validate_btn = QPushButton("验证")
        self.validate_btn.clicked.connect(self.validate_config)
        button_layout.addWidget(self.validate_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_server_tab(self):
        """创建服务器配置标签"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QGridLayout()
        
        # 工作目录
        basic_layout.addWidget(QLabel("工作目录:"), 0, 0)
        self.work_dir_edit = QLineEdit()
        basic_layout.addWidget(self.work_dir_edit, 0, 1)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_work_directory)
        basic_layout.addWidget(browse_btn, 0, 2)
        
        # 最大客户端数
        basic_layout.addWidget(QLabel("最大客户端:"), 1, 0)
        self.max_clients_spin = QSpinBox()
        self.max_clients_spin.setRange(1, 65535)
        self.max_clients_spin.setValue(1024)
        basic_layout.addWidget(self.max_clients_spin, 1, 1)
        
        # CPU 核心数
        basic_layout.addWidget(QLabel("CPU 核心:"), 1, 2)
        self.cpu_cores_spin = QSpinBox()
        self.cpu_cores_spin.setRange(1, 64)
        self.cpu_cores_spin.setValue(1)
        basic_layout.addWidget(self.cpu_cores_spin, 1, 3)
        
        # 服务器名称
        basic_layout.addWidget(QLabel("服务器名称:"), 2, 0)
        self.server_name_edit = QLineEdit()
        self.server_name_edit.setText("copyparty")
        basic_layout.addWidget(self.server_name_edit, 2, 1)
        
        # 窗口标题
        basic_layout.addWidget(QLabel("窗口标题:"), 2, 2)
        self.window_title_edit = QLineEdit()
        self.window_title_edit.setText("cpp @ $pub")
        basic_layout.addWidget(self.window_title_edit, 2, 3)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 功能设置组
        features_group = QGroupBox("功能设置")
        features_layout = QGridLayout()
        
        self.enable_dots_check = QCheckBox("启用点文件")
        features_layout.addWidget(self.enable_dots_check, 0, 0)
        
        self.expensive_mime_check = QCheckBox("启用扩展MIME检测")
        features_layout.addWidget(self.expensive_mime_check, 0, 1)
        
        features_layout.addWidget(QLabel("URL表单:"), 1, 0)
        self.urlform_edit = QLineEdit()
        self.urlform_edit.setText("print,xm")
        features_layout.addWidget(self.urlform_edit, 1, 1)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 账户管理组
        accounts_group = QGroupBox("账户管理")
        accounts_layout = QVBoxLayout()
        
        # 账户列表
        self.accounts_list = QListWidget()
        self.accounts_list.setMaximumHeight(100)
        accounts_layout.addWidget(self.accounts_list)
        
        # 账户操作按钮
        account_btn_layout = QHBoxLayout()
        
        add_account_btn = QPushButton("添加账户")
        add_account_btn.clicked.connect(self.add_account)
        account_btn_layout.addWidget(add_account_btn)
        
        edit_account_btn = QPushButton("编辑账户")
        edit_account_btn.clicked.connect(self.edit_account)
        account_btn_layout.addWidget(edit_account_btn)
        
        remove_account_btn = QPushButton("删除账户")
        remove_account_btn.clicked.connect(self.remove_account)
        account_btn_layout.addWidget(remove_account_btn)
        
        accounts_layout.addLayout(account_btn_layout)
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)
        
        # 卷管理组
        volumes_group = QGroupBox("卷管理")
        volumes_layout = QVBoxLayout()
        
        # 卷列表
        self.volumes_list = QListWidget()
        self.volumes_list.setMaximumHeight(100)
        volumes_layout.addWidget(self.volumes_list)
        
        # 卷操作按钮
        volume_btn_layout = QHBoxLayout()
        
        add_volume_btn = QPushButton("添加卷")
        add_volume_btn.clicked.connect(self.add_volume)
        volume_btn_layout.addWidget(add_volume_btn)
        
        edit_volume_btn = QPushButton("编辑卷")
        edit_volume_btn.clicked.connect(self.edit_volume)
        volume_btn_layout.addWidget(edit_volume_btn)
        
        remove_volume_btn = QPushButton("删除卷")
        remove_volume_btn.clicked.connect(self.remove_volume)
        volume_btn_layout.addWidget(remove_volume_btn)
        
        volumes_layout.addLayout(volume_btn_layout)
        volumes_group.setLayout(volumes_layout)
        layout.addWidget(volumes_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.tabs.addTab(scroll, "服务器")
    
    def create_network_tab(self):
        """创建网络配置标签"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 基本网络设置组
        network_group = QGroupBox("网络设置")
        network_layout = QGridLayout()
        
        # 监听IP
        network_layout.addWidget(QLabel("监听IP:"), 0, 0)
        self.listen_ips_edit = QLineEdit()
        self.listen_ips_edit.setText("::")
        network_layout.addWidget(self.listen_ips_edit, 0, 1)
        
        # 监听端口
        network_layout.addWidget(QLabel("监听端口:"), 0, 2)
        self.listen_ports_edit = QLineEdit()
        self.listen_ports_edit.setText("3923")
        network_layout.addWidget(self.listen_ports_edit, 0, 3)
        
        # 链路本地
        self.include_link_local_check = QCheckBox("包含链路本地地址")
        network_layout.addWidget(self.include_link_local_check, 1, 0, 1, 2)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # 反向代理设置组
        proxy_group = QGroupBox("反向代理")
        proxy_layout = QGridLayout()
        
        # 反向代理深度
        proxy_layout.addWidget(QLabel("代理深度:"), 0, 0)
        self.reverse_proxy_depth_spin = QSpinBox()
        self.reverse_proxy_depth_spin.setRange(0, 10)
        self.reverse_proxy_depth_spin.setValue(1)
        proxy_layout.addWidget(self.reverse_proxy_depth_spin, 0, 1)
        
        # XFF 头
        proxy_layout.addWidget(QLabel("XFF 头:"), 0, 2)
        self.xff_header_edit = QLineEdit()
        self.xff_header_edit.setText("x-forwarded-for")
        proxy_layout.addWidget(self.xff_header_edit, 0, 3)
        
        # XFF 源
        proxy_layout.addWidget(QLabel("XFF 源:"), 1, 0)
        self.xff_sources_edit = QLineEdit()
        self.xff_sources_edit.setText("127.0.0.0/8, ::1/128")
        proxy_layout.addWidget(self.xff_sources_edit, 1, 1, 1, 3)
        
        # 反向代理位置
        proxy_layout.addWidget(QLabel("代理位置:"), 2, 0)
        self.reverse_proxy_location_edit = QLineEdit()
        proxy_layout.addWidget(self.reverse_proxy_location_edit, 2, 1, 1, 3)
        
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        # 超时设置组
        timeout_group = QGroupBox("超时设置")
        timeout_layout = QGridLayout()
        
        # 头部超时
        timeout_layout.addWidget(QLabel("头部超时(秒):"), 0, 0)
        self.socket_timeout_header_spin = QSpinBox()
        self.socket_timeout_header_spin.setRange(1, 3600)
        self.socket_timeout_header_spin.setValue(120)
        timeout_layout.addWidget(self.socket_timeout_header_spin, 0, 1)
        
        # 主体超时
        timeout_layout.addWidget(QLabel("主体超时(秒):"), 0, 2)
        self.socket_timeout_body_spin = QDoubleSpinBox()
        self.socket_timeout_body_spin.setRange(0.1, 3600.0)
        self.socket_timeout_body_spin.setValue(128.0)
        timeout_layout.addWidget(self.socket_timeout_body_spin, 0, 3)
        
        # 读取大小
        timeout_layout.addWidget(QLabel("读取大小(KB):"), 1, 0)
        self.socket_read_size_spin = QSpinBox()
        self.socket_read_size_spin.setRange(1, 10240)
        self.socket_read_size_spin.setValue(256)
        timeout_layout.addWidget(self.socket_read_size_spin, 1, 1)
        
        # 写入大小
        timeout_layout.addWidget(QLabel("写入大小(KB):"), 1, 2)
        self.socket_write_size_spin = QSpinBox()
        self.socket_write_size_spin.setRange(1, 10240)
        self.socket_write_size_spin.setValue(256)
        timeout_layout.addWidget(self.socket_write_size_spin, 1, 3)
        
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.tabs.addTab(scroll, "网络")
    
    def create_security_tab(self):
        """创建安全配置标签"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # TLS设置组
        tls_group = QGroupBox("TLS/SSL 设置")
        tls_layout = QGridLayout()
        
        # HTTP/HTTPS 模式
        self.http_only_check = QCheckBox("仅HTTP")
        tls_layout.addWidget(self.http_only_check, 0, 0)
        
        self.https_only_check = QCheckBox("仅HTTPS")
        tls_layout.addWidget(self.https_only_check, 0, 1)
        
        # 证书路径
        tls_layout.addWidget(QLabel("证书路径:"), 1, 0)
        self.cert_path_edit = QLineEdit()
        tls_layout.addWidget(self.cert_path_edit, 1, 1)
        
        browse_cert_btn = QPushButton("浏览")
        browse_cert_btn.clicked.connect(self.browse_cert_file)
        tls_layout.addWidget(browse_cert_btn, 1, 2)
        
        # SSL版本
        tls_layout.addWidget(QLabel("SSL版本:"), 2, 0)
        self.ssl_versions_edit = QLineEdit()
        tls_layout.addWidget(self.ssl_versions_edit, 2, 1, 1, 2)
        
        # 密码套件
        tls_layout.addWidget(QLabel("密码套件:"), 3, 0)
        self.ciphers_edit = QLineEdit()
        tls_layout.addWidget(self.ciphers_edit, 3, 1, 1, 2)
        
        # SSL调试
        self.ssl_debug_check = QCheckBox("SSL调试")
        tls_layout.addWidget(self.ssl_debug_check, 4, 0)
        
        tls_group.setLayout(tls_layout)
        layout.addWidget(tls_group)
        
        # 认证设置组
        auth_group = QGroupBox("身份认证")
        auth_layout = QGridLayout()
        
        self.enable_authentication_check = QCheckBox("启用身份认证")
        auth_layout.addWidget(self.enable_authentication_check, 0, 0)
        
        # 默认权限
        auth_layout.addWidget(QLabel("默认权限:"), 1, 0)
        self.default_permissions_combo = QComboBox()
        self.default_permissions_combo.addItems(["r", "rw", "rwm", "rwmd"])
        auth_layout.addWidget(self.default_permissions_combo, 1, 1)
        
        # 会话超时
        auth_layout.addWidget(QLabel("会话超时(秒):"), 1, 2)
        self.session_timeout_spin = QSpinBox()
        self.session_timeout_spin.setRange(60, 86400)
        self.session_timeout_spin.setValue(3600)
        auth_layout.addWidget(self.session_timeout_spin, 1, 3)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.tabs.addTab(scroll, "安全")
    
    def create_upload_tab(self):
        """创建上传配置标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 上传限制组
        upload_group = QGroupBox("上传限制")
        upload_layout = QGridLayout()
        
        # 最大文件大小
        upload_layout.addWidget(QLabel("最大文件大小(MB):"), 0, 0)
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(0, 10240)
        self.max_file_size_spin.setValue(0)
        self.max_file_size_spin.setSpecialValueText("无限制")
        upload_layout.addWidget(self.max_file_size_spin, 0, 1)
        
        # 最大文件数
        upload_layout.addWidget(QLabel("最大文件数:"), 0, 2)
        self.max_files_per_upload_spin = QSpinBox()
        self.max_files_per_upload_spin.setRange(0, 1000)
        self.max_files_per_upload_spin.setValue(0)
        self.max_files_per_upload_spin.setSpecialValueText("无限制")
        upload_layout.addWidget(self.max_files_per_upload_spin, 0, 3)
        
        # 上传行为
        self.overwrite_existing_check = QCheckBox("覆盖现有文件")
        upload_layout.addWidget(self.overwrite_existing_check, 1, 0)
        
        self.create_directories_check = QCheckBox("创建目录")
        self.create_directories_check.setChecked(True)
        upload_layout.addWidget(self.create_directories_check, 1, 1)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.tabs.addTab(widget, "上传")

    def create_protocol_tab(self):
        """创建协议配置标签"""
        try:
            from .protocol_config import ProtocolConfigWidget
            self.protocol_config_widget = ProtocolConfigWidget(self.app)
            self.tabs.addTab(self.protocol_config_widget, "协议")
        except Exception as e:
            # 如果协议配置组件不可用，创建占位符
            widget = QWidget()
            layout = QVBoxLayout()

            error_label = QLabel("协议配置功能暂不可用")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #666; font-size: 14px;")
            layout.addWidget(error_label)

            detail_label = QLabel(f"错误: {str(e)}")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_label.setStyleSheet("color: #999; font-size: 12px;")
            layout.addWidget(detail_label)

            layout.addStretch()
            widget.setLayout(layout)

            self.tabs.addTab(widget, "协议")
            self.protocol_config_widget = None

    def create_file_index_tab(self):
        """创建文件索引标签"""
        try:
            from .file_index_widget import FileIndexWidget
            self.file_index_widget = FileIndexWidget(self.app)
            self.tabs.addTab(self.file_index_widget, "文件索引")
        except Exception as e:
            # 如果文件索引组件不可用，创建占位符
            widget = QWidget()
            layout = QVBoxLayout()

            error_label = QLabel("文件索引功能暂不可用")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #666; font-size: 14px;")
            layout.addWidget(error_label)

            detail_label = QLabel(f"错误: {str(e)}")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_label.setStyleSheet("color: #999; font-size: 12px;")
            layout.addWidget(detail_label)

            layout.addStretch()
            widget.setLayout(layout)

            self.tabs.addTab(widget, "文件索引")
            self.file_index_widget = None

    def create_account_volume_tab(self):
        """创建账户和卷管理标签"""
        try:
            from .account_volume_manager import AccountVolumeManagerWidget
            self.account_volume_widget = AccountVolumeManagerWidget(self.app)
            self.tabs.addTab(self.account_volume_widget, "账户&卷管理")
        except Exception as e:
            # 如果账户和卷管理组件不可用，创建占位符
            widget = QWidget()
            layout = QVBoxLayout()

            error_label = QLabel("账户和卷管理功能暂不可用")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #666; font-size: 14px;")
            layout.addWidget(error_label)

            detail_label = QLabel(f"错误: {str(e)}")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_label.setStyleSheet("color: #999; font-size: 12px;")
            layout.addWidget(detail_label)

            layout.addStretch()
            widget.setLayout(layout)

            self.tabs.addTab(widget, "账户&卷管理")
            self.account_volume_widget = None

    def create_advanced_tab(self):
        """创建高级配置标签"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 原始配置编辑器
        raw_group = QGroupBox("原始配置")
        raw_layout = QVBoxLayout()
        
        self.raw_config_edit = QTextEdit()
        self.raw_config_edit.setMaximumHeight(200)
        self.raw_config_edit.setFont(self.font())
        raw_layout.addWidget(self.raw_config_edit)
        
        raw_btn_layout = QHBoxLayout()
        
        load_raw_btn = QPushButton("加载到编辑器")
        load_raw_btn.clicked.connect(self.load_raw_config)
        raw_btn_layout.addWidget(load_raw_btn)
        
        apply_raw_btn = QPushButton("应用原始配置")
        apply_raw_btn.clicked.connect(self.apply_raw_config)
        raw_btn_layout.addWidget(apply_raw_btn)
        
        raw_btn_layout.addStretch()
        raw_layout.addLayout(raw_btn_layout)
        
        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.tabs.addTab(widget, "高级")
    
    def load_config_to_ui(self):
        """从配置管理器加载配置到UI"""
        try:
            # 服务器配置
            server_config = self.config_manager.server_config
            self.work_dir_edit.setText(server_config.working_directory)
            self.max_clients_spin.setValue(server_config.max_clients)
            self.cpu_cores_spin.setValue(server_config.cpu_cores)
            self.server_name_edit.setText(server_config.server_name)
            self.window_title_edit.setText(server_config.window_title)
            self.enable_dots_check.setChecked(server_config.enable_dots)
            self.expensive_mime_check.setChecked(server_config.expensive_mime)
            self.urlform_edit.setText(server_config.urlform)
            
            # 更新账户和卷列表
            self.update_accounts_list()
            self.update_volumes_list()
            
            # 网络配置
            network_config = self.config_manager.network_config
            self.listen_ips_edit.setText(network_config.listen_ips)
            self.listen_ports_edit.setText(network_config.listen_ports)
            self.include_link_local_check.setChecked(network_config.include_link_local)
            self.reverse_proxy_depth_spin.setValue(network_config.reverse_proxy_depth)
            self.xff_header_edit.setText(network_config.xff_header)
            self.xff_sources_edit.setText(network_config.xff_sources)
            self.reverse_proxy_location_edit.setText(network_config.reverse_proxy_location)
            self.socket_timeout_header_spin.setValue(network_config.socket_timeout_header)
            self.socket_timeout_body_spin.setValue(network_config.socket_timeout_body)
            self.socket_read_size_spin.setValue(network_config.socket_read_size // 1024)
            self.socket_write_size_spin.setValue(network_config.socket_write_size // 1024)
            
            # 安全配置
            security_config = self.config_manager.security_config
            self.http_only_check.setChecked(security_config.tls.http_only)
            self.https_only_check.setChecked(security_config.tls.https_only)
            self.cert_path_edit.setText(security_config.tls.cert_path)
            self.ssl_versions_edit.setText(security_config.tls.ssl_versions)
            self.ciphers_edit.setText(security_config.tls.ciphers)
            self.ssl_debug_check.setChecked(security_config.tls.ssl_debug)
            
            self.enable_authentication_check.setChecked(security_config.authentication.enable_authentication)
            self.default_permissions_combo.setCurrentText(security_config.authentication.default_permissions)
            self.session_timeout_spin.setValue(security_config.authentication.session_timeout)
            
            # 上传配置
            upload_config = self.config_manager.upload_config
            self.max_file_size_spin.setValue(upload_config.max_file_size)
            self.max_files_per_upload_spin.setValue(upload_config.max_files_per_upload)
            self.overwrite_existing_check.setChecked(upload_config.overwrite_existing)
            self.create_directories_check.setChecked(upload_config.create_directories)
            
        except Exception as e:
            QMessageBox.warning(self, "加载配置失败", f"无法加载配置到UI: {str(e)}")
    
    def apply_config(self):
        """应用配置更改"""
        try:
            # 服务器配置
            server_config = self.config_manager.server_config
            server_config.working_directory = self.work_dir_edit.text()
            server_config.max_clients = self.max_clients_spin.value()
            server_config.cpu_cores = self.cpu_cores_spin.value()
            server_config.server_name = self.server_name_edit.text()
            server_config.window_title = self.window_title_edit.text()
            server_config.enable_dots = self.enable_dots_check.isChecked()
            server_config.expensive_mime = self.expensive_mime_check.isChecked()
            server_config.urlform = self.urlform_edit.text()
            
            # 网络配置
            network_config = self.config_manager.network_config
            network_config.listen_ips = self.listen_ips_edit.text()
            network_config.listen_ports = self.listen_ports_edit.text()
            network_config.include_link_local = self.include_link_local_check.isChecked()
            network_config.reverse_proxy_depth = self.reverse_proxy_depth_spin.value()
            network_config.xff_header = self.xff_header_edit.text()
            network_config.xff_sources = self.xff_sources_edit.text()
            network_config.reverse_proxy_location = self.reverse_proxy_location_edit.text()
            network_config.socket_timeout_header = self.socket_timeout_header_spin.value()
            network_config.socket_timeout_body = self.socket_timeout_body_spin.value()
            network_config.socket_read_size = self.socket_read_size_spin.value() * 1024
            network_config.socket_write_size = self.socket_write_size_spin.value() * 1024
            
            # 安全配置
            security_config = self.config_manager.security_config
            security_config.tls.http_only = self.http_only_check.isChecked()
            security_config.tls.https_only = self.https_only_check.isChecked()
            security_config.tls.cert_path = self.cert_path_edit.text()
            security_config.tls.ssl_versions = self.ssl_versions_edit.text()
            security_config.tls.ciphers = self.ciphers_edit.text()
            security_config.tls.ssl_debug = self.ssl_debug_check.isChecked()
            
            security_config.authentication.enable_authentication = self.enable_authentication_check.isChecked()
            security_config.authentication.default_permissions = self.default_permissions_combo.currentText()
            security_config.authentication.session_timeout = self.session_timeout_spin.value()
            
            # 上传配置
            upload_config = self.config_manager.upload_config
            upload_config.max_file_size = self.max_file_size_spin.value()
            upload_config.max_files_per_upload = self.max_files_per_upload_spin.value()
            upload_config.overwrite_existing = self.overwrite_existing_check.isChecked()
            upload_config.create_directories = self.create_directories_check.isChecked()
            
            # 标记配置已更改
            self.config_manager.mark_changed()
            
            QMessageBox.information(self, "成功", "配置已应用")
            
        except Exception as e:
            QMessageBox.critical(self, "应用失败", f"应用配置失败: {str(e)}")
    
    def reset_config(self):
        """重置配置"""
        self.load_config_to_ui()
        QMessageBox.information(self, "成功", "配置已重置")
    
    def validate_config(self):
        """验证配置"""
        # 先应用当前UI的配置
        self.apply_config()
        
        # 然后验证
        result = self.config_manager.validate_all()
        
        if result.is_valid:
            QMessageBox.information(self, "验证结果", "配置验证通过！")
        else:
            error_msg = "配置验证失败：\n\n"
            for error in result.errors[:10]:
                error_msg += f"• {error}\n"
            
            if len(result.errors) > 10:
                error_msg += f"\n... 还有 {len(result.errors) - 10} 个错误"
            
            QMessageBox.warning(self, "验证结果", error_msg)
    
    # 辅助方法
    def browse_work_directory(self):
        """浏览工作目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if directory:
            self.work_dir_edit.setText(directory)
    
    def browse_cert_file(self):
        """浏览证书文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择证书文件", "", 
            "证书文件 (*.pem *.crt *.cert);;所有文件 (*)"
        )
        if file_path:
            self.cert_path_edit.setText(file_path)
    
    def update_accounts_list(self):
        """更新账户列表"""
        self.accounts_list.clear()
        for account in self.config_manager.server_config.accounts:
            account_info = self.config_manager.server_config.get_account_info(account)
            display_text = f"{account_info['username']} ({account_info['permissions'] or '默认'})"
            self.accounts_list.addItem(display_text)
    
    def update_volumes_list(self):
        """更新卷列表"""
        self.volumes_list.clear()
        for volume in self.config_manager.server_config.volumes:
            volume_info = self.config_manager.server_config.get_volume_info(volume)
            display_text = f"{volume_info['path']} -> {volume_info['alias'] or '/'} ({volume_info['permissions']})"
            self.volumes_list.addItem(display_text)
    
    def add_account(self):
        """添加账户"""
        # TODO: 实现账户添加对话框
        QMessageBox.information(self, "添加账户", "账户添加功能开发中")
    
    def edit_account(self):
        """编辑账户"""
        # TODO: 实现账户编辑对话框
        QMessageBox.information(self, "编辑账户", "账户编辑功能开发中")
    
    def remove_account(self):
        """删除账户"""
        current_row = self.accounts_list.currentRow()
        if current_row >= 0:
            accounts = self.config_manager.server_config.accounts
            if current_row < len(accounts):
                account = accounts[current_row]
                account_info = self.config_manager.server_config.get_account_info(account)
                
                reply = QMessageBox.question(
                    self, "确认删除", f"确定要删除账户 '{account_info['username']}' 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.config_manager.server_config.remove_account(account_info['username'])
                    self.update_accounts_list()
    
    def add_volume(self):
        """添加卷"""
        # TODO: 实现卷添加对话框
        QMessageBox.information(self, "添加卷", "卷添加功能开发中")
    
    def edit_volume(self):
        """编辑卷"""
        # TODO: 实现卷编辑对话框
        QMessageBox.information(self, "编辑卷", "卷编辑功能开发中")
    
    def remove_volume(self):
        """删除卷"""
        current_row = self.volumes_list.currentRow()
        if current_row >= 0:
            volumes = self.config_manager.server_config.volumes
            if current_row < len(volumes):
                volume = volumes[current_row]
                volume_info = self.config_manager.server_config.get_volume_info(volume)
                
                reply = QMessageBox.question(
                    self, "确认删除", f"确定要删除卷 '{volume_info['path']}' 吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.config_manager.server_config.remove_volume(volume_info['path'])
                    self.update_volumes_list()
    
    def load_raw_config(self):
        """加载原始配置到编辑器"""
        try:
            config_json = self.config_manager.to_json(indent=2)
            self.raw_config_edit.setPlainText(config_json)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载原始配置: {str(e)}")
    
    def apply_raw_config(self):
        """应用原始配置"""
        try:
            config_text = self.raw_config_edit.toPlainText()
            self.config_manager.from_json(config_text)
            self.load_config_to_ui()
            QMessageBox.information(self, "成功", "原始配置已应用")
        except Exception as e:
            QMessageBox.critical(self, "应用失败", f"应用原始配置失败: {str(e)}")
    
    def refresh(self):
        """刷新组件"""
        self.load_config_to_ui()
