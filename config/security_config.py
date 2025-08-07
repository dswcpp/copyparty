"""
安全配置模块
迁移自 copyparty_complete_config.py 中的 TLSConfig 并扩展
"""

import os
from typing import List, Dict, Any, Optional
from .base_config import BaseConfig, ValidationResult


class TLSConfig(BaseConfig):
    """TLS/SSL 配置 - 迁移自 TLSConfig"""
    
    def __init__(self):
        super().__init__()
        
        # 基本 TLS 设置
        self.http_only: bool = False  # --http-only
        self.https_only: bool = False  # --https-only
        self.cert_path: str = ""  # --cert
        self.ssl_versions: str = ""  # --ssl-ver
        self.ciphers: str = ""  # --ciphers
        
        # 调试选项
        self.ssl_debug: bool = False  # --ssl-dbg
        self.ssl_log_path: str = ""  # --ssl-log
        
        # 设置验证规则
        self._type_rules = {
            'http_only': bool,
            'https_only': bool,
            'cert_path': str,
            'ssl_versions': str,
            'ciphers': str,
            'ssl_debug': bool,
            'ssl_log_path': str
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'http_only': self.http_only,
            'https_only': self.https_only,
            'cert_path': self.cert_path,
            'ssl_versions': self.ssl_versions,
            'ciphers': self.ciphers,
            'ssl_debug': self.ssl_debug,
            'ssl_log_path': self.ssl_log_path
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.http_only = data.get('http_only', False)
        self.https_only = data.get('https_only', False)
        self.cert_path = data.get('cert_path', "")
        self.ssl_versions = data.get('ssl_versions', "")
        self.ciphers = data.get('ciphers', "")
        self.ssl_debug = data.get('ssl_debug', False)
        self.ssl_log_path = data.get('ssl_log_path', "")
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # HTTP/HTTPS 模式
        if self.http_only:
            args.append('--http-only')
        elif self.https_only:
            args.append('--https-only')
        
        # 证书路径
        if self.cert_path:
            args.extend(['--cert', self.cert_path])
        
        # SSL 版本
        if self.ssl_versions:
            args.extend(['--ssl-ver', self.ssl_versions])
        
        # 密码套件
        if self.ciphers:
            args.extend(['--ciphers', self.ciphers])
        
        # 调试选项
        if self.ssl_debug:
            args.append('--ssl-dbg')
        
        if self.ssl_log_path:
            args.extend(['--ssl-log', self.ssl_log_path])
        
        return args
    
    def _custom_validation(self, result: ValidationResult):
        """自定义验证"""
        # 验证互斥选项
        if self.http_only and self.https_only:
            result.add_error("http_only 和 https_only 不能同时启用")
        
        # 验证证书文件
        if self.cert_path and not os.path.exists(self.cert_path):
            result.add_error(f"证书文件不存在: {self.cert_path}")
        
        # 验证SSL日志路径
        if self.ssl_log_path:
            log_dir = os.path.dirname(self.ssl_log_path)
            if log_dir and not os.path.exists(log_dir):
                result.add_warning(f"SSL日志目录不存在: {log_dir}")


class AuthenticationConfig(BaseConfig):
    """身份认证配置"""
    
    def __init__(self):
        super().__init__()
        
        # 基本认证
        self.enable_authentication: bool = False
        self.default_permissions: str = "r"  # 默认权限
        
        # 身份提供商
        self.identity_providers: List[str] = []  # --idp-*
        
        # IP 认证
        self.ip_authentication: Dict[str, str] = {}  # IP -> 用户名映射
        
        # 会话管理
        self.session_timeout: int = 3600  # 会话超时时间（秒）
        self.max_sessions_per_user: int = 5  # 每用户最大会话数
        
        # 密码策略
        self.min_password_length: int = 6
        self.require_strong_password: bool = False
        
        # 设置验证规则
        self._type_rules = {
            'enable_authentication': bool,
            'default_permissions': str,
            'identity_providers': list,
            'ip_authentication': dict,
            'session_timeout': int,
            'max_sessions_per_user': int,
            'min_password_length': int,
            'require_strong_password': bool
        }
        self._value_rules = {
            'session_timeout': {'min': 60, 'max': 86400},
            'max_sessions_per_user': {'min': 1, 'max': 100},
            'min_password_length': {'min': 1, 'max': 128}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enable_authentication': self.enable_authentication,
            'default_permissions': self.default_permissions,
            'identity_providers': self.identity_providers,
            'ip_authentication': self.ip_authentication,
            'session_timeout': self.session_timeout,
            'max_sessions_per_user': self.max_sessions_per_user,
            'min_password_length': self.min_password_length,
            'require_strong_password': self.require_strong_password
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enable_authentication = data.get('enable_authentication', False)
        self.default_permissions = data.get('default_permissions', "r")
        self.identity_providers = data.get('identity_providers', [])
        self.ip_authentication = data.get('ip_authentication', {})
        self.session_timeout = data.get('session_timeout', 3600)
        self.max_sessions_per_user = data.get('max_sessions_per_user', 5)
        self.min_password_length = data.get('min_password_length', 6)
        self.require_strong_password = data.get('require_strong_password', False)
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # 身份提供商
        for idp in self.identity_providers:
            args.extend(['--idp', idp])
        
        # IP 认证
        for ip, username in self.ip_authentication.items():
            args.extend(['--ipu', f"{ip}:{username}"])
        
        # TODO: 添加其他认证相关的命令行参数
        
        return args
    
    def add_ip_authentication(self, ip: str, username: str):
        """添加IP认证"""
        self.ip_authentication[ip] = username
        self.mark_changed()
    
    def remove_ip_authentication(self, ip: str):
        """删除IP认证"""
        if ip in self.ip_authentication:
            del self.ip_authentication[ip]
            self.mark_changed()
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度"""
        if len(password) < self.min_password_length:
            return False
        
        if self.require_strong_password:
            # 检查强密码要求
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            return has_upper and has_lower and has_digit and has_special
        
        return True


class SecurityConfig(BaseConfig):
    """安全配置组合"""
    
    def __init__(self):
        super().__init__()
        
        self.tls = TLSConfig()
        self.authentication = AuthenticationConfig()
        
        # 安全选项
        self.enable_cors: bool = False  # 启用CORS
        self.cors_origins: List[str] = []  # 允许的CORS源
        
        # 访问控制
        self.ip_whitelist: List[str] = []  # IP白名单
        self.ip_blacklist: List[str] = []  # IP黑名单
        
        # 安全头
        self.security_headers: Dict[str, str] = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        
        # 设置验证规则
        self._type_rules = {
            'enable_cors': bool,
            'cors_origins': list,
            'ip_whitelist': list,
            'ip_blacklist': list,
            'security_headers': dict
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'tls': self.tls.to_dict(),
            'authentication': self.authentication.to_dict(),
            'enable_cors': self.enable_cors,
            'cors_origins': self.cors_origins,
            'ip_whitelist': self.ip_whitelist,
            'ip_blacklist': self.ip_blacklist,
            'security_headers': self.security_headers
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        if 'tls' in data:
            self.tls.from_dict(data['tls'])
        
        if 'authentication' in data:
            self.authentication.from_dict(data['authentication'])
        
        self.enable_cors = data.get('enable_cors', False)
        self.cors_origins = data.get('cors_origins', [])
        self.ip_whitelist = data.get('ip_whitelist', [])
        self.ip_blacklist = data.get('ip_blacklist', [])
        self.security_headers = data.get('security_headers', {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        })
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # TLS 参数
        args.extend(self.tls.get_command_args())
        
        # 认证参数
        args.extend(self.authentication.get_command_args())
        
        # TODO: 添加其他安全相关的命令行参数
        
        return args
    
    def validate(self) -> ValidationResult:
        """验证安全配置"""
        result = super().validate()
        
        # 验证子配置
        tls_result = self.tls.validate()
        if not tls_result:
            for error in tls_result.errors:
                result.add_error(f"TLS: {error}")
            for warning in tls_result.warnings:
                result.add_warning(f"TLS: {warning}")
        
        auth_result = self.authentication.validate()
        if not auth_result:
            for error in auth_result.errors:
                result.add_error(f"Authentication: {error}")
            for warning in auth_result.warnings:
                result.add_warning(f"Authentication: {warning}")
        
        return result
    
    @property
    def changed(self) -> bool:
        """检查是否有任何配置更改"""
        return super().changed or self.tls.changed or self.authentication.changed
