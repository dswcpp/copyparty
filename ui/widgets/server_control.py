"""
服务器控制组件
迁移自 copyparty_ultimate_gui.py 中的控制面板逻辑
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QPushButton, QLabel, QTabWidget,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class ServerControlWidget(QWidget):
    """服务器控制组件 - 迁移控制面板逻辑"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.server_manager = app.server_manager
        
        # 状态变量
        self.server_running = False
        self.current_connections = 0
        self.server_uptime = 0
        
        self.init_ui()
        self.init_timers()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 服务器控制组
        self.create_server_control_group(layout)
        
        # 服务器状态组
        self.create_server_status_group(layout)
        
        # 性能监控组
        self.create_performance_group(layout)
        
        # 快速操作组
        self.create_quick_actions_group(layout)
        
        # 管理工具组（标签页）
        self.create_management_tools_group(layout)
        
        # 配置管理组
        self.create_config_group(layout)
        
        # 配置预设组
        self.create_presets_group(layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_server_control_group(self, parent_layout):
        """创建服务器控制组"""
        group = QGroupBox("服务器控制")
        layout = QHBoxLayout()
        layout.setSpacing(5)
        
        self.start_btn = QPushButton("▶️ 启动")
        self.start_btn.clicked.connect(self.start_server)
        self.start_btn.setMaximumHeight(30)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMaximumHeight(30)
        layout.addWidget(self.stop_btn)
        
        self.restart_btn = QPushButton("🔄 重启")
        self.restart_btn.clicked.connect(self.restart_server)
        self.restart_btn.setEnabled(False)
        self.restart_btn.setMaximumHeight(30)
        layout.addWidget(self.restart_btn)
        
        group.setLayout(layout)
        group.setMaximumHeight(70)
        parent_layout.addWidget(group)
    
    def create_server_status_group(self, parent_layout):
        """创建服务器状态组"""
        group = QGroupBox("状态")
        layout = QGridLayout()
        layout.setSpacing(3)
        
        # 第一行：状态和端口
        layout.addWidget(QLabel("状态:"), 0, 0)
        self.status_label = QLabel("已停止")
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.status_label, 0, 1)
        
        layout.addWidget(QLabel("端口:"), 0, 2)
        self.port_label = QLabel("-")
        self.port_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.port_label, 0, 3)
        
        # 第二行：地址
        layout.addWidget(QLabel("地址:"), 1, 0)
        self.url_label = QLabel("-")
        self.url_label.setStyleSheet("font-size: 11px;")
        self.url_label.setWordWrap(True)
        layout.addWidget(self.url_label, 1, 1, 1, 3)
        
        # 第三行：运行时间和连接数
        layout.addWidget(QLabel("运行:"), 2, 0)
        self.uptime_label = QLabel("-")
        self.uptime_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.uptime_label, 2, 1)
        
        layout.addWidget(QLabel("连接:"), 2, 2)
        self.connections_label = QLabel("-")
        self.connections_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.connections_label, 2, 3)
        
        group.setLayout(layout)
        group.setMaximumHeight(100)
        parent_layout.addWidget(group)
    
    def create_performance_group(self, parent_layout):
        """创建性能监控组"""
        group = QGroupBox("性能")
        layout = QGridLayout()
        layout.setSpacing(3)
        
        # CPU 和内存在一行
        layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_label = QLabel("-")
        self.cpu_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.cpu_label, 0, 1)
        
        layout.addWidget(QLabel("内存:"), 0, 2)
        self.memory_label = QLabel("-")
        self.memory_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.memory_label, 0, 3)
        
        # PID 单独一行
        layout.addWidget(QLabel("PID:"), 1, 0)
        self.pid_label = QLabel("-")
        self.pid_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.pid_label, 1, 1, 1, 3)
        
        group.setLayout(layout)
        group.setMaximumHeight(80)
        parent_layout.addWidget(group)
    
    def create_quick_actions_group(self, parent_layout):
        """创建快速操作组"""
        group = QGroupBox("快速操作")
        layout = QGridLayout()
        layout.setSpacing(3)
        
        # 第一行：浏览器和复制
        self.open_browser_btn = QPushButton("🌐 浏览器")
        self.open_browser_btn.clicked.connect(self.open_in_browser)
        self.open_browser_btn.setEnabled(False)
        self.open_browser_btn.setMaximumHeight(28)
        layout.addWidget(self.open_browser_btn, 0, 0)
        
        self.copy_url_btn = QPushButton("📋 复制")
        self.copy_url_btn.clicked.connect(self.copy_url)
        self.copy_url_btn.setEnabled(False)
        self.copy_url_btn.setMaximumHeight(28)
        layout.addWidget(self.copy_url_btn, 0, 1)
        
        # 第二行：文件夹和二维码
        self.open_folder_btn = QPushButton("📁 目录")
        self.open_folder_btn.clicked.connect(self.open_working_directory)
        self.open_folder_btn.setMaximumHeight(28)
        layout.addWidget(self.open_folder_btn, 1, 0)
        
        self.generate_qr_btn = QPushButton("📱 二维码")
        self.generate_qr_btn.clicked.connect(self.generate_qr_code)
        self.generate_qr_btn.setEnabled(False)
        self.generate_qr_btn.setMaximumHeight(28)
        layout.addWidget(self.generate_qr_btn, 1, 1)
        
        group.setLayout(layout)
        group.setMaximumHeight(90)
        parent_layout.addWidget(group)
    
    def create_management_tools_group(self, parent_layout):
        """创建管理工具组（标签页）"""
        group = QGroupBox("管理工具")
        layout = QVBoxLayout()
        layout.setSpacing(3)
        
        # 创建标签页
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setMaximumHeight(120)
        
        # 文件管理标签
        file_widget = QWidget()
        file_layout = QGridLayout()
        file_layout.setSpacing(2)
        
        add_volume_btn = QPushButton("➕ 添加目录")
        add_volume_btn.setMaximumHeight(25)
        file_layout.addWidget(add_volume_btn, 0, 0)
        
        manage_volumes_btn = QPushButton("📂 管理目录")
        manage_volumes_btn.setMaximumHeight(25)
        file_layout.addWidget(manage_volumes_btn, 0, 1)
        
        check_permissions_btn = QPushButton("🔐 检查权限")
        check_permissions_btn.setMaximumHeight(25)
        file_layout.addWidget(check_permissions_btn, 1, 0, 1, 2)
        
        file_widget.setLayout(file_layout)
        self.tools_tabs.addTab(file_widget, "文件")
        
        # 用户管理标签
        user_widget = QWidget()
        user_layout = QGridLayout()
        user_layout.setSpacing(2)
        
        add_user_btn = QPushButton("👤 添加用户")
        add_user_btn.setMaximumHeight(25)
        user_layout.addWidget(add_user_btn, 0, 0)
        
        manage_users_btn = QPushButton("👥 管理用户")
        manage_users_btn.setMaximumHeight(25)
        user_layout.addWidget(manage_users_btn, 0, 1)
        
        view_sessions_btn = QPushButton("🔗 查看会话")
        view_sessions_btn.setMaximumHeight(25)
        user_layout.addWidget(view_sessions_btn, 1, 0, 1, 2)
        
        user_widget.setLayout(user_layout)
        self.tools_tabs.addTab(user_widget, "用户")
        
        # 网络工具标签
        network_widget = QWidget()
        network_layout = QGridLayout()
        network_layout.setSpacing(2)
        
        test_port_btn = QPushButton("🔍 测试端口")
        test_port_btn.setMaximumHeight(25)
        network_layout.addWidget(test_port_btn, 0, 0)
        
        scan_network_btn = QPushButton("📡 扫描网络")
        scan_network_btn.setMaximumHeight(25)
        network_layout.addWidget(scan_network_btn, 0, 1)
        
        check_firewall_btn = QPushButton("🛡️ 防火墙")
        check_firewall_btn.setMaximumHeight(25)
        network_layout.addWidget(check_firewall_btn, 1, 0, 1, 2)
        
        network_widget.setLayout(network_layout)
        self.tools_tabs.addTab(network_widget, "网络")
        
        layout.addWidget(self.tools_tabs)
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def create_config_group(self, parent_layout):
        """创建配置管理组"""
        group = QGroupBox("配置")
        layout = QGridLayout()
        layout.setSpacing(3)
        
        # 第一行：保存和加载
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_config)
        save_btn.setMaximumHeight(28)
        layout.addWidget(save_btn, 0, 0)
        
        load_btn = QPushButton("📂 加载")
        load_btn.clicked.connect(self.load_config)
        load_btn.setMaximumHeight(28)
        layout.addWidget(load_btn, 0, 1)
        
        # 第二行：重置
        reset_btn = QPushButton("🔄 重置")
        reset_btn.clicked.connect(self.reset_config)
        reset_btn.setMaximumHeight(28)
        layout.addWidget(reset_btn, 1, 0, 1, 2)
        
        group.setLayout(layout)
        group.setMaximumHeight(90)
        parent_layout.addWidget(group)
    
    def create_presets_group(self, parent_layout):
        """创建配置预设组"""
        group = QGroupBox("预设")
        layout = QVBoxLayout()
        layout.setSpacing(3)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["选择预设...", "基础服务器", "安全服务器", "媒体服务器", "开发服务器"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.preset_combo.setMaximumHeight(30)
        layout.addWidget(self.preset_combo)
        
        group.setLayout(layout)
        group.setMaximumHeight(70)
        parent_layout.addWidget(group)
    
    def init_timers(self):
        """初始化定时器"""
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # 2秒更新一次
    
    def start_server(self):
        """启动服务器"""
        try:
            # 验证配置
            result = self.config_manager.validate_all()
            if not result.is_valid:
                QMessageBox.warning(self, "配置错误", f"配置验证失败:\n{result.errors[0]}")
                return
            
            # 启动服务器
            self.server_manager.start_server()
            
            # 更新UI状态
            self.server_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            
            self.status_label.setText("运行中")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px;")
            
            # 启用快速操作按钮
            self.open_browser_btn.setEnabled(True)
            self.copy_url_btn.setEnabled(True)
            self.generate_qr_btn.setEnabled(True)
            
            # 更新地址和端口
            ports = self.config_manager.network_config.get_listen_ports_list()
            if ports:
                self.port_label.setText(str(ports[0]))
            
            # 生成URL
            url = self.generate_server_url()
            self.url_label.setText(url)
            
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"服务器启动失败: {str(e)}")
    
    def stop_server(self):
        """停止服务器"""
        try:
            self.server_manager.stop_server()
            
            # 更新UI状态
            self.server_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            
            self.status_label.setText("已停止")
            self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")
            
            # 禁用快速操作按钮
            self.open_browser_btn.setEnabled(False)
            self.copy_url_btn.setEnabled(False)
            self.generate_qr_btn.setEnabled(False)
            
            # 清空状态
            self.url_label.setText("-")
            self.port_label.setText("-")
            self.uptime_label.setText("-")
            self.connections_label.setText("-")
            
        except Exception as e:
            QMessageBox.critical(self, "停止失败", f"服务器停止失败: {str(e)}")
    
    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        self.start_server()
    
    def update_status(self):
        """更新状态显示"""
        if self.server_running:
            # 更新运行时间
            self.server_uptime += 2
            hours = self.server_uptime // 3600
            minutes = (self.server_uptime % 3600) // 60
            seconds = self.server_uptime % 60
            self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # 更新连接数（模拟）
            self.connections_label.setText(str(self.current_connections))
    
    def generate_server_url(self) -> str:
        """生成服务器URL"""
        # 获取配置
        network_config = self.config_manager.network_config
        security_config = self.config_manager.security_config
        
        # 确定协议
        protocol = "https" if security_config.tls.https_only else "http"
        
        # 确定IP
        listen_ips = network_config.listen_ips
        if listen_ips in ["::", "0.0.0.0"]:
            # 获取本地IP
            ip = self.get_local_ip()
        else:
            ip = listen_ips.split(',')[0].strip()
        
        # 确定端口
        ports = network_config.get_listen_ports_list()
        port = ports[0] if ports else 3923
        
        return f"{protocol}://{ip}:{port}"
    
    def get_local_ip(self) -> str:
        """获取本地IP地址"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "localhost"
    
    # 快速操作方法
    def open_in_browser(self):
        """在浏览器中打开"""
        url = self.url_label.text()
        if url and url != "-":
            import webbrowser
            webbrowser.open(url)
    
    def copy_url(self):
        """复制URL"""
        url = self.url_label.text()
        if url and url != "-":
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(url)
            QMessageBox.information(self, "成功", "地址已复制到剪贴板")
    
    def open_working_directory(self):
        """打开工作目录"""
        import subprocess
        import platform
        
        work_dir = self.config_manager.server_config.working_directory
        try:
            if platform.system() == "Windows":
                os.startfile(work_dir)
            elif platform.system() == "Darwin":
                subprocess.run(["open", work_dir])
            else:
                subprocess.run(["xdg-open", work_dir])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开目录: {str(e)}")
    
    def generate_qr_code(self):
        """生成二维码"""
        url = self.url_label.text()
        if url and url != "-":
            # TODO: 实现二维码生成
            QMessageBox.information(self, "二维码", f"二维码功能开发中\nURL: {url}")
    
    # 配置操作方法
    def save_config(self):
        """保存配置"""
        try:
            self.config_manager.save_config()
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
    
    def load_config(self):
        """加载配置"""
        # TODO: 实现配置加载对话框
        QMessageBox.information(self, "加载配置", "配置加载功能开发中")
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置配置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            QMessageBox.information(self, "成功", "配置已重置")
    
    def on_preset_changed(self, preset_name):
        """预设选择改变"""
        if preset_name != "选择预设...":
            # TODO: 实现预设加载
            QMessageBox.information(self, "预设", f"预设 '{preset_name}' 功能开发中")
            self.preset_combo.setCurrentIndex(0)
    
    def refresh(self):
        """刷新组件"""
        # 更新状态显示
        self.update_status()
