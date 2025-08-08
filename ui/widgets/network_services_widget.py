"""
网络服务配置组件
支持WebDAV、TFTP、SMB等网络服务的配置
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QCheckBox, QSpinBox, QLineEdit, QLabel,
                             QComboBox, QPushButton, QTextEdit, QMessageBox,
                             QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NetworkServicesWidget(QWidget):
    """网络服务配置组件"""

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.network_config = config_manager.network_config
        
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # WebDAV标签页
        self.webdav_tab = self.create_webdav_tab()
        self.tabs.addTab(self.webdav_tab, "📁 WebDAV")
        
        # TFTP标签页
        self.tftp_tab = self.create_tftp_tab()
        self.tabs.addTab(self.tftp_tab, "📡 TFTP")
        
        # SMB标签页
        self.smb_tab = self.create_smb_tab()
        self.tabs.addTab(self.smb_tab, "🗂️ SMB/CIFS")
        
        # 连接说明标签页
        self.help_tab = self.create_help_tab()
        self.tabs.addTab(self.help_tab, "❓ 连接说明")
        
        layout.addWidget(self.tabs)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存配置")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.load_config)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.test_btn = QPushButton("🧪 测试连接")
        self.test_btn.clicked.connect(self.test_connections)
        button_layout.addWidget(self.test_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def create_webdav_tab(self):
        """创建WebDAV配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # WebDAV基本设置
        webdav_group = QGroupBox("WebDAV 设置")
        webdav_layout = QGridLayout()
        
        # WebDAV启用状态（总是启用，只显示信息）
        webdav_layout.addWidget(QLabel("状态:"), 0, 0)
        status_label = QLabel("✅ 默认启用")
        status_label.setStyleSheet("color: green; font-weight: bold;")
        webdav_layout.addWidget(status_label, 0, 1)
        
        # 强制认证
        webdav_layout.addWidget(QLabel("强制认证:"), 1, 0)
        self.webdav_auth_cb = QCheckBox("要求所有WebDAV客户端进行身份验证")
        self.webdav_auth_cb.setToolTip("启用此选项可解决Windows匿名连接导致的写入问题")
        webdav_layout.addWidget(self.webdav_auth_cb, 1, 1)
        
        webdav_group.setLayout(webdav_layout)
        layout.addWidget(webdav_group)
        
        # WebDAV使用说明
        help_group = QGroupBox("WebDAV 使用说明")
        help_layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setMaximumHeight(150)
        help_text.setReadOnly(True)
        help_text.setPlainText("""Windows 连接方法:
1. 右键点击"我的电脑" → "映射网络驱动器"
2. 文件夹: http://服务器IP:端口/
3. 用户名建议使用密码，密码字段可为空

常见问题解决:
• Win7+重启后需要重新认证: 先输入错误密码，再输入正确密码
• 匿名读取文件夹无法写入: 启用"强制认证"选项
• 包含特殊字符的文件名可能无法访问""")
        
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tftp_tab(self):
        """创建TFTP配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # TFTP基本设置
        tftp_group = QGroupBox("TFTP 服务器设置")
        tftp_layout = QGridLayout()
        
        # 启用TFTP
        tftp_layout.addWidget(QLabel("启用TFTP:"), 0, 0)
        self.tftp_enabled_cb = QCheckBox("启用TFTP服务器")
        self.tftp_enabled_cb.setToolTip("TFTP适用于与90年代硬件通信，一般情况建议使用FTP")
        tftp_layout.addWidget(self.tftp_enabled_cb, 0, 1)
        
        # TFTP端口
        tftp_layout.addWidget(QLabel("TFTP端口:"), 1, 0)
        self.tftp_port_spin = QSpinBox()
        self.tftp_port_spin.setRange(1, 65535)
        self.tftp_port_spin.setValue(3969)
        self.tftp_port_spin.setToolTip("标准端口69需要管理员权限，建议使用3969")
        tftp_layout.addWidget(self.tftp_port_spin, 1, 1)
        
        # 端口范围
        tftp_layout.addWidget(QLabel("回复端口范围:"), 2, 0)
        self.tftp_port_range_edit = QLineEdit()
        self.tftp_port_range_edit.setPlaceholderText("例如: 4000-4100 (可选)")
        self.tftp_port_range_edit.setToolTip("指定TFTP回复使用的端口范围，有助于防火墙配置")
        tftp_layout.addWidget(self.tftp_port_range_edit, 2, 1)
        
        tftp_group.setLayout(tftp_layout)
        layout.addWidget(tftp_group)
        
        # TFTP使用说明
        help_group = QGroupBox("TFTP 使用说明")
        help_layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setMaximumHeight(150)
        help_text.setReadOnly(True)
        help_text.setPlainText("""TFTP 客户端示例:
• curl: curl --tftp-blksize 1428 tftp://127.0.0.1:3969/firmware.bin
• Windows: tftp -i 127.0.0.1 put firmware.bin
• Linux: atftp --option "blksize 1428" 127.0.0.1 3969 -p -l firmware.bin

注意事项:
• 只支持二进制传输模式
• 读取需要world-readable权限，写入需要world-writable权限
• 性能有限，WAN环境下速度较慢
• 大多数客户端期望端口69，可使用NAT转发""")
        
        help_layout.addWidget(help_text)
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_smb_tab(self):
        """创建SMB配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # SMB基本设置
        smb_group = QGroupBox("SMB/CIFS 服务器设置")
        smb_layout = QGridLayout()
        
        # SMB模式
        smb_layout.addWidget(QLabel("SMB模式:"), 0, 0)
        mode_layout = QHBoxLayout()
        
        self.smb_disabled_cb = QCheckBox("禁用")
        self.smb_readonly_cb = QCheckBox("只读")
        self.smb_readwrite_cb = QCheckBox("读写")
        
        # 设置互斥
        self.smb_disabled_cb.toggled.connect(lambda checked: self.update_smb_mode(0 if checked else -1))
        self.smb_readonly_cb.toggled.connect(lambda checked: self.update_smb_mode(1 if checked else -1))
        self.smb_readwrite_cb.toggled.connect(lambda checked: self.update_smb_mode(2 if checked else -1))
        
        mode_layout.addWidget(self.smb_disabled_cb)
        mode_layout.addWidget(self.smb_readonly_cb)
        mode_layout.addWidget(self.smb_readwrite_cb)
        mode_layout.addStretch()
        
        smb_layout.addLayout(mode_layout, 0, 1)
        
        # SMB端口
        smb_layout.addWidget(QLabel("SMB端口:"), 1, 0)
        self.smb_port_spin = QSpinBox()
        self.smb_port_spin.setRange(1, 65535)
        self.smb_port_spin.setValue(3945)
        self.smb_port_spin.setToolTip("标准端口445需要管理员权限，建议使用3945")
        smb_layout.addWidget(self.smb_port_spin, 1, 1)
        
        # SMB版本
        smb_layout.addWidget(QLabel("SMB版本:"), 2, 0)
        self.smb_version_combo = QComboBox()
        self.smb_version_combo.addItems(["SMB2 (推荐)", "SMB1 (Win7兼容)"])
        self.smb_version_combo.setToolTip("SMB1在Win7上更快，但存在安全风险")
        smb_layout.addWidget(self.smb_version_combo, 2, 1)
        
        # 高级选项
        smb_layout.addWidget(QLabel("高级选项:"), 3, 0)
        self.smb_disable_workaround_cb = QCheckBox("禁用文件数量限制解决方案")
        self.smb_disable_workaround_cb.setToolTip("可能提高性能但限制大文件夹中的文件显示")
        smb_layout.addWidget(self.smb_disable_workaround_cb, 3, 1)
        
        smb_group.setLayout(smb_layout)
        layout.addWidget(smb_group)
        
        # SMB警告
        warning_group = QGroupBox("⚠️ 重要警告")
        warning_layout = QVBoxLayout()
        
        warning_text = QTextEdit()
        warning_text.setMaximumHeight(100)
        warning_text.setReadOnly(True)
        warning_text.setStyleSheet("background-color: #fff3cd; color: #856404;")
        warning_text.setPlainText("""SMB功能警告:
• 不建议在WAN环境使用，存在安全风险
• 性能较慢，建议优先使用WebDAV
• 需要安装依赖: pip install impacket==0.11.0
• 只读模式的安全性未完全确认""")
        
        warning_layout.addWidget(warning_text)
        warning_group.setLayout(warning_layout)
        layout.addWidget(warning_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_help_tab(self):
        """创建连接说明标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText("""网络服务连接说明

=== WebDAV 连接 ===
Windows:
1. 右键"我的电脑" → "映射网络驱动器"
2. 文件夹: http://192.168.1.100:3923/
3. 用户名: 您的密码 (推荐)
4. 密码: 可为空或任意值

Linux/macOS:
• 使用rclone: rclone mount webdav:/ /mnt/copyparty
• 文件管理器: 连接到服务器 → http://IP:端口

=== TFTP 连接 ===
上传文件:
• curl -T firmware.bin tftp://192.168.1.100:3969/
• tftp -i 192.168.1.100 put firmware.bin

下载文件:
• curl tftp://192.168.1.100:3969/firmware.bin -o firmware.bin
• tftp -i 192.168.1.100 get firmware.bin

=== SMB/CIFS 连接 ===
Windows:
• \\\\192.168.1.100:3945 (如果使用非标准端口)
• 网络驱动器映射

Linux:
• mount -t cifs //192.168.1.100/share /mnt/smb
• smbclient //192.168.1.100/share

macOS:
• Finder → 连接服务器 → smb://192.168.1.100

=== 端口转发 (可选) ===
如需使用标准端口，可配置NAT转发:

Linux iptables:
• TFTP: iptables -t nat -A PREROUTING -i eth0 -p udp --dport 69 -j REDIRECT --to-port 3969
• SMB: iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 445 -j REDIRECT --to-port 3945

=== 故障排除 ===
• 检查防火墙设置
• 确认服务器正在运行
• 验证网络连接
• 查看服务器日志获取详细错误信息""")
        
        layout.addWidget(help_text)
        widget.setLayout(layout)
        return widget

    def update_smb_mode(self, mode):
        """更新SMB模式（互斥选择）"""
        if mode == -1:  # 取消选择，不做处理
            return
            
        # 暂时断开信号连接
        self.smb_disabled_cb.toggled.disconnect()
        self.smb_readonly_cb.toggled.disconnect()
        self.smb_readwrite_cb.toggled.disconnect()
        
        # 更新状态
        self.smb_disabled_cb.setChecked(mode == 0)
        self.smb_readonly_cb.setChecked(mode == 1)
        self.smb_readwrite_cb.setChecked(mode == 2)
        
        # 重新连接信号
        self.smb_disabled_cb.toggled.connect(lambda checked: self.update_smb_mode(0 if checked else -1))
        self.smb_readonly_cb.toggled.connect(lambda checked: self.update_smb_mode(1 if checked else -1))
        self.smb_readwrite_cb.toggled.connect(lambda checked: self.update_smb_mode(2 if checked else -1))

    def load_config(self):
        """加载配置"""
        # WebDAV配置
        self.webdav_auth_cb.setChecked(self.network_config.webdav_auth_required)
        
        # TFTP配置
        self.tftp_enabled_cb.setChecked(self.network_config.tftp_enabled)
        self.tftp_port_spin.setValue(self.network_config.tftp_port)
        self.tftp_port_range_edit.setText(self.network_config.tftp_port_range)
        
        # SMB配置
        if not self.network_config.smb_enabled and not self.network_config.smb_write_enabled:
            self.update_smb_mode(0)  # 禁用
        elif self.network_config.smb_enabled and not self.network_config.smb_write_enabled:
            self.update_smb_mode(1)  # 只读
        else:
            self.update_smb_mode(2)  # 读写
            
        self.smb_port_spin.setValue(self.network_config.smb_port)
        self.smb_version_combo.setCurrentIndex(0 if self.network_config.smb_version == 2 else 1)
        self.smb_disable_workaround_cb.setChecked(self.network_config.smb_disable_workaround)

    def save_config(self):
        """保存配置"""
        try:
            # WebDAV配置
            self.network_config.webdav_auth_required = self.webdav_auth_cb.isChecked()
            
            # TFTP配置
            self.network_config.tftp_enabled = self.tftp_enabled_cb.isChecked()
            self.network_config.tftp_port = self.tftp_port_spin.value()
            self.network_config.tftp_port_range = self.tftp_port_range_edit.text().strip()
            
            # SMB配置
            if self.smb_disabled_cb.isChecked():
                self.network_config.smb_enabled = False
                self.network_config.smb_write_enabled = False
            elif self.smb_readonly_cb.isChecked():
                self.network_config.smb_enabled = True
                self.network_config.smb_write_enabled = False
            else:  # 读写模式
                self.network_config.smb_enabled = False
                self.network_config.smb_write_enabled = True
                
            self.network_config.smb_port = self.smb_port_spin.value()
            self.network_config.smb_version = 2 if self.smb_version_combo.currentIndex() == 0 else 1
            self.network_config.smb_disable_workaround = self.smb_disable_workaround_cb.isChecked()
            
            # 保存配置
            self.config_manager.save_config()
            
            QMessageBox.information(self, "成功", "网络服务配置已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")

    def test_connections(self):
        """测试网络服务连接"""
        QMessageBox.information(self, "测试连接", 
                               "连接测试功能开发中\n\n"
                               "请手动测试各项服务:\n"
                               "1. 启动服务器\n"
                               "2. 使用相应客户端连接\n"
                               "3. 查看连接说明标签页获取详细方法")
