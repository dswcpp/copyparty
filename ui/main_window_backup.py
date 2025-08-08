"""
主窗口
迁移自 copyparty_ultimate_gui.py 中的 UltimateMainWindow
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
                             QStatusBar, QMenuBar, QMenu, QMessageBox, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .widgets.server_control import ServerControlWidget
from .widgets.config_editor import ConfigEditorWidget
from .widgets.monitoring_panel import MonitoringPanel, LogViewer
from .widgets.responsive_layout import ResponsiveLayout

# 导入完整配置系统
try:
    from copyparty_complete_config import CopyPartyCompleteConfig
    from copyparty_complete_widgets import GeneralConfigWidget, CompleteNetworkConfigWidget
    COMPLETE_CONFIG_AVAILABLE = True
except ImportError:
    COMPLETE_CONFIG_AVAILABLE = False
    print("⚠️ 完整配置系统不可用，使用基础配置")


class MainWindow(QWidget):
    """主窗口 - 迁移自 UltimateMainWindow"""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.server_manager = app.server_manager

        # 应用主题（如果可用）
        if hasattr(app, 'theme_manager') and app.theme_manager:
            app.theme_manager.apply_theme(self, app.theme_manager.get_current_theme())

        # 初始化UI
        self.init_ui()
        self.apply_styles()

        # 初始化定时器
        self.init_timers()

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 尝试使用方形logo作为窗口图标
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'logo-sq.svg')
            if os.path.exists(icon_path):
                # 对于SVG图标，我们需要先转换为QPixmap
                svg_widget = QSvgWidget(icon_path)
                svg_widget.resize(64, 64)

                # 创建QPixmap并设置为图标
                pixmap = QPixmap(64, 64)
                pixmap.fill(Qt.GlobalColor.transparent)
                svg_widget.render(pixmap)

                icon = QIcon(pixmap)
                self.setWindowIcon(icon)
                print(f"✓ 窗口图标设置成功: {icon_path}")
            else:
                print(f"⚠️ 图标文件不存在: {icon_path}")

        except Exception as e:
            print(f"❌ 设置窗口图标失败: {e}")
            # 使用默认图标
            pass
    
    def init_ui(self):
        """初始化用户界面"""
        # 使用响应式布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 添加工具栏（如果应用程序有的话）
        if hasattr(self.app, 'toolbar'):
            main_layout.addWidget(self.app.toolbar)

        # 创建响应式布局管理器
        self.responsive_layout = ResponsiveLayout()
        self.responsive_layout.layout_changed.connect(self.on_layout_changed)

        # 创建完整功能的控制面板
        self.control_panel = self.create_ultimate_control_panel()

        # 创建完整功能的配置编辑器
        if COMPLETE_CONFIG_AVAILABLE and hasattr(self.app, 'complete_config'):
            self.config_editor = self.create_ultimate_config_editor()
        else:
            self.config_editor = ConfigEditorWidget(self.app)

        self.monitoring_panel = MonitoringPanel(self.app)
        self.log_viewer = LogViewer(self.app)

        # 将组件添加到响应式布局的不同面板
        self.responsive_layout.add_widget_to_panel(self.control_panel, 'left')
        self.responsive_layout.add_widget_to_panel(self.config_editor, 'center')
        self.responsive_layout.add_widget_to_panel(self.monitoring_panel, 'right')
        self.responsive_layout.add_widget_to_panel(self.log_viewer, 'bottom')

        main_layout.addWidget(self.responsive_layout)
        self.setLayout(main_layout)

    def create_ultimate_control_panel(self):
        """创建完整功能的控制面板"""
        from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                                     QPushButton, QGridLayout, QTabWidget, QTextEdit,
                                     QProgressBar, QLabel)

        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(8, 8, 8, 8)

        # 服务器控制组
        server_group = QGroupBox("🎛️ 服务器控制")
        server_layout = QHBoxLayout()
        server_layout.setSpacing(5)

        self.start_btn = QPushButton("▶️ 启动")
        self.start_btn.clicked.connect(self.start_server)
        self.start_btn.setMinimumHeight(32)
        server_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(32)
        server_layout.addWidget(self.stop_btn)

        self.restart_btn = QPushButton("🔄 重启")
        self.restart_btn.clicked.connect(self.restart_server)
        self.restart_btn.setEnabled(False)
        self.restart_btn.setMinimumHeight(32)
        server_layout.addWidget(self.restart_btn)

        server_group.setLayout(server_layout)
        control_layout.addWidget(server_group)

        # 配置预设组
        preset_group = QGroupBox("⚡ 配置预设")
        preset_layout = QGridLayout()
        preset_layout.setSpacing(5)

        quick_btn = QPushButton("🚀 快速服务器")
        quick_btn.clicked.connect(self.load_quick_preset)
        quick_btn.setToolTip("基础文件服务器，快速启动")
        preset_layout.addWidget(quick_btn, 0, 0)

        secure_btn = QPushButton("🛡️ 安全服务器")
        secure_btn.clicked.connect(self.load_secure_preset)
        secure_btn.setToolTip("HTTPS + 认证 + 高级安全")
        preset_layout.addWidget(secure_btn, 0, 1)

        media_btn = QPushButton("🎬 媒体服务器")
        media_btn.clicked.connect(self.load_media_preset)
        media_btn.setToolTip("数据库 + 缩略图 + 转码")
        preset_layout.addWidget(media_btn, 1, 0)

        custom_btn = QPushButton("⚙️ 自定义")
        custom_btn.clicked.connect(self.load_custom_preset)
        custom_btn.setToolTip("自定义配置")
        preset_layout.addWidget(custom_btn, 1, 1)

        preset_group.setLayout(preset_layout)
        control_layout.addWidget(preset_group)

        # 快速操作组
        quick_group = QGroupBox("🔧 快速操作")
        quick_layout = QGridLayout()
        quick_layout.setSpacing(5)

        self.open_browser_btn = QPushButton("🌐 浏览器")
        self.open_browser_btn.clicked.connect(self.open_browser)
        self.open_browser_btn.setEnabled(False)
        quick_layout.addWidget(self.open_browser_btn, 0, 0)

        self.generate_qr_btn = QPushButton("📱 二维码")
        self.generate_qr_btn.clicked.connect(self.generate_qr_code)
        self.generate_qr_btn.setEnabled(False)
        quick_layout.addWidget(self.generate_qr_btn, 0, 1)

        self.copy_url_btn = QPushButton("📋 复制URL")
        self.copy_url_btn.clicked.connect(self.copy_url)
        self.copy_url_btn.setEnabled(False)
        quick_layout.addWidget(self.copy_url_btn, 1, 0)

        self.open_folder_btn = QPushButton("📁 文件夹")
        self.open_folder_btn.clicked.connect(self.open_server_folder)
        quick_layout.addWidget(self.open_folder_btn, 1, 1)

        quick_group.setLayout(quick_layout)
        control_layout.addWidget(quick_group)

        return control_panel

    def create_ultimate_config_editor(self):
        """创建完整功能的配置编辑器"""
        from PyQt6.QtWidgets import QTabWidget

        # 创建标签页容器
        config_tabs = QTabWidget()

        if COMPLETE_CONFIG_AVAILABLE:
            # 通用配置
            general_widget = GeneralConfigWidget(self.app.complete_config)
            config_tabs.addTab(general_widget, "🔧 通用配置")

            # 网络配置
            network_widget = CompleteNetworkConfigWidget(self.app.complete_config)
            config_tabs.addTab(network_widget, "🌐 网络配置")

        # SSL/TLS 配置
        ssl_widget = self.create_ssl_config_widget()
        config_tabs.addTab(ssl_widget, "🔒 SSL/TLS")

        # 数据库配置
        db_widget = self.create_database_config_widget()
        config_tabs.addTab(db_widget, "🗄️ 数据库")

        # 上传配置
        upload_widget = self.create_upload_config_widget()
        config_tabs.addTab(upload_widget, "📤 上传配置")

        # 安全配置
        security_widget = self.create_security_config_widget()
        config_tabs.addTab(security_widget, "🛡️ 安全配置")

        # 高级配置
        advanced_widget = self.create_advanced_config_widget()
        config_tabs.addTab(advanced_widget, "⚙️ 高级配置")

        return config_tabs

    def create_complete_config_editor(self):
        """创建完整的配置编辑器"""
        from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout
        from copyparty_complete_widgets import GeneralConfigWidget, CompleteNetworkConfigWidget

        # 创建标签页容器
        config_tabs = QTabWidget()

        # 通用配置
        general_widget = GeneralConfigWidget(self.app.complete_config)
        config_tabs.addTab(general_widget, "🔧 通用配置")

        # 网络配置
        network_widget = CompleteNetworkConfigWidget(self.app.complete_config)
        config_tabs.addTab(network_widget, "🌐 网络配置")

        # SSL/TLS 配置
        ssl_widget = self.create_ssl_config_widget()
        config_tabs.addTab(ssl_widget, "🔒 SSL/TLS")

        # 数据库配置
        db_widget = self.create_database_config_widget()
        config_tabs.addTab(db_widget, "🗄️ 数据库")

        # 上传配置
        upload_widget = self.create_upload_config_widget()
        config_tabs.addTab(upload_widget, "📤 上传配置")

        # 安全配置
        security_widget = self.create_security_config_widget()
        config_tabs.addTab(security_widget, "🛡️ 安全配置")

        # 高级配置
        advanced_widget = self.create_advanced_config_widget()
        config_tabs.addTab(advanced_widget, "⚙️ 高级配置")

        return config_tabs

    def create_ssl_config_widget(self):
        """创建SSL配置组件"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLineEdit, QPushButton, QHBoxLayout

        widget = QWidget()
        layout = QVBoxLayout()

        # SSL基本设置
        ssl_group = QGroupBox("SSL/TLS 设置")
        ssl_layout = QFormLayout()

        self.https_only_cb = QCheckBox("仅HTTPS (-lo)")
        ssl_layout.addRow("", self.https_only_cb)

        self.auto_cert_cb = QCheckBox("自动证书 (--cert)")
        ssl_layout.addRow("", self.auto_cert_cb)

        self.cert_file_edit = QLineEdit()
        cert_browse_btn = QPushButton("浏览...")
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.cert_file_edit)
        cert_layout.addWidget(cert_browse_btn)
        ssl_layout.addRow("证书文件:", cert_layout)

        self.key_file_edit = QLineEdit()
        key_browse_btn = QPushButton("浏览...")
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_file_edit)
        key_layout.addWidget(key_browse_btn)
        ssl_layout.addRow("私钥文件:", key_layout)

        ssl_group.setLayout(ssl_layout)
        layout.addWidget(ssl_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_database_config_widget(self):
        """创建数据库配置组件"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QSpinBox

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
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLineEdit

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
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QSpinBox

        widget = QWidget()
        layout = QVBoxLayout()

        # 安全设置
        security_group = QGroupBox("安全设置")
        security_layout = QFormLayout()

        self.early_ban_cb = QCheckBox("早期封禁 (--ban-403)")
        security_layout.addRow("", self.early_ban_cb)

        self.vague_403_cb = QCheckBox("模糊403错误 (--vague-403)")
        security_layout.addRow("", self.vague_403_cb)

        self.max_conn_spin = QSpinBox()
        self.max_conn_spin.setRange(1, 10000)
        self.max_conn_spin.setValue(100)
        security_layout.addRow("最大连接数:", self.max_conn_spin)

        security_group.setLayout(security_layout)
        layout.addWidget(security_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_advanced_config_widget(self):
        """创建高级配置组件"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLineEdit, QPushButton, QHBoxLayout

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
        log_layout = QHBoxLayout()
        log_layout.addWidget(self.log_file_edit)
        log_layout.addWidget(log_browse_btn)
        advanced_layout.addRow("日志文件:", log_layout)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def on_layout_changed(self, layout_type):
        """响应布局变更"""
        print(f"界面布局已切换到: {layout_type}")
        # 可以在这里添加特定布局的调整逻辑
        if layout_type == 'mobile':
            # 移动布局下的特殊处理
            pass
        elif layout_type == 'tablet':
            # 平板布局下的特殊处理
            pass
        elif layout_type == 'desktop':
            # 桌面布局下的特殊处理
            pass

    # ==================== 完整功能方法 ====================

    def start_server(self):
        """启动服务器"""
        try:
            if hasattr(self.app, 'server_manager'):
                self.app.server_manager.start_server()
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.restart_btn.setEnabled(True)
                self.open_browser_btn.setEnabled(True)
                self.generate_qr_btn.setEnabled(True)
                self.copy_url_btn.setEnabled(True)

                if hasattr(self.app, 'notification_manager'):
                    self.app.notification_manager.show_success("服务器启动", "CopyParty 服务器已成功启动")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("启动失败", f"服务器启动失败: {str(e)}")

    def stop_server(self):
        """停止服务器"""
        try:
            if hasattr(self.app, 'server_manager'):
                self.app.server_manager.stop_server()
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.restart_btn.setEnabled(False)
                self.open_browser_btn.setEnabled(False)
                self.generate_qr_btn.setEnabled(False)
                self.copy_url_btn.setEnabled(False)

                if hasattr(self.app, 'notification_manager'):
                    self.app.notification_manager.show_info("服务器停止", "CopyParty 服务器已停止")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("停止失败", f"服务器停止失败: {str(e)}")

    def restart_server(self):
        """重启服务器"""
        try:
            if hasattr(self.app, 'server_manager'):
                self.app.server_manager.restart_server()
                if hasattr(self.app, 'notification_manager'):
                    self.app.notification_manager.show_warning("服务器重启", "CopyParty 服务器正在重启...")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("重启失败", f"服务器重启失败: {str(e)}")

    def load_quick_preset(self):
        """加载快速服务器预设"""
        if hasattr(self.app, 'load_quick_preset'):
            self.app.load_quick_preset()
        else:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_info("预设加载", "快速服务器预设已应用")

    def load_secure_preset(self):
        """加载安全服务器预设"""
        if hasattr(self.app, 'load_secure_preset'):
            self.app.load_secure_preset()
        else:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_info("预设加载", "安全服务器预设已应用")

    def load_media_preset(self):
        """加载媒体服务器预设"""
        if hasattr(self.app, 'load_media_preset'):
            self.app.load_media_preset()
        else:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_info("预设加载", "媒体服务器预设已应用")

    def load_custom_preset(self):
        """加载自定义预设"""
        if hasattr(self.app, 'notification_manager'):
            self.app.notification_manager.show_info("自定义预设", "请在配置标签页中手动配置")

    def open_browser(self):
        """在浏览器中打开服务器"""
        try:
            import webbrowser
            url = "http://localhost:8080"  # 默认URL
            if hasattr(self.app, 'server_manager') and hasattr(self.app.server_manager, 'get_server_url'):
                url = self.app.server_manager.get_server_url()
            webbrowser.open(url)
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_success("浏览器打开", f"已在浏览器中打开: {url}")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("打开失败", f"无法打开浏览器: {str(e)}")

    def generate_qr_code(self):
        """生成二维码"""
        try:
            from .dialogs.qr_dialog import QRCodeDialog
            url = "http://localhost:8080"  # 默认URL
            if hasattr(self.app, 'server_manager') and hasattr(self.app.server_manager, 'get_server_url'):
                url = self.app.server_manager.get_server_url()

            dialog = QRCodeDialog(url, self)
            dialog.exec()
        except ImportError:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_warning("功能不可用", "二维码功能需要安装 qrcode 库")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("生成失败", f"二维码生成失败: {str(e)}")

    def copy_url(self):
        """复制服务器URL到剪贴板"""
        try:
            from PyQt6.QtWidgets import QApplication
            url = "http://localhost:8080"  # 默认URL
            if hasattr(self.app, 'server_manager') and hasattr(self.app.server_manager, 'get_server_url'):
                url = self.app.server_manager.get_server_url()

            clipboard = QApplication.clipboard()
            clipboard.setText(url)

            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_success("URL已复制", f"服务器URL已复制到剪贴板: {url}")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("复制失败", f"URL复制失败: {str(e)}")

    def open_server_folder(self):
        """打开服务器文件夹"""
        try:
            import subprocess
            import platform

            folder_path = os.getcwd()  # 默认当前目录
            if hasattr(self.app, 'config_manager') and hasattr(self.app.config_manager, 'get_work_directory'):
                folder_path = self.app.config_manager.get_work_directory()

            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])

            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_info("文件夹打开", f"已打开服务器目录: {folder_path}")
        except Exception as e:
            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.show_error("打开失败", f"无法打开文件夹: {str(e)}")

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
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
                color: #495057;
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 2px 4px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                font-size: 12px;
                background-color: white;
            }
            
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }

            QCheckBox {
                font-size: 12px;
                color: #495057;
                spacing: 5px;
                background-color: transparent;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: white;
            }

            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }

            QCheckBox::indicator:hover {
                border-color: #007bff;
            }

            QCheckBox::indicator:disabled {
                background-color: #e9ecef;
                border-color: #dee2e6;
            }

            QSplitter::handle {
                background-color: #dee2e6;
                width: 2px;
                height: 2px;
            }

            QSplitter::handle:hover {
                background-color: #007bff;
            }
        """)
    
    def init_timers(self):
        """初始化定时器"""
        # 自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_config)
        self.auto_save_timer.start(30000)  # 30秒自动保存
        
        # UI更新定时器
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(1000)  # 1秒更新一次
    
    def auto_save_config(self):
        """自动保存配置"""
        try:
            if self.config_manager.changed:
                self.config_manager.auto_save_if_needed()
        except Exception as e:
            print(f"自动保存配置失败: {e}")
    
    def update_ui(self):
        """更新UI状态"""
        try:
            # 更新各个组件
            if hasattr(self.control_panel, 'update_status'):
                self.control_panel.update_status()
            
            if hasattr(self.monitoring_panel, 'update_metrics'):
                self.monitoring_panel.update_metrics()
            
        except Exception as e:
            print(f"UI更新失败: {e}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于 CopyParty Desktop", 
                         "CopyParty Desktop v2.0\n\n"
                         "基于模块化架构的 CopyParty 桌面管理工具\n"
                         "支持完整的 CopyParty 功能集\n\n"
                         "© 2024 CopyParty Desktop")
    
    def show_preferences(self):
        """显示偏好设置"""
        from .dialogs.preferences import PreferencesDialog
        dialog = PreferencesDialog(self.app, self)
        dialog.exec()
    
    def load_config_file(self):
        """加载配置文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置文件", "", 
            "JSON 文件 (*.json);;YAML 文件 (*.yaml *.yml);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.config_manager.load_config(file_path)
                self.refresh_all_widgets()
                QMessageBox.information(self, "成功", f"配置已从 {file_path} 加载")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置失败: {str(e)}")
    
    def save_config_file(self):
        """保存配置文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "", 
            "JSON 文件 (*.json);;YAML 文件 (*.yaml);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 根据文件扩展名确定格式
                if file_path.lower().endswith(('.yaml', '.yml')):
                    format = 'yaml'
                else:
                    format = 'json'
                
                self.config_manager.save_config(file_path)
                QMessageBox.information(self, "成功", f"配置已保存到 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
    
    def validate_config(self):
        """验证配置"""
        result = self.config_manager.validate_all()
        
        if result.is_valid:
            QMessageBox.information(self, "验证结果", "配置验证通过！")
        else:
            error_msg = "配置验证失败：\n\n"
            for error in result.errors[:10]:  # 显示前10个错误
                error_msg += f"• {error}\n"
            
            if len(result.errors) > 10:
                error_msg += f"\n... 还有 {len(result.errors) - 10} 个错误"
            
            if result.warnings:
                error_msg += f"\n\n警告 ({len(result.warnings)} 个)：\n"
                for warning in result.warnings[:5]:  # 显示前5个警告
                    error_msg += f"• {warning}\n"
            
            QMessageBox.warning(self, "验证结果", error_msg)
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有配置为默认值吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            self.refresh_all_widgets()
            QMessageBox.information(self, "成功", "配置已重置为默认值")
    
    def refresh_all_widgets(self):
        """刷新所有组件"""
        try:
            if hasattr(self.config_editor, 'refresh'):
                self.config_editor.refresh()
            
            if hasattr(self.control_panel, 'refresh'):
                self.control_panel.refresh()
            
            if hasattr(self.monitoring_panel, 'refresh'):
                self.monitoring_panel.refresh()
            
        except Exception as e:
            print(f"刷新组件失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 检查是否有未保存的配置
        if self.config_manager.changed:
            reply = QMessageBox.question(
                self, "未保存的更改", "配置已更改但未保存，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                try:
                    self.config_manager.save_config()
                    event.accept()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # 停止服务器
        if hasattr(self.server_manager, 'stop_server'):
            self.server_manager.stop_server()
        
        # 停止定时器
        self.auto_save_timer.stop()
        self.ui_update_timer.stop()
        
        event.accept()
