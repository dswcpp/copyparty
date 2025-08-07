"""
协议基类
定义所有网络协议的通用接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget


class ProtocolConfig:
    """协议配置基类"""
    
    def __init__(self):
        self.enabled = False
        self.port = 0
        self.bind_address = "0.0.0.0"
        self.max_connections = 100
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'port': self.port,
            'bind_address': self.bind_address,
            'max_connections': self.max_connections
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enabled = data.get('enabled', False)
        self.port = data.get('port', 0)
        self.bind_address = data.get('bind_address', "0.0.0.0")
        self.max_connections = data.get('max_connections', 100)


class BaseProtocol(ABC):
    """协议基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.config = ProtocolConfig()
        self.is_running = False
        
    @abstractmethod
    def get_display_name(self) -> str:
        """获取显示名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取协议描述"""
        pass
    
    @abstractmethod
    def get_default_port(self) -> int:
        """获取默认端口"""
        pass
    
    @abstractmethod
    def get_config_widget(self, parent=None) -> QWidget:
        """获取配置界面组件"""
        pass
    
    @abstractmethod
    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        pass
    
    @abstractmethod
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """获取支持的功能特性"""
        pass
    
    def is_enabled(self) -> bool:
        """检查协议是否启用"""
        return self.config.enabled
    
    def enable(self):
        """启用协议"""
        self.config.enabled = True
    
    def disable(self):
        """禁用协议"""
        self.config.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取协议状态"""
        return {
            'name': self.name,
            'display_name': self.get_display_name(),
            'enabled': self.config.enabled,
            'running': self.is_running,
            'port': self.config.port,
            'bind_address': self.config.bind_address
        }
    
    def get_config_summary(self) -> str:
        """获取配置摘要"""
        if not self.config.enabled:
            return f"{self.get_display_name()}: 已禁用"
        
        return f"{self.get_display_name()}: {self.config.bind_address}:{self.config.port}"


class ProtocolManager:
    """协议管理器"""
    
    def __init__(self):
        self.protocols: Dict[str, BaseProtocol] = {}
        self.load_builtin_protocols()
    
    def load_builtin_protocols(self):
        """加载内置协议"""
        try:
            from .http_server import HTTPProtocol
            self.register_protocol(HTTPProtocol())
        except ImportError:
            pass
        
        try:
            from .ftp_server import FTPProtocol
            self.register_protocol(FTPProtocol())
        except ImportError:
            pass
        
        try:
            from .webdav_server import WebDAVProtocol
            self.register_protocol(WebDAVProtocol())
        except ImportError:
            pass

        try:
            from .smb_server import SMBProtocol
            self.register_protocol(SMBProtocol())
        except ImportError:
            pass
        
        try:
            from .smb_server import SMBProtocol
            self.register_protocol(SMBProtocol())
        except ImportError:
            pass
    
    def register_protocol(self, protocol: BaseProtocol):
        """注册协议"""
        self.protocols[protocol.name] = protocol
    
    def get_protocol(self, name: str) -> Optional[BaseProtocol]:
        """获取协议"""
        return self.protocols.get(name)
    
    def get_all_protocols(self) -> List[BaseProtocol]:
        """获取所有协议"""
        return list(self.protocols.values())
    
    def get_enabled_protocols(self) -> List[BaseProtocol]:
        """获取启用的协议"""
        return [p for p in self.protocols.values() if p.is_enabled()]
    
    def generate_all_command_args(self) -> List[str]:
        """生成所有启用协议的命令行参数"""
        args = []
        for protocol in self.get_enabled_protocols():
            args.extend(protocol.generate_command_args())
        return args
    
    def validate_all_configs(self) -> tuple[bool, Dict[str, List[str]]]:
        """验证所有协议配置
        
        Returns:
            tuple: (all_valid, {protocol_name: error_messages})
        """
        all_valid = True
        errors = {}
        
        for name, protocol in self.protocols.items():
            if protocol.is_enabled():
                is_valid, error_messages = protocol.validate_config()
                if not is_valid:
                    all_valid = False
                    errors[name] = error_messages
        
        return all_valid, errors
    
    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        enabled_count = len(self.get_enabled_protocols())
        total_count = len(self.protocols)
        
        return {
            'total_protocols': total_count,
            'enabled_protocols': enabled_count,
            'protocols': {name: p.get_status() for name, p in self.protocols.items()}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            name: protocol.config.to_dict() 
            for name, protocol in self.protocols.items()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        for name, config_data in data.items():
            if name in self.protocols:
                self.protocols[name].config.from_dict(config_data)


class ProtocolPlugin(BaseProtocol):
    """协议插件基类"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.plugin_info = {
            'version': '1.0.0',
            'author': 'Unknown',
            'description': 'Protocol plugin',
            'dependencies': []
        }
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return self.plugin_info.copy()
    
    def check_dependencies(self) -> tuple[bool, List[str]]:
        """检查依赖项
        
        Returns:
            tuple: (dependencies_met, missing_dependencies)
        """
        missing = []
        
        for dep in self.plugin_info.get('dependencies', []):
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        return len(missing) == 0, missing
    
    def install_dependencies(self) -> bool:
        """安装依赖项"""
        # 子类可以重写此方法来实现自动依赖安装
        return False
