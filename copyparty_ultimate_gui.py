#!/usr/bin/env python3
"""
CopyParty 终极桌面应用 - 100% 源码覆盖
严格遵循 copyparty/__main__.py 中的所有配置选项
"""

import sys
import os
import json
import subprocess
import threading
import time
import webbrowser
import platform
from typing import List, Dict, Any, Optional
from datetime import datetime

# 可选依赖处理
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("警告: psutil 模块未安装，性能监控功能将被禁用")

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 导入完整配置系统
from copyparty_complete_config import (
    CopyPartyCompleteConfig, GeneralConfig, NetworkConfig, TLSConfig, CertConfig,
    AuthConfig, PasswordChangeConfig, QRConfig, ZeroconfConfig, MDNSConfig, SSDPConfig,
    FilesystemConfig, ShareConfig, UploadConfig, DatabaseConfig, ThumbnailConfig,
    TranscodingConfig, ProtocolConfig, SecurityConfig, UIConfig, LoggingConfig,
    AdminConfig, HandlersConfig, HooksConfig, StatsConfig, YoloConfig, OptoutsConfig,
    SafetyConfig, SaltConfig, ShutdownConfig, CompleteLoggingConfig, TailConfig,
    RSSConfig, DatabaseGeneralConfig, DatabaseMetadataConfig, TextConfig,
    OpenGraphConfig, CompleteUIConfig, WebDAVConfig, DebugConfig
)

# 导入界面组件
from copyparty_complete_widgets import GeneralConfigWidget, CompleteNetworkConfigWidget


class CopyPartyServerThread(QThread):
    """CopyParty 服务器线程 - 增强版"""

    log_message = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    server_started = pyqtSignal(str, int)
    server_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)
    performance_update = pyqtSignal(dict)  # 新增：性能监控信号
    connection_count = pyqtSignal(int)     # 新增：连接数信号

    def __init__(self, config: CopyPartyCompleteConfig):
        super().__init__()
        self.config = config
        self.server_process = None
        self.should_stop = False
        self.start_time = None
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance)
        self.performance_timer.setInterval(2000)  # 每2秒更新一次

    def get_local_ip(self):
        """获取局域网IP地址"""
        try:
            import socket
            # 创建一个UDP socket连接到外部地址来获取本机IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 连接到一个外部地址（不会实际发送数据）
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception:
            try:
                # 备用方法：获取主机名对应的IP
                import socket
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                # 如果获取到的是127.0.0.1，尝试其他方法
                if local_ip.startswith("127."):
                    # 尝试获取所有网络接口
                    import subprocess
                    import platform

                    if platform.system() == "Windows":
                        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "IPv4" in line and "192.168." in line:
                                ip = line.split(':')[-1].strip()
                                if ip and not ip.startswith("127."):
                                    return ip
                    else:
                        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
                        ips = result.stdout.strip().split()
                        for ip in ips:
                            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                                return ip

                return local_ip if not local_ip.startswith("127.") else "localhost"
            except Exception:
                return "localhost"
    
    def run(self):
        """运行服务器"""
        try:
            # 生成命令行参数
            args = self.config.to_args()
            
            # 构建完整命令
            cmd = [sys.executable, "-m", "copyparty"] + args
            
            self.log_message.emit(f"启动命令: {' '.join(cmd)}")
            
            # 启动服务器进程
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.config.working_directory
            )
            
            # 解析端口
            port = int(self.config.network.listen_ports.split(',')[0].split('-')[0])
            
            # 生成 URL - 修复为使用局域网IP
            interface = self.config.network.listen_ips
            if interface == "::" or interface == "0.0.0.0":
                # 获取局域网IP地址
                interface = self.get_local_ip()

            protocol = "https" if self.config.tls.https_only else "http"
            url = f"{protocol}://{interface}:{port}"
            
            self.server_started.emit(url, port)
            self.status_changed.emit("服务器运行中")
            self.start_time = time.time()

            # 同时发送局域网URL供二维码使用
            if hasattr(self, 'parent') and hasattr(self.parent(), 'set_lan_url'):
                self.parent().set_lan_url(url)

            # 启动性能监控
            self.performance_timer.start()

            # 读取服务器输出
            while self.server_process and self.server_process.poll() is None:
                if self.should_stop:
                    break

                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        self.log_message.emit(line.strip())
                        # 解析连接数等信息
                        self.parse_server_output(line.strip())
                except:
                    break

            if self.server_process:
                self.server_process.wait()
            
        except Exception as e:
            self.error_occurred.emit(f"服务器启动失败: {str(e)}")
        finally:
            self.performance_timer.stop()
            self.server_stopped.emit()
            self.status_changed.emit("服务器已停止")

    def parse_server_output(self, line: str):
        """解析服务器输出，提取有用信息"""
        try:
            # 解析连接数信息
            if "clients:" in line.lower():
                import re
                match = re.search(r'clients:\s*(\d+)', line.lower())
                if match:
                    count = int(match.group(1))
                    self.connection_count.emit(count)
        except:
            pass

    def update_performance(self):
        """更新性能信息"""
        if not self.server_process:
            return

        try:
            # 计算运行时间
            uptime = time.time() - self.start_time if self.start_time else 0

            # 基本性能数据
            perf_data = {
                'uptime': uptime,
                'pid': self.server_process.pid
            }

            # 如果有 psutil，获取详细信息
            if HAS_PSUTIL:
                try:
                    process = psutil.Process(self.server_process.pid)
                    cpu_percent = process.cpu_percent()
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024

                    perf_data.update({
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_mb
                    })
                except:
                    pass
            else:
                # 没有 psutil 时的默认值
                perf_data.update({
                    'cpu_percent': 0.0,
                    'memory_mb': 0.0
                })

            # 发送性能数据
            self.performance_update.emit(perf_data)
        except:
            pass

    def stop_server(self):
        """停止服务器"""
        self.should_stop = True
        self.performance_timer.stop()
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
            self.server_process = None


class UltimateMainWindow(QMainWindow):
    """CopyParty 终极主窗口 - 增强版"""

    def __init__(self):
        super().__init__()
        self.config = CopyPartyCompleteConfig()
        self.server_thread = None
        self.current_connections = 0
        self.server_uptime = 0
        self.config_file_path = None
        self.lan_url = None  # 局域网URL，用于二维码生成
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_config)
        self.auto_save_timer.setInterval(30000)  # 30秒自动保存

        # 设置应用图标和样式
        self.setup_appearance()
        self.init_ui()
        self.load_default_config()
        self.setup_shortcuts()

        # 启动自动保存
        self.auto_save_timer.start()

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+S 保存配置
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_config)

        # Ctrl+O 加载配置
        load_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        load_shortcut.activated.connect(self.load_config)

        # F5 启动/重启服务器
        start_shortcut = QShortcut(QKeySequence("F5"), self)
        start_shortcut.activated.connect(self.toggle_server)

        # Ctrl+Q 退出
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

    def toggle_server(self):
        """切换服务器状态"""
        if self.server_thread and self.server_thread.isRunning():
            self.stop_server()
        else:
            self.start_server()

    def auto_save_config(self):
        """自动保存配置"""
        if self.config_file_path:
            try:
                self.save_current_config()
                self.config.save_to_file(self.config_file_path)
            except:
                pass  # 静默失败

    def setup_appearance(self):
        """设置外观和样式"""
        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

        # 设置现代化紧凑样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                border: none;
                color: white;
                padding: 4px 8px;
                text-align: center;
                font-size: 12px;
                border-radius: 3px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 4px 8px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 2px 4px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                font-size: 12px;
            }
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 3px;
            }
        """)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("CopyParty 终极桌面应用")
        self.setGeometry(100, 100, 1200, 700)  # 减小窗口尺寸
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧控制面板
        self.create_control_panel(main_layout)
        
        # 右侧配置面板
        self.create_config_panel(main_layout)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_control_panel(self, main_layout):
        """创建左侧控制面板"""
        control_panel = QWidget()
        control_panel.setFixedWidth(280)  # 减小宽度
        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)  # 减小间距
        control_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        control_panel.setLayout(control_layout)
        
        # 服务器控制组 - 使用水平布局
        server_group = QGroupBox("服务器控制")
        server_layout = QHBoxLayout()  # 改为水平布局
        server_layout.setSpacing(5)

        self.start_btn = QPushButton("▶️ 启动")
        self.start_btn.clicked.connect(self.start_server)
        self.start_btn.setMaximumHeight(30)  # 限制按钮高度
        server_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMaximumHeight(30)
        server_layout.addWidget(self.stop_btn)

        self.restart_btn = QPushButton("🔄 重启")
        self.restart_btn.clicked.connect(self.restart_server)
        self.restart_btn.setEnabled(False)
        self.restart_btn.setMaximumHeight(30)
        server_layout.addWidget(self.restart_btn)

        server_group.setLayout(server_layout)
        server_group.setMaximumHeight(70)  # 限制组高度
        control_layout.addWidget(server_group)
        
        # 服务器状态组 - 紧凑布局
        status_group = QGroupBox("状态")
        status_layout = QGridLayout()  # 使用网格布局
        status_layout.setSpacing(3)

        # 第一行：状态和端口
        status_layout.addWidget(QLabel("状态:"), 0, 0)
        self.status_label = QLabel("已停止")
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.status_label, 0, 1)

        status_layout.addWidget(QLabel("端口:"), 0, 2)
        self.port_label = QLabel("-")
        self.port_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.port_label, 0, 3)

        # 第二行：地址
        status_layout.addWidget(QLabel("地址:"), 1, 0)
        self.url_label = QLabel("-")
        self.url_label.setStyleSheet("font-size: 11px;")
        self.url_label.setWordWrap(True)
        status_layout.addWidget(self.url_label, 1, 1, 1, 3)  # 跨列显示

        # 第三行：运行时间和连接数
        status_layout.addWidget(QLabel("运行:"), 2, 0)
        self.uptime_label = QLabel("-")
        self.uptime_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.uptime_label, 2, 1)

        status_layout.addWidget(QLabel("连接:"), 2, 2)
        self.connections_label = QLabel("-")
        self.connections_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.connections_label, 2, 3)

        status_group.setLayout(status_layout)
        status_group.setMaximumHeight(100)  # 限制高度
        control_layout.addWidget(status_group)

        # 性能监控组 - 紧凑布局
        perf_group = QGroupBox("性能")
        perf_layout = QGridLayout()
        perf_layout.setSpacing(3)

        # CPU 和内存在一行
        perf_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_label = QLabel("-")
        self.cpu_label.setStyleSheet("font-size: 12px;")
        perf_layout.addWidget(self.cpu_label, 0, 1)

        perf_layout.addWidget(QLabel("内存:"), 0, 2)
        self.memory_label = QLabel("-")
        self.memory_label.setStyleSheet("font-size: 12px;")
        perf_layout.addWidget(self.memory_label, 0, 3)

        # PID 单独一行
        perf_layout.addWidget(QLabel("PID:"), 1, 0)
        self.pid_label = QLabel("-")
        self.pid_label.setStyleSheet("font-size: 12px;")
        perf_layout.addWidget(self.pid_label, 1, 1, 1, 3)

        perf_group.setLayout(perf_layout)
        perf_group.setMaximumHeight(80)  # 限制高度
        control_layout.addWidget(perf_group)
        
        # 快速操作组 - 网格布局
        quick_group = QGroupBox("快速操作")
        quick_layout = QGridLayout()
        quick_layout.setSpacing(3)

        # 第一行：浏览器和复制
        self.open_browser_btn = QPushButton("🌐 浏览器")
        self.open_browser_btn.clicked.connect(self.open_in_browser)
        self.open_browser_btn.setEnabled(False)
        self.open_browser_btn.setMaximumHeight(28)
        quick_layout.addWidget(self.open_browser_btn, 0, 0)

        self.copy_url_btn = QPushButton("📋 复制")
        self.copy_url_btn.clicked.connect(self.copy_url)
        self.copy_url_btn.setEnabled(False)
        self.copy_url_btn.setMaximumHeight(28)
        quick_layout.addWidget(self.copy_url_btn, 0, 1)

        # 第二行：文件夹和二维码
        self.open_folder_btn = QPushButton("📁 目录")
        self.open_folder_btn.clicked.connect(self.open_working_directory)
        self.open_folder_btn.setMaximumHeight(28)
        quick_layout.addWidget(self.open_folder_btn, 1, 0)

        self.generate_qr_btn = QPushButton("📱 二维码")
        self.generate_qr_btn.clicked.connect(self.generate_qr_code)
        self.generate_qr_btn.setEnabled(False)
        self.generate_qr_btn.setMaximumHeight(28)
        quick_layout.addWidget(self.generate_qr_btn, 1, 1)

        quick_group.setLayout(quick_layout)
        quick_group.setMaximumHeight(90)  # 限制高度
        control_layout.addWidget(quick_group)

        # 管理工具组 - 使用标签页
        tools_group = QGroupBox("管理工具")
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(3)

        # 创建标签页
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setMaximumHeight(120)  # 限制标签页高度

        # 文件管理标签
        file_widget = QWidget()
        file_layout = QGridLayout()
        file_layout.setSpacing(2)

        self.add_volume_btn = QPushButton("➕ 添加目录")
        self.add_volume_btn.clicked.connect(self.add_volume_quick)
        self.add_volume_btn.setMaximumHeight(25)
        file_layout.addWidget(self.add_volume_btn, 0, 0)

        self.manage_volumes_btn = QPushButton("📂 管理目录")
        self.manage_volumes_btn.clicked.connect(self.manage_volumes)
        self.manage_volumes_btn.setMaximumHeight(25)
        file_layout.addWidget(self.manage_volumes_btn, 0, 1)

        self.check_permissions_btn = QPushButton("🔐 检查权限")
        self.check_permissions_btn.clicked.connect(self.check_file_permissions)
        self.check_permissions_btn.setMaximumHeight(25)
        file_layout.addWidget(self.check_permissions_btn, 1, 0, 1, 2)

        file_widget.setLayout(file_layout)
        self.tools_tabs.addTab(file_widget, "文件")

        # 用户管理标签
        user_widget = QWidget()
        user_layout = QGridLayout()
        user_layout.setSpacing(2)

        self.add_user_btn = QPushButton("👤 添加用户")
        self.add_user_btn.clicked.connect(self.add_user_quick)
        self.add_user_btn.setMaximumHeight(25)
        user_layout.addWidget(self.add_user_btn, 0, 0)

        self.manage_users_btn = QPushButton("👥 管理用户")
        self.manage_users_btn.clicked.connect(self.manage_users)
        self.manage_users_btn.setMaximumHeight(25)
        user_layout.addWidget(self.manage_users_btn, 0, 1)

        self.view_sessions_btn = QPushButton("🔗 查看会话")
        self.view_sessions_btn.clicked.connect(self.view_active_sessions)
        self.view_sessions_btn.setMaximumHeight(25)
        user_layout.addWidget(self.view_sessions_btn, 1, 0, 1, 2)

        user_widget.setLayout(user_layout)
        self.tools_tabs.addTab(user_widget, "用户")

        tools_layout.addWidget(self.tools_tabs)
        tools_group.setLayout(tools_layout)
        control_layout.addWidget(tools_group)
        
        # 配置和工具组 - 继续使用标签页
        # 网络工具标签
        network_widget = QWidget()
        network_layout = QGridLayout()
        network_layout.setSpacing(2)

        self.test_port_btn = QPushButton("🔍 测试端口")
        self.test_port_btn.clicked.connect(self.test_port)
        self.test_port_btn.setMaximumHeight(25)
        network_layout.addWidget(self.test_port_btn, 0, 0)

        self.scan_network_btn = QPushButton("📡 扫描网络")
        self.scan_network_btn.clicked.connect(self.scan_network)
        self.scan_network_btn.setMaximumHeight(25)
        network_layout.addWidget(self.scan_network_btn, 0, 1)

        self.check_firewall_btn = QPushButton("🛡️ 防火墙")
        self.check_firewall_btn.clicked.connect(self.check_firewall)
        self.check_firewall_btn.setMaximumHeight(25)
        network_layout.addWidget(self.check_firewall_btn, 1, 0, 1, 2)

        network_widget.setLayout(network_layout)
        self.tools_tabs.addTab(network_widget, "网络")

        # 系统工具标签
        system_widget = QWidget()
        system_layout = QGridLayout()
        system_layout.setSpacing(2)

        self.create_shortcut_btn = QPushButton("🔗 快捷方式")
        self.create_shortcut_btn.clicked.connect(self.create_desktop_shortcut)
        self.create_shortcut_btn.setMaximumHeight(25)
        system_layout.addWidget(self.create_shortcut_btn, 0, 0)

        self.open_logs_btn = QPushButton("📄 日志目录")
        self.open_logs_btn.clicked.connect(self.open_logs_directory)
        self.open_logs_btn.setMaximumHeight(25)
        system_layout.addWidget(self.open_logs_btn, 0, 1)

        self.install_service_btn = QPushButton("⚙️ 系统服务")
        self.install_service_btn.clicked.connect(self.install_as_service)
        self.install_service_btn.setMaximumHeight(25)
        system_layout.addWidget(self.install_service_btn, 1, 0, 1, 2)

        system_widget.setLayout(system_layout)
        self.tools_tabs.addTab(system_widget, "系统")

        # 配置管理组 - 紧凑布局
        config_group = QGroupBox("配置")
        config_layout = QGridLayout()
        config_layout.setSpacing(3)

        # 第一行：保存和加载
        self.save_config_btn = QPushButton("� 保存")
        self.save_config_btn.clicked.connect(self.save_config)
        self.save_config_btn.setMaximumHeight(28)
        config_layout.addWidget(self.save_config_btn, 0, 0)

        self.load_config_btn = QPushButton("� 加载")
        self.load_config_btn.clicked.connect(self.load_config)
        self.load_config_btn.setMaximumHeight(28)
        config_layout.addWidget(self.load_config_btn, 0, 1)

        # 第二行：重置
        self.reset_config_btn = QPushButton("� 重置")
        self.reset_config_btn.clicked.connect(self.reset_config)
        self.reset_config_btn.setMaximumHeight(28)
        config_layout.addWidget(self.reset_config_btn, 1, 0, 1, 2)

        config_group.setLayout(config_layout)
        config_group.setMaximumHeight(90)
        control_layout.addWidget(config_group)

        # 配置预设组 - 下拉菜单
        preset_group = QGroupBox("预设")
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(3)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["选择预设...", "基础服务器", "安全服务器", "媒体服务器", "开发服务器"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.preset_combo.setMaximumHeight(30)
        preset_layout.addWidget(self.preset_combo)

        preset_group.setLayout(preset_layout)
        preset_group.setMaximumHeight(70)
        control_layout.addWidget(preset_group)
        
        # 日志显示 - 更紧凑
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()
        log_layout.setSpacing(3)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)  # 减小高度
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-size: 11px; font-family: Consolas, monospace;")
        log_layout.addWidget(self.log_text)

        # 日志控制按钮
        log_btn_layout = QHBoxLayout()
        log_btn_layout.setSpacing(3)

        clear_log_btn = QPushButton("清空")
        clear_log_btn.setMaximumHeight(25)
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_btn_layout.addWidget(clear_log_btn)

        save_log_btn = QPushButton("保存")
        save_log_btn.setMaximumHeight(25)
        save_log_btn.clicked.connect(self.save_log)
        log_btn_layout.addWidget(save_log_btn)

        log_btn_layout.addStretch()
        log_layout.addLayout(log_btn_layout)

        log_group.setLayout(log_layout)
        log_group.setMaximumHeight(180)  # 限制整个日志组高度
        control_layout.addWidget(log_group)

        control_layout.addStretch()
        main_layout.addWidget(control_panel)
    
    def create_config_panel(self, main_layout):
        """创建右侧配置面板"""
        config_panel = QWidget()
        config_layout = QVBoxLayout()
        config_panel.setLayout(config_layout)
        
        # 配置标签页
        self.config_tabs = QTabWidget()

        # 通用配置
        self.general_widget = GeneralConfigWidget(self.config)
        self.config_tabs.addTab(self.general_widget, "🔧 通用配置")

        # 网络配置
        self.network_widget = CompleteNetworkConfigWidget(self.config)
        self.config_tabs.addTab(self.network_widget, "🌐 网络配置")

        # 添加更多配置标签页
        self.add_additional_config_tabs()

        config_layout.addWidget(self.config_tabs)
        main_layout.addWidget(config_panel)

    def add_additional_config_tabs(self):
        """添加额外的配置标签页"""
        # SSL/TLS 配置
        ssl_widget = self.create_ssl_config_widget()
        self.config_tabs.addTab(ssl_widget, "🔒 SSL/TLS")

        # 数据库配置
        db_widget = self.create_database_config_widget()
        self.config_tabs.addTab(db_widget, "🗄️ 数据库")

        # 上传配置
        upload_widget = self.create_upload_config_widget()
        self.config_tabs.addTab(upload_widget, "📤 上传配置")

        # 安全配置
        security_widget = self.create_security_config_widget()
        self.config_tabs.addTab(security_widget, "🛡️ 安全配置")

        # 高级配置
        advanced_widget = self.create_advanced_config_widget()
        self.config_tabs.addTab(advanced_widget, "⚙️ 高级配置")

    def create_ssl_config_widget(self):
        """创建 SSL 配置组件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # SSL 基本设置
        ssl_group = QGroupBox("SSL/TLS 设置")
        ssl_layout = QFormLayout()

        self.https_only_cb = QCheckBox("仅 HTTPS")
        ssl_layout.addRow("", self.https_only_cb)

        self.http_only_cb = QCheckBox("仅 HTTP")
        ssl_layout.addRow("", self.http_only_cb)

        self.cert_path_edit = QLineEdit()
        cert_browse_btn = QPushButton("浏览...")
        cert_browse_btn.clicked.connect(lambda: self.browse_file(self.cert_path_edit, "选择证书文件"))
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.cert_path_edit)
        cert_layout.addWidget(cert_browse_btn)
        ssl_layout.addRow("证书路径:", cert_layout)

        ssl_group.setLayout(ssl_layout)
        layout.addWidget(ssl_group)

        # 证书生成设置
        cert_group = QGroupBox("证书生成")
        cert_gen_layout = QFormLayout()

        self.cert_domains_edit = QLineEdit()
        self.cert_domains_edit.setPlaceholderText("example.com,*.example.com")
        cert_gen_layout.addRow("域名列表:", self.cert_domains_edit)

        self.cert_cn_edit = QLineEdit()
        self.cert_cn_edit.setText("partyco")
        cert_gen_layout.addRow("通用名称:", self.cert_cn_edit)

        cert_group.setLayout(cert_gen_layout)
        layout.addWidget(cert_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_database_config_widget(self):
        """创建数据库配置组件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 数据库基本设置
        db_group = QGroupBox("数据库设置")
        db_layout = QFormLayout()

        self.enable_db_cb = QCheckBox("启用数据库 (-e2d)")
        db_layout.addRow("", self.enable_db_cb)

        self.scan_on_startup_cb = QCheckBox("启动时扫描 (-e2ds)")
        db_layout.addRow("", self.scan_on_startup_cb)

        self.enable_metadata_cb = QCheckBox("启用元数据索引 (-e2t)")
        db_layout.addRow("", self.enable_metadata_cb)

        self.hash_threads_spin = QSpinBox()
        self.hash_threads_spin.setRange(1, 32)
        self.hash_threads_spin.setValue(5)
        db_layout.addRow("哈希线程数:", self.hash_threads_spin)

        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_upload_config_widget(self):
        """创建上传配置组件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 上传基本设置
        upload_group = QGroupBox("上传设置")
        upload_layout = QFormLayout()

        self.enable_upload_cb = QCheckBox("启用上传")
        upload_layout.addRow("", self.enable_upload_cb)

        self.enable_dedup_cb = QCheckBox("启用去重 (--dedup)")
        upload_layout.addRow("", self.enable_dedup_cb)

        self.chmod_dir_edit = QLineEdit()
        self.chmod_dir_edit.setText("755")
        upload_layout.addRow("目录权限:", self.chmod_dir_edit)

        self.chmod_file_edit = QLineEdit()
        self.chmod_file_edit.setText("644")
        upload_layout.addRow("文件权限:", self.chmod_file_edit)

        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_security_config_widget(self):
        """创建安全配置组件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 安全基本设置
        security_group = QGroupBox("安全设置")
        security_layout = QFormLayout()

        self.early_ban_cb = QCheckBox("早期封禁 (--early-ban)")
        security_layout.addRow("", self.early_ban_cb)

        self.vague_403_cb = QCheckBox("模糊 403 错误 (--vague-403)")
        security_layout.addRow("", self.vague_403_cb)

        self.logout_hours_spin = QDoubleSpinBox()
        self.logout_hours_spin.setRange(0.1, 8760.0)
        self.logout_hours_spin.setValue(8086.0)
        self.logout_hours_spin.setSuffix(" 小时")
        security_layout.addRow("登出时间:", self.logout_hours_spin)

        security_group.setLayout(security_layout)
        layout.addWidget(security_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_advanced_config_widget(self):
        """创建高级配置组件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 高级设置
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout()

        self.debug_mode_cb = QCheckBox("调试模式 (--debug)")
        advanced_layout.addRow("", self.debug_mode_cb)

        self.verbose_mode_cb = QCheckBox("详细模式 (--verbose)")
        advanced_layout.addRow("", self.verbose_mode_cb)

        self.log_file_edit = QLineEdit()
        log_browse_btn = QPushButton("浏览...")
        log_browse_btn.clicked.connect(lambda: self.browse_file(self.log_file_edit, "选择日志文件", save=True))
        log_layout = QHBoxLayout()
        log_layout.addWidget(self.log_file_edit)
        log_layout.addWidget(log_browse_btn)
        advanced_layout.addRow("日志文件:", log_layout)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def browse_file(self, line_edit: QLineEdit, title: str, save: bool = False):
        """浏览文件对话框"""
        if save:
            file_path, _ = QFileDialog.getSaveFileName(self, title, "", "所有文件 (*)")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, title, "", "所有文件 (*)")

        if file_path:
            line_edit.setText(file_path)

    def load_basic_preset(self):
        """加载基础服务器预设"""
        self.config = CopyPartyCompleteConfig()
        self.config.general.server_name = "基础服务器"
        self.config.network.listen_ports = "3923"
        self.config.network.listen_ips = "::"
        self.load_default_config()
        QMessageBox.information(self, "预设", "已加载基础服务器配置")

    def load_secure_preset(self):
        """加载安全服务器预设"""
        self.config = CopyPartyCompleteConfig()
        self.config.general.server_name = "安全服务器"
        self.config.network.listen_ports = "3923"
        self.config.tls.https_only = True
        self.config.cert.auto_cert = True
        self.config.security.early_ban = True
        self.config.security.vague_403 = True
        self.config.auth.anon_read = False
        self.load_default_config()
        QMessageBox.information(self, "预设", "已加载安全服务器配置")

    def load_media_preset(self):
        """加载媒体服务器预设"""
        self.config = CopyPartyCompleteConfig()
        self.config.general.server_name = "媒体服务器"
        self.config.network.listen_ports = "3923"
        self.config.database.enable_database = True
        self.config.database.enable_metadata = True
        self.config.thumbnail.enable_thumbnails = True
        self.config.transcoding.enable_transcoding = True
        self.load_default_config()
        QMessageBox.information(self, "预设", "已加载媒体服务器配置")

    def load_dev_preset(self):
        """加载开发服务器预设"""
        self.config = CopyPartyCompleteConfig()
        self.config.general.server_name = "开发服务器"
        self.config.network.listen_ports = "8080"
        self.config.upload.enable_upload = True
        self.config.debug.debug_mode = True
        self.config.debug.verbose_mode = True
        self.config.auth.anon_read = True
        self.config.auth.anon_write = True
        self.load_default_config()
        QMessageBox.information(self, "预设", "已加载开发服务器配置")

    def on_preset_changed(self, preset_name):
        """预设选择改变处理"""
        if preset_name == "基础服务器":
            self.load_basic_preset()
        elif preset_name == "安全服务器":
            self.load_secure_preset()
        elif preset_name == "媒体服务器":
            self.load_media_preset()
        elif preset_name == "开发服务器":
            self.load_dev_preset()

        # 重置下拉框
        if preset_name != "选择预设...":
            self.preset_combo.setCurrentIndex(0)

    def save_log(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "copyparty_log.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "成功", "日志已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        save_action = QAction("保存配置", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction("加载配置", self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 服务器菜单
        server_menu = menubar.addMenu("服务器")
        
        start_action = QAction("启动", self)
        start_action.triggered.connect(self.start_server)
        server_menu.addAction(start_action)
        
        stop_action = QAction("停止", self)
        stop_action.triggered.connect(self.stop_server)
        server_menu.addAction(stop_action)
        
        restart_action = QAction("重启", self)
        restart_action.triggered.connect(self.restart_server)
        server_menu.addAction(restart_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
    
    def load_default_config(self):
        """加载默认配置"""
        # 加载配置到界面
        self.general_widget.load_config()
        self.network_widget.load_config()

        # 加载到新增的配置组件
        self.load_ssl_config()
        self.load_database_config()
        self.load_upload_config()
        self.load_security_config()
        self.load_advanced_config()

    def load_ssl_config(self):
        """加载 SSL 配置"""
        try:
            self.https_only_cb.setChecked(self.config.tls.https_only)
            self.http_only_cb.setChecked(self.config.tls.http_only)
            self.cert_path_edit.setText(self.config.tls.cert_path)
            self.cert_domains_edit.setText(",".join(self.config.cert.cert_domains))
            self.cert_cn_edit.setText(self.config.cert.cert_common_name)
        except:
            pass

    def load_database_config(self):
        """加载数据库配置"""
        try:
            self.enable_db_cb.setChecked(self.config.database.enable_database)
            self.scan_on_startup_cb.setChecked(self.config.database.scan_on_startup)
            self.enable_metadata_cb.setChecked(self.config.database.enable_metadata)
            self.hash_threads_spin.setValue(self.config.database.hash_threads)
        except:
            pass

    def load_upload_config(self):
        """加载上传配置"""
        try:
            self.enable_upload_cb.setChecked(self.config.upload.enable_upload)
            self.enable_dedup_cb.setChecked(self.config.upload.enable_dedup)
            self.chmod_dir_edit.setText(self.config.upload.chmod_dir)
            self.chmod_file_edit.setText(self.config.upload.chmod_file)
        except:
            pass

    def load_security_config(self):
        """加载安全配置"""
        try:
            self.early_ban_cb.setChecked(self.config.security.early_ban)
            self.vague_403_cb.setChecked(self.config.security.vague_403)
            self.logout_hours_spin.setValue(self.config.security.logout_hours)
        except:
            pass

    def load_advanced_config(self):
        """加载高级配置"""
        try:
            self.debug_mode_cb.setChecked(self.config.debug.debug_mode)
            self.verbose_mode_cb.setChecked(self.config.debug.verbose_mode)
            self.log_file_edit.setText(self.config.complete_logging.log_file)
        except:
            pass
    
    def start_server(self):
        """启动服务器"""
        if self.server_thread and self.server_thread.isRunning():
            return
        
        # 保存当前配置
        self.save_current_config()
        
        # 创建并启动服务器线程
        self.server_thread = CopyPartyServerThread(self.config)
        self.server_thread.log_message.connect(self.add_log)
        self.server_thread.status_changed.connect(self.update_status)
        self.server_thread.server_started.connect(self.on_server_started)
        self.server_thread.server_stopped.connect(self.on_server_stopped)
        self.server_thread.error_occurred.connect(self.on_error)
        self.server_thread.performance_update.connect(self.on_performance_update)
        self.server_thread.connection_count.connect(self.on_connection_count_update)

        self.server_thread.start()

        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.restart_btn.setEnabled(True)

        self.add_log("正在启动服务器...")
    
    def stop_server(self):
        """停止服务器"""
        if self.server_thread:
            self.server_thread.stop_server()
    
    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        QTimer.singleShot(2000, self.start_server)  # 2秒后重启
    
    def save_current_config(self):
        """保存当前配置"""
        self.general_widget.save_config()
        self.network_widget.save_config()

        # 保存新增的配置组件
        self.save_ssl_config()
        self.save_database_config()
        self.save_upload_config()
        self.save_security_config()
        self.save_advanced_config()

    def save_ssl_config(self):
        """保存 SSL 配置"""
        try:
            self.config.tls.https_only = self.https_only_cb.isChecked()
            self.config.tls.http_only = self.http_only_cb.isChecked()
            self.config.tls.cert_path = self.cert_path_edit.text().strip()

            domains_text = self.cert_domains_edit.text().strip()
            if domains_text:
                self.config.cert.cert_domains = [d.strip() for d in domains_text.split(",") if d.strip()]
            else:
                self.config.cert.cert_domains = []

            self.config.cert.cert_common_name = self.cert_cn_edit.text().strip()
        except:
            pass

    def save_database_config(self):
        """保存数据库配置"""
        try:
            self.config.database.enable_database = self.enable_db_cb.isChecked()
            self.config.database.scan_on_startup = self.scan_on_startup_cb.isChecked()
            self.config.database.enable_metadata = self.enable_metadata_cb.isChecked()
            self.config.database.hash_threads = self.hash_threads_spin.value()
        except:
            pass

    def save_upload_config(self):
        """保存上传配置"""
        try:
            self.config.upload.enable_upload = self.enable_upload_cb.isChecked()
            self.config.upload.enable_dedup = self.enable_dedup_cb.isChecked()
            self.config.upload.chmod_dir = self.chmod_dir_edit.text().strip()
            self.config.upload.chmod_file = self.chmod_file_edit.text().strip()
        except:
            pass

    def save_security_config(self):
        """保存安全配置"""
        try:
            self.config.security.early_ban = self.early_ban_cb.isChecked()
            self.config.security.vague_403 = self.vague_403_cb.isChecked()
            self.config.security.logout_hours = self.logout_hours_spin.value()
        except:
            pass

    def save_advanced_config(self):
        """保存高级配置"""
        try:
            self.config.debug.debug_mode = self.debug_mode_cb.isChecked()
            self.config.debug.verbose_mode = self.verbose_mode_cb.isChecked()
            self.config.complete_logging.log_file = self.log_file_edit.text().strip()
        except:
            pass
    
    def save_config(self):
        """保存配置到文件"""
        self.save_current_config()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置", "copyparty_config.json",
            "JSON 文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.config.save_to_file(file_path)
                self.config_file_path = file_path
                QMessageBox.information(self, "成功", "配置已保存")
                self.setWindowTitle(f"CopyParty 终极桌面应用 - {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def load_config(self):
        """从文件加载配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置", "",
            "JSON 文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.config.load_from_file(file_path)
                self.config_file_path = file_path
                self.load_default_config()
                QMessageBox.information(self, "成功", "配置已加载")
                self.setWindowTitle(f"CopyParty 终极桌面应用 - {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认", "确定要重置所有配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = CopyPartyCompleteConfig()
            self.load_default_config()
            QMessageBox.information(self, "成功", "配置已重置")
    
    def open_in_browser(self):
        """在浏览器中打开"""
        url = self.url_label.text()
        if url and url != "-":
            import webbrowser
            webbrowser.open(url)
    
    def copy_url(self):
        """复制地址"""
        url = self.url_label.text()
        if url and url != "-":
            QApplication.clipboard().setText(url)
            self.status_bar.showMessage("地址已复制到剪贴板", 2000)
    
    def add_log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
    
    def update_status(self, status: str):
        """更新状态"""
        self.status_label.setText(status)
        if status == "服务器运行中":
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def on_server_started(self, url: str, port: int):
        """服务器启动处理"""
        self.url_label.setText(url)
        self.port_label.setText(str(port))
        self.lan_url = url  # 保存局域网URL用于二维码
        self.open_browser_btn.setEnabled(True)
        self.copy_url_btn.setEnabled(True)
        self.generate_qr_btn.setEnabled(True)  # 启用二维码按钮
        self.status_bar.showMessage(f"服务器已启动: {url}")
    
    def on_server_stopped(self):
        """服务器停止处理"""
        self.url_label.setText("-")
        self.port_label.setText("-")
        self.lan_url = None  # 清除局域网URL
        self.open_browser_btn.setEnabled(False)
        self.copy_url_btn.setEnabled(False)
        self.generate_qr_btn.setEnabled(False)  # 禁用二维码按钮

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)

        self.status_bar.showMessage("服务器已停止")
    
    def on_performance_update(self, perf_data: dict):
        """性能数据更新处理"""
        try:
            # 更新运行时间
            uptime = perf_data.get('uptime', 0)
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # 更新 CPU 使用率
            cpu_percent = perf_data.get('cpu_percent', 0)
            self.cpu_label.setText(f"{cpu_percent:.1f}%")

            # 更新内存使用
            memory_mb = perf_data.get('memory_mb', 0)
            self.memory_label.setText(f"{memory_mb:.1f} MB")

            # 更新进程 ID
            pid = perf_data.get('pid', 0)
            self.pid_label.setText(str(pid))
        except:
            pass

    def on_connection_count_update(self, count: int):
        """连接数更新处理"""
        self.current_connections = count
        self.connections_label.setText(str(count))

    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
        self.add_log(f"错误: {error}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "CopyParty 终极桌面应用\n\n"
            "100% 源码覆盖的完整配置管理工具\n"
            "严格遵循 CopyParty 源码中的所有配置选项\n\n"
            "版本: 1.0.0"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.server_thread and self.server_thread.isRunning():
            reply = QMessageBox.question(
                self, "确认", "服务器正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_server()
                if self.server_thread:
                    self.server_thread.wait(3000)  # 等待3秒
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # ==================== 新增操作功能实现 ====================

    def open_working_directory(self):
        """打开工作目录"""
        try:
            work_dir = self.config.working_directory
            if platform.system() == "Windows":
                os.startfile(work_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", work_dir])
            else:  # Linux
                subprocess.run(["xdg-open", work_dir])
        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法打开目录: {str(e)}")

    def generate_qr_code(self):
        """生成二维码"""
        # 使用局域网URL而不是显示的URL
        url = self.lan_url if self.lan_url else self.url_label.text()
        if not url or url == "-":
            QMessageBox.warning(self, "警告", "服务器未运行，无法生成二维码")
            return

        try:
            # 尝试使用 qrcode 库生成二维码
            try:
                import qrcode

                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(url)
                qr.make(fit=True)

                # 创建二维码图片
                img = qr.make_image(fill_color="black", back_color="white")

                # 保存到临时文件
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                img.save(temp_file.name)

                # 显示二维码对话框
                self.show_qr_dialog(temp_file.name, url)

            except ImportError:
                # 如果没有 qrcode 库，显示文本二维码和安装提示
                self.show_text_qr_dialog(url)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成二维码失败: {str(e)}")

    def show_qr_dialog(self, image_path, url):
        """显示二维码对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("服务器地址二维码")
        dialog.setFixedSize(400, 500)

        layout = QVBoxLayout()

        # 显示二维码图片
        label = QLabel()
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # 显示URL
        url_label = QLabel(f"地址: {url}")
        url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_label.setWordWrap(True)
        layout.addWidget(url_label)

        # 按钮
        btn_layout = QHBoxLayout()
        copy_btn = QPushButton("复制地址")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(url))
        save_btn = QPushButton("保存图片")
        save_btn.clicked.connect(lambda: self.save_qr_image(image_path))
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

        # 清理临时文件
        try:
            os.unlink(image_path)
        except:
            pass

    def show_text_qr_dialog(self, url):
        """显示文本二维码对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("服务器地址 - 二维码")
        dialog.setFixedSize(500, 350)

        layout = QVBoxLayout()

        # 标题信息
        title_label = QLabel("📱 服务器地址二维码")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007bff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 说明信息
        info_label = QLabel("qrcode 库未安装，无法生成图片二维码。\n您可以复制下面的地址或安装二维码库。")
        info_label.setStyleSheet("color: #6c757d; margin: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # URL 显示
        url_group = QGroupBox("服务器地址")
        url_layout = QVBoxLayout()

        url_edit = QLineEdit(url)
        url_edit.setReadOnly(True)
        url_edit.setStyleSheet("font-size: 14px; padding: 8px; background-color: #f8f9fa;")
        url_layout.addWidget(url_edit)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # 使用说明
        usage_group = QGroupBox("使用说明")
        usage_layout = QVBoxLayout()

        usage_text = QLabel(
            "1. 复制上面的地址到手机浏览器\n"
            "2. 或者安装 qrcode 库生成图片二维码\n"
            "3. 手机和电脑需要在同一网络中"
        )
        usage_text.setStyleSheet("font-size: 12px; color: #495057;")
        usage_layout.addWidget(usage_text)

        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)

        # 按钮区域
        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 复制地址")
        copy_btn.clicked.connect(lambda: self.copy_url_and_notify(url))
        copy_btn.setStyleSheet("background-color: #28a745;")
        btn_layout.addWidget(copy_btn)

        install_btn = QPushButton("📦 安装二维码库")
        install_btn.clicked.connect(self.install_qrcode_lib)
        install_btn.setStyleSheet("background-color: #17a2b8;")
        btn_layout.addWidget(install_btn)

        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def copy_url_and_notify(self, url):
        """复制URL并显示通知"""
        QApplication.clipboard().setText(url)
        QMessageBox.information(self, "成功", "地址已复制到剪贴板！")

    def save_qr_image(self, source_path):
        """保存二维码图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存二维码", "copyparty_qr.png",
            "PNG 图片 (*.png);;所有文件 (*)"
        )

        if file_path:
            try:
                import shutil
                shutil.copy2(source_path, file_path)
                QMessageBox.information(self, "成功", "二维码已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def install_qrcode_lib(self):
        """安装二维码库"""
        # 创建安装确认对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("安装二维码库")
        dialog.setFixedSize(450, 300)

        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("📦 安装 qrcode 库")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007bff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 说明
        info_label = QLabel(
            "qrcode 库可以生成漂亮的二维码图片。\n"
            "安装后您就可以:\n"
            "• 生成高质量的二维码图片\n"
            "• 保存二维码到本地\n"
            "• 方便手机扫码访问"
        )
        info_label.setStyleSheet("margin: 15px; color: #495057;")
        layout.addWidget(info_label)

        # 安装命令显示
        cmd_group = QGroupBox("安装命令")
        cmd_layout = QVBoxLayout()

        cmd_text = QLineEdit("pip install qrcode[pil]")
        cmd_text.setReadOnly(True)
        cmd_text.setStyleSheet("font-family: Consolas, monospace; background-color: #f8f9fa; padding: 8px;")
        cmd_layout.addWidget(cmd_text)

        copy_cmd_btn = QPushButton("📋 复制命令")
        copy_cmd_btn.clicked.connect(lambda: QApplication.clipboard().setText("pip install qrcode[pil]"))
        cmd_layout.addWidget(copy_cmd_btn)

        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        # 按钮
        btn_layout = QHBoxLayout()

        auto_install_btn = QPushButton("🚀 自动安装")
        auto_install_btn.clicked.connect(lambda: self.auto_install_qrcode(dialog))
        auto_install_btn.setStyleSheet("background-color: #28a745;")
        btn_layout.addWidget(auto_install_btn)

        manual_btn = QPushButton("📝 手动安装")
        manual_btn.clicked.connect(lambda: self.show_manual_install_guide())
        btn_layout.addWidget(manual_btn)

        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def auto_install_qrcode(self, parent_dialog):
        """自动安装qrcode库"""
        try:
            # 显示进度对话框
            progress = QProgressDialog("正在安装 qrcode 库...", "取消", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            # 执行安装
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "qrcode[pil]"],
                capture_output=True, text=True, timeout=60
            )

            progress.close()

            if result.returncode == 0:
                parent_dialog.close()
                QMessageBox.information(
                    self, "安装成功",
                    "qrcode 库安装成功！\n现在可以生成漂亮的二维码图片了。"
                )
            else:
                QMessageBox.critical(
                    self, "安装失败",
                    f"自动安装失败，请尝试手动安装。\n\n错误信息:\n{result.stderr}"
                )
        except subprocess.TimeoutExpired:
            progress.close()
            QMessageBox.warning(self, "安装超时", "安装超时，请检查网络连接或尝试手动安装。")
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "安装错误", f"安装过程出错: {str(e)}")

    def show_manual_install_guide(self):
        """显示手动安装指南"""
        guide_text = """
手动安装 qrcode 库指南:

1. 打开命令提示符 (Windows) 或终端 (Linux/macOS)

2. 运行以下命令:
   pip install qrcode[pil]

3. 如果上述命令失败，尝试:
   python -m pip install qrcode[pil]

4. 如果仍然失败，可能需要:
   - 检查网络连接
   - 使用国内镜像源
   - 更新 pip: python -m pip install --upgrade pip

5. 安装完成后重新启动应用程序

国内镜像源安装命令:
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrcode[pil]
        """

        QMessageBox.information(self, "手动安装指南", guide_text)

    def add_volume_quick(self):
        """快速添加共享目录"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加共享目录")
        dialog.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # 目录选择
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("目录路径:"))
        self.volume_path_edit = QLineEdit()
        dir_browse_btn = QPushButton("浏览...")
        dir_browse_btn.clicked.connect(self.browse_volume_directory)
        dir_layout.addWidget(self.volume_path_edit)
        dir_layout.addWidget(dir_browse_btn)
        layout.addLayout(dir_layout)

        # 别名设置
        alias_layout = QHBoxLayout()
        alias_layout.addWidget(QLabel("别名:"))
        self.volume_alias_edit = QLineEdit()
        self.volume_alias_edit.setPlaceholderText("可选，如: files")
        alias_layout.addWidget(self.volume_alias_edit)
        layout.addLayout(alias_layout)

        # 权限设置
        perm_group = QGroupBox("权限设置")
        perm_layout = QVBoxLayout()

        self.read_perm_cb = QCheckBox("读取 (r)")
        self.read_perm_cb.setChecked(True)
        perm_layout.addWidget(self.read_perm_cb)

        self.write_perm_cb = QCheckBox("写入 (w)")
        perm_layout.addWidget(self.write_perm_cb)

        self.upload_perm_cb = QCheckBox("上传 (u)")
        perm_layout.addWidget(self.upload_perm_cb)

        self.delete_perm_cb = QCheckBox("删除 (d)")
        perm_layout.addWidget(self.delete_perm_cb)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        # 按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(lambda: self.confirm_add_volume(dialog))
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def browse_volume_directory(self):
        """浏览卷目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择共享目录")
        if dir_path:
            self.volume_path_edit.setText(dir_path)
            # 自动生成别名
            if not self.volume_alias_edit.text():
                alias = os.path.basename(dir_path)
                self.volume_alias_edit.setText(alias)

    def confirm_add_volume(self, dialog):
        """确认添加卷"""
        path = self.volume_path_edit.text().strip()
        alias = self.volume_alias_edit.text().strip()

        if not path:
            QMessageBox.warning(dialog, "警告", "请选择目录路径")
            return

        if not os.path.exists(path):
            QMessageBox.warning(dialog, "警告", "目录不存在")
            return

        # 构建权限字符串
        perms = []
        if self.read_perm_cb.isChecked():
            perms.append("r")
        if self.write_perm_cb.isChecked():
            perms.append("w")
        if self.upload_perm_cb.isChecked():
            perms.append("u")
        if self.delete_perm_cb.isChecked():
            perms.append("d")

        perm_str = "".join(perms) if perms else "r"

        # 构建卷字符串
        if alias:
            volume_str = f"{path}:{alias}:{perm_str}"
        else:
            volume_str = f"{path}::{perm_str}"

        # 添加到配置
        self.config.general.volumes.append(volume_str)

        # 刷新界面
        self.general_widget.load_config()

        dialog.close()
        QMessageBox.information(self, "成功", f"已添加共享目录: {alias or os.path.basename(path)}")

    def manage_volumes(self):
        """管理共享目录"""
        dialog = QDialog(self)
        dialog.setWindowTitle("管理共享目录")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # 卷列表
        self.volumes_list = QListWidget()
        self.refresh_volumes_list()
        layout.addWidget(QLabel("当前共享目录:"))
        layout.addWidget(self.volumes_list)

        # 按钮
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_selected_volume)
        remove_btn = QPushButton("删除")
        remove_btn.clicked.connect(self.remove_selected_volume)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_volumes_list)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        self.volumes_dialog = dialog  # 保存引用
        dialog.exec()

    def refresh_volumes_list(self):
        """刷新卷列表"""
        if hasattr(self, 'volumes_list'):
            self.volumes_list.clear()
            for volume in self.config.general.volumes:
                self.volumes_list.addItem(volume)

    def edit_selected_volume(self):
        """编辑选中的卷"""
        current_item = self.volumes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self.volumes_dialog, "警告", "请选择要编辑的目录")
            return

        volume_str = current_item.text()
        # 这里可以实现编辑功能，暂时显示信息
        QMessageBox.information(self.volumes_dialog, "编辑", f"编辑功能开发中\n当前卷: {volume_str}")

    def remove_selected_volume(self):
        """删除选中的卷"""
        current_item = self.volumes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self.volumes_dialog, "警告", "请选择要删除的目录")
            return

        volume_str = current_item.text()
        reply = QMessageBox.question(
            self.volumes_dialog, "确认删除", f"确定要删除共享目录吗？\n{volume_str}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config.general.volumes.remove(volume_str)
            self.refresh_volumes_list()
            self.general_widget.load_config()
            QMessageBox.information(self.volumes_dialog, "成功", "共享目录已删除")

    def check_file_permissions(self):
        """检查文件权限"""
        dialog = QDialog(self)
        dialog.setWindowTitle("文件权限检查")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()

        # 检查结果显示
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        layout.addWidget(QLabel("权限检查结果:"))
        layout.addWidget(result_text)

        # 开始检查
        check_results = []

        # 检查工作目录权限
        work_dir = self.config.working_directory
        try:
            if os.access(work_dir, os.R_OK):
                check_results.append(f"✓ 工作目录可读: {work_dir}")
            else:
                check_results.append(f"✗ 工作目录不可读: {work_dir}")

            if os.access(work_dir, os.W_OK):
                check_results.append(f"✓ 工作目录可写: {work_dir}")
            else:
                check_results.append(f"✗ 工作目录不可写: {work_dir}")
        except Exception as e:
            check_results.append(f"✗ 工作目录检查失败: {e}")

        # 检查共享目录权限
        for volume in self.config.general.volumes:
            try:
                # 解析卷字符串
                parts = volume.split(':')
                if len(parts) >= 1:
                    vol_path = parts[0]
                    if os.path.exists(vol_path):
                        if os.access(vol_path, os.R_OK):
                            check_results.append(f"✓ 共享目录可读: {vol_path}")
                        else:
                            check_results.append(f"✗ 共享目录不可读: {vol_path}")

                        if os.access(vol_path, os.W_OK):
                            check_results.append(f"✓ 共享目录可写: {vol_path}")
                        else:
                            check_results.append(f"✗ 共享目录不可写: {vol_path}")
                    else:
                        check_results.append(f"✗ 共享目录不存在: {vol_path}")
            except Exception as e:
                check_results.append(f"✗ 共享目录检查失败: {e}")

        result_text.setText("\n".join(check_results))

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def add_user_quick(self):
        """快速添加用户"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加用户")
        dialog.setFixedSize(400, 250)

        layout = QVBoxLayout()

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)

        # 权限
        perm_group = QGroupBox("权限")
        perm_layout = QVBoxLayout()

        self.admin_perm_cb = QCheckBox("管理员权限")
        perm_layout.addWidget(self.admin_perm_cb)

        self.upload_perm_user_cb = QCheckBox("上传权限")
        perm_layout.addWidget(self.upload_perm_user_cb)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        # 按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(lambda: self.confirm_add_user(dialog))
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def confirm_add_user(self, dialog):
        """确认添加用户"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username:
            QMessageBox.warning(dialog, "警告", "请输入用户名")
            return

        if not password:
            QMessageBox.warning(dialog, "警告", "请输入密码")
            return

        # 构建用户字符串
        user_str = f"{username}:{password}"

        # 添加权限
        if self.admin_perm_cb.isChecked():
            user_str += ":a"  # admin
        elif self.upload_perm_user_cb.isChecked():
            user_str += ":u"  # upload

        # 添加到配置
        self.config.general.accounts.append(user_str)

        # 刷新界面
        self.general_widget.load_config()

        dialog.close()
        QMessageBox.information(self, "成功", f"已添加用户: {username}")

    def manage_users(self):
        """管理用户"""
        dialog = QDialog(self)
        dialog.setWindowTitle("用户管理")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # 用户列表
        self.users_list = QListWidget()
        self.refresh_users_list()
        layout.addWidget(QLabel("当前用户:"))
        layout.addWidget(self.users_list)

        # 按钮
        btn_layout = QHBoxLayout()
        edit_user_btn = QPushButton("编辑")
        edit_user_btn.clicked.connect(self.edit_selected_user)
        remove_user_btn = QPushButton("删除")
        remove_user_btn.clicked.connect(self.remove_selected_user)
        refresh_user_btn = QPushButton("刷新")
        refresh_user_btn.clicked.connect(self.refresh_users_list)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(edit_user_btn)
        btn_layout.addWidget(remove_user_btn)
        btn_layout.addWidget(refresh_user_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        self.users_dialog = dialog
        dialog.exec()

    def refresh_users_list(self):
        """刷新用户列表"""
        if hasattr(self, 'users_list'):
            self.users_list.clear()
            for account in self.config.general.accounts:
                # 隐藏密码显示
                parts = account.split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    permissions = ':'.join(parts[2:]) if len(parts) > 2 else "普通用户"
                    display_text = f"{username} ({permissions})"
                else:
                    display_text = account
                self.users_list.addItem(display_text)

    def edit_selected_user(self):
        """编辑选中用户"""
        current_row = self.users_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.users_dialog, "警告", "请选择要编辑的用户")
            return

        # 暂时显示信息
        account = self.config.general.accounts[current_row]
        QMessageBox.information(self.users_dialog, "编辑", f"编辑功能开发中\n当前用户: {account.split(':')[0]}")

    def remove_selected_user(self):
        """删除选中用户"""
        current_row = self.users_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.users_dialog, "警告", "请选择要删除的用户")
            return

        account = self.config.general.accounts[current_row]
        username = account.split(':')[0]

        reply = QMessageBox.question(
            self.users_dialog, "确认删除", f"确定要删除用户吗？\n用户名: {username}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.config.general.accounts[current_row]
            self.refresh_users_list()
            self.general_widget.load_config()
            QMessageBox.information(self.users_dialog, "成功", f"用户 {username} 已删除")

    def view_active_sessions(self):
        """查看活动会话"""
        dialog = QDialog(self)
        dialog.setWindowTitle("活动会话")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout()

        info_label = QLabel("活动会话监控功能需要服务器运行时才能获取数据")
        layout.addWidget(info_label)

        # 会话列表
        sessions_text = QTextEdit()
        sessions_text.setReadOnly(True)

        if self.server_thread and self.server_thread.isRunning():
            sessions_text.setText("会话监控功能开发中...\n当前连接数: " + str(self.current_connections))
        else:
            sessions_text.setText("服务器未运行，无法获取会话信息")

        layout.addWidget(sessions_text)

        # 刷新按钮
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(lambda: sessions_text.setText(
            "会话监控功能开发中...\n当前连接数: " + str(self.current_connections)
            if self.server_thread and self.server_thread.isRunning()
            else "服务器未运行，无法获取会话信息"
        ))
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def test_port(self):
        """测试端口"""
        port_str = self.config.network.listen_ports
        ports = []

        # 解析端口
        for port_part in port_str.split(','):
            port_part = port_part.strip()
            if '-' in port_part:
                start, end = port_part.split('-')
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(port_part))

        dialog = QDialog(self)
        dialog.setWindowTitle("端口测试")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()

        result_text = QTextEdit()
        result_text.setReadOnly(True)
        layout.addWidget(QLabel("端口测试结果:"))
        layout.addWidget(result_text)

        # 测试端口
        results = []
        for port in ports[:10]:  # 限制测试前10个端口
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                if result == 0:
                    results.append(f"端口 {port}: ✓ 已占用")
                else:
                    results.append(f"端口 {port}: ✓ 可用")
            except Exception as e:
                results.append(f"端口 {port}: ✗ 测试失败 ({e})")

        result_text.setText("\n".join(results))

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def scan_network(self):
        """扫描网络"""
        dialog = QDialog(self)
        dialog.setWindowTitle("网络扫描")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()

        info_label = QLabel("扫描本地网络中的设备...")
        layout.addWidget(info_label)

        result_text = QTextEdit()
        result_text.setReadOnly(True)
        layout.addWidget(result_text)

        # 简单的网络扫描
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            results = [f"本机信息:"]
            results.append(f"主机名: {hostname}")
            results.append(f"本地IP: {local_ip}")
            results.append("")
            results.append("网络扫描功能开发中...")

            result_text.setText("\n".join(results))
        except Exception as e:
            result_text.setText(f"网络扫描失败: {e}")

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def check_firewall(self):
        """检查防火墙"""
        dialog = QDialog(self)
        dialog.setWindowTitle("防火墙检查")
        dialog.setFixedSize(500, 300)

        layout = QVBoxLayout()

        result_text = QTextEdit()
        result_text.setReadOnly(True)
        layout.addWidget(QLabel("防火墙状态检查:"))
        layout.addWidget(result_text)

        results = []
        system = platform.system()

        if system == "Windows":
            results.append("Windows 防火墙检查:")
            results.append("请手动检查 Windows Defender 防火墙设置")
            results.append("确保允许 Python 程序通过防火墙")
        elif system == "Linux":
            results.append("Linux 防火墙检查:")
            results.append("请检查 iptables 或 ufw 设置")
        elif system == "Darwin":
            results.append("macOS 防火墙检查:")
            results.append("请检查系统偏好设置中的防火墙")
        else:
            results.append("未知系统，无法检查防火墙")

        results.append("")
        results.append("建议:")
        results.append("1. 确保防火墙允许配置的端口")
        results.append("2. 检查路由器端口转发设置")
        results.append("3. 验证网络连接")

        result_text.setText("\n".join(results))

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def create_desktop_shortcut(self):
        """创建桌面快捷方式"""
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.expanduser("~")

            if platform.system() == "Windows":
                # Windows 快捷方式
                shortcut_path = os.path.join(desktop, "CopyParty Ultimate.lnk")
                target = sys.executable
                args = os.path.abspath(__file__)

                # 创建简单的批处理文件作为替代
                bat_path = os.path.join(desktop, "CopyParty Ultimate.bat")
                with open(bat_path, 'w') as f:
                    f.write(f'@echo off\n')
                    f.write(f'cd /d "{os.path.dirname(os.path.abspath(__file__))}"\n')
                    f.write(f'"{target}" "{args}"\n')
                    f.write(f'pause\n')

                QMessageBox.information(self, "成功", f"桌面快捷方式已创建:\n{bat_path}")

            else:
                # Linux/macOS 脚本
                script_path = os.path.join(desktop, "copyparty_ultimate.sh")
                with open(script_path, 'w') as f:
                    f.write(f'#!/bin/bash\n')
                    f.write(f'cd "{os.path.dirname(os.path.abspath(__file__))}"\n')
                    f.write(f'"{sys.executable}" "{os.path.abspath(__file__)}"\n')

                os.chmod(script_path, 0o755)
                QMessageBox.information(self, "成功", f"桌面快捷方式已创建:\n{script_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快捷方式失败: {str(e)}")

    def install_as_service(self):
        """安装为系统服务"""
        QMessageBox.information(
            self, "系统服务",
            "系统服务安装功能开发中...\n\n"
            "当前可以通过以下方式实现开机自启:\n"
            "1. 将快捷方式添加到启动文件夹\n"
            "2. 使用任务计划程序 (Windows)\n"
            "3. 使用 systemd (Linux)\n"
            "4. 使用 launchd (macOS)"
        )

    def open_logs_directory(self):
        """打开日志目录"""
        try:
            # 创建日志目录
            logs_dir = os.path.join(self.config.working_directory, "logs")
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            # 打开目录
            if platform.system() == "Windows":
                os.startfile(logs_dir)
            elif platform.system() == "Darwin":
                subprocess.run(["open", logs_dir])
            else:
                subprocess.run(["xdg-open", logs_dir])

        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法打开日志目录: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("CopyParty Ultimate")
    app.setApplicationVersion("1.0.0")

    window = UltimateMainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
