"""
账户管理功能模块
实现CopyParty的完整账户和用户组管理系统
对应CopyParty的 -a, --accounts, -g, --groups 等选项
"""

import os
import time
import hashlib
import secrets
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class PermissionType(Enum):
    """权限类型枚举 - 对应CopyParty权限系统"""
    READ = "r"           # 读取权限
    WRITE = "w"          # 写入权限
    MOVE = "m"           # 移动/重命名权限
    DELETE = "d"         # 删除权限
    ADMIN = "a"          # 管理员权限
    GET = "g"            # GET请求权限
    PUT = "p"            # PUT请求权限
    POST = "o"           # POST请求权限


@dataclass
class Account:
    """账户数据类 - 对应CopyParty的账户格式"""
    username: str
    password: str = ""
    password_hash: str = ""
    permissions: Set[PermissionType] = field(default_factory=set)
    volumes: List[str] = field(default_factory=list)  # 可访问的卷路径
    ip_whitelist: List[str] = field(default_factory=list)  # IP白名单
    groups: List[str] = field(default_factory=list)  # 所属用户组
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    last_login: float = 0
    login_count: int = 0
    
    def to_copyparty_format(self) -> str:
        """转换为CopyParty账户格式: username:password:permissions:volumes"""
        # 按照CopyParty标准顺序排列权限: r,w,m,d,a,g,p,o
        perm_order = ['r', 'w', 'm', 'd', 'a', 'g', 'p', 'o']
        perms = "".join([p for p in perm_order if PermissionType(p) in self.permissions])
        volumes_str = ",".join(self.volumes) if self.volumes else ""

        if volumes_str:
            return f"{self.username}:{self.password}:{perms}:{volumes_str}"
        else:
            return f"{self.username}:{self.password}:{perms}"
    
    @classmethod
    def from_copyparty_format(cls, account_str: str) -> 'Account':
        """从CopyParty账户格式解析"""
        parts = account_str.split(":")
        if len(parts) < 3:
            raise ValueError(f"无效的账户格式: {account_str}")
        
        username = parts[0]
        password = parts[1]
        perms_str = parts[2]
        volumes = parts[3].split(",") if len(parts) > 3 and parts[3] else []
        
        # 解析权限
        permissions = set()
        for char in perms_str:
            try:
                permissions.add(PermissionType(char))
            except ValueError:
                pass  # 忽略无效权限字符
        
        return cls(
            username=username,
            password=password,
            permissions=permissions,
            volumes=volumes
        )


@dataclass
class UserGroup:
    """用户组数据类 - 对应CopyParty的用户组系统"""
    name: str
    permissions: Set[PermissionType] = field(default_factory=set)
    volumes: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)  # 成员用户名列表
    description: str = ""
    created_at: float = field(default_factory=time.time)
    
    def to_copyparty_format(self) -> str:
        """转换为CopyParty用户组格式"""
        # 按照CopyParty标准顺序排列权限: r,w,m,d,a,g,p,o
        perm_order = ['r', 'w', 'm', 'd', 'a', 'g', 'p', 'o']
        perms = "".join([p for p in perm_order if PermissionType(p) in self.permissions])
        volumes_str = ",".join(self.volumes) if self.volumes else ""

        if volumes_str:
            return f"{self.name}:{perms}:{volumes_str}"
        else:
            return f"{self.name}:{perms}"
    
    @classmethod
    def from_copyparty_format(cls, group_str: str) -> 'UserGroup':
        """从CopyParty用户组格式解析"""
        parts = group_str.split(":")
        if len(parts) < 2:
            raise ValueError(f"无效的用户组格式: {group_str}")
        
        name = parts[0]
        perms_str = parts[1]
        volumes = parts[2].split(",") if len(parts) > 2 and parts[2] else []
        
        # 解析权限
        permissions = set()
        for char in perms_str:
            try:
                permissions.add(PermissionType(char))
            except ValueError:
                pass
        
        return cls(
            name=name,
            permissions=permissions,
            volumes=volumes
        )


class AccountManagerConfig:
    """账户管理配置类"""
    
    def __init__(self):
        # 基础配置
        self.enabled = False
        self.require_auth = True
        
        # CopyParty账户选项
        self.accounts = []              # -a: 内联账户列表
        self.accounts_file = ""         # --accounts: 账户文件路径
        self.groups = []                # -g: 内联用户组列表
        self.groups_file = ""           # --groups: 用户组文件路径
        
        # 高级认证选项
        self.identity_providers = []    # --idp-*: 身份提供商配置
        self.ip_auth_users = []         # --ipu: IP认证用户
        self.ip_auth_admin = []         # --ipa: IP认证管理员
        
        # 密码策略
        self.min_password_length = 6
        self.require_strong_password = False
        self.password_hash_algorithm = "sha256"
        self.password_salt_length = 16
        
        # 会话管理
        self.session_timeout = 3600
        self.max_sessions_per_user = 5
        self.remember_me_duration = 30 * 24 * 3600  # 30天
        
        # 安全选项
        self.enable_brute_force_protection = True
        self.max_login_attempts = 5
        self.lockout_duration = 300
        self.enable_audit_log = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'require_auth': self.require_auth,
            'accounts': self.accounts,
            'accounts_file': self.accounts_file,
            'groups': self.groups,
            'groups_file': self.groups_file,
            'identity_providers': self.identity_providers,
            'ip_auth_users': self.ip_auth_users,
            'ip_auth_admin': self.ip_auth_admin,
            'min_password_length': self.min_password_length,
            'require_strong_password': self.require_strong_password,
            'password_hash_algorithm': self.password_hash_algorithm,
            'password_salt_length': self.password_salt_length,
            'session_timeout': self.session_timeout,
            'max_sessions_per_user': self.max_sessions_per_user,
            'remember_me_duration': self.remember_me_duration,
            'enable_brute_force_protection': self.enable_brute_force_protection,
            'max_login_attempts': self.max_login_attempts,
            'lockout_duration': self.lockout_duration,
            'enable_audit_log': self.enable_audit_log
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enabled = data.get('enabled', False)
        self.require_auth = data.get('require_auth', True)
        self.accounts = data.get('accounts', [])
        self.accounts_file = data.get('accounts_file', "")
        self.groups = data.get('groups', [])
        self.groups_file = data.get('groups_file', "")
        self.identity_providers = data.get('identity_providers', [])
        self.ip_auth_users = data.get('ip_auth_users', [])
        self.ip_auth_admin = data.get('ip_auth_admin', [])
        self.min_password_length = data.get('min_password_length', 6)
        self.require_strong_password = data.get('require_strong_password', False)
        self.password_hash_algorithm = data.get('password_hash_algorithm', "sha256")
        self.password_salt_length = data.get('password_salt_length', 16)
        self.session_timeout = data.get('session_timeout', 3600)
        self.max_sessions_per_user = data.get('max_sessions_per_user', 5)
        self.remember_me_duration = data.get('remember_me_duration', 30 * 24 * 3600)
        self.enable_brute_force_protection = data.get('enable_brute_force_protection', True)
        self.max_login_attempts = data.get('max_login_attempts', 5)
        self.lockout_duration = data.get('lockout_duration', 300)
        self.enable_audit_log = data.get('enable_audit_log', True)
    
    def generate_copyparty_args(self) -> List[str]:
        """生成CopyParty命令行参数"""
        args = []
        
        # 账户配置
        for account in self.accounts:
            args.extend(['-a', account])
        
        if self.accounts_file:
            args.extend(['--accounts', self.accounts_file])
        
        # 用户组配置
        for group in self.groups:
            args.extend(['-g', group])
        
        if self.groups_file:
            args.extend(['--groups', self.groups_file])
        
        # IP认证配置
        for ip_user in self.ip_auth_users:
            args.extend(['--ipu', ip_user])
        
        for ip_admin in self.ip_auth_admin:
            args.extend(['--ipa', ip_admin])
        
        # 身份提供商配置
        for idp in self.identity_providers:
            args.extend(['--idp', idp])
        
        # 会话配置
        if self.session_timeout != 3600:
            args.extend(['--session-timeout', str(self.session_timeout)])
        
        return args


class AccountManager:
    """账户管理器 - 完整的CopyParty账户管理实现"""
    
    def __init__(self, config: AccountManagerConfig):
        self.config = config
        self.accounts: Dict[str, Account] = {}
        self.groups: Dict[str, UserGroup] = {}
        self.sessions: Dict[str, Dict] = {}
        self.failed_attempts: Dict[str, List[float]] = {}
        self.locked_ips: Dict[str, float] = {}
        
        self.load_accounts()
        self.load_groups()
    
    def load_accounts(self):
        """加载账户"""
        # 加载内联账户
        for account_str in self.config.accounts:
            try:
                account = Account.from_copyparty_format(account_str)
                self.accounts[account.username] = account
            except ValueError as e:
                print(f"加载账户失败: {e}")
        
        # 加载账户文件
        if self.config.accounts_file and os.path.exists(self.config.accounts_file):
            try:
                with open(self.config.accounts_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            account = Account.from_copyparty_format(line)
                            self.accounts[account.username] = account
            except Exception as e:
                print(f"加载账户文件失败: {e}")
    
    def load_groups(self):
        """加载用户组"""
        # 加载内联用户组
        for group_str in self.config.groups:
            try:
                group = UserGroup.from_copyparty_format(group_str)
                self.groups[group.name] = group
            except ValueError as e:
                print(f"加载用户组失败: {e}")
        
        # 加载用户组文件
        if self.config.groups_file and os.path.exists(self.config.groups_file):
            try:
                with open(self.config.groups_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            group = UserGroup.from_copyparty_format(line)
                            self.groups[group.name] = group
            except Exception as e:
                print(f"加载用户组文件失败: {e}")
    
    def create_account(self, username: str, password: str, permissions: List[str], 
                      volumes: List[str] = None, groups: List[str] = None) -> bool:
        """创建账户"""
        if username in self.accounts:
            return False
        
        # 验证密码
        if not self._validate_password(password):
            return False
        
        # 转换权限
        perm_set = set()
        for perm in permissions:
            try:
                perm_set.add(PermissionType(perm))
            except ValueError:
                continue
        
        # 创建账户
        account = Account(
            username=username,
            password=password,
            permissions=perm_set,
            volumes=volumes or [],
            groups=groups or []
        )
        
        self.accounts[username] = account
        return True
    
    def create_group(self, name: str, permissions: List[str], volumes: List[str] = None) -> bool:
        """创建用户组"""
        if name in self.groups:
            return False
        
        # 转换权限
        perm_set = set()
        for perm in permissions:
            try:
                perm_set.add(PermissionType(perm))
            except ValueError:
                continue
        
        # 创建用户组
        group = UserGroup(
            name=name,
            permissions=perm_set,
            volumes=volumes or []
        )
        
        self.groups[name] = group
        return True
    
    def add_user_to_group(self, username: str, group_name: str) -> bool:
        """将用户添加到用户组"""
        if username not in self.accounts or group_name not in self.groups:
            return False
        
        account = self.accounts[username]
        group = self.groups[group_name]
        
        if group_name not in account.groups:
            account.groups.append(group_name)
        
        if username not in group.members:
            group.members.append(username)
        
        return True
    
    def get_user_effective_permissions(self, username: str) -> Set[PermissionType]:
        """获取用户的有效权限（包括用户组权限）"""
        if username not in self.accounts:
            return set()
        
        account = self.accounts[username]
        permissions = account.permissions.copy()
        
        # 添加用户组权限
        for group_name in account.groups:
            if group_name in self.groups:
                permissions.update(self.groups[group_name].permissions)
        
        return permissions
    
    def get_user_accessible_volumes(self, username: str) -> List[str]:
        """获取用户可访问的卷"""
        if username not in self.accounts:
            return []
        
        account = self.accounts[username]
        volumes = account.volumes.copy()
        
        # 添加用户组卷
        for group_name in account.groups:
            if group_name in self.groups:
                volumes.extend(self.groups[group_name].volumes)
        
        return list(set(volumes))  # 去重
    
    def save_accounts_file(self, file_path: str = None):
        """保存账户到文件"""
        if not file_path:
            file_path = self.config.accounts_file
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# CopyParty Desktop 账户文件\n")
                f.write("# 格式: username:password:permissions:volumes\n\n")
                
                for account in self.accounts.values():
                    f.write(account.to_copyparty_format() + "\n")
            
            return True
        except Exception as e:
            print(f"保存账户文件失败: {e}")
            return False
    
    def save_groups_file(self, file_path: str = None):
        """保存用户组到文件"""
        if not file_path:
            file_path = self.config.groups_file
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# CopyParty Desktop 用户组文件\n")
                f.write("# 格式: groupname:permissions:volumes\n\n")
                
                for group in self.groups.values():
                    f.write(group.to_copyparty_format() + "\n")
            
            return True
        except Exception as e:
            print(f"保存用户组文件失败: {e}")
            return False
    
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取账户管理统计信息"""
        return {
            'total_accounts': len(self.accounts),
            'total_groups': len(self.groups),
            'enabled_accounts': len([a for a in self.accounts.values() if a.enabled]),
            'admin_accounts': len([a for a in self.accounts.values() if PermissionType.ADMIN in a.permissions]),
            'active_sessions': len(self.sessions),
            'locked_ips': len(self.locked_ips)
        }
