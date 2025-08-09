"""
主应用程序类
"""

import sys
import os
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .config_manager import ConfigManager
from .server_manager import ServerManager
from .plugin_manager import PluginManager


class CopyPartyApplication(QMainWindow):
    """主应用程序类 - 协调所有模块"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CopyParty Desktop v2.0")
        self.setGeometry(100, 100, 1200, 700)

        # 初始化管理器
        self.config_manager = ConfigManager()
        self.server_manager = ServerManager(self.config_manager)
        self.plugin_manager = PluginManager()

        # 加载默认配置
        self.load_default_config()

        self.init_ui()
        self.load_plugins()

        # 设置窗口图标和其他属性
        self.setup_window_properties()

        # 自动启动服务器
        self.auto_start_server()

    def load_default_config(self):
        """加载默认配置"""
        try:
            # 尝试加载默认配置文件
            default_config_path = self.config_manager.get_default_config_path()
            if os.path.exists(default_config_path):
                self.config_manager.load_config(default_config_path)
                print(f"已加载默认配置: {default_config_path}")
            else:
                print("使用内置默认配置")
        except Exception as e:
            print(f"加载默认配置失败: {e}")
            QMessageBox.warning(self, "配置警告", f"加载默认配置失败: {str(e)}")

    def init_ui(self):
        """初始化用户界面"""
        try:
            from ui.main_window import MainWindow
            self.main_window = MainWindow(self)
            self.setCentralWidget(self.main_window)
            print("UI初始化完成")
        except Exception as e:
            print(f"UI初始化失败: {e}")
            QMessageBox.critical(self, "初始化错误", f"UI初始化失败: {str(e)}")
            sys.exit(1)

    def load_plugins(self):
        """加载插件"""
        try:
            self.plugin_manager.load_plugins()
            print("插件加载完成")
        except Exception as e:
            print(f"插件加载失败: {e}")

    def setup_window_properties(self):
        """设置窗口属性"""
        # 设置窗口最小尺寸
        self.setMinimumSize(800, 600)

        # 设置状态栏
        self.statusBar().showMessage("就绪")

        # 创建菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        # 新建配置
        new_action = file_menu.addAction('新建配置(&N)')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_config)

        # 打开配置
        open_action = file_menu.addAction('打开配置(&O)')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_config)

        # 保存配置
        save_action = file_menu.addAction('保存配置(&S)')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_config)

        # 另存为
        save_as_action = file_menu.addAction('另存为(&A)')
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_config_as)

        file_menu.addSeparator()

        # 退出
        exit_action = file_menu.addAction('退出(&X)')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)

        # 服务器菜单
        server_menu = menubar.addMenu('服务器(&S)')

        # 启动服务器
        start_action = server_menu.addAction('启动服务器(&S)')
        start_action.setShortcut('F5')
        start_action.triggered.connect(self.start_server)

        # 停止服务器
        stop_action = server_menu.addAction('停止服务器(&T)')
        stop_action.setShortcut('F6')
        stop_action.triggered.connect(self.stop_server)

        # 重启服务器
        restart_action = server_menu.addAction('重启服务器(&R)')
        restart_action.setShortcut('F7')
        restart_action.triggered.connect(self.restart_server)

        server_menu.addSeparator()

        # 服务器状态
        status_action = server_menu.addAction('服务器状态(&I)')
        status_action.triggered.connect(self.show_server_status)

        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')

        # 验证配置
        validate_action = tools_menu.addAction('验证配置(&V)')
        validate_action.triggered.connect(self.validate_config)

        # 重置配置
        reset_action = tools_menu.addAction('重置配置(&R)')
        reset_action.triggered.connect(self.reset_config)

        tools_menu.addSeparator()

        # 偏好设置
        preferences_action = tools_menu.addAction('偏好设置(&P)')
        preferences_action.triggered.connect(self.show_preferences)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        # 用户手册
        manual_action = help_menu.addAction('用户手册(&M)')
        manual_action.triggered.connect(self.show_manual)

        # 关于
        about_action = help_menu.addAction('关于(&A)')
        about_action.triggered.connect(self.show_about)

    # 菜单动作方法
    def new_config(self):
        """新建配置"""
        reply = QMessageBox.question(
            self, "新建配置", "确定要创建新配置吗？当前配置将被重置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            if hasattr(self.main_window, 'refresh_all_widgets'):
                self.main_window.refresh_all_widgets()
            self.statusBar().showMessage("已创建新配置")

    def open_config(self):
        """打开配置"""
        if hasattr(self.main_window, 'load_config_file'):
            self.main_window.load_config_file()

    def save_config(self):
        """保存配置"""
        try:
            self.config_manager.save_config()
            self.statusBar().showMessage("配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存配置失败: {str(e)}")

    def save_config_as(self):
        """另存为配置"""
        if hasattr(self.main_window, 'save_config_file'):
            self.main_window.save_config_file()

    def start_server(self):
        """启动服务器"""
        try:
            self.server_manager.start_server()
            self.statusBar().showMessage("服务器已启动")
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"启动服务器失败: {str(e)}")

    def stop_server(self):
        """停止服务器"""
        try:
            self.server_manager.stop_server()
            self.statusBar().showMessage("服务器已停止")
        except Exception as e:
            QMessageBox.critical(self, "停止失败", f"停止服务器失败: {str(e)}")

    def restart_server(self):
        """重启服务器"""
        try:
            self.server_manager.restart_server()
            self.statusBar().showMessage("服务器已重启")
        except Exception as e:
            QMessageBox.critical(self, "重启失败", f"重启服务器失败: {str(e)}")

    def show_server_status(self):
        """显示服务器状态"""
        status = self.server_manager.get_server_status()

        status_text = f"""
服务器状态: {'运行中' if status['running'] else '已停止'}
进程ID: {status['pid'] or 'N/A'}
运行时间: {int(status['uptime'])} 秒
命令行: {' '.join(status['command'])}
        """.strip()

        QMessageBox.information(self, "服务器状态", status_text)

    def validate_config(self):
        """验证配置"""
        if hasattr(self.main_window, 'validate_config'):
            self.main_window.validate_config()

    def reset_config(self):
        """重置配置"""
        if hasattr(self.main_window, 'reset_config'):
            self.main_window.reset_config()

    def show_preferences(self):
        """显示偏好设置"""
        if hasattr(self.main_window, 'show_preferences'):
            self.main_window.show_preferences()

    def show_manual(self):
        """显示用户手册"""
        QMessageBox.information(self, "用户手册", "用户手册功能开发中...")

    def show_about(self):
        """显示关于对话框"""
        if hasattr(self.main_window, 'show_about'):
            self.main_window.show_about()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止服务器
        if self.server_manager.is_server_running():
            reply = QMessageBox.question(
                self, "确认退出", "服务器正在运行，是否停止服务器并退出？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.server_manager.stop_server()
            else:
                event.ignore()
                return

        # 检查未保存的配置
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
                except Exception as e:
                    QMessageBox.critical(self, "保存失败", f"保存配置失败: {str(e)}")
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # 自动停止服务器
        self.auto_stop_server()

        event.accept()

    def auto_start_server(self):
        """自动启动服务器"""
        try:
            print("🚀 自动启动服务器...")
            self.server_manager.start_server()
            print("✅ 服务器启动请求已发送")
        except Exception as e:
            print(f"❌ 自动启动服务器失败: {e}")

    def auto_stop_server(self):
        """自动停止服务器"""
        try:
            print("🛑 自动停止服务器...")
            self.server_manager.stop_server()
            print("✅ 服务器停止请求已发送")
        except Exception as e:
            print(f"❌ 自动停止服务器失败: {e}")
