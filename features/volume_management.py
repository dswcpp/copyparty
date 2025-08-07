"""
卷管理功能模块
实现CopyParty的完整卷和路径管理系统
对应CopyParty的卷配置和路径映射功能
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class VolumeType(Enum):
    """卷类型枚举"""
    READ_ONLY = "ro"         # 只读卷
    READ_WRITE = "rw"        # 读写卷
    WRITE_ONLY = "wo"        # 只写卷
    APPEND_ONLY = "ao"       # 追加卷
    TEMPORARY = "tmp"        # 临时卷


class AccessMode(Enum):
    """访问模式枚举"""
    PUBLIC = "public"        # 公开访问
    PRIVATE = "private"      # 私有访问
    PROTECTED = "protected"  # 受保护访问
    HIDDEN = "hidden"        # 隐藏访问


@dataclass
class VolumeConfig:
    """卷配置数据类"""
    name: str                           # 卷名称
    local_path: str                     # 本地路径
    virtual_path: str = "/"             # 虚拟路径
    volume_type: VolumeType = VolumeType.READ_WRITE
    access_mode: AccessMode = AccessMode.PUBLIC
    
    # 权限设置
    allowed_users: List[str] = field(default_factory=list)
    allowed_groups: List[str] = field(default_factory=list)
    denied_users: List[str] = field(default_factory=list)
    denied_groups: List[str] = field(default_factory=list)
    
    # 功能选项
    enable_upload: bool = True
    enable_delete: bool = True
    enable_move: bool = True
    enable_mkdir: bool = True
    enable_listing: bool = True
    enable_search: bool = True
    enable_thumbnail: bool = True
    enable_preview: bool = True
    
    # 限制设置
    max_file_size: int = 0              # 最大文件大小 (0=无限制)
    max_total_size: int = 0             # 最大总大小 (0=无限制)
    allowed_extensions: List[str] = field(default_factory=list)
    denied_extensions: List[str] = field(default_factory=list)
    
    # 高级选项
    enable_compression: bool = False     # 启用压缩
    enable_encryption: bool = False      # 启用加密
    enable_versioning: bool = False      # 启用版本控制
    enable_backup: bool = False          # 启用备份
    
    # 元数据
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    
    def to_copyparty_format(self) -> str:
        """转换为CopyParty卷格式"""
        # 基础格式: virtual_path:local_path:permissions
        # 简化权限生成，只生成基础的读写权限
        if self.volume_type == VolumeType.READ_ONLY:
            perm_str = "r"
        elif self.volume_type == VolumeType.WRITE_ONLY:
            perm_str = "w"
        elif self.volume_type == VolumeType.APPEND_ONLY:
            perm_str = "a"
        else:  # READ_WRITE
            perm_str = "rw"

        return f"{self.virtual_path}:{self.local_path}:{perm_str}"
    
    def validate(self) -> tuple[bool, List[str]]:
        """验证卷配置"""
        errors = []
        
        # 检查名称
        if not self.name:
            errors.append("卷名称不能为空")
        
        # 检查本地路径
        if not self.local_path:
            errors.append("本地路径不能为空")
        elif not os.path.exists(self.local_path):
            errors.append(f"本地路径不存在: {self.local_path}")
        elif not os.path.isdir(self.local_path):
            errors.append(f"本地路径不是目录: {self.local_path}")
        
        # 检查虚拟路径
        if not self.virtual_path:
            errors.append("虚拟路径不能为空")
        elif not self.virtual_path.startswith("/"):
            errors.append("虚拟路径必须以 / 开头")
        
        # 检查权限一致性
        if self.volume_type == VolumeType.READ_ONLY:
            if self.enable_upload or self.enable_delete or self.enable_move or self.enable_mkdir:
                errors.append("只读卷不能启用写入相关功能")
        
        # 检查文件大小限制
        if self.max_file_size < 0:
            errors.append("最大文件大小不能为负数")
        
        if self.max_total_size < 0:
            errors.append("最大总大小不能为负数")
        
        return len(errors) == 0, errors


class VolumeManagerConfig:
    """卷管理器配置类"""
    
    def __init__(self):
        # 基础配置
        self.enabled = True
        self.default_volume_type = VolumeType.READ_WRITE
        self.default_access_mode = AccessMode.PUBLIC
        
        # 卷配置文件
        self.volumes_config_file = "volumes.json"
        self.auto_save = True
        self.backup_config = True
        
        # 全局限制
        self.max_volumes = 100
        self.max_volume_size = 0  # 0=无限制
        self.global_upload_limit = 0  # 全局上传限制
        self.global_download_limit = 0  # 全局下载限制
        
        # 安全选项
        self.enable_path_traversal_protection = True
        self.enable_symlink_protection = True
        self.enable_hidden_file_protection = True
        self.allowed_path_patterns = []
        self.denied_path_patterns = []
        
        # 监控选项
        self.enable_file_monitoring = True
        self.enable_usage_tracking = True
        self.enable_access_logging = True
        
        # 自动化选项
        self.auto_create_directories = True
        self.auto_cleanup_empty_dirs = False
        self.auto_index_new_files = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'default_volume_type': self.default_volume_type.value,
            'default_access_mode': self.default_access_mode.value,
            'volumes_config_file': self.volumes_config_file,
            'auto_save': self.auto_save,
            'backup_config': self.backup_config,
            'max_volumes': self.max_volumes,
            'max_volume_size': self.max_volume_size,
            'global_upload_limit': self.global_upload_limit,
            'global_download_limit': self.global_download_limit,
            'enable_path_traversal_protection': self.enable_path_traversal_protection,
            'enable_symlink_protection': self.enable_symlink_protection,
            'enable_hidden_file_protection': self.enable_hidden_file_protection,
            'allowed_path_patterns': self.allowed_path_patterns,
            'denied_path_patterns': self.denied_path_patterns,
            'enable_file_monitoring': self.enable_file_monitoring,
            'enable_usage_tracking': self.enable_usage_tracking,
            'enable_access_logging': self.enable_access_logging,
            'auto_create_directories': self.auto_create_directories,
            'auto_cleanup_empty_dirs': self.auto_cleanup_empty_dirs,
            'auto_index_new_files': self.auto_index_new_files
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enabled = data.get('enabled', True)
        self.default_volume_type = VolumeType(data.get('default_volume_type', 'rw'))
        self.default_access_mode = AccessMode(data.get('default_access_mode', 'public'))
        self.volumes_config_file = data.get('volumes_config_file', "volumes.json")
        self.auto_save = data.get('auto_save', True)
        self.backup_config = data.get('backup_config', True)
        self.max_volumes = data.get('max_volumes', 100)
        self.max_volume_size = data.get('max_volume_size', 0)
        self.global_upload_limit = data.get('global_upload_limit', 0)
        self.global_download_limit = data.get('global_download_limit', 0)
        self.enable_path_traversal_protection = data.get('enable_path_traversal_protection', True)
        self.enable_symlink_protection = data.get('enable_symlink_protection', True)
        self.enable_hidden_file_protection = data.get('enable_hidden_file_protection', True)
        self.allowed_path_patterns = data.get('allowed_path_patterns', [])
        self.denied_path_patterns = data.get('denied_path_patterns', [])
        self.enable_file_monitoring = data.get('enable_file_monitoring', True)
        self.enable_usage_tracking = data.get('enable_usage_tracking', True)
        self.enable_access_logging = data.get('enable_access_logging', True)
        self.auto_create_directories = data.get('auto_create_directories', True)
        self.auto_cleanup_empty_dirs = data.get('auto_cleanup_empty_dirs', False)
        self.auto_index_new_files = data.get('auto_index_new_files', True)


class VolumeManager:
    """卷管理器 - 完整的CopyParty卷管理实现"""
    
    def __init__(self, config: VolumeManagerConfig):
        self.config = config
        self.volumes: Dict[str, VolumeConfig] = {}
        self.volume_stats: Dict[str, Dict] = {}
        self.access_log: List[Dict] = []
        
        self.load_volumes()
    
    def load_volumes(self):
        """加载卷配置"""
        config_file = self.config.volumes_config_file
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for volume_data in data.get('volumes', []):
                    volume = self._dict_to_volume(volume_data)
                    self.volumes[volume.name] = volume
                    
            except Exception as e:
                print(f"加载卷配置失败: {e}")
    
    def save_volumes(self):
        """保存卷配置"""
        if not self.config.auto_save:
            return False
        
        config_file = self.config.volumes_config_file
        
        # 备份现有配置
        if self.config.backup_config and os.path.exists(config_file):
            backup_file = f"{config_file}.backup.{int(time.time())}"
            try:
                os.rename(config_file, backup_file)
            except Exception:
                pass
        
        try:
            data = {
                'version': '2.0.0',
                'created_at': time.time(),
                'volumes': [self._volume_to_dict(vol) for vol in self.volumes.values()]
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存卷配置失败: {e}")
            return False
    
    def create_volume(self, name: str, local_path: str, virtual_path: str = None,
                     volume_type: VolumeType = None, access_mode: AccessMode = None) -> bool:
        """创建新卷"""
        if name in self.volumes:
            print(f"卷 {name} 已存在")
            return False

        if len(self.volumes) >= self.config.max_volumes:
            print(f"已达到最大卷数量限制: {self.config.max_volumes}")
            return False
        
        # 使用默认值
        if virtual_path is None:
            virtual_path = f"/{name}"
        if volume_type is None:
            volume_type = self.config.default_volume_type
        if access_mode is None:
            access_mode = self.config.default_access_mode
        
        # 创建卷配置
        volume = VolumeConfig(
            name=name,
            local_path=local_path,
            virtual_path=virtual_path,
            volume_type=volume_type,
            access_mode=access_mode
        )
        
        # 验证配置
        is_valid, errors = volume.validate()
        if not is_valid:
            print(f"卷配置验证失败: {errors}")
            return False
        
        # 创建目录（如果启用）
        if self.config.auto_create_directories and not os.path.exists(local_path):
            try:
                os.makedirs(local_path, exist_ok=True)
            except Exception as e:
                print(f"创建目录失败: {e}")
                return False
        
        self.volumes[name] = volume
        self.volume_stats[name] = {
            'created_at': time.time(),
            'file_count': 0,
            'total_size': 0,
            'access_count': 0,
            'last_accessed': 0
        }
        
        self.save_volumes()
        return True
    
    def delete_volume(self, name: str, delete_files: bool = False) -> bool:
        """删除卷"""
        if name not in self.volumes:
            return False
        
        volume = self.volumes[name]
        
        # 删除文件（如果请求）
        if delete_files and os.path.exists(volume.local_path):
            try:
                import shutil
                shutil.rmtree(volume.local_path)
            except Exception as e:
                print(f"删除卷文件失败: {e}")
                return False
        
        del self.volumes[name]
        if name in self.volume_stats:
            del self.volume_stats[name]
        
        self.save_volumes()
        return True
    
    def update_volume(self, name: str, **kwargs) -> bool:
        """更新卷配置"""
        if name not in self.volumes:
            return False
        
        volume = self.volumes[name]
        
        # 更新属性
        for key, value in kwargs.items():
            if hasattr(volume, key):
                setattr(volume, key, value)
        
        volume.modified_at = time.time()
        
        # 验证更新后的配置
        is_valid, errors = volume.validate()
        if not is_valid:
            print(f"卷配置验证失败: {errors}")
            return False
        
        self.save_volumes()
        return True
    
    def get_volume(self, name: str) -> Optional[VolumeConfig]:
        """获取卷配置"""
        return self.volumes.get(name)
    
    def list_volumes(self, volume_type: VolumeType = None, 
                    access_mode: AccessMode = None) -> List[VolumeConfig]:
        """列出卷"""
        volumes = list(self.volumes.values())
        
        if volume_type:
            volumes = [v for v in volumes if v.volume_type == volume_type]
        
        if access_mode:
            volumes = [v for v in volumes if v.access_mode == access_mode]
        
        return volumes
    
    def get_volume_by_path(self, virtual_path: str) -> Optional[VolumeConfig]:
        """根据虚拟路径获取卷"""
        for volume in self.volumes.values():
            if virtual_path.startswith(volume.virtual_path):
                return volume
        return None
    
    def check_access(self, volume_name: str, username: str, 
                    user_groups: List[str] = None) -> bool:
        """检查用户对卷的访问权限"""
        if volume_name not in self.volumes:
            return False
        
        volume = self.volumes[volume_name]
        user_groups = user_groups or []
        
        # 检查拒绝列表
        if username in volume.denied_users:
            return False
        
        for group in user_groups:
            if group in volume.denied_groups:
                return False
        
        # 检查允许列表
        if volume.allowed_users or volume.allowed_groups:
            # 如果有允许列表，必须在列表中
            if username in volume.allowed_users:
                return True
            
            for group in user_groups:
                if group in volume.allowed_groups:
                    return True
            
            return False
        
        # 默认允许访问
        return True
    
    def update_volume_stats(self, volume_name: str):
        """更新卷统计信息"""
        if volume_name not in self.volumes:
            return
        
        volume = self.volumes[volume_name]
        
        if not os.path.exists(volume.local_path):
            return
        
        try:
            file_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(volume.local_path):
                file_count += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        pass
            
            self.volume_stats[volume_name].update({
                'file_count': file_count,
                'total_size': total_size,
                'last_updated': time.time()
            })
            
        except Exception as e:
            print(f"更新卷统计失败: {e}")
    
    def generate_copyparty_args(self) -> List[str]:
        """生成CopyParty命令行参数"""
        args = []
        
        for volume in self.volumes.values():
            # 添加卷配置
            args.extend(['-v', volume.to_copyparty_format()])
            
            # 添加特殊选项
            if volume.enable_compression:
                args.append('--compress')
            
            if volume.max_file_size > 0:
                args.extend(['--max-file-size', str(volume.max_file_size)])
        
        return args
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取卷管理统计信息"""
        total_files = sum(stats.get('file_count', 0) for stats in self.volume_stats.values())
        total_size = sum(stats.get('total_size', 0) for stats in self.volume_stats.values())
        
        volume_types = {}
        access_modes = {}
        
        for volume in self.volumes.values():
            volume_types[volume.volume_type.value] = volume_types.get(volume.volume_type.value, 0) + 1
            access_modes[volume.access_mode.value] = access_modes.get(volume.access_mode.value, 0) + 1
        
        return {
            'total_volumes': len(self.volumes),
            'total_files': total_files,
            'total_size': total_size,
            'volume_types': volume_types,
            'access_modes': access_modes,
            'average_files_per_volume': total_files / len(self.volumes) if self.volumes else 0
        }
    
    def _volume_to_dict(self, volume: VolumeConfig) -> Dict[str, Any]:
        """将卷配置转换为字典"""
        return {
            'name': volume.name,
            'local_path': volume.local_path,
            'virtual_path': volume.virtual_path,
            'volume_type': volume.volume_type.value,
            'access_mode': volume.access_mode.value,
            'allowed_users': volume.allowed_users,
            'allowed_groups': volume.allowed_groups,
            'denied_users': volume.denied_users,
            'denied_groups': volume.denied_groups,
            'enable_upload': volume.enable_upload,
            'enable_delete': volume.enable_delete,
            'enable_move': volume.enable_move,
            'enable_mkdir': volume.enable_mkdir,
            'enable_listing': volume.enable_listing,
            'enable_search': volume.enable_search,
            'enable_thumbnail': volume.enable_thumbnail,
            'enable_preview': volume.enable_preview,
            'max_file_size': volume.max_file_size,
            'max_total_size': volume.max_total_size,
            'allowed_extensions': volume.allowed_extensions,
            'denied_extensions': volume.denied_extensions,
            'enable_compression': volume.enable_compression,
            'enable_encryption': volume.enable_encryption,
            'enable_versioning': volume.enable_versioning,
            'enable_backup': volume.enable_backup,
            'description': volume.description,
            'tags': volume.tags,
            'created_at': volume.created_at,
            'modified_at': volume.modified_at
        }
    
    def _dict_to_volume(self, data: Dict[str, Any]) -> VolumeConfig:
        """从字典创建卷配置"""
        return VolumeConfig(
            name=data['name'],
            local_path=data['local_path'],
            virtual_path=data.get('virtual_path', '/'),
            volume_type=VolumeType(data.get('volume_type', 'rw')),
            access_mode=AccessMode(data.get('access_mode', 'public')),
            allowed_users=data.get('allowed_users', []),
            allowed_groups=data.get('allowed_groups', []),
            denied_users=data.get('denied_users', []),
            denied_groups=data.get('denied_groups', []),
            enable_upload=data.get('enable_upload', True),
            enable_delete=data.get('enable_delete', True),
            enable_move=data.get('enable_move', True),
            enable_mkdir=data.get('enable_mkdir', True),
            enable_listing=data.get('enable_listing', True),
            enable_search=data.get('enable_search', True),
            enable_thumbnail=data.get('enable_thumbnail', True),
            enable_preview=data.get('enable_preview', True),
            max_file_size=data.get('max_file_size', 0),
            max_total_size=data.get('max_total_size', 0),
            allowed_extensions=data.get('allowed_extensions', []),
            denied_extensions=data.get('denied_extensions', []),
            enable_compression=data.get('enable_compression', False),
            enable_encryption=data.get('enable_encryption', False),
            enable_versioning=data.get('enable_versioning', False),
            enable_backup=data.get('enable_backup', False),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            created_at=data.get('created_at', time.time()),
            modified_at=data.get('modified_at', time.time())
        )
