# 🏗️ CopyParty 桌面应用架构设计

## 📋 设计原则

基于功能完整性分析，我们需要重新设计架构来支持 160+ 个功能特性：

1. **模块化设计** - 每个功能模块独立开发和维护
2. **插件化架构** - 支持功能扩展和第三方插件
3. **分层架构** - 清晰的职责分离
4. **配置驱动** - 统一的配置管理系统
5. **可扩展性** - 易于添加新功能和协议

## 🏗️ 目录结构设计

```
copyparty_desktop/
├── main.py                     # 应用程序入口
├── requirements.txt            # 依赖管理
├── setup.py                   # 安装配置
├── README.md                  # 项目文档
│
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── application.py         # 主应用程序类
│   ├── config_manager.py      # 配置管理器
│   ├── server_manager.py      # 服务器管理器
│   ├── plugin_manager.py      # 插件管理器
│   └── event_system.py        # 事件系统
│
├── config/                    # 配置模块
│   ├── __init__.py
│   ├── base_config.py         # 基础配置类
│   ├── server_config.py       # 服务器配置
│   ├── network_config.py      # 网络配置
│   ├── security_config.py     # 安全配置
│   ├── media_config.py        # 媒体配置
│   ├── monitoring_config.py   # 监控配置
│   └── validation.py          # 配置验证
│
├── protocols/                 # 协议模块
│   ├── __init__.py
│   ├── base_protocol.py       # 协议基类
│   ├── http_server.py         # HTTP/HTTPS 服务器
│   ├── ftp_server.py          # FTP/FTPS 服务器
│   ├── webdav_server.py       # WebDAV 服务器
│   ├── smb_server.py          # SMB 服务器
│   └── tftp_server.py         # TFTP 服务器
│
├── features/                  # 功能模块
│   ├── __init__.py
│   ├── file_indexing.py       # 文件索引系统
│   ├── search_engine.py       # 搜索引擎
│   ├── deduplication.py       # 去重功能
│   ├── compression.py         # 压缩功能
│   ├── media_server.py        # 媒体服务器
│   ├── transcoding.py         # 音频转码
│   ├── thumbnail.py           # 缩略图生成
│   └── file_sharing.py        # 文件分享
│
├── security/                  # 安全模块
│   ├── __init__.py
│   ├── authentication.py     # 身份认证
│   ├── authorization.py      # 权限管理
│   ├── identity_providers.py # 身份提供商
│   ├── ip_auth.py            # IP 认证
│   ├── oauth_handler.py      # OAuth 处理
│   └── ldap_handler.py       # LDAP 处理
│
├── monitoring/                # 监控模块
│   ├── __init__.py
│   ├── metrics_collector.py  # 指标收集
│   ├── prometheus_exporter.py # Prometheus 导出
│   ├── event_hooks.py        # 事件钩子
│   ├── logging_manager.py    # 日志管理
│   └── performance_monitor.py # 性能监控
│
├── ui/                        # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   ├── widgets/               # UI 组件
│   │   ├── __init__.py
│   │   ├── server_control.py  # 服务器控制组件
│   │   ├── config_editor.py   # 配置编辑器
│   │   ├── protocol_config.py # 协议配置组件
│   │   ├── security_config.py # 安全配置组件
│   │   ├── monitoring_panel.py # 监控面板
│   │   └── log_viewer.py      # 日志查看器
│   ├── dialogs/               # 对话框
│   │   ├── __init__.py
│   │   ├── preferences.py     # 偏好设置
│   │   ├── about.py          # 关于对话框
│   │   ├── wizard.py         # 配置向导
│   │   └── plugin_manager.py # 插件管理对话框
│   └── themes/                # 主题系统
│       ├── __init__.py
│       ├── theme_manager.py   # 主题管理器
│       ├── default.qss        # 默认主题
│       └── dark.qss          # 暗色主题
│
├── plugins/                   # 插件系统
│   ├── __init__.py
│   ├── base_plugin.py         # 插件基类
│   ├── protocol_plugin.py     # 协议插件基类
│   ├── feature_plugin.py      # 功能插件基类
│   └── examples/              # 示例插件
│       ├── custom_auth.py     # 自定义认证插件
│       └── custom_protocol.py # 自定义协议插件
│
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── file_utils.py          # 文件工具
│   ├── network_utils.py       # 网络工具
│   ├── system_utils.py        # 系统工具
│   ├── crypto_utils.py        # 加密工具
│   └── validation_utils.py    # 验证工具
│
├── resources/                 # 资源文件
│   ├── icons/                 # 图标文件
│   ├── translations/          # 国际化文件
│   └── templates/             # 配置模板
│
├── tests/                     # 测试模块
│   ├── __init__.py
│   ├── test_config.py         # 配置测试
│   ├── test_protocols.py      # 协议测试
│   ├── test_features.py       # 功能测试
│   └── test_ui.py            # UI 测试
│
└── docs/                      # 文档
    ├── user_guide.md          # 用户指南
    ├── developer_guide.md     # 开发者指南
    ├── api_reference.md       # API 参考
    └── plugin_development.md  # 插件开发指南
```

## 🔧 核心架构组件

### 1. **应用程序入口** (`main.py`)
```python
#!/usr/bin/env python3
"""
CopyParty Desktop Application
主应用程序入口点
"""

import sys
from PyQt6.QtWidgets import QApplication
from core.application import CopyPartyApplication

def main():
    app = QApplication(sys.argv)
    copyparty_app = CopyPartyApplication()
    copyparty_app.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

### 2. **主应用程序类** (`core/application.py`)
```python
class CopyPartyApplication(QMainWindow):
    """主应用程序类 - 协调所有模块"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.server_manager = ServerManager()
        self.plugin_manager = PluginManager()
        self.init_ui()
        self.load_plugins()
    
    def init_ui(self):
        """初始化用户界面"""
        from ui.main_window import MainWindow
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
```

### 3. **配置管理器** (`core/config_manager.py`)
```python
class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self):
        self.server_config = ServerConfig()
        self.network_config = NetworkConfig()
        self.security_config = SecurityConfig()
        self.media_config = MediaConfig()
        self.monitoring_config = MonitoringConfig()
    
    def load_config(self, file_path: str):
        """加载配置文件"""
        pass
    
    def save_config(self, file_path: str):
        """保存配置文件"""
        pass
    
    def validate_config(self) -> ValidationResult:
        """验证配置有效性"""
        pass
```

### 4. **插件管理器** (`core/plugin_manager.py`)
```python
class PluginManager:
    """插件管理器 - 支持功能扩展"""
    
    def __init__(self):
        self.loaded_plugins = {}
        self.protocol_plugins = {}
        self.feature_plugins = {}
    
    def load_plugins(self):
        """加载所有插件"""
        pass
    
    def register_protocol(self, name: str, plugin: ProtocolPlugin):
        """注册协议插件"""
        pass
    
    def register_feature(self, name: str, plugin: FeaturePlugin):
        """注册功能插件"""
        pass
```

## 🎯 模块职责划分

### 📊 **配置模块** (`config/`)
- **职责**: 管理所有配置选项和验证
- **包含**: 160+ 个 CopyParty 配置选项的结构化管理
- **特点**: 类型安全、验证完整、易于扩展

### 🌐 **协议模块** (`protocols/`)
- **职责**: 实现各种网络协议服务器
- **包含**: HTTP/HTTPS, FTP/FTPS, WebDAV, SMB, TFTP
- **特点**: 插件化设计、统一接口、独立配置

### ⚙️ **功能模块** (`features/`)
- **职责**: 实现核心功能特性
- **包含**: 文件索引、搜索、去重、压缩、媒体服务
- **特点**: 模块化实现、可选启用、性能优化

### 🔒 **安全模块** (`security/`)
- **职责**: 处理身份认证和权限管理
- **包含**: OAuth, LDAP, IP认证, 权限控制
- **特点**: 安全第一、多种认证方式、细粒度权限

### 📈 **监控模块** (`monitoring/`)
- **职责**: 系统监控和指标收集
- **包含**: Prometheus集成、事件钩子、性能监控
- **特点**: 实时监控、可扩展指标、事件驱动

### 🎨 **UI模块** (`ui/`)
- **职责**: 用户界面和交互
- **包含**: 主窗口、配置界面、监控面板
- **特点**: 响应式设计、主题支持、用户友好

## 🔌 插件化设计

### **协议插件接口**
```python
class ProtocolPlugin:
    def get_name(self) -> str:
        """获取协议名称"""
        pass
    
    def get_config_widget(self) -> QWidget:
        """获取配置界面"""
        pass
    
    def generate_args(self, config) -> List[str]:
        """生成命令行参数"""
        pass
    
    def validate_config(self, config) -> bool:
        """验证配置"""
        pass
```

### **功能插件接口**
```python
class FeaturePlugin:
    def get_name(self) -> str:
        """获取功能名称"""
        pass
    
    def get_dependencies(self) -> List[str]:
        """获取依赖项"""
        pass
    
    def initialize(self, app_context):
        """初始化功能"""
        pass
    
    def get_config_options(self) -> Dict:
        """获取配置选项"""
        pass
```

## 🚀 实施计划

### **阶段 1: 核心架构** (1周)
1. 创建目录结构
2. 实现核心类框架
3. 建立配置系统基础
4. 设计插件接口

### **阶段 2: 基础功能** (2周)
1. 迁移现有功能到新架构
2. 实现HTTP协议模块
3. 完善配置管理
4. 基础UI框架

### **阶段 3: 扩展功能** (3-4周)
1. 实现其他协议模块
2. 添加核心功能模块
3. 完善安全模块
4. 监控系统集成

### **阶段 4: 完善优化** (1-2周)
1. 插件系统完善
2. UI优化和主题
3. 测试和文档
4. 性能优化

这个架构设计支持渐进式开发，可以逐步迁移现有功能并添加新功能，同时保持代码的可维护性和可扩展性。
