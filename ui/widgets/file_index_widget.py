"""
文件索引UI组件
提供文件索引和搜索的用户界面
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel, QPushButton, QLineEdit,
                             QProgressBar, QTableWidget, QTableWidgetItem,
                             QTabWidget, QCheckBox, QSpinBox, QTextEdit,
                             QListWidget, QSplitter, QMessageBox, QFileDialog,
                             QHeaderView)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from features.file_indexing import FileIndexer, FileIndexConfig, FileInfo
except ImportError:
    # 如果文件索引模块不可用，创建占位符
    class FileIndexConfig:
        def __init__(self):
            self.enabled = True
    
    class FileIndexer:
        def __init__(self, config, db_path):
            pass
        
        def search(self, query, limit=100):
            return []
        
        def get_statistics(self):
            return {'total_files': 0, 'total_directories': 0, 'total_size': 0}


class IndexingThread(QThread):
    """索引线程"""
    progress_updated = pyqtSignal(int, int, str)
    indexing_finished = pyqtSignal()
    
    def __init__(self, indexer, paths):
        super().__init__()
        self.indexer = indexer
        self.paths = paths
    
    def run(self):
        """运行索引"""
        self.indexer.set_progress_callback(self.on_progress)
        self.indexer.start_indexing(self.paths)
        self.indexing_finished.emit()
    
    def on_progress(self, current, total, message):
        """进度回调"""
        self.progress_updated.emit(current, total, message)


class FileIndexWidget(QWidget):
    """文件索引组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        
        # 初始化索引器
        self.index_config = FileIndexConfig()
        self.indexer = None
        self.indexing_thread = None
        
        self.init_ui()
        self.init_indexer()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 搜索标签页
        self.create_search_tab()
        
        # 索引管理标签页
        self.create_index_tab()
        
        # 配置标签页
        self.create_config_tab()
        
        # 统计标签页
        self.create_stats_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def create_search_tab(self):
        """创建搜索标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 搜索区域
        search_group = QGroupBox("文件搜索")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入文件名进行搜索...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 搜索结果
        results_group = QGroupBox("搜索结果")
        results_layout = QVBoxLayout()
        
        # 结果统计
        self.results_label = QLabel("准备搜索...")
        results_layout.addWidget(self.results_label)
        
        # 结果表格
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "文件名", "路径", "大小", "类型", "修改时间", "MD5"
        ])
        
        # 设置表格属性
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "搜索")
    
    def create_index_tab(self):
        """创建索引管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 索引控制
        control_group = QGroupBox("索引控制")
        control_layout = QGridLayout()
        
        # 索引路径
        control_layout.addWidget(QLabel("索引路径:"), 0, 0)
        self.index_paths_list = QListWidget()
        self.index_paths_list.setMaximumHeight(100)
        control_layout.addWidget(self.index_paths_list, 0, 1, 2, 1)
        
        self.add_path_btn = QPushButton("添加路径")
        self.add_path_btn.clicked.connect(self.add_index_path)
        control_layout.addWidget(self.add_path_btn, 0, 2)
        
        self.remove_path_btn = QPushButton("删除路径")
        self.remove_path_btn.clicked.connect(self.remove_index_path)
        control_layout.addWidget(self.remove_path_btn, 1, 2)
        
        # 索引操作
        control_layout.addWidget(QLabel("操作:"), 2, 0)
        
        button_layout = QHBoxLayout()
        
        self.start_index_btn = QPushButton("开始索引")
        self.start_index_btn.clicked.connect(self.start_indexing)
        button_layout.addWidget(self.start_index_btn)
        
        self.stop_index_btn = QPushButton("停止索引")
        self.stop_index_btn.clicked.connect(self.stop_indexing)
        self.stop_index_btn.setEnabled(False)
        button_layout.addWidget(self.stop_index_btn)
        
        self.rebuild_index_btn = QPushButton("重建索引")
        self.rebuild_index_btn.clicked.connect(self.rebuild_index)
        button_layout.addWidget(self.rebuild_index_btn)
        
        button_layout.addStretch()
        control_layout.addLayout(button_layout, 2, 1, 1, 2)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 索引进度
        progress_group = QGroupBox("索引进度")
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 索引日志
        log_group = QGroupBox("索引日志")
        log_layout = QVBoxLayout()
        
        self.index_log = QTextEdit()
        self.index_log.setMaximumHeight(150)
        self.index_log.setReadOnly(True)
        self.index_log.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.index_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "索引管理")
    
    def create_config_tab(self):
        """创建配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 基本配置
        basic_group = QGroupBox("基本配置")
        basic_layout = QGridLayout()
        
        self.enable_indexing_check = QCheckBox("启用文件索引")
        self.enable_indexing_check.setChecked(True)
        basic_layout.addWidget(self.enable_indexing_check, 0, 0, 1, 2)
        
        self.index_hidden_check = QCheckBox("索引隐藏文件")
        basic_layout.addWidget(self.index_hidden_check, 1, 0)
        
        self.index_system_check = QCheckBox("索引系统文件")
        basic_layout.addWidget(self.index_system_check, 1, 1)
        
        basic_layout.addWidget(QLabel("索引间隔(秒):"), 2, 0)
        self.index_interval_spin = QSpinBox()
        self.index_interval_spin.setRange(60, 3600)
        self.index_interval_spin.setValue(300)
        basic_layout.addWidget(self.index_interval_spin, 2, 1)
        
        basic_layout.addWidget(QLabel("批处理大小:"), 3, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(10, 1000)
        self.batch_size_spin.setValue(100)
        basic_layout.addWidget(self.batch_size_spin, 3, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 哈希配置
        hash_group = QGroupBox("哈希计算")
        hash_layout = QGridLayout()
        
        self.calculate_hashes_check = QCheckBox("计算文件哈希值")
        self.calculate_hashes_check.setChecked(True)
        hash_layout.addWidget(self.calculate_hashes_check, 0, 0, 1, 2)
        
        self.md5_check = QCheckBox("MD5")
        self.md5_check.setChecked(True)
        hash_layout.addWidget(self.md5_check, 1, 0)
        
        self.sha1_check = QCheckBox("SHA1")
        self.sha1_check.setChecked(True)
        hash_layout.addWidget(self.sha1_check, 1, 1)
        
        hash_layout.addWidget(QLabel("最大文件大小(MB):"), 2, 0)
        self.max_hash_size_spin = QSpinBox()
        self.max_hash_size_spin.setRange(1, 1024)
        self.max_hash_size_spin.setValue(100)
        hash_layout.addWidget(self.max_hash_size_spin, 2, 1)
        
        hash_group.setLayout(hash_layout)
        layout.addWidget(hash_group)
        
        # 过滤配置
        filter_group = QGroupBox("过滤设置")
        filter_layout = QVBoxLayout()
        
        filter_layout.addWidget(QLabel("排除的文件扩展名 (用逗号分隔):"))
        self.excluded_ext_edit = QLineEdit()
        self.excluded_ext_edit.setText(".tmp,.log,.cache")
        filter_layout.addWidget(self.excluded_ext_edit)
        
        filter_layout.addWidget(QLabel("排除的目录名 (用逗号分隔):"))
        self.excluded_dirs_edit = QLineEdit()
        self.excluded_dirs_edit.setText(".git,__pycache__,node_modules")
        filter_layout.addWidget(self.excluded_dirs_edit)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 配置按钮
        config_btn_layout = QHBoxLayout()
        
        self.apply_config_btn = QPushButton("应用配置")
        self.apply_config_btn.clicked.connect(self.apply_config)
        config_btn_layout.addWidget(self.apply_config_btn)
        
        self.reset_config_btn = QPushButton("重置配置")
        self.reset_config_btn.clicked.connect(self.reset_config)
        config_btn_layout.addWidget(self.reset_config_btn)
        
        config_btn_layout.addStretch()
        layout.addLayout(config_btn_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "配置")
    
    def create_stats_tab(self):
        """创建统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 统计信息
        stats_group = QGroupBox("索引统计")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("总文件数:"), 0, 0)
        self.total_files_label = QLabel("0")
        stats_layout.addWidget(self.total_files_label, 0, 1)
        
        stats_layout.addWidget(QLabel("总目录数:"), 0, 2)
        self.total_dirs_label = QLabel("0")
        stats_layout.addWidget(self.total_dirs_label, 0, 3)
        
        stats_layout.addWidget(QLabel("总大小:"), 1, 0)
        self.total_size_label = QLabel("0 B")
        stats_layout.addWidget(self.total_size_label, 1, 1)
        
        stats_layout.addWidget(QLabel("MIME类型:"), 1, 2)
        self.mime_types_label = QLabel("0")
        stats_layout.addWidget(self.mime_types_label, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "统计")
    
    def init_indexer(self):
        """初始化索引器"""
        try:
            # 创建索引数据库路径
            db_path = os.path.join(os.path.expanduser("~"), ".copyparty_desktop", "file_index.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.indexer = FileIndexer(self.index_config, db_path)
            self.log_message("文件索引器初始化成功")
            
            # 添加默认索引路径
            if hasattr(self.config_manager, 'server_config'):
                work_dir = self.config_manager.server_config.working_directory
                if work_dir and os.path.exists(work_dir):
                    self.index_paths_list.addItem(work_dir)
            
        except Exception as e:
            self.log_message(f"文件索引器初始化失败: {e}")
    
    def perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        if not self.indexer:
            QMessageBox.warning(self, "搜索失败", "文件索引器未初始化")
            return
        
        try:
            results = self.indexer.search(query, limit=1000)
            self.display_search_results(results)
            self.results_label.setText(f"找到 {len(results)} 个结果")
            
        except Exception as e:
            QMessageBox.critical(self, "搜索错误", f"搜索失败: {str(e)}")
    
    def display_search_results(self, results):
        """显示搜索结果"""
        self.results_table.setRowCount(len(results))
        
        for row, file_info in enumerate(results):
            # 文件名
            self.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
            
            # 路径
            self.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
            
            # 大小
            size_str = self.format_file_size(file_info.size) if not file_info.is_directory else "目录"
            self.results_table.setItem(row, 2, QTableWidgetItem(size_str))
            
            # 类型
            type_str = file_info.mime_type or "未知"
            self.results_table.setItem(row, 3, QTableWidgetItem(type_str))
            
            # 修改时间
            import datetime
            mtime_str = datetime.datetime.fromtimestamp(file_info.mtime).strftime("%Y-%m-%d %H:%M:%S")
            self.results_table.setItem(row, 4, QTableWidgetItem(mtime_str))
            
            # MD5
            md5_str = file_info.hash_md5 or ""
            self.results_table.setItem(row, 5, QTableWidgetItem(md5_str))
    
    def clear_search(self):
        """清空搜索"""
        self.search_input.clear()
        self.results_table.setRowCount(0)
        self.results_label.setText("准备搜索...")
    
    def add_index_path(self):
        """添加索引路径"""
        path = QFileDialog.getExistingDirectory(self, "选择索引目录")
        if path:
            self.index_paths_list.addItem(path)
    
    def remove_index_path(self):
        """删除索引路径"""
        current_row = self.index_paths_list.currentRow()
        if current_row >= 0:
            self.index_paths_list.takeItem(current_row)
    
    def start_indexing(self):
        """开始索引"""
        if not self.indexer:
            QMessageBox.warning(self, "索引失败", "文件索引器未初始化")
            return
        
        # 获取索引路径
        paths = []
        for i in range(self.index_paths_list.count()):
            paths.append(self.index_paths_list.item(i).text())
        
        if not paths:
            QMessageBox.warning(self, "索引失败", "请先添加索引路径")
            return
        
        # 启动索引线程
        self.indexing_thread = IndexingThread(self.indexer, paths)
        self.indexing_thread.progress_updated.connect(self.on_indexing_progress)
        self.indexing_thread.indexing_finished.connect(self.on_indexing_finished)
        self.indexing_thread.start()
        
        # 更新UI状态
        self.start_index_btn.setEnabled(False)
        self.stop_index_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_message("开始文件索引...")
    
    def stop_indexing(self):
        """停止索引"""
        if self.indexer:
            self.indexer.stop_indexing()
        
        if self.indexing_thread:
            self.indexing_thread.quit()
            self.indexing_thread.wait()
        
        self.on_indexing_finished()
        self.log_message("索引已停止")
    
    def rebuild_index(self):
        """重建索引"""
        reply = QMessageBox.question(
            self, "确认重建", "确定要重建索引吗？这将删除现有的索引数据。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: 实现重建索引
            self.log_message("重建索引功能开发中...")
    
    def on_indexing_progress(self, current, total, message):
        """索引进度更新"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        
        self.progress_label.setText(f"{message} ({current}/{total})")
    
    def on_indexing_finished(self):
        """索引完成"""
        self.start_index_btn.setEnabled(True)
        self.stop_index_btn.setEnabled(False)
        self.progress_label.setText("索引完成")
        self.log_message("文件索引完成")
        self.refresh_statistics()
    
    def apply_config(self):
        """应用配置"""
        try:
            # 更新配置
            self.index_config.enabled = self.enable_indexing_check.isChecked()
            self.index_config.index_hidden_files = self.index_hidden_check.isChecked()
            self.index_config.index_system_files = self.index_system_check.isChecked()
            self.index_config.index_interval = self.index_interval_spin.value()
            self.index_config.batch_size = self.batch_size_spin.value()
            
            self.index_config.calculate_hashes = self.calculate_hashes_check.isChecked()
            
            hash_algorithms = []
            if self.md5_check.isChecked():
                hash_algorithms.append('md5')
            if self.sha1_check.isChecked():
                hash_algorithms.append('sha1')
            self.index_config.hash_algorithms = hash_algorithms
            
            self.index_config.max_file_size_for_hash = self.max_hash_size_spin.value() * 1024 * 1024
            
            # 解析排除列表
            excluded_ext = [ext.strip() for ext in self.excluded_ext_edit.text().split(',') if ext.strip()]
            self.index_config.excluded_extensions = excluded_ext
            
            excluded_dirs = [dir.strip() for dir in self.excluded_dirs_edit.text().split(',') if dir.strip()]
            self.index_config.excluded_directories = excluded_dirs
            
            QMessageBox.information(self, "配置成功", "索引配置已应用")
            self.log_message("索引配置已更新")
            
        except Exception as e:
            QMessageBox.critical(self, "配置失败", f"应用配置失败: {str(e)}")
    
    def reset_config(self):
        """重置配置"""
        self.index_config = FileIndexConfig()
        self.load_config_to_ui()
        QMessageBox.information(self, "重置成功", "配置已重置为默认值")
    
    def load_config_to_ui(self):
        """加载配置到UI"""
        self.enable_indexing_check.setChecked(self.index_config.enabled)
        self.index_hidden_check.setChecked(self.index_config.index_hidden_files)
        self.index_system_check.setChecked(self.index_config.index_system_files)
        self.index_interval_spin.setValue(self.index_config.index_interval)
        self.batch_size_spin.setValue(self.index_config.batch_size)
        
        self.calculate_hashes_check.setChecked(self.index_config.calculate_hashes)
        self.md5_check.setChecked('md5' in self.index_config.hash_algorithms)
        self.sha1_check.setChecked('sha1' in self.index_config.hash_algorithms)
        self.max_hash_size_spin.setValue(self.index_config.max_file_size_for_hash // (1024 * 1024))
        
        self.excluded_ext_edit.setText(','.join(self.index_config.excluded_extensions))
        self.excluded_dirs_edit.setText(','.join(self.index_config.excluded_directories))
    
    def refresh_statistics(self):
        """刷新统计信息"""
        if not self.indexer:
            return
        
        try:
            stats = self.indexer.get_statistics()
            
            self.total_files_label.setText(str(stats.get('total_files', 0)))
            self.total_dirs_label.setText(str(stats.get('total_directories', 0)))
            self.total_size_label.setText(self.format_file_size(stats.get('total_size', 0)))
            self.mime_types_label.setText(str(stats.get('mime_types_count', 0)))
            
        except Exception as e:
            self.log_message(f"刷新统计失败: {e}")
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def log_message(self, message):
        """记录日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.index_log.append(f"[{timestamp}] {message}")
    
    def refresh(self):
        """刷新组件"""
        self.refresh_statistics()
