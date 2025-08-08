"""
服务器控制组件
迁移自 copyparty_ultimate_gui.py 中的控制面板逻辑
"""

import sys
import os
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QPushButton, QLabel, QTabWidget,
                             QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QMetaObject
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtSvgWidgets import QSvgWidget

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

        # 注册服务器管理器回调
        self.server_manager.add_status_callback(self.on_server_status_changed)
        self.server_manager.add_log_callback(self.on_server_log_message)

        self.init_ui()
        self.init_timers()

    def on_server_status_changed(self, status: str):
        """服务器状态变化回调（线程安全）"""
        # 使用QTimer.singleShot确保在主线程中执行UI更新
        def update_ui():
            try:
                self.status_label.setText(status)

                # 根据状态更新按钮状态
                if "运行中" in status:
                    self.server_running = True
                    self.start_btn.setEnabled(False)
                    self.stop_btn.setEnabled(True)
                    self.restart_btn.setEnabled(True)
                    self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px;")

                    # 启用快速操作按钮
                    if hasattr(self, 'open_browser_btn'):
                        self.open_browser_btn.setEnabled(True)
                    if hasattr(self, 'copy_url_btn'):
                        self.copy_url_btn.setEnabled(True)
                    if hasattr(self, 'generate_qr_btn'):
                        self.generate_qr_btn.setEnabled(True)

                elif "已停止" in status or "停止" in status:
                    self.server_running = False
                    self.start_btn.setEnabled(True)
                    self.stop_btn.setEnabled(False)
                    self.restart_btn.setEnabled(False)
                    self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")

                    # 禁用快速操作按钮
                    if hasattr(self, 'open_browser_btn'):
                        self.open_browser_btn.setEnabled(False)
                    if hasattr(self, 'copy_url_btn'):
                        self.copy_url_btn.setEnabled(False)
                    if hasattr(self, 'generate_qr_btn'):
                        self.generate_qr_btn.setEnabled(False)

                    # 清空状态
                    self.url_label.setText("-")
                    if hasattr(self, 'port_label'):
                        self.port_label.setText("-")
                    if hasattr(self, 'uptime_label'):
                        self.uptime_label.setText("-")
                    if hasattr(self, 'connections_label'):
                        self.connections_label.setText("-")

                elif "启动" in status or "停止" in status or "重启" in status:
                    # 过程状态
                    self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 12px;")

            except Exception as e:
                print(f"UI更新错误: {e}")

        # 使用QTimer.singleShot在主线程中执行
        QTimer.singleShot(0, update_ui)

    def on_server_log_message(self, message: str):
        """服务器日志消息回调（线程安全）"""
        # 可以在这里处理日志消息，比如显示在状态栏或日志窗口
        print(f"[ServerLog] {message}")

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # Logo和标题组
        self.create_logo_header(layout)

        # 服务器控制组
        self.create_server_control_group(layout)
        
        # 服务器状态组
        self.create_server_status_group(layout)
        
        # 性能监控组
        self.create_performance_group(layout)
        
        # 快速操作组
        self.create_quick_actions_group(layout)

        # 配置管理组
        self.create_config_group(layout)
        
        # 配置预设组
        self.create_presets_group(layout)
        
        layout.addStretch()
        self.setLayout(layout)

    def create_logo_header(self, parent_layout):
        """创建Logo和标题头部"""
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setContentsMargins(10, 10, 10, 15)

        try:
            # 尝试加载logo
            logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'logo.svg')
            if os.path.exists(logo_path):
                # 创建SVG widget显示logo
                logo_widget = QSvgWidget(logo_path)

                # 根据1062:733的精确比例计算尺寸
                # 1062/733 = 1.448840的精确宽高比
                logo_height = 55  # 适合左侧面板的高度
                logo_width = int(logo_height * (1062/733))  # 使用精确比例
                logo_widget.setFixedSize(logo_width, logo_height)

                print(f"✓ Logo尺寸: {logo_width}x{logo_height}px (比例: {logo_width/logo_height:.6f})")

                # 添加样式
                logo_widget.setStyleSheet("""
                    QSvgWidget {
                        background-color: transparent;
                        border: none;
                    }
                """)

                # 居中显示logo
                logo_container = QHBoxLayout()
                logo_container.setContentsMargins(0, 0, 0, 0)
                logo_container.addStretch()
                logo_container.addWidget(logo_widget)
                logo_container.addStretch()

                logo_container_widget = QWidget()
                logo_container_widget.setLayout(logo_container)
                header_layout.addWidget(logo_container_widget)

                print(f"✓ Logo加载成功: {logo_path}")
            else:
                print(f"⚠️ Logo文件不存在: {logo_path}")
                # 如果logo不存在，显示文字标题
                title_label = QLabel("CopyParty")
                title_font = QFont()
                title_font.setPointSize(16)
                title_font.setBold(True)
                title_label.setFont(title_font)
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header_layout.addWidget(title_label)

        except Exception as e:
            print(f"❌ Logo加载失败: {e}")
            # 显示文字标题作为备选
            title_label = QLabel("CopyParty")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("Desktop Manager")
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle_font.setWeight(QFont.Weight.Light)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #888;
            margin-bottom: 8px;
            padding: 2px;
        """)
        header_layout.addWidget(subtitle_label)

        # 添加分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #ddd; margin: 5px 20px;")
        header_layout.addWidget(separator)

        header_widget.setLayout(header_layout)
        parent_layout.addWidget(header_widget)
    
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
        """启动服务器（异步，不阻塞UI）"""
        try:
            # 验证配置
            result = self.config_manager.validate_all()
            if not result.is_valid:
                QMessageBox.warning(self, "配置错误", f"配置验证失败:\n{result.errors[0]}")
                return

            # 异步启动服务器
            self.server_manager.start_server()

            # 立即更新UI状态（启动中）
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)  # 启动过程中禁用停止按钮
            self.restart_btn.setEnabled(False)

            self.status_label.setText("正在启动...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 12px;")

            # 禁用快速操作按钮
            self.open_browser_btn.setEnabled(False)
            self.copy_url_btn.setEnabled(False)
            self.generate_qr_btn.setEnabled(False)

            # 生成预期的URL（实际状态会通过回调更新）
            ports = self.config_manager.network_config.get_listen_ports_list()
            if ports:
                self.port_label.setText(str(ports[0]))

            url = self.generate_server_url()
            self.url_label.setText(url)

        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"服务器启动失败: {str(e)}")
            # 恢复按钮状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
    
    def stop_server(self):
        """停止服务器（异步，不阻塞UI）"""
        try:
            # 异步停止服务器
            self.server_manager.stop_server()

            # 立即更新UI状态（停止中）
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)

            self.status_label.setText("正在停止...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 12px;")

            # 禁用快速操作按钮
            self.open_browser_btn.setEnabled(False)
            self.copy_url_btn.setEnabled(False)
            self.generate_qr_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "停止失败", f"服务器停止失败: {str(e)}")
            # 恢复按钮状态
            if self.server_manager.is_running:
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.restart_btn.setEnabled(True)
            else:
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.restart_btn.setEnabled(False)

    def restart_server(self):
        """重启服务器（异步，不阻塞UI）"""
        try:
            # 异步重启服务器
            self.server_manager.restart_server()

            # 立即更新UI状态（重启中）
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)

            self.status_label.setText("正在重启...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 12px;")

            # 禁用快速操作按钮
            self.open_browser_btn.setEnabled(False)
            self.copy_url_btn.setEnabled(False)
            self.generate_qr_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "重启失败", f"服务器重启失败: {str(e)}")
    
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
        if not url or url == "-":
            QMessageBox.warning(self, "警告", "服务器未运行，无法生成二维码")
            return

        try:
            # 尝试使用qrcode库生成二维码
            try:
                import qrcode
                from qrcode.image.styledpil import StyledPilImage
                from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

                # 创建二维码
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)

                # 生成图片
                img = qr.make_image(
                    fill_color="black",
                    back_color="white",
                    image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer()
                )

                # 显示二维码对话框
                self.show_qr_dialog(img, url)

            except ImportError:
                # 如果没有qrcode库，使用内置的二维码生成器
                self.show_builtin_qr_dialog(url)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成二维码失败: {str(e)}")

    def show_qr_dialog(self, qr_image, url):
        """显示二维码对话框（使用qrcode库）"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PyQt6.QtGui import QPixmap, QFont
        from PyQt6.QtCore import Qt
        import io

        dialog = QDialog(self)
        dialog.setWindowTitle("服务器地址二维码")
        dialog.setFixedSize(450, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("📱 扫码访问服务器")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #007bff; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 二维码图片
        qr_label = QLabel()

        # 将PIL图片转换为QPixmap
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        # 缩放图片
        scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        qr_label.setPixmap(scaled_pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setStyleSheet("border: 2px solid #dee2e6; border-radius: 8px; padding: 10px; background-color: white;")
        layout.addWidget(qr_label)

        # URL显示
        url_label = QLabel("服务器地址:")
        url_label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(url_label)

        url_text = QTextEdit()
        url_text.setPlainText(url)
        url_text.setMaximumHeight(60)
        url_text.setReadOnly(True)
        url_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
                font-family: monospace;
            }
        """)
        layout.addWidget(url_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 复制地址")
        copy_btn.clicked.connect(lambda: self.copy_url_to_clipboard(url))
        button_layout.addWidget(copy_btn)

        save_btn = QPushButton("💾 保存二维码")
        save_btn.clicked.connect(lambda: self.save_qr_image(qr_image))
        button_layout.addWidget(save_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # 使用说明
        info_label = QLabel("💡 使用手机扫描二维码即可快速访问服务器")
        info_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-top: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        dialog.setLayout(layout)
        dialog.exec()

    def show_builtin_qr_dialog(self, url):
        """显示内置二维码对话框（使用CopyParty内置生成器）"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import Qt

        try:
            # 使用CopyParty内置的二维码生成器
            from copyparty.stolen.qrcodegen import QrCode, qr2svg

            # 生成二维码
            qr_code = QrCode.encode_binary(url.encode('utf-8'))
            svg_content = qr2svg(qr_code, 2)

            dialog = QDialog(self)
            dialog.setWindowTitle("服务器地址二维码")
            dialog.setFixedSize(500, 650)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                }
                QLabel {
                    color: #333;
                }
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # 标题
            title_label = QLabel("📱 扫码访问服务器")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #28a745; margin-bottom: 10px;")
            layout.addWidget(title_label)

            # SVG二维码显示
            from PyQt6.QtSvgWidgets import QSvgWidget
            svg_widget = QSvgWidget()
            svg_widget.load(svg_content.encode('utf-8'))
            svg_widget.setFixedSize(300, 300)

            # 居中显示SVG
            svg_container = QHBoxLayout()
            svg_container.addStretch()
            svg_container.addWidget(svg_widget)
            svg_container.addStretch()

            svg_container_widget = QWidget()
            svg_container_widget.setLayout(svg_container)
            svg_container_widget.setStyleSheet("border: 2px solid #dee2e6; border-radius: 8px; padding: 10px; background-color: white;")
            layout.addWidget(svg_container_widget)

            # URL显示
            url_label = QLabel("服务器地址:")
            url_label.setStyleSheet("font-weight: bold; color: #495057;")
            layout.addWidget(url_label)

            url_text = QTextEdit()
            url_text.setPlainText(url)
            url_text.setMaximumHeight(60)
            url_text.setReadOnly(True)
            url_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: #f8f9fa;
                    font-family: monospace;
                }
            """)
            layout.addWidget(url_text)

            # 按钮区域
            button_layout = QHBoxLayout()

            copy_btn = QPushButton("📋 复制地址")
            copy_btn.clicked.connect(lambda: self.copy_url_to_clipboard(url))
            button_layout.addWidget(copy_btn)

            install_btn = QPushButton("📦 安装qrcode库")
            install_btn.clicked.connect(self.show_qrcode_install_dialog)
            button_layout.addWidget(install_btn)

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            # 使用说明
            info_label = QLabel("💡 使用手机扫描二维码即可快速访问服务器\n📦 安装qrcode库可获得更好的二维码效果")
            info_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-top: 10px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            # 如果内置生成器也失败，显示文本二维码
            self.show_text_qr_dialog(url)

    def show_text_qr_dialog(self, url):
        """显示文本二维码对话框（备用方案）"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("服务器地址")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("📱 服务器地址")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #dc3545; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 说明
        info_label = QLabel("二维码生成功能暂时不可用\n请复制下面的地址手动访问")
        info_label.setStyleSheet("color: #6c757d; margin-bottom: 15px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # URL显示
        url_label = QLabel("服务器地址:")
        url_label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(url_label)

        url_text = QTextEdit()
        url_text.setPlainText(url)
        url_text.setMaximumHeight(80)
        url_text.setReadOnly(True)
        url_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 12px;
                background-color: #f8f9fa;
                font-family: monospace;
                font-size: 14px;
            }
        """)
        layout.addWidget(url_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 复制地址")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        copy_btn.clicked.connect(lambda: self.copy_url_to_clipboard(url))
        button_layout.addWidget(copy_btn)

        install_btn = QPushButton("📦 安装qrcode库")
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        install_btn.clicked.connect(self.show_qrcode_install_dialog)
        button_layout.addWidget(install_btn)

        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def copy_url_to_clipboard(self, url):
        """复制URL到剪贴板"""
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        QMessageBox.information(self, "成功", "地址已复制到剪贴板")

    def save_qr_image(self, qr_image):
        """保存二维码图片"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存二维码",
            f"copyparty_qr_{int(time.time())}.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*)"
        )

        if file_path:
            try:
                qr_image.save(file_path)
                QMessageBox.information(self, "成功", f"二维码已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def show_qrcode_install_dialog(self):
        """显示qrcode库安装对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("安装qrcode库")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("📦 安装qrcode库")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #007bff; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 说明
        info_label = QLabel(
            "qrcode库可以生成高质量的二维码图片。\n"
            "安装后您就可以:\n"
            "• 生成美观的二维码图片\n"
            "• 保存二维码到本地\n"
            "• 获得更好的扫码体验"
        )
        info_label.setStyleSheet("color: #495057; margin-bottom: 15px; line-height: 1.5;")
        layout.addWidget(info_label)

        # 安装命令
        cmd_label = QLabel("安装命令:")
        cmd_label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(cmd_label)

        cmd_text = QTextEdit()
        cmd_text.setPlainText("pip install qrcode[pil]")
        cmd_text.setMaximumHeight(40)
        cmd_text.setReadOnly(True)
        cmd_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
                font-family: monospace;
                font-weight: bold;
            }
        """)
        layout.addWidget(cmd_text)

        # 按钮区域
        button_layout = QHBoxLayout()

        copy_cmd_btn = QPushButton("📋 复制命令")
        copy_cmd_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        copy_cmd_btn.clicked.connect(lambda: self.copy_url_to_clipboard("pip install qrcode[pil]"))
        button_layout.addWidget(copy_cmd_btn)

        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # 提示
        tip_label = QLabel("💡 安装完成后重启应用程序即可使用高质量二维码功能")
        tip_label.setStyleSheet("color: #6c757d; font-size: 12px; margin-top: 10px;")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tip_label)

        dialog.setLayout(layout)
        dialog.exec()

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
