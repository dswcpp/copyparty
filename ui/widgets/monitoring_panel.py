"""
监控面板组件
显示服务器性能和状态信息
"""

import sys
import os
import random
import datetime
import psutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, QTimer

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class MonitoringPanel(QWidget):
    """监控面板组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.server_manager = app.server_manager
        
        self.init_ui()
        self.init_timers()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 系统性能组
        self.create_system_performance_group(layout)
        
        # 服务器统计组
        self.create_server_stats_group(layout)
        
        # 实时日志组
        self.create_realtime_log_group(layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_system_performance_group(self, parent_layout):
        """创建系统性能组"""
        group = QGroupBox("系统性能")
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # CPU 使用率
        layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximumHeight(20)
        layout.addWidget(self.cpu_progress, 0, 1)
        self.cpu_label = QLabel("0%")
        layout.addWidget(self.cpu_label, 0, 2)
        
        # 内存使用率
        layout.addWidget(QLabel("内存:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximumHeight(20)
        layout.addWidget(self.memory_progress, 1, 1)
        self.memory_label = QLabel("0%")
        layout.addWidget(self.memory_label, 1, 2)
        
        # 磁盘使用率
        layout.addWidget(QLabel("磁盘:"), 2, 0)
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximumHeight(20)
        layout.addWidget(self.disk_progress, 2, 1)
        self.disk_label = QLabel("0%")
        layout.addWidget(self.disk_label, 2, 2)
        
        # 网络IO
        layout.addWidget(QLabel("网络:"), 3, 0)
        self.network_label = QLabel("↑ 0 KB/s ↓ 0 KB/s")
        self.network_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.network_label, 3, 1, 1, 2)
        
        group.setLayout(layout)
        group.setMaximumHeight(140)
        parent_layout.addWidget(group)
    
    def create_server_stats_group(self, parent_layout):
        """创建服务器统计组"""
        group = QGroupBox("服务器统计")
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # 连接数
        layout.addWidget(QLabel("连接数:"), 0, 0)
        self.connections_label = QLabel("0")
        layout.addWidget(self.connections_label, 0, 1)
        
        # 请求数
        layout.addWidget(QLabel("请求数:"), 0, 2)
        self.requests_label = QLabel("0")
        layout.addWidget(self.requests_label, 0, 3)
        
        # 上传数
        layout.addWidget(QLabel("上传:"), 1, 0)
        self.uploads_label = QLabel("0")
        layout.addWidget(self.uploads_label, 1, 1)
        
        # 下载数
        layout.addWidget(QLabel("下载:"), 1, 2)
        self.downloads_label = QLabel("0")
        layout.addWidget(self.downloads_label, 1, 3)
        
        # 数据传输
        layout.addWidget(QLabel("传输:"), 2, 0)
        self.transfer_label = QLabel("↑ 0 MB ↓ 0 MB")
        self.transfer_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.transfer_label, 2, 1, 1, 3)
        
        group.setLayout(layout)
        group.setMaximumHeight(100)
        parent_layout.addWidget(group)
    
    def create_realtime_log_group(self, parent_layout):
        """创建实时日志组"""
        group = QGroupBox("实时日志")
        layout = QVBoxLayout()
        layout.setSpacing(3)
        
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                border: 1px solid #444444;
            }
        """)
        layout.addWidget(self.log_display)
        
        # 日志控制按钮
        button_layout = QHBoxLayout()
        
        from PyQt6.QtWidgets import QPushButton
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_log)
        clear_btn.setMaximumHeight(25)
        button_layout.addWidget(clear_btn)
        
        pause_btn = QPushButton("暂停")
        pause_btn.clicked.connect(self.toggle_log_pause)
        pause_btn.setMaximumHeight(25)
        button_layout.addWidget(pause_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
        # 日志状态
        self.log_paused = False
    
    def init_timers(self):
        """初始化定时器"""
        # 性能监控定时器
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_metrics)
        self.performance_timer.start(2000)  # 2秒更新一次
        
        # 日志更新定时器
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(1000)  # 1秒更新一次
        
        # 初始化网络统计
        self.last_net_io = psutil.net_io_counters()
    
    def update_metrics(self):
        """更新性能指标"""
        try:
            # 更新CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            # 更新内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.setValue(int(memory_percent))
            self.memory_label.setText(f"{memory_percent:.1f}%")
            
            # 更新磁盘使用率
            work_dir = self.config_manager.server_config.working_directory
            if os.path.exists(work_dir):
                disk = psutil.disk_usage(work_dir)
                disk_percent = disk.percent
                self.disk_progress.setValue(int(disk_percent))
                self.disk_label.setText(f"{disk_percent:.1f}%")
            
            # 更新网络IO
            current_net_io = psutil.net_io_counters()
            if hasattr(self, 'last_net_io'):
                bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
                bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
                
                # 转换为KB/s (2秒间隔)
                sent_kbs = bytes_sent / 1024 / 2
                recv_kbs = bytes_recv / 1024 / 2
                
                self.network_label.setText(f"↑ {sent_kbs:.1f} KB/s ↓ {recv_kbs:.1f} KB/s")
            
            self.last_net_io = current_net_io
            
            # 更新服务器统计（模拟数据）
            self.update_server_stats()
            
        except Exception as e:
            print(f"更新性能指标失败: {e}")
    
    def update_server_stats(self):
        """更新服务器统计"""
        # TODO: 从实际的服务器管理器获取统计数据
        # 这里使用模拟数据
        
        # 模拟连接数
        connections = random.randint(0, 10)
        self.connections_label.setText(str(connections))
        
        # 模拟请求数
        requests = random.randint(100, 1000)
        self.requests_label.setText(str(requests))
        
        # 模拟上传下载数
        uploads = random.randint(0, 50)
        downloads = random.randint(0, 100)
        self.uploads_label.setText(str(uploads))
        self.downloads_label.setText(str(downloads))
        
        # 模拟传输量
        upload_mb = random.randint(0, 100)
        download_mb = random.randint(0, 500)
        self.transfer_label.setText(f"↑ {upload_mb} MB ↓ {download_mb} MB")
    
    def update_log(self):
        """更新日志显示"""
        if not self.log_paused:
            # TODO: 从实际的日志系统获取日志
            # 这里使用模拟日志

            # 模拟日志条目
            log_entries = [
                "Server started on port 3923",
                "New connection from 192.168.1.100",
                "File uploaded: document.pdf",
                "User authenticated: admin",
                "Connection closed: 192.168.1.100"
            ]

            if random.randint(1, 10) == 1:  # 10% 概率添加日志
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                entry = random.choice(log_entries)
                log_line = f"[{timestamp}] {entry}"

                self.log_display.append(log_line)

                # 限制日志行数
                if self.log_display.document().blockCount() > 100:
                    cursor = self.log_display.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    cursor.select(cursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
    
    def clear_log(self):
        """清空日志"""
        self.log_display.clear()
    
    def toggle_log_pause(self):
        """切换日志暂停状态"""
        self.log_paused = not self.log_paused
        
        # 更新按钮文本
        sender = self.sender()
        if self.log_paused:
            sender.setText("继续")
        else:
            sender.setText("暂停")
    
    def refresh(self):
        """刷新组件"""
        self.update_metrics()


class LogViewer(QWidget):
    """日志查看器组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: 1px solid #555555;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        from PyQt6.QtWidgets import QPushButton
        
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_log)
        clear_btn.setMaximumHeight(25)
        button_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("保存日志")
        save_btn.clicked.connect(self.save_log)
        save_btn.setMaximumHeight(25)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        # 日志级别过滤
        from PyQt6.QtWidgets import QComboBox
        level_combo = QComboBox()
        level_combo.addItems(["全部", "错误", "警告", "信息", "调试"])
        level_combo.setMaximumHeight(25)
        button_layout.addWidget(level_combo)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 添加一些示例日志
        self.add_sample_logs()
    
    def add_sample_logs(self):
        """添加示例日志"""
        import datetime
        
        sample_logs = [
            "[INFO] CopyParty Desktop v2.0 启动",
            "[INFO] 配置已加载",
            "[INFO] 服务器管理器已初始化",
            "[DEBUG] 监听地址: 0.0.0.0:3923",
            "[INFO] 服务器已准备就绪"
        ]
        
        for log in sample_logs:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.append(f"[{timestamp}] {log}")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def save_log(self):
        """保存日志"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "copyparty_log.txt", 
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", f"日志已保存到 {file_path}")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")
    
    def add_log(self, level: str, message: str):
        """添加日志条目"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        self.log_text.append(log_line)
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
