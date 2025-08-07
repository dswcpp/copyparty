"""
协议配置组件
管理所有网络协议的配置
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QTabWidget, QGroupBox, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QSplitter,
                             QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from protocols.base_protocol import ProtocolManager
except ImportError:
    # 如果协议模块不可用，创建一个占位符
    class ProtocolManager:
        def __init__(self):
            self.protocols = {}
        
        def get_all_protocols(self):
            return []
        
        def get_enabled_protocols(self):
            return []
        
        def validate_all_configs(self):
            return True, {}
        
        def generate_all_command_args(self):
            return []


class ProtocolConfigWidget(QWidget):
    """协议配置组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        
        # 初始化协议管理器
        try:
            self.protocol_manager = ProtocolManager()
        except Exception as e:
            print(f"协议管理器初始化失败: {e}")
            self.protocol_manager = ProtocolManager()  # 使用占位符
        
        self.current_protocol = None
        self.current_config_widget = None
        
        self.init_ui()
        self.load_protocols()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：协议列表
        left_widget = self.create_protocol_list()
        left_widget.setMaximumWidth(250)
        splitter.addWidget(left_widget)
        
        # 右侧：协议配置
        right_widget = self.create_config_area()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([250, 500])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_protocol_list(self):
        """创建协议列表"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("网络协议")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title_label)
        
        # 协议列表
        self.protocol_list = QListWidget()
        self.protocol_list.itemClicked.connect(self.on_protocol_selected)
        layout.addWidget(self.protocol_list)
        
        # 状态信息
        status_group = QGroupBox("状态")
        status_layout = QVBoxLayout()
        
        self.enabled_count_label = QLabel("已启用: 0")
        status_layout.addWidget(self.enabled_count_label)
        
        self.total_count_label = QLabel("总计: 0")
        status_layout.addWidget(self.total_count_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 操作按钮
        button_layout = QVBoxLayout()
        
        self.validate_all_btn = QPushButton("验证所有协议")
        self.validate_all_btn.clicked.connect(self.validate_all_protocols)
        button_layout.addWidget(self.validate_all_btn)
        
        self.apply_all_btn = QPushButton("应用所有配置")
        self.apply_all_btn.clicked.connect(self.apply_all_configs)
        button_layout.addWidget(self.apply_all_btn)
        
        self.reset_all_btn = QPushButton("重置所有配置")
        self.reset_all_btn.clicked.connect(self.reset_all_configs)
        button_layout.addWidget(self.reset_all_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_config_area(self):
        """创建配置区域"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        self.config_title_label = QLabel("选择一个协议进行配置")
        self.config_title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        title_layout.addWidget(self.config_title_label)
        
        title_layout.addStretch()
        
        # 协议操作按钮
        self.enable_protocol_btn = QPushButton("启用")
        self.enable_protocol_btn.clicked.connect(self.toggle_protocol)
        self.enable_protocol_btn.setEnabled(False)
        title_layout.addWidget(self.enable_protocol_btn)
        
        self.validate_protocol_btn = QPushButton("验证")
        self.validate_protocol_btn.clicked.connect(self.validate_current_protocol)
        self.validate_protocol_btn.setEnabled(False)
        title_layout.addWidget(self.validate_protocol_btn)
        
        layout.addLayout(title_layout)
        
        # 配置区域 (滚动)
        self.config_scroll = QScrollArea()
        self.config_scroll.setWidgetResizable(True)
        self.config_scroll.setMinimumHeight(400)
        
        # 默认显示的占位符
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout()
        placeholder_layout.addStretch()
        
        placeholder_label = QLabel("请从左侧列表选择一个协议进行配置")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #666; font-size: 16px;")
        placeholder_layout.addWidget(placeholder_label)
        
        placeholder_layout.addStretch()
        placeholder_widget.setLayout(placeholder_layout)
        
        self.config_scroll.setWidget(placeholder_widget)
        layout.addWidget(self.config_scroll)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("应用配置")
        self.apply_btn.clicked.connect(self.apply_current_config)
        self.apply_btn.setEnabled(False)
        bottom_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("重置配置")
        self.reset_btn.clicked.connect(self.reset_current_config)
        self.reset_btn.setEnabled(False)
        bottom_layout.addWidget(self.reset_btn)
        
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_protocols(self):
        """加载协议列表"""
        self.protocol_list.clear()
        
        protocols = self.protocol_manager.get_all_protocols()
        
        for protocol in protocols:
            item = QListWidgetItem()
            
            # 设置显示文本
            status = "✓" if protocol.is_enabled() else "○"
            item.setText(f"{status} {protocol.get_display_name()}")
            
            # 设置工具提示
            item.setToolTip(protocol.get_description())
            
            # 存储协议对象
            item.setData(Qt.ItemDataRole.UserRole, protocol)
            
            # 设置样式
            if protocol.is_enabled():
                from PyQt6.QtGui import QColor
                item.setBackground(QColor(144, 238, 144))  # lightgreen
            
            self.protocol_list.addItem(item)
        
        # 更新状态
        self.update_status()
    
    def update_status(self):
        """更新状态显示"""
        all_protocols = self.protocol_manager.get_all_protocols()
        enabled_protocols = self.protocol_manager.get_enabled_protocols()
        
        self.total_count_label.setText(f"总计: {len(all_protocols)}")
        self.enabled_count_label.setText(f"已启用: {len(enabled_protocols)}")
    
    def on_protocol_selected(self, item):
        """协议选择事件"""
        protocol = item.data(Qt.ItemDataRole.UserRole)
        if protocol:
            self.current_protocol = protocol
            self.load_protocol_config(protocol)
            self.update_protocol_buttons()
    
    def load_protocol_config(self, protocol):
        """加载协议配置界面"""
        try:
            # 更新标题
            self.config_title_label.setText(f"{protocol.get_display_name()} 配置")
            
            # 获取配置组件
            config_widget = protocol.get_config_widget()
            self.current_config_widget = config_widget
            
            # 设置到滚动区域
            self.config_scroll.setWidget(config_widget)
            
        except Exception as e:
            # 如果获取配置组件失败，显示错误信息
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            
            error_label = QLabel(f"无法加载 {protocol.get_display_name()} 的配置界面")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px;")
            error_layout.addWidget(error_label)
            
            detail_label = QLabel(f"错误详情: {str(e)}")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_label.setStyleSheet("color: #666; font-size: 12px;")
            detail_label.setWordWrap(True)
            error_layout.addWidget(detail_label)
            
            error_widget.setLayout(error_layout)
            self.config_scroll.setWidget(error_widget)
            self.current_config_widget = None
    
    def update_protocol_buttons(self):
        """更新协议按钮状态"""
        if self.current_protocol:
            # 启用/禁用按钮
            if self.current_protocol.is_enabled():
                self.enable_protocol_btn.setText("禁用")
            else:
                self.enable_protocol_btn.setText("启用")
            
            self.enable_protocol_btn.setEnabled(True)
            self.validate_protocol_btn.setEnabled(True)
            self.apply_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
        else:
            self.enable_protocol_btn.setEnabled(False)
            self.validate_protocol_btn.setEnabled(False)
            self.apply_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
    
    def toggle_protocol(self):
        """切换协议启用状态"""
        if not self.current_protocol:
            return
        
        if self.current_protocol.is_enabled():
            self.current_protocol.disable()
            QMessageBox.information(self, "协议状态", f"{self.current_protocol.get_display_name()} 已禁用")
        else:
            self.current_protocol.enable()
            QMessageBox.information(self, "协议状态", f"{self.current_protocol.get_display_name()} 已启用")
        
        # 刷新列表和按钮
        self.load_protocols()
        self.update_protocol_buttons()
    
    def validate_current_protocol(self):
        """验证当前协议配置"""
        if not self.current_protocol:
            return
        
        # 先保存当前配置
        self.apply_current_config()
        
        # 验证配置
        is_valid, errors = self.current_protocol.validate_config()
        
        if is_valid:
            QMessageBox.information(self, "验证结果", f"{self.current_protocol.get_display_name()} 配置验证通过！")
        else:
            error_msg = f"{self.current_protocol.get_display_name()} 配置验证失败：\n\n"
            for error in errors:
                error_msg += f"• {error}\n"
            QMessageBox.warning(self, "验证结果", error_msg)
    
    def apply_current_config(self):
        """应用当前协议配置"""
        if self.current_config_widget and hasattr(self.current_config_widget, 'save_config'):
            try:
                self.current_config_widget.save_config()
                print(f"已应用 {self.current_protocol.get_display_name()} 配置")
            except Exception as e:
                QMessageBox.warning(self, "应用失败", f"应用配置失败: {str(e)}")
    
    def reset_current_config(self):
        """重置当前协议配置"""
        if self.current_config_widget and hasattr(self.current_config_widget, 'load_config'):
            try:
                self.current_config_widget.load_config()
                QMessageBox.information(self, "重置成功", f"{self.current_protocol.get_display_name()} 配置已重置")
            except Exception as e:
                QMessageBox.warning(self, "重置失败", f"重置配置失败: {str(e)}")
    
    def validate_all_protocols(self):
        """验证所有协议配置"""
        is_valid, errors = self.protocol_manager.validate_all_configs()
        
        if is_valid:
            QMessageBox.information(self, "验证结果", "所有协议配置验证通过！")
        else:
            error_msg = "协议配置验证失败：\n\n"
            for protocol_name, protocol_errors in errors.items():
                error_msg += f"{protocol_name}:\n"
                for error in protocol_errors:
                    error_msg += f"  • {error}\n"
                error_msg += "\n"
            QMessageBox.warning(self, "验证结果", error_msg)
    
    def apply_all_configs(self):
        """应用所有协议配置"""
        # 先应用当前配置
        self.apply_current_config()
        
        # 生成命令行参数
        args = self.protocol_manager.generate_all_command_args()
        
        QMessageBox.information(self, "应用成功", 
                               f"所有协议配置已应用\n生成了 {len(args)} 个命令行参数")
    
    def reset_all_configs(self):
        """重置所有协议配置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有协议配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 重新初始化协议管理器
            self.protocol_manager = ProtocolManager()
            self.load_protocols()
            
            # 清空配置区域
            placeholder_widget = QWidget()
            self.config_scroll.setWidget(placeholder_widget)
            self.current_protocol = None
            self.current_config_widget = None
            self.update_protocol_buttons()
            
            QMessageBox.information(self, "重置成功", "所有协议配置已重置为默认值")
    
    def get_protocol_command_args(self):
        """获取协议命令行参数"""
        return self.protocol_manager.generate_all_command_args()
    
    def refresh(self):
        """刷新组件"""
        self.load_protocols()
        if self.current_protocol:
            self.load_protocol_config(self.current_protocol)
