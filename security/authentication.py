"""
用户认证和权限管理模块
实现CopyParty的完整认证系统
"""

import hashlib
import secrets
import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class PermissionLevel(Enum):
    """权限级别枚举"""
    READ = "r"           # 只读
    WRITE = "w"          # 写入
    MOVE = "m"           # 移动/重命名
    DELETE = "d"         # 删除
    ADMIN = "a"          # 管理员
    GET = "g"            # GET请求
    PUT = "p"            # PUT请求
    POST = "o"           # POST请求


@dataclass
class User:
    """用户数据类"""
    username: str
    password_hash: str
    salt: str
    permissions: Set[PermissionLevel]
    volumes: List[str] = None  # 可访问的卷
    ip_restrictions: List[str] = None  # IP限制
    session_timeout: int = 3600  # 会话超时(秒)
    max_sessions: int = 5  # 最大并发会话数
    enabled: bool = True
    created_at: float = None
    last_login: float = None
    login_count: int = 0
    
    def __post_init__(self):
        if self.volumes is None:
            self.volumes = []
        if self.ip_restrictions is None:
            self.ip_restrictions = []
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class Session:
    """会话数据类"""
    session_id: str
    username: str
    ip_address: str
    user_agent: str
    created_at: float
    last_accessed: float
    expires_at: float
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return time.time() > self.expires_at
    
    def refresh(self, timeout: int):
        """刷新会话"""
        self.last_accessed = time.time()
        self.expires_at = self.last_accessed + timeout


class AuthenticationConfig:
    """认证配置类 - 对应CopyParty的认证选项"""
    
    def __init__(self):
        # 基础认证配置
        self.enabled = False
        self.require_auth_for_read = False
        self.require_auth_for_write = True
        
        # CopyParty 认证选项对应
        self.accounts = []              # -a: 账户列表
        self.account_file = ""          # --accounts: 账户文件
        self.groups = []                # -g: 用户组
        self.group_file = ""            # --groups: 用户组文件
        
        # 密码策略
        self.min_password_length = 6
        self.require_strong_password = False
        self.password_expiry_days = 0  # 0表示不过期
        self.max_login_attempts = 5
        self.lockout_duration = 300    # 锁定时间(秒)
        
        # 会话管理
        self.session_timeout = 3600    # 会话超时
        self.max_sessions_per_user = 5
        self.session_cleanup_interval = 300
        
        # IP访问控制
        self.ip_whitelist = []
        self.ip_blacklist = []
        self.enable_ip_restrictions = False
        
        # 高级认证选项
        self.enable_2fa = False        # 双因素认证
        self.enable_ldap = False       # LDAP认证
        self.ldap_server = ""
        self.ldap_base_dn = ""
        self.ldap_bind_dn = ""
        self.ldap_bind_password = ""
        
        # 审计日志
        self.enable_audit_log = True
        self.audit_log_file = "auth_audit.log"
        self.log_failed_attempts = True
        self.log_successful_logins = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'require_auth_for_read': self.require_auth_for_read,
            'require_auth_for_write': self.require_auth_for_write,
            
            # CopyParty选项
            'accounts': self.accounts,
            'account_file': self.account_file,
            'groups': self.groups,
            'group_file': self.group_file,
            
            # 密码策略
            'min_password_length': self.min_password_length,
            'require_strong_password': self.require_strong_password,
            'password_expiry_days': self.password_expiry_days,
            'max_login_attempts': self.max_login_attempts,
            'lockout_duration': self.lockout_duration,
            
            # 会话管理
            'session_timeout': self.session_timeout,
            'max_sessions_per_user': self.max_sessions_per_user,
            'session_cleanup_interval': self.session_cleanup_interval,
            
            # IP访问控制
            'ip_whitelist': self.ip_whitelist,
            'ip_blacklist': self.ip_blacklist,
            'enable_ip_restrictions': self.enable_ip_restrictions,
            
            # 高级认证
            'enable_2fa': self.enable_2fa,
            'enable_ldap': self.enable_ldap,
            'ldap_server': self.ldap_server,
            'ldap_base_dn': self.ldap_base_dn,
            'ldap_bind_dn': self.ldap_bind_dn,
            'ldap_bind_password': self.ldap_bind_password,
            
            # 审计日志
            'enable_audit_log': self.enable_audit_log,
            'audit_log_file': self.audit_log_file,
            'log_failed_attempts': self.log_failed_attempts,
            'log_successful_logins': self.log_successful_logins
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enabled = data.get('enabled', False)
        self.require_auth_for_read = data.get('require_auth_for_read', False)
        self.require_auth_for_write = data.get('require_auth_for_write', True)
        
        # CopyParty选项
        self.accounts = data.get('accounts', [])
        self.account_file = data.get('account_file', "")
        self.groups = data.get('groups', [])
        self.group_file = data.get('group_file', "")
        
        # 密码策略
        self.min_password_length = data.get('min_password_length', 6)
        self.require_strong_password = data.get('require_strong_password', False)
        self.password_expiry_days = data.get('password_expiry_days', 0)
        self.max_login_attempts = data.get('max_login_attempts', 5)
        self.lockout_duration = data.get('lockout_duration', 300)
        
        # 会话管理
        self.session_timeout = data.get('session_timeout', 3600)
        self.max_sessions_per_user = data.get('max_sessions_per_user', 5)
        self.session_cleanup_interval = data.get('session_cleanup_interval', 300)
        
        # IP访问控制
        self.ip_whitelist = data.get('ip_whitelist', [])
        self.ip_blacklist = data.get('ip_blacklist', [])
        self.enable_ip_restrictions = data.get('enable_ip_restrictions', False)
        
        # 高级认证
        self.enable_2fa = data.get('enable_2fa', False)
        self.enable_ldap = data.get('enable_ldap', False)
        self.ldap_server = data.get('ldap_server', "")
        self.ldap_base_dn = data.get('ldap_base_dn', "")
        self.ldap_bind_dn = data.get('ldap_bind_dn', "")
        self.ldap_bind_password = data.get('ldap_bind_password', "")
        
        # 审计日志
        self.enable_audit_log = data.get('enable_audit_log', True)
        self.audit_log_file = data.get('audit_log_file', "auth_audit.log")
        self.log_failed_attempts = data.get('log_failed_attempts', True)
        self.log_successful_logins = data.get('log_successful_logins', True)
    
    def generate_copyparty_args(self) -> List[str]:
        """生成CopyParty命令行参数"""
        args = []
        
        # 账户配置
        for account in self.accounts:
            args.extend(['-a', account])
        
        if self.account_file:
            args.extend(['--accounts', self.account_file])
        
        # 用户组配置
        for group in self.groups:
            args.extend(['-g', group])
        
        if self.group_file:
            args.extend(['--groups', self.group_file])
        
        # 会话超时
        if self.session_timeout != 3600:
            args.extend(['--session-timeout', str(self.session_timeout)])
        
        # IP访问控制
        for ip in self.ip_whitelist:
            args.extend(['--allow-ip', ip])
        
        for ip in self.ip_blacklist:
            args.extend(['--deny-ip', ip])
        
        return args


class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self, config: AuthenticationConfig):
        self.config = config
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.failed_attempts: Dict[str, List[float]] = {}  # IP -> 失败时间列表
        self.locked_ips: Dict[str, float] = {}  # IP -> 锁定到期时间
        
    def create_user(self, username: str, password: str, permissions: List[str], 
                   volumes: List[str] = None, ip_restrictions: List[str] = None) -> bool:
        """创建用户"""
        if username in self.users:
            return False
        
        # 验证密码强度
        if not self._validate_password(password):
            return False
        
        # 生成盐值和密码哈希
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        # 转换权限
        perm_set = set()
        for perm in permissions:
            try:
                perm_set.add(PermissionLevel(perm))
            except ValueError:
                continue
        
        # 创建用户
        user = User(
            username=username,
            password_hash=password_hash,
            salt=salt,
            permissions=perm_set,
            volumes=volumes or [],
            ip_restrictions=ip_restrictions or []
        )
        
        self.users[username] = user
        return True
    
    def authenticate(self, username: str, password: str, ip_address: str) -> Optional[str]:
        """用户认证，返回会话ID"""
        # 检查IP是否被锁定
        if self._is_ip_locked(ip_address):
            return None
        
        # 检查用户是否存在
        if username not in self.users:
            self._record_failed_attempt(ip_address)
            return None
        
        user = self.users[username]
        
        # 检查用户是否启用
        if not user.enabled:
            return None
        
        # 检查IP限制
        if user.ip_restrictions and ip_address not in user.ip_restrictions:
            return None
        
        # 验证密码
        if not self._verify_password(password, user.password_hash, user.salt):
            self._record_failed_attempt(ip_address)
            return None
        
        # 检查最大会话数
        active_sessions = self._get_user_sessions(username)
        if len(active_sessions) >= user.max_sessions:
            # 清理最旧的会话
            oldest_session = min(active_sessions, key=lambda s: s.last_accessed)
            del self.sessions[oldest_session.session_id]
        
        # 创建新会话
        session_id = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            username=username,
            ip_address=ip_address,
            user_agent="",  # 可以从请求头获取
            created_at=time.time(),
            last_accessed=time.time(),
            expires_at=time.time() + user.session_timeout
        )
        
        self.sessions[session_id] = session
        
        # 更新用户登录信息
        user.last_login = time.time()
        user.login_count += 1
        
        # 清除失败尝试记录
        if ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """验证会话"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # 检查会话是否过期
        if session.is_expired():
            del self.sessions[session_id]
            return None
        
        # 刷新会话
        user = self.users.get(session.username)
        if user:
            session.refresh(user.session_timeout)
            return user
        
        return None
    
    def logout(self, session_id: str) -> bool:
        """用户登出"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def check_permission(self, session_id: str, required_permission: PermissionLevel, 
                        volume: str = None) -> bool:
        """检查权限"""
        user = self.validate_session(session_id)
        if not user:
            return False
        
        # 检查是否有所需权限
        if required_permission not in user.permissions:
            return False
        
        # 检查卷访问权限
        if volume and user.volumes and volume not in user.volumes:
            return False
        
        return True
    
    def _validate_password(self, password: str) -> bool:
        """验证密码强度"""
        if len(password) < self.config.min_password_length:
            return False
        
        if self.config.require_strong_password:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            return has_upper and has_lower and has_digit and has_special
        
        return True
    
    def _hash_password(self, password: str, salt: str) -> str:
        """哈希密码"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """验证密码"""
        return self._hash_password(password, salt) == password_hash
    
    def _record_failed_attempt(self, ip_address: str):
        """记录失败尝试"""
        now = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        # 清理过期的失败记录（1小时内）
        self.failed_attempts[ip_address] = [
            attempt_time for attempt_time in self.failed_attempts[ip_address]
            if now - attempt_time < 3600
        ]
        
        self.failed_attempts[ip_address].append(now)
        
        # 检查是否需要锁定IP
        if len(self.failed_attempts[ip_address]) >= self.config.max_login_attempts:
            self.locked_ips[ip_address] = now + self.config.lockout_duration
    
    def _is_ip_locked(self, ip_address: str) -> bool:
        """检查IP是否被锁定"""
        if ip_address not in self.locked_ips:
            return False
        
        if time.time() > self.locked_ips[ip_address]:
            del self.locked_ips[ip_address]
            return False
        
        return True
    
    def _get_user_sessions(self, username: str) -> List[Session]:
        """获取用户的所有活跃会话"""
        return [session for session in self.sessions.values() 
                if session.username == username and not session.is_expired()]
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取认证统计信息"""
        active_sessions = len([s for s in self.sessions.values() if not s.is_expired()])
        
        return {
            'total_users': len(self.users),
            'active_sessions': active_sessions,
            'locked_ips': len(self.locked_ips),
            'failed_attempts_ips': len(self.failed_attempts)
        }
