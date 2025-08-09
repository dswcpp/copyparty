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

from .widgets.config_editor import ConfigEditorWidget
from .widgets.monitoring_panel import MonitoringPanel, LogViewer


class MainWindow(QWidget):
    """主窗口 - 迁移自 UltimateMainWindow"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.server_manager = app.server_manager
        
        # 窗口设置
        self.setWindowTitle("CopyParty Desktop Manager")
        self.setGeometry(100, 100, 1200, 700)  # 优化后的尺寸

        # 设置窗口图标
        self.set_window_icon()
        
        # 初始化UI
        self.init_ui()
        self.init_menu()
        self.init_status_bar()
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
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 上方：配置编辑器和监控面板的分割器
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 配置编辑器
        self.config_editor = ConfigEditorWidget(self.app)
        top_splitter.addWidget(self.config_editor)

        # 监控面板
        self.monitoring_panel = MonitoringPanel(self.app)
        self.monitoring_panel.setFixedWidth(350)  # 稍微增加宽度
        top_splitter.addWidget(self.monitoring_panel)

        # 设置分割器比例
        top_splitter.setSizes([850, 350])
        main_layout.addWidget(top_splitter)

        # 下方：日志查看器
        self.log_viewer = LogViewer(self.app)
        self.log_viewer.setMaximumHeight(150)  # 限制日志区域高度
        main_layout.addWidget(self.log_viewer)

        self.setLayout(main_layout)
    
    def init_menu(self):
        """初始化菜单栏"""
        # 注意：QWidget 不能直接添加菜单栏，这里为了演示
        # 实际使用时应该在 QMainWindow 中实现
        pass
    
    def init_status_bar(self):
        """初始化状态栏"""
        # 注意：QWidget 不能直接添加状态栏，这里为了演示
        # 实际使用时应该在 QMainWindow 中实现
        pass
    
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
