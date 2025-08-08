"""
监控面板组件
显示服务器性能和状态信息
"""

import sys
import os
import datetime
import psutil
from collections import deque
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QProgressBar, QTextEdit,
                             QPushButton, QTabWidget)
from PyQt6.QtCore import Qt, QTimer

# matplotlib相关导入 - 延迟加载避免阻塞
MATPLOTLIB_AVAILABLE = False

def init_matplotlib():
    """延迟初始化matplotlib，避免启动时阻塞"""
    global MATPLOTLIB_AVAILABLE
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        MATPLOTLIB_AVAILABLE = True
        print("✓ matplotlib延迟加载成功")
        return True
    except ImportError:
        print("⚠️ matplotlib未安装，图表功能不可用")
        return False

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class PerformanceChart(QWidget):
    """性能图表组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.init_data()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 总是创建QLabel，但延迟初始化matplotlib
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setMinimumSize(400, 300)
        self.chart_label.setScaledContents(True)
        self.chart_label.setStyleSheet("border: 1px solid #ddd; background-color: white;")
        layout.addWidget(self.chart_label)

        # 显示加载提示
        self.chart_label.setText("图表功能加载中...\n点击此处启用图表")
        self.chart_label.mousePressEvent = self.init_chart_on_click

        # matplotlib相关变量初始化为None
        self.figure = None
        self.ax_cpu = None
        self.ax_memory = None
        self.ax_network = None
        self.matplotlib_initialized = False

        self.setLayout(layout)

    def init_chart_on_click(self, event):
        """点击时初始化图表"""
        if not self.matplotlib_initialized:
            self.chart_label.setText("正在初始化图表...")

            # 在后台线程中初始化matplotlib
            from PyQt6.QtCore import QThread, QObject, pyqtSignal

            class MatplotlibInitializer(QObject):
                finished = pyqtSignal(bool)

                def run(self):
                    success = init_matplotlib()
                    self.finished.emit(success)

            self.initializer = MatplotlibInitializer()
            self.init_thread = QThread()
            self.initializer.moveToThread(self.init_thread)

            self.initializer.finished.connect(self.on_matplotlib_initialized)
            self.init_thread.started.connect(self.initializer.run)

            self.init_thread.start()

    def on_matplotlib_initialized(self, success):
        """matplotlib初始化完成回调"""
        if success:
            self.matplotlib_initialized = True
            global MATPLOTLIB_AVAILABLE
            MATPLOTLIB_AVAILABLE = True

            # 现在可以安全地初始化图表
            self.init_matplotlib_components()
            self.chart_label.setText("图表已就绪")
        else:
            self.chart_label.setText("图表初始化失败\n请检查matplotlib安装")

        # 清理线程
        self.init_thread.quit()
        self.init_thread.wait()

    def init_matplotlib_components(self):
        """初始化matplotlib组件"""
        try:
            from matplotlib.figure import Figure

            # 创建matplotlib图表
            self.figure = Figure(figsize=(10, 6), dpi=100)

            # 创建子图
            self.ax_cpu = self.figure.add_subplot(3, 1, 1)
            self.ax_memory = self.figure.add_subplot(3, 1, 2)
            self.ax_network = self.figure.add_subplot(3, 1, 3)

            # 设置图表样式
            self.figure.patch.set_facecolor('#f8f9fa')
            for ax in [self.ax_cpu, self.ax_memory, self.ax_network]:
                ax.set_facecolor('#ffffff')
                ax.grid(True, alpha=0.3)
                ax.set_xlim(0, 60)

            # 设置标题
            self.ax_cpu.set_title('CPU Usage (%)', fontsize=9, pad=3)
            self.ax_cpu.set_ylim(0, 100)

            self.ax_memory.set_title('Memory Usage (%)', fontsize=9, pad=3)
            self.ax_memory.set_ylim(0, 100)

            self.ax_network.set_title('Network I/O (KB/s)', fontsize=9, pad=3)
            self.ax_network.set_ylim(0, 1000)

            # 调整布局
            self.figure.subplots_adjust(
                left=0.08, right=0.95, top=0.95, bottom=0.08, hspace=0.4
            )

            print("✓ matplotlib图表组件初始化成功")

        except Exception as e:
            print(f"❌ matplotlib组件初始化失败: {e}")

    def init_data(self):
        """初始化数据存储"""
        if MATPLOTLIB_AVAILABLE:
            # 使用deque存储最近60个数据点
            self.cpu_data = deque(maxlen=60)
            self.memory_data = deque(maxlen=60)
            self.network_up_data = deque(maxlen=60)
            self.network_down_data = deque(maxlen=60)
            self.time_data = deque(maxlen=60)

            # 初始化空数据
            for i in range(60):
                self.cpu_data.append(0)
                self.memory_data.append(0)
                self.network_up_data.append(0)
                self.network_down_data.append(0)
                self.time_data.append(i)

    def update_chart(self, cpu_percent, memory_percent, network_up_kbs, network_down_kbs):
        """更新图表数据"""
        if not self.matplotlib_initialized or not self.figure:
            return

        # 数据验证和转换
        cpu_val = float(cpu_percent) if cpu_percent is not None else 0.0
        memory_val = float(memory_percent) if memory_percent is not None else 0.0
        net_up_val = float(network_up_kbs) if network_up_kbs is not None else 0.0
        net_down_val = float(network_down_kbs) if network_down_kbs is not None else 0.0

        # 添加新数据
        self.cpu_data.append(cpu_val)
        self.memory_data.append(memory_val)
        self.network_up_data.append(net_up_val)
        self.network_down_data.append(net_down_val)

        # 更新时间轴
        if len(self.time_data) > 0:
            self.time_data.append(self.time_data[-1] + 1)
        else:
            self.time_data.append(0)



        # 清除旧图
        self.ax_cpu.clear()
        self.ax_memory.clear()
        self.ax_network.clear()

        # 绘制CPU图表
        self.ax_cpu.plot(list(self.time_data), list(self.cpu_data),
                        color='#ff6b6b', linewidth=2, label='CPU')
        self.ax_cpu.fill_between(list(self.time_data), list(self.cpu_data),
                               alpha=0.3, color='#ff6b6b')
        self.ax_cpu.set_title('CPU Usage (%)', fontsize=9, pad=3)
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.grid(True, alpha=0.3)

        # 绘制内存图表
        self.ax_memory.plot(list(self.time_data), list(self.memory_data),
                           color='#4ecdc4', linewidth=2, label='Memory')
        self.ax_memory.fill_between(list(self.time_data), list(self.memory_data),
                                  alpha=0.3, color='#4ecdc4')
        self.ax_memory.set_title('Memory Usage (%)', fontsize=9, pad=3)
        self.ax_memory.set_ylim(0, 100)
        self.ax_memory.grid(True, alpha=0.3)

        # 绘制网络图表
        self.ax_network.plot(list(self.time_data), list(self.network_up_data),
                           color='#45b7d1', linewidth=2, label='Upload')
        self.ax_network.plot(list(self.time_data), list(self.network_down_data),
                           color='#96ceb4', linewidth=2, label='Download')
        self.ax_network.set_title('Network I/O (KB/s)', fontsize=9, pad=3)

        # 动态调整网络图表的Y轴范围
        max_network = max(max(self.network_up_data), max(self.network_down_data))
        if max_network > 0:
            self.ax_network.set_ylim(0, max(100, max_network * 1.1))
        else:
            self.ax_network.set_ylim(0, 100)

        self.ax_network.grid(True, alpha=0.3)
        self.ax_network.legend(fontsize=8)

        # 设置X轴范围（显示最近60个点）
        if len(self.time_data) > 0:
            x_min = max(0, self.time_data[-1] - 59)
            x_max = self.time_data[-1] + 1
            for ax in [self.ax_cpu, self.ax_memory, self.ax_network]:
                ax.set_xlim(x_min, x_max)

        # 保存图表为图片并显示在QLabel中
        try:
            import io
            from PyQt6.QtGui import QPixmap

            # 保存图表到内存中的字节流
            buf = io.BytesIO()
            self.figure.savefig(
                buf,
                format='png',
                dpi=100,  # 提高DPI获得更清晰的图像
                bbox_inches='tight',  # 自动调整边界
                facecolor='white',    # 设置背景色
                edgecolor='none',     # 无边框
                pad_inches=0.1        # 小的内边距
            )
            buf.seek(0)

            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())

            # 缩放pixmap以适应QLabel大小
            if not pixmap.isNull():
                label_size = self.chart_label.size()
                if label_size.width() > 0 and label_size.height() > 0:
                    scaled_pixmap = pixmap.scaled(
                        label_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.chart_label.setPixmap(scaled_pixmap)
                else:
                    self.chart_label.setPixmap(pixmap)

            buf.close()

        except Exception as e:
            print(f"更新图表显示失败: {e}")

    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        # 移除自动调整图表大小，避免阻塞
        # 图表大小将在初始化时设置，不再动态调整

    def adjust_chart_size(self):
        """调整图表大小以适应容器（简化版，避免阻塞）"""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'chart_label'):
            return

        try:
            # 只调整QLabel的最小尺寸，不修改matplotlib figure
            container_size = self.size()
            width = max(400, container_size.width() - 40)
            height = max(300, container_size.height() - 40)

            self.chart_label.setMinimumSize(width, height)

        except Exception as e:
            print(f"调整图表大小失败: {e}")


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
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # 创建标签页
        self.tabs = QTabWidget()

        # 数值视图标签页
        self.create_numeric_view()
        self.tabs.addTab(self.numeric_view, "数值视图")

        # 图表视图标签页
        if MATPLOTLIB_AVAILABLE:
            self.create_chart_view()
            self.tabs.addTab(self.chart_view, "图表视图")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_numeric_view(self):
        """创建数值视图"""
        self.numeric_view = QWidget()
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
        self.numeric_view.setLayout(layout)

    def create_chart_view(self):
        """创建图表视图"""
        self.chart_view = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # 创建性能图表
        self.performance_chart = PerformanceChart()
        layout.addWidget(self.performance_chart)

        self.chart_view.setLayout(layout)
    
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
            sent_kbs = 0
            recv_kbs = 0

            if hasattr(self, 'last_net_io'):
                bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
                bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv

                # 转换为KB/s (2秒间隔)
                sent_kbs = max(0, bytes_sent / 1024 / 2)  # 确保非负数
                recv_kbs = max(0, bytes_recv / 1024 / 2)  # 确保非负数

                self.network_label.setText(f"↑ {sent_kbs:.1f} KB/s ↓ {recv_kbs:.1f} KB/s")
            else:
                # 第一次更新时显示0
                self.network_label.setText("↑ 0.0 KB/s ↓ 0.0 KB/s")

            self.last_net_io = current_net_io

            # 更新图表（如果可用）- 确保数据一致性
            if MATPLOTLIB_AVAILABLE and hasattr(self, 'performance_chart'):
                # 使用与显示完全相同的数据
                chart_cpu = float(cpu_percent)
                chart_memory = float(memory_percent)
                chart_sent = float(sent_kbs)
                chart_recv = float(recv_kbs)

                self.performance_chart.update_chart(chart_cpu, chart_memory, chart_sent, chart_recv)



            # 更新服务器统计
            self.update_server_stats()
            
        except Exception as e:
            print(f"更新性能指标失败: {e}")
    
    def update_server_stats(self):
        """更新服务器统计"""
        try:
            # 检查服务器是否运行
            if not self.server_manager.is_running:
                # 服务器未运行时显示0
                self.connections_label.setText("0")
                self.requests_label.setText("0")
                self.uploads_label.setText("0")
                self.downloads_label.setText("0")
                self.transfer_label.setText("↑ 0.0 MB ↓ 0.0 MB")
                return

            # 从服务器管理器获取真实统计数据（非阻塞）
            stats = self.server_manager.get_server_statistics()

            # 更新连接数
            connections = stats.get('connections', 0)
            self.connections_label.setText(str(connections))

            # 更新请求数
            requests = stats.get('requests', 0)
            self.requests_label.setText(str(requests))

            # 更新上传下载数
            uploads = stats.get('uploads', 0)
            downloads = stats.get('downloads', 0)
            self.uploads_label.setText(str(uploads))
            self.downloads_label.setText(str(downloads))

            # 更新传输量
            upload_bytes = stats.get('upload_bytes', 0)
            download_bytes = stats.get('download_bytes', 0)

            # 转换为MB
            upload_mb = upload_bytes / (1024 * 1024) if upload_bytes > 0 else 0
            download_mb = download_bytes / (1024 * 1024) if download_bytes > 0 else 0

            self.transfer_label.setText(f"↑ {upload_mb:.1f} MB ↓ {download_mb:.1f} MB")

        except Exception as e:
            # 静默处理错误，避免日志污染
            # 发生错误时显示基本信息
            if self.server_manager.is_running:
                # 服务器运行但无法获取统计时，显示基本状态
                self.connections_label.setText("-")
                self.requests_label.setText("-")
                self.uploads_label.setText("-")
                self.downloads_label.setText("-")
                self.transfer_label.setText("获取中...")
            else:
                # 服务器未运行
                self.connections_label.setText("0")
                self.requests_label.setText("0")
                self.uploads_label.setText("0")
                self.downloads_label.setText("0")
                self.transfer_label.setText("↑ 0.0 MB ↓ 0.0 MB")
    
    def update_log(self):
        """更新日志显示"""
        if not self.log_paused:
            try:
                # 从服务器管理器获取真实日志
                if self.server_manager.is_running:
                    stdout, stderr = self.server_manager.get_server_logs()

                    # 处理新的日志输出
                    if stdout:
                        lines = stdout.strip().split('\n')
                        for line in lines[-5:]:  # 只显示最新的5行
                            if line.strip():
                                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                                log_line = f"[{timestamp}] {line.strip()}"
                                self.log_display.append(log_line)

                    if stderr:
                        lines = stderr.strip().split('\n')
                        for line in lines[-3:]:  # 只显示最新的3行错误
                            if line.strip():
                                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                                log_line = f"[{timestamp}] ERROR: {line.strip()}"
                                self.log_display.append(log_line)

                # 限制日志行数
                if self.log_display.document().blockCount() > 100:
                    cursor = self.log_display.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    cursor.select(cursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()

            except Exception as e:
                # 如果获取真实日志失败，显示状态信息
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                if self.server_manager.is_running:
                    status_msg = "服务器运行中..."
                else:
                    status_msg = "服务器未运行"

                # 每30秒显示一次状态（避免频繁显示）
                import time
                current_time = int(time.time())
                if not hasattr(self, '_last_status_time') or current_time - self._last_status_time >= 30:
                    log_line = f"[{timestamp}] {status_msg}"
                    self.log_display.append(log_line)
                    self._last_status_time = current_time
    
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
