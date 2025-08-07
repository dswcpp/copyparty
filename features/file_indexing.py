"""
文件索引功能模块
实现CopyParty的文件索引和搜索功能
"""

import os
import time
import hashlib
import sqlite3
import threading
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    name: str
    size: int
    mtime: float
    ctime: float
    is_directory: bool
    hash_md5: Optional[str] = None
    hash_sha1: Optional[str] = None
    mime_type: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class FileIndexConfig:
    """文件索引配置 - 对应CopyParty的-e2d*选项"""

    def __init__(self):
        # 基础索引配置
        self.enabled = True
        self.index_hidden_files = False
        self.index_system_files = False

        # CopyParty -e2d* 选项对应
        self.e2d = False          # -e2d: 启用文件索引
        self.e2ds = False         # -e2ds: 启用搜索功能
        self.e2dsa = False        # -e2dsa: 启用高级搜索
        self.e2t = False          # -e2t: 启用标签系统
        self.e2ts = False         # -e2ts: 启用标签搜索

        # 哈希计算配置
        self.calculate_hashes = True
        self.hash_algorithms = ['md5', 'sha1']
        self.max_file_size_for_hash = 100 * 1024 * 1024  # 100MB

        # 过滤配置
        self.excluded_extensions = ['.tmp', '.log', '.cache']
        self.excluded_directories = ['.git', '__pycache__', 'node_modules']

        # 性能配置
        self.index_interval = 300  # 5分钟
        self.batch_size = 100
        self.max_workers = 4       # 并发工作线程数

        # 功能配置
        self.enable_mime_detection = True
        self.enable_content_indexing = False
        self.enable_thumbnail_generation = False
        self.enable_metadata_extraction = True

        # 搜索配置
        self.search_result_limit = 1000
        self.enable_fuzzy_search = False
        self.enable_regex_search = False
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'index_hidden_files': self.index_hidden_files,
            'index_system_files': self.index_system_files,

            # CopyParty -e2d* 选项
            'e2d': self.e2d,
            'e2ds': self.e2ds,
            'e2dsa': self.e2dsa,
            'e2t': self.e2t,
            'e2ts': self.e2ts,

            # 哈希配置
            'calculate_hashes': self.calculate_hashes,
            'hash_algorithms': self.hash_algorithms,
            'max_file_size_for_hash': self.max_file_size_for_hash,

            # 过滤配置
            'excluded_extensions': self.excluded_extensions,
            'excluded_directories': self.excluded_directories,

            # 性能配置
            'index_interval': self.index_interval,
            'batch_size': self.batch_size,
            'max_workers': self.max_workers,

            # 功能配置
            'enable_mime_detection': self.enable_mime_detection,
            'enable_content_indexing': self.enable_content_indexing,
            'enable_thumbnail_generation': self.enable_thumbnail_generation,
            'enable_metadata_extraction': self.enable_metadata_extraction,

            # 搜索配置
            'search_result_limit': self.search_result_limit,
            'enable_fuzzy_search': self.enable_fuzzy_search,
            'enable_regex_search': self.enable_regex_search
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.enabled = data.get('enabled', True)
        self.index_hidden_files = data.get('index_hidden_files', False)
        self.index_system_files = data.get('index_system_files', False)

        # CopyParty -e2d* 选项
        self.e2d = data.get('e2d', False)
        self.e2ds = data.get('e2ds', False)
        self.e2dsa = data.get('e2dsa', False)
        self.e2t = data.get('e2t', False)
        self.e2ts = data.get('e2ts', False)

        # 哈希配置
        self.calculate_hashes = data.get('calculate_hashes', True)
        self.hash_algorithms = data.get('hash_algorithms', ['md5', 'sha1'])
        self.max_file_size_for_hash = data.get('max_file_size_for_hash', 100 * 1024 * 1024)

        # 过滤配置
        self.excluded_extensions = data.get('excluded_extensions', ['.tmp', '.log', '.cache'])
        self.excluded_directories = data.get('excluded_directories', ['.git', '__pycache__', 'node_modules'])

        # 性能配置
        self.index_interval = data.get('index_interval', 300)
        self.batch_size = data.get('batch_size', 100)
        self.max_workers = data.get('max_workers', 4)

        # 功能配置
        self.enable_mime_detection = data.get('enable_mime_detection', True)
        self.enable_content_indexing = data.get('enable_content_indexing', False)
        self.enable_thumbnail_generation = data.get('enable_thumbnail_generation', False)
        self.enable_metadata_extraction = data.get('enable_metadata_extraction', True)

        # 搜索配置
        self.search_result_limit = data.get('search_result_limit', 1000)
        self.enable_fuzzy_search = data.get('enable_fuzzy_search', False)
        self.enable_regex_search = data.get('enable_regex_search', False)

    def generate_copyparty_args(self) -> List[str]:
        """生成CopyParty命令行参数"""
        args = []

        # CopyParty -e2d* 选项
        if self.e2d:
            args.append('-e2d')

        if self.e2ds:
            args.append('-e2ds')

        if self.e2dsa:
            args.append('-e2dsa')

        if self.e2t:
            args.append('-e2t')

        if self.e2ts:
            args.append('-e2ts')

        return args


class FileIndexDatabase:
    """文件索引数据库"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.execute('PRAGMA foreign_keys = ON')
        
        # 创建文件表
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                ctime REAL NOT NULL,
                is_directory BOOLEAN NOT NULL,
                hash_md5 TEXT,
                hash_sha1 TEXT,
                mime_type TEXT,
                indexed_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # 创建标签表
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # 创建文件标签关联表
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files (path)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files (name)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_size ON files (size)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_mtime ON files (mtime)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_hash_md5 ON files (hash_md5)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_files_mime_type ON files (mime_type)')
        
        self.connection.commit()
    
    def insert_file(self, file_info: FileInfo):
        """插入文件信息"""
        now = time.time()
        
        cursor = self.connection.execute('''
            INSERT OR REPLACE INTO files 
            (path, name, size, mtime, ctime, is_directory, hash_md5, hash_sha1, mime_type, indexed_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info.path,
            file_info.name,
            file_info.size,
            file_info.mtime,
            file_info.ctime,
            file_info.is_directory,
            file_info.hash_md5,
            file_info.hash_sha1,
            file_info.mime_type,
            now,
            now
        ))
        
        file_id = cursor.lastrowid
        
        # 插入标签
        for tag_name in file_info.tags:
            self.connection.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
            tag_id = self.connection.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()[0]
            self.connection.execute('INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)', (file_id, tag_id))
        
        self.connection.commit()
        return file_id
    
    def search_files(self, query: str, limit: int = 100) -> List[FileInfo]:
        """搜索文件"""
        # 简单的文件名搜索
        cursor = self.connection.execute('''
            SELECT path, name, size, mtime, ctime, is_directory, hash_md5, hash_sha1, mime_type
            FROM files 
            WHERE name LIKE ? 
            ORDER BY name 
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            file_info = FileInfo(
                path=row[0],
                name=row[1],
                size=row[2],
                mtime=row[3],
                ctime=row[4],
                is_directory=bool(row[5]),
                hash_md5=row[6],
                hash_sha1=row[7],
                mime_type=row[8]
            )
            results.append(file_info)
        
        return results
    
    def get_file_by_path(self, path: str) -> Optional[FileInfo]:
        """根据路径获取文件信息"""
        cursor = self.connection.execute('''
            SELECT path, name, size, mtime, ctime, is_directory, hash_md5, hash_sha1, mime_type
            FROM files 
            WHERE path = ?
        ''', (path,))
        
        row = cursor.fetchone()
        if row:
            return FileInfo(
                path=row[0],
                name=row[1],
                size=row[2],
                mtime=row[3],
                ctime=row[4],
                is_directory=bool(row[5]),
                hash_md5=row[6],
                hash_sha1=row[7],
                mime_type=row[8]
            )
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        cursor = self.connection.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        cursor = self.connection.execute('SELECT COUNT(*) FROM files WHERE is_directory = 1')
        total_directories = cursor.fetchone()[0]
        
        cursor = self.connection.execute('SELECT SUM(size) FROM files WHERE is_directory = 0')
        total_size = cursor.fetchone()[0] or 0
        
        cursor = self.connection.execute('SELECT COUNT(DISTINCT mime_type) FROM files WHERE mime_type IS NOT NULL')
        mime_types_count = cursor.fetchone()[0]
        
        return {
            'total_files': total_files,
            'total_directories': total_directories,
            'total_size': total_size,
            'mime_types_count': mime_types_count
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


class FileIndexer:
    """文件索引器"""
    
    def __init__(self, config: FileIndexConfig, db_path: str):
        self.config = config
        self.database = FileIndexDatabase(db_path)
        self.is_running = False
        self.indexing_thread = None
        self.progress_callback: Optional[Callable] = None
        self.current_progress = 0
        self.total_files = 0
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def start_indexing(self, paths: List[str]):
        """开始索引"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.indexing_thread = threading.Thread(target=self._index_paths, args=(paths,), daemon=True)
        self.indexing_thread.start()
        return True
    
    def stop_indexing(self):
        """停止索引"""
        self.is_running = False
        if self.indexing_thread:
            self.indexing_thread.join(timeout=5)
    
    def _index_paths(self, paths: List[str]):
        """索引指定路径"""
        try:
            # 计算总文件数
            self.total_files = 0
            for path in paths:
                if os.path.exists(path):
                    self.total_files += self._count_files(path)
            
            self.current_progress = 0
            
            # 开始索引
            for path in paths:
                if not self.is_running:
                    break
                
                if os.path.exists(path):
                    self._index_directory(path)
            
            if self.progress_callback:
                self.progress_callback(self.total_files, self.total_files, "索引完成")
                
        except Exception as e:
            print(f"索引过程出错: {e}")
        finally:
            self.is_running = False
    
    def _count_files(self, path: str) -> int:
        """计算文件数量"""
        count = 0
        try:
            for root, dirs, files in os.walk(path):
                # 过滤目录
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(d)]
                
                count += len(files)
                count += len(dirs)
        except (OSError, PermissionError):
            pass
        
        return count
    
    def _index_directory(self, path: str):
        """索引目录"""
        try:
            for root, dirs, files in os.walk(path):
                if not self.is_running:
                    break
                
                # 过滤目录
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(d)]
                
                # 索引目录
                for dir_name in dirs:
                    if not self.is_running:
                        break
                    
                    dir_path = os.path.join(root, dir_name)
                    self._index_file(dir_path, is_directory=True)
                
                # 索引文件
                for file_name in files:
                    if not self.is_running:
                        break
                    
                    file_path = os.path.join(root, file_name)
                    if not self._should_exclude_file(file_name):
                        self._index_file(file_path, is_directory=False)
                
        except (OSError, PermissionError) as e:
            print(f"索引目录 {path} 时出错: {e}")
    
    def _index_file(self, file_path: str, is_directory: bool):
        """索引单个文件"""
        try:
            stat = os.stat(file_path)
            
            file_info = FileInfo(
                path=file_path,
                name=os.path.basename(file_path),
                size=stat.st_size if not is_directory else 0,
                mtime=stat.st_mtime,
                ctime=stat.st_ctime,
                is_directory=is_directory
            )
            
            # 计算哈希值
            if (not is_directory and 
                self.config.calculate_hashes and 
                stat.st_size <= self.config.max_file_size_for_hash):
                
                file_info.hash_md5, file_info.hash_sha1 = self._calculate_hashes(file_path)
            
            # 检测MIME类型
            if not is_directory and self.config.enable_mime_detection:
                file_info.mime_type = self._detect_mime_type(file_path)
            
            # 插入数据库
            self.database.insert_file(file_info)
            
            # 更新进度
            self.current_progress += 1
            if self.progress_callback and self.current_progress % 10 == 0:
                self.progress_callback(self.current_progress, self.total_files, f"正在索引: {file_info.name}")
                
        except (OSError, PermissionError) as e:
            print(f"索引文件 {file_path} 时出错: {e}")
    
    def _calculate_hashes(self, file_path: str) -> tuple[Optional[str], Optional[str]]:
        """计算文件哈希值"""
        md5_hash = None
        sha1_hash = None
        
        try:
            md5_hasher = hashlib.md5() if 'md5' in self.config.hash_algorithms else None
            sha1_hasher = hashlib.sha1() if 'sha1' in self.config.hash_algorithms else None
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    if md5_hasher:
                        md5_hasher.update(chunk)
                    if sha1_hasher:
                        sha1_hasher.update(chunk)
            
            if md5_hasher:
                md5_hash = md5_hasher.hexdigest()
            if sha1_hasher:
                sha1_hash = sha1_hasher.hexdigest()
                
        except (OSError, PermissionError):
            pass
        
        return md5_hash, sha1_hash
    
    def _detect_mime_type(self, file_path: str) -> Optional[str]:
        """检测MIME类型"""
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type
        except:
            return None
    
    def _should_exclude_file(self, file_name: str) -> bool:
        """判断是否应该排除文件"""
        # 隐藏文件
        if not self.config.index_hidden_files and file_name.startswith('.'):
            return True
        
        # 扩展名过滤
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext in self.config.excluded_extensions:
            return True
        
        return False
    
    def _should_exclude_directory(self, dir_name: str) -> bool:
        """判断是否应该排除目录"""
        # 隐藏目录
        if not self.config.index_hidden_files and dir_name.startswith('.'):
            return True
        
        # 排除的目录
        if dir_name in self.config.excluded_directories:
            return True
        
        return False
    
    def search(self, query: str, limit: int = 100) -> List[FileInfo]:
        """搜索文件"""
        return self.database.search_files(query, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return self.database.get_statistics()
    
    def close(self):
        """关闭索引器"""
        self.stop_indexing()
        self.database.close()
