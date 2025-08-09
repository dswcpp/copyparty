"""
账户和卷管理UI组件
提供完整的账户管理和卷管理用户界面
"""

import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QTabWidget, QGroupBox, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QComboBox, QCheckBox, QSpinBox, QTextEdit,
                             QListWidget, QSplitter, QMessageBox, QFileDialog,
                             QHeaderView, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    from features.account_management import AccountManager, AccountManagerConfig, Account, UserGroup, PermissionType
    from features.volume_management import VolumeManager, VolumeManagerConfig, VolumeConfig, VolumeType, AccessMode
except ImportError:
    # 如果模块不可用，创建占位符
    class AccountManager:
        def __init__(self, config): pass
        def get_statistics(self): return {}
    
    class VolumeManager:
        def __init__(self, config): pass
        def get_statistics(self): return {}


class SimpleAccountDialog(QDialog):
    """简化的账户编辑对话框"""

    def __init__(self, account=None, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("编辑账户" if account else "创建账户")
        self.setModal(True)
        self.resize(400, 300)

        # 主布局
        layout = QVBoxLayout()

        # 用户名
        layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit)

        # 密码
        layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)

        # 权限设置
        layout.addWidget(QLabel("权限设置:"))

        # 权限复选框
        self.perm_checks = {}
        permissions = [
            ("读取", "r"), ("写入", "w"), ("移动", "m"), ("删除", "d"),
            ("管理员", "a"), ("GET", "g"), ("PUT", "p"), ("POST", "o")
        ]

        for name, code in permissions:
            check = QCheckBox(name)
            check.setVisible(True)
            check.show()
            self.perm_checks[code] = check
            layout.addWidget(check)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # 确保所有权限复选框可见
        for checkbox in self.perm_checks.values():
            checkbox.setVisible(True)
            checkbox.show()

    def showEvent(self, event):
        """对话框显示事件"""
        super().showEvent(event)
        # 在对话框显示后强制设置复选框可见
        for checkbox in self.perm_checks.values():
            checkbox.setVisible(True)
            checkbox.show()
            checkbox.update()
        self.update()

    def get_data(self):
        """获取对话框数据"""
        permissions = []
        for code, check in self.perm_checks.items():
            if check.isChecked():
                permissions.append(code)

        return {
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'permissions': permissions
        }


class AccountDialog(QDialog):
    """账户编辑对话框"""

    def __init__(self, account=None, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("编辑账户" if account else "创建账户")
        self.setModal(True)

        # 初始化权限复选框字典
        self.perm_checks = {}

        self.init_ui()
        if account:
            self.load_account()

        # 在UI初始化后设置大小
        self.resize(500, 400)

    def showEvent(self, event):
        """对话框显示事件 - 确保复选框可见"""
        super().showEvent(event)
        # 在对话框显示后强制设置复选框可见
        for checkbox in self.perm_checks.values():
            checkbox.setVisible(True)
            checkbox.show()
            checkbox.update()
        self.update()

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("用户名:"), 0, 0)
        self.username_edit = QLineEdit()
        basic_layout.addWidget(self.username_edit, 0, 1)
        
        basic_layout.addWidget(QLabel("密码:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        basic_layout.addWidget(self.password_edit, 1, 1)

        basic_layout.addWidget(QLabel("确认密码:"), 2, 0)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        basic_layout.addWidget(self.confirm_password_edit, 2, 1)
        
        self.enabled_check = QCheckBox("启用账户")
        self.enabled_check.setChecked(True)
        basic_layout.addWidget(self.enabled_check, 3, 0, 1, 2)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 权限设置 - 恢复原来的QGroupBox布局
        perm_group = QGroupBox("权限设置")
        perm_layout = QGridLayout()

        self.perm_checks = {}
        permissions = [
            ("读取", "r"), ("写入", "w"), ("移动", "m"), ("删除", "d"),
            ("管理员", "a"), ("GET", "g"), ("PUT", "p"), ("POST", "o")
        ]

        # 使用2行4列的网格布局
        for i, (name, code) in enumerate(permissions):
            check = QCheckBox(name)
            check.setVisible(True)  # 确保可见
            check.show()  # 强制显示
            self.perm_checks[code] = check
            row = i // 4
            col = i % 4
            perm_layout.addWidget(check, row, col)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)
        
        # 卷访问
        volume_group = QGroupBox("卷访问")
        volume_layout = QVBoxLayout()
        
        volume_layout.addWidget(QLabel("可访问的卷 (每行一个):"))
        self.volumes_edit = QTextEdit()
        self.volumes_edit.setMaximumHeight(80)
        volume_layout.addWidget(self.volumes_edit)
        
        volume_group.setLayout(volume_layout)
        layout.addWidget(volume_group)
        
        # 用户组
        group_group = QGroupBox("用户组")
        group_layout = QVBoxLayout()
        
        group_layout.addWidget(QLabel("所属用户组 (每行一个):"))
        self.groups_edit = QTextEdit()
        self.groups_edit.setMaximumHeight(60)
        group_layout.addWidget(self.groups_edit)
        
        group_group.setLayout(group_layout)
        layout.addWidget(group_group)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def force_show_permissions(self):
        """强制显示权限复选框"""
        # 强制显示所有权限复选框
        for code, checkbox in self.perm_checks.items():
            checkbox.setVisible(True)
            checkbox.show()
            checkbox.update()

        # 强制更新布局
        self.updateGeometry()
        self.update()

    def load_account(self):
        """加载账户信息"""
        if not self.account:
            return

        self.username_edit.setText(self.account.username)
        self.username_edit.setEnabled(False)  # 不允许修改用户名
        self.enabled_check.setChecked(self.account.enabled)

        # 加载权限
        for perm in self.account.permissions:
            if perm.value in self.perm_checks:
                self.perm_checks[perm.value].setChecked(True)

        # 加载卷
        self.volumes_edit.setPlainText('\n'.join(self.account.volumes))

        # 加载用户组
        self.groups_edit.setPlainText('\n'.join(self.account.groups))
    
    def get_account_data(self):
        """获取账户数据"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # 验证
        if not username:
            QMessageBox.warning(self, "错误", "用户名不能为空")
            return None

        if not self.account and not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return None

        if password and password != confirm_password:
            QMessageBox.warning(self, "错误", "密码确认不匹配")
            return None
        
        # 收集权限
        permissions = []
        for code, check in self.perm_checks.items():
            if check.isChecked():
                permissions.append(code)
        
        # 收集卷
        volumes_text = self.volumes_edit.toPlainText().strip()
        volumes = [v.strip() for v in volumes_text.split('\n') if v.strip()]
        
        # 收集用户组
        groups_text = self.groups_edit.toPlainText().strip()
        groups = [g.strip() for g in groups_text.split('\n') if g.strip()]
        
        return {
            'username': username,
            'password': password,
            'permissions': permissions,
            'volumes': volumes,
            'groups': groups,
            'enabled': self.enabled_check.isChecked()
        }


class VolumeDialog(QDialog):
    """卷编辑对话框"""
    
    def __init__(self, volume=None, parent=None):
        super().__init__(parent)
        self.volume = volume
        self.setWindowTitle("编辑卷" if volume else "创建卷")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
        if volume:
            self.load_volume()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("卷名称:"), 0, 0)
        self.name_edit = QLineEdit()
        basic_layout.addWidget(self.name_edit, 0, 1)
        
        basic_layout.addWidget(QLabel("本地路径:"), 1, 0)
        path_layout = QHBoxLayout()
        self.local_path_edit = QLineEdit()
        path_layout.addWidget(self.local_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_local_path)
        path_layout.addWidget(browse_btn)
        basic_layout.addLayout(path_layout, 1, 1)
        
        basic_layout.addWidget(QLabel("虚拟路径:"), 2, 0)
        self.virtual_path_edit = QLineEdit()
        self.virtual_path_edit.setText("/")
        basic_layout.addWidget(self.virtual_path_edit, 2, 1)
        
        basic_layout.addWidget(QLabel("卷类型:"), 3, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["读写", "只读", "只写", "追加"])
        basic_layout.addWidget(self.type_combo, 3, 1)
        
        basic_layout.addWidget(QLabel("访问模式:"), 4, 0)
        self.access_combo = QComboBox()
        self.access_combo.addItems(["公开", "私有", "受保护", "隐藏"])
        basic_layout.addWidget(self.access_combo, 4, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 功能选项
        features_group = QGroupBox("功能选项")
        features_layout = QGridLayout()
        
        self.feature_checks = {}
        features = [
            ("启用上传", "enable_upload"), ("启用删除", "enable_delete"),
            ("启用移动", "enable_move"), ("启用创建目录", "enable_mkdir"),
            ("启用列表", "enable_listing"), ("启用搜索", "enable_search"),
            ("启用缩略图", "enable_thumbnail"), ("启用预览", "enable_preview")
        ]
        
        for i, (name, attr) in enumerate(features):
            check = QCheckBox(name)
            check.setChecked(True)
            self.feature_checks[attr] = check
            features_layout.addWidget(check, i // 4, i % 4)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 限制设置
        limits_group = QGroupBox("限制设置")
        limits_layout = QGridLayout()
        
        limits_layout.addWidget(QLabel("最大文件大小(MB):"), 0, 0)
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(0, 10240)
        self.max_file_size_spin.setSuffix(" MB")
        limits_layout.addWidget(self.max_file_size_spin, 0, 1)
        
        limits_layout.addWidget(QLabel("最大总大小(GB):"), 0, 2)
        self.max_total_size_spin = QSpinBox()
        self.max_total_size_spin.setRange(0, 1024)
        self.max_total_size_spin.setSuffix(" GB")
        limits_layout.addWidget(self.max_total_size_spin, 0, 3)
        
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)
        
        # 描述
        desc_group = QGroupBox("描述")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def browse_local_path(self):
        """浏览本地路径"""
        path = QFileDialog.getExistingDirectory(self, "选择卷目录")
        if path:
            self.local_path_edit.setText(path)
    
    def load_volume(self):
        """加载卷信息"""
        if not self.volume:
            return
        
        self.name_edit.setText(self.volume.name)
        self.name_edit.setEnabled(False)  # 不允许修改卷名
        self.local_path_edit.setText(self.volume.local_path)
        self.virtual_path_edit.setText(self.volume.virtual_path)
        
        # 设置类型
        type_map = {"rw": 0, "ro": 1, "wo": 2, "ao": 3}
        self.type_combo.setCurrentIndex(type_map.get(self.volume.volume_type.value, 0))
        
        # 设置访问模式
        access_map = {"public": 0, "private": 1, "protected": 2, "hidden": 3}
        self.access_combo.setCurrentIndex(access_map.get(self.volume.access_mode.value, 0))
        
        # 设置功能选项
        for attr, check in self.feature_checks.items():
            check.setChecked(getattr(self.volume, attr, True))
        
        # 设置限制
        self.max_file_size_spin.setValue(self.volume.max_file_size // (1024 * 1024))
        self.max_total_size_spin.setValue(self.volume.max_total_size // (1024 * 1024 * 1024))
        
        # 设置描述
        self.description_edit.setPlainText(self.volume.description)
    
    def get_volume_data(self):
        """获取卷数据"""
        name = self.name_edit.text().strip()
        local_path = self.local_path_edit.text().strip()
        virtual_path = self.virtual_path_edit.text().strip()
        
        # 验证
        if not name:
            QMessageBox.warning(self, "错误", "卷名称不能为空")
            return None
        
        if not local_path:
            QMessageBox.warning(self, "错误", "本地路径不能为空")
            return None
        
        if not virtual_path:
            QMessageBox.warning(self, "错误", "虚拟路径不能为空")
            return None
        
        # 类型映射
        type_values = ["rw", "ro", "wo", "ao"]
        access_values = ["public", "private", "protected", "hidden"]
        
        return {
            'name': name,
            'local_path': local_path,
            'virtual_path': virtual_path,
            'volume_type': type_values[self.type_combo.currentIndex()],
            'access_mode': access_values[self.access_combo.currentIndex()],
            'features': {attr: check.isChecked() for attr, check in self.feature_checks.items()},
            'max_file_size': self.max_file_size_spin.value() * 1024 * 1024,
            'max_total_size': self.max_total_size_spin.value() * 1024 * 1024 * 1024,
            'description': self.description_edit.toPlainText().strip()
        }


class AccountVolumeManagerWidget(QWidget):
    """账户和卷管理组件"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        
        # 初始化管理器
        self.account_config = AccountManagerConfig()
        self.volume_config = VolumeManagerConfig()
        
        try:
            self.account_manager = AccountManager(self.account_config)
            self.volume_manager = VolumeManager(self.volume_config)
        except Exception as e:
            print(f"管理器初始化失败: {e}")
            self.account_manager = None
            self.volume_manager = None
        
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 账户管理标签页
        self.create_accounts_tab()
        
        # 卷管理标签页
        self.create_volumes_tab()
        
        # 统计信息标签页
        self.create_statistics_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def create_accounts_tab(self):
        """创建账户管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_account_btn = QPushButton("添加账户")
        self.add_account_btn.clicked.connect(self.add_account)
        toolbar_layout.addWidget(self.add_account_btn)
        
        self.edit_account_btn = QPushButton("编辑账户")
        self.edit_account_btn.clicked.connect(self.edit_account)
        toolbar_layout.addWidget(self.edit_account_btn)
        
        self.delete_account_btn = QPushButton("删除账户")
        self.delete_account_btn.clicked.connect(self.delete_account)
        toolbar_layout.addWidget(self.delete_account_btn)
        
        toolbar_layout.addStretch()
        
        self.refresh_accounts_btn = QPushButton("刷新")
        self.refresh_accounts_btn.clicked.connect(self.refresh_accounts)
        toolbar_layout.addWidget(self.refresh_accounts_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 账户表格
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(6)
        self.accounts_table.setHorizontalHeaderLabels([
            "用户名", "权限", "卷数量", "用户组", "状态", "最后登录"
        ])
        
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.accounts_table)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "账户管理")
    
    def create_volumes_tab(self):
        """创建卷管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_volume_btn = QPushButton("添加卷")
        self.add_volume_btn.clicked.connect(self.add_volume)
        toolbar_layout.addWidget(self.add_volume_btn)
        
        self.edit_volume_btn = QPushButton("编辑卷")
        self.edit_volume_btn.clicked.connect(self.edit_volume)
        toolbar_layout.addWidget(self.edit_volume_btn)
        
        self.delete_volume_btn = QPushButton("删除卷")
        self.delete_volume_btn.clicked.connect(self.delete_volume)
        toolbar_layout.addWidget(self.delete_volume_btn)
        
        toolbar_layout.addStretch()
        
        self.refresh_volumes_btn = QPushButton("刷新")
        self.refresh_volumes_btn.clicked.connect(self.refresh_volumes)
        toolbar_layout.addWidget(self.refresh_volumes_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 卷表格
        self.volumes_table = QTableWidget()
        self.volumes_table.setColumnCount(6)
        self.volumes_table.setHorizontalHeaderLabels([
            "卷名称", "本地路径", "虚拟路径", "类型", "访问模式", "文件数量"
        ])
        
        header = self.volumes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.volumes_table.setAlternatingRowColors(True)
        self.volumes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.volumes_table)
        
        widget.setLayout(layout)
        self.tabs.addTab(widget, "卷管理")
    
    def create_statistics_tab(self):
        """创建统计信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 账户统计
        account_stats_group = QGroupBox("账户统计")
        account_stats_layout = QGridLayout()
        
        self.total_accounts_label = QLabel("0")
        account_stats_layout.addWidget(QLabel("总账户数:"), 0, 0)
        account_stats_layout.addWidget(self.total_accounts_label, 0, 1)
        
        self.enabled_accounts_label = QLabel("0")
        account_stats_layout.addWidget(QLabel("启用账户:"), 0, 2)
        account_stats_layout.addWidget(self.enabled_accounts_label, 0, 3)
        
        self.admin_accounts_label = QLabel("0")
        account_stats_layout.addWidget(QLabel("管理员账户:"), 1, 0)
        account_stats_layout.addWidget(self.admin_accounts_label, 1, 1)
        
        self.active_sessions_label = QLabel("0")
        account_stats_layout.addWidget(QLabel("活跃会话:"), 1, 2)
        account_stats_layout.addWidget(self.active_sessions_label, 1, 3)
        
        account_stats_group.setLayout(account_stats_layout)
        layout.addWidget(account_stats_group)
        
        # 卷统计
        volume_stats_group = QGroupBox("卷统计")
        volume_stats_layout = QGridLayout()
        
        self.total_volumes_label = QLabel("0")
        volume_stats_layout.addWidget(QLabel("总卷数:"), 0, 0)
        volume_stats_layout.addWidget(self.total_volumes_label, 0, 1)
        
        self.total_files_label = QLabel("0")
        volume_stats_layout.addWidget(QLabel("总文件数:"), 0, 2)
        volume_stats_layout.addWidget(self.total_files_label, 0, 3)
        
        self.total_size_label = QLabel("0 B")
        volume_stats_layout.addWidget(QLabel("总大小:"), 1, 0)
        volume_stats_layout.addWidget(self.total_size_label, 1, 1)
        
        volume_stats_group.setLayout(volume_stats_layout)
        layout.addWidget(volume_stats_group)
        
        # 刷新按钮
        refresh_stats_btn = QPushButton("刷新统计")
        refresh_stats_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_stats_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "统计信息")
    
    def add_account(self):
        """添加账户"""
        dialog = AccountDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_account_data()
            if data and self.account_manager:
                success = self.account_manager.create_account(
                    data['username'], data['password'], data['permissions'],
                    data['volumes'], data['groups']
                )
                if success:
                    self.refresh_accounts()
                    QMessageBox.information(self, "成功", "账户创建成功")
                else:
                    QMessageBox.warning(self, "失败", "账户创建失败")
    
    def edit_account(self):
        """编辑账户"""
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要编辑的账户")
            return
        
        username = self.accounts_table.item(current_row, 0).text()
        if self.account_manager and username in self.account_manager.accounts:
            account = self.account_manager.accounts[username]
            dialog = AccountDialog(account, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 这里可以实现账户更新逻辑
                self.refresh_accounts()
    
    def delete_account(self):
        """删除账户"""
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要删除的账户")
            return
        
        username = self.accounts_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除账户 '{username}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.account_manager and username in self.account_manager.accounts:
                del self.account_manager.accounts[username]
                self.refresh_accounts()
                QMessageBox.information(self, "成功", "账户删除成功")
    
    def add_volume(self):
        """添加卷"""
        dialog = VolumeDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_volume_data()
            if data and self.volume_manager:
                from features.volume_management import VolumeType, AccessMode
                success = self.volume_manager.create_volume(
                    data['name'], data['local_path'], data['virtual_path'],
                    VolumeType(data['volume_type']), AccessMode(data['access_mode'])
                )
                if success:
                    self.refresh_volumes()
                    QMessageBox.information(self, "成功", "卷创建成功")
                else:
                    QMessageBox.warning(self, "失败", "卷创建失败")
    
    def edit_volume(self):
        """编辑卷"""
        current_row = self.volumes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要编辑的卷")
            return
        
        volume_name = self.volumes_table.item(current_row, 0).text()
        if self.volume_manager:
            volume = self.volume_manager.get_volume(volume_name)
            if volume:
                dialog = VolumeDialog(volume, parent=self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # 这里可以实现卷更新逻辑
                    self.refresh_volumes()
    
    def delete_volume(self):
        """删除卷"""
        current_row = self.volumes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要删除的卷")
            return
        
        volume_name = self.volumes_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除卷 '{volume_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.volume_manager:
                success = self.volume_manager.delete_volume(volume_name)
                if success:
                    self.refresh_volumes()
                    QMessageBox.information(self, "成功", "卷删除成功")
                else:
                    QMessageBox.warning(self, "失败", "卷删除失败")
    
    def refresh_accounts(self):
        """刷新账户列表"""
        if not self.account_manager:
            return
        
        self.accounts_table.setRowCount(0)
        
        for account in self.account_manager.accounts.values():
            row = self.accounts_table.rowCount()
            self.accounts_table.insertRow(row)
            
            # 用户名
            self.accounts_table.setItem(row, 0, QTableWidgetItem(account.username))
            
            # 权限
            perms = "".join([p.value for p in account.permissions])
            self.accounts_table.setItem(row, 1, QTableWidgetItem(perms))
            
            # 卷数量
            self.accounts_table.setItem(row, 2, QTableWidgetItem(str(len(account.volumes))))
            
            # 用户组
            groups = ", ".join(account.groups)
            self.accounts_table.setItem(row, 3, QTableWidgetItem(groups))
            
            # 状态
            status = "启用" if account.enabled else "禁用"
            self.accounts_table.setItem(row, 4, QTableWidgetItem(status))
            
            # 最后登录
            if account.last_login > 0:
                import datetime
                last_login = datetime.datetime.fromtimestamp(account.last_login).strftime("%Y-%m-%d %H:%M")
            else:
                last_login = "从未"
            self.accounts_table.setItem(row, 5, QTableWidgetItem(last_login))
    
    def refresh_volumes(self):
        """刷新卷列表"""
        if not self.volume_manager:
            return
        
        self.volumes_table.setRowCount(0)
        
        for volume in self.volume_manager.volumes.values():
            row = self.volumes_table.rowCount()
            self.volumes_table.insertRow(row)
            
            # 卷名称
            self.volumes_table.setItem(row, 0, QTableWidgetItem(volume.name))
            
            # 本地路径
            self.volumes_table.setItem(row, 1, QTableWidgetItem(volume.local_path))
            
            # 虚拟路径
            self.volumes_table.setItem(row, 2, QTableWidgetItem(volume.virtual_path))
            
            # 类型
            type_names = {"rw": "读写", "ro": "只读", "wo": "只写", "ao": "追加"}
            type_name = type_names.get(volume.volume_type.value, volume.volume_type.value)
            self.volumes_table.setItem(row, 3, QTableWidgetItem(type_name))
            
            # 访问模式
            access_names = {"public": "公开", "private": "私有", "protected": "受保护", "hidden": "隐藏"}
            access_name = access_names.get(volume.access_mode.value, volume.access_mode.value)
            self.volumes_table.setItem(row, 4, QTableWidgetItem(access_name))
            
            # 文件数量
            stats = self.volume_manager.volume_stats.get(volume.name, {})
            file_count = stats.get('file_count', 0)
            self.volumes_table.setItem(row, 5, QTableWidgetItem(str(file_count)))
    
    def refresh_statistics(self):
        """刷新统计信息"""
        if self.account_manager:
            account_stats = self.account_manager.get_statistics()
            self.total_accounts_label.setText(str(account_stats.get('total_accounts', 0)))
            self.enabled_accounts_label.setText(str(account_stats.get('enabled_accounts', 0)))
            self.admin_accounts_label.setText(str(account_stats.get('admin_accounts', 0)))
            self.active_sessions_label.setText(str(account_stats.get('active_sessions', 0)))
        
        if self.volume_manager:
            volume_stats = self.volume_manager.get_statistics()
            self.total_volumes_label.setText(str(volume_stats.get('total_volumes', 0)))
            self.total_files_label.setText(str(volume_stats.get('total_files', 0)))
            
            total_size = volume_stats.get('total_size', 0)
            size_str = self.format_file_size(total_size)
            self.total_size_label.setText(size_str)
    
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
    
    def refresh_data(self):
        """刷新所有数据"""
        self.refresh_accounts()
        self.refresh_volumes()
        self.refresh_statistics()
    
    def refresh(self):
        """刷新组件"""
        self.refresh_data()
