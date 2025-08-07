#!/usr/bin/env python3
"""
CopyParty 完整配置系统 - 严格遵循源码
基于 copyparty/__main__.py 中的所有 add_* 函数
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class GeneralConfig:
    """通用配置 - 对应 add_general()"""
    
    # 基本选项
    config_files: List[str] = field(default_factory=list)  # -c
    max_clients: int = 1024  # -nc
    cpu_cores: int = 1  # -j
    accounts: List[str] = field(default_factory=list)  # -a
    volumes: List[str] = field(default_factory=list)  # -v
    groups: List[str] = field(default_factory=list)  # --grp
    
    # 功能开关
    enable_dots: bool = False  # -ed
    urlform: str = "print,xm"  # --urlform
    
    # 显示设置
    window_title: str = "cpp @ $pub"  # --wintitle
    server_name: str = "copyparty"  # --name
    
    # MIME 类型
    mime_mappings: List[str] = field(default_factory=list)  # --mime
    list_mimes: bool = False  # --mimes
    expensive_mime: bool = False  # --rmagic
    
    # 信息选项
    show_license: bool = False  # --license
    show_version: bool = False  # --version


@dataclass
class NetworkConfig:
    """网络配置 - 对应 add_network()"""
    
    # 基本网络
    listen_ips: str = "::"  # -i
    listen_ports: str = "3923"  # -p
    include_link_local: bool = False  # --ll
    
    # 反向代理
    reverse_proxy_depth: int = 1  # --rproxy
    xff_header: str = "x-forwarded-for"  # --xff-hdr
    xff_sources: str = "127.0.0.0/8, ::1/128"  # --xff-src
    ip_allowlist: str = ""  # --ipa
    reverse_proxy_location: str = ""  # --rp-loc
    
    # 系统选项
    reuseaddr: bool = False  # --reuseaddr (Windows)
    freebind: bool = False  # --freebind (Linux)
    
    # 文件输出
    write_endpoints: str = ""  # --wr-h-eps
    write_accessible: str = ""  # --wr-h-aon
    
    # 超时设置
    socket_timeout_header: int = 120  # --s-thead
    socket_timeout_body: float = 128.0  # --s-tbody
    socket_read_size: int = 256 * 1024  # --s-rd-sz
    socket_write_size: int = 256 * 1024  # --s-wr-sz
    socket_write_sleep: float = 0.0  # --s-wr-slp
    
    # 调试选项
    response_sleep: float = 0.0  # --rsp-slp
    response_jitter: float = 0.0  # --rsp-jtr


@dataclass
class TLSConfig:
    """TLS/SSL 配置 - 对应 add_tls()"""
    
    # 基本 TLS 设置
    http_only: bool = False  # --http-only
    https_only: bool = False  # --https-only
    cert_path: str = ""  # --cert
    ssl_versions: str = ""  # --ssl-ver
    ciphers: str = ""  # --ciphers
    
    # 调试选项
    ssl_debug: bool = False  # --ssl-dbg
    ssl_log_path: str = ""  # --ssl-log


@dataclass
class CertConfig:
    """证书配置 - 对应 add_cert()"""
    
    # 自动证书
    auto_cert: bool = True  # 默认启用
    cert_domains: List[str] = field(default_factory=list)  # --cert-dns
    cert_exact: bool = False  # --cert-exact
    cert_no_ip: bool = False  # --cert-no-ip
    cert_no_localhost: bool = False  # --cert-no-localhost
    cert_no_hostname: bool = False  # --cert-no-hostname
    cert_directory: str = ""  # --cert-dir
    
    # 证书生成选项
    ca_cert_days: int = 3650  # --ca-days
    server_cert_days: int = 365  # --srv-days
    cert_common_name: str = "partyco"  # --cert-cn
    cert_algorithm: str = "ecdsa-256"  # --cert-alg


@dataclass
class AuthConfig:
    """认证配置 - 对应 add_auth()"""
    
    # 基本认证
    anon_read: bool = False  # --anon-read
    anon_write: bool = False  # --anon-write
    anon_upload: bool = False  # --anon-upload
    
    # 会话管理
    logout_hours: float = 8086.0  # --logout
    session_timeout: int = 0  # --ses-to
    
    # 身份提供者
    idp_header_user: str = ""  # --idp-h-usr
    idp_header_groups: str = ""  # --idp-h-grp
    idp_group_separator: str = ","  # --idp-gsep
    
    # 安全选项
    force_js: bool = False  # --force-js
    vague_403: bool = False  # --vague-403
    early_ban: bool = False  # --early-ban


@dataclass
class PasswordChangeConfig:
    """密码修改配置 - 对应 add_chpw()"""
    
    # 基本设置
    enable_password_change: bool = False  # --chpw
    password_database: str = ""  # --chpw-db
    minimum_password_length: int = 8  # --chpw-len
    
    # 限制设置
    no_password_change_users: List[str] = field(default_factory=list)  # --chpw-no
    
    # 显示设置
    verbosity: int = 2  # --chpw-v


@dataclass
class QRConfig:
    """二维码配置 - 对应 add_qr()"""
    
    # 基本设置
    show_qr_http: bool = False  # --qr
    show_qr_https: bool = False  # --qrs
    qr_location: str = ""  # --qrl
    qr_ip_prefix: str = ""  # --qri
    
    # 显示选项
    qr_foreground: int = 0  # --qr-fg
    qr_background: int = 15  # --qr-bg
    qr_invert: bool = False  # --qr-inv


@dataclass
class ZeroconfConfig:
    """Zeroconf 配置 - 对应 add_zeroconf()"""
    
    # 基本设置
    enable_zeroconf: bool = False  # -z
    zeroconf_interfaces: List[str] = field(default_factory=list)  # --zi
    zeroconf_exclude: List[str] = field(default_factory=list)  # --ze
    
    # 检查设置
    network_check_interval: int = 10  # --z-chk
    verbose_zeroconf: bool = False  # --z-v
    multicast_hop_interval: int = 0  # --z-hop


@dataclass
class MDNSConfig:
    """mDNS 配置 - 对应 add_zc_mdns()"""
    
    # 基本设置
    enable_mdns: bool = True  # --zm (默认启用)
    mdns_port: int = 5353  # --zm-port
    mdns_ttl: int = 120  # --zm-ttl


@dataclass
class SSDPConfig:
    """SSDP 配置 - 对应 add_zc_ssdp()"""
    
    # 基本设置
    enable_ssdp: bool = True  # --zs (默认启用)
    ssdp_interval: int = 1800  # --zs-int


@dataclass
class FilesystemConfig:
    """文件系统配置 - 对应 add_fs()"""
    
    # 基本设置
    io_buffer_size: int = 256 * 1024  # --iobuf
    directory_timeout: int = 300  # --dir-to
    
    # 文件操作
    move_retry_timeout: int = 0  # --mv-to
    remove_retry_timeout: int = 0  # --rm-to
    
    # 性能选项
    no_scandir: bool = False  # --no-scandir
    no_sendfile: bool = False  # --no-sendfile
    
    # 符号链接
    follow_symlinks: bool = False  # --follow-symlinks
    never_symlink: bool = False  # --never-symlink
    hardlink_only: bool = False  # --hardlink-only


@dataclass
class ShareConfig:
    """共享配置 - 对应 add_share()"""
    
    # 基本设置
    no_robots: bool = False  # --no-robots
    force_js: bool = False  # --force-js
    
    # 访问控制
    allow_csrf: bool = False  # --allow-csrf
    cookie_lax: bool = False  # --cookie-lax
    
    # 下载选项
    zip_max_files: int = 0  # --zip-max-files
    zip_max_size: int = 0  # --zip-max-size
    zip_timeout: str = "no"  # --zip-to
    zip_no_limit_auth: bool = False  # --zip-no-limit-auth
    
    # 其他选项
    getmod: bool = False  # --getmod
    no_pipe: bool = False  # --no-pipe


@dataclass
class UploadConfig:
    """上传配置 - 对应 add_upload()"""
    
    # 基本上传
    enable_upload: bool = False  # -e2d
    upload_methods: List[str] = field(default_factory=lambda: ["basic", "bup"])
    
    # 文件处理
    enable_dedup: bool = False  # --dedup
    dedup_method: str = "symlink"  # --dedup-method
    safe_dedup: bool = False  # --safe-dedup
    no_clone: bool = False  # --no-clone
    no_dupe: bool = False  # --no-dupe
    
    # 权限设置
    chmod_dir: str = "755"  # --chmod-dir
    chmod_file: str = "644"  # --chmod-file
    uid: int = 0  # --uid
    gid: int = 0  # --gid
    
    # 文件系统选项
    sparse_files: bool = False  # --sparse
    no_sparse_files: bool = False  # --no-sparse
    webdav_write: bool = False  # --webdav-write
    force_upload_to_root: bool = False  # --nosub
    
    # 文件类型检测
    magic_detection: bool = False  # --magic
    default_filename: str = "file"  # --default-fn
    
    # 校验和
    put_checksum: str = "md5"  # --put-csum
    bup_checksum: str = "md5"  # --bup-csum
    
    # 压缩
    allow_gzip: bool = False  # --gz
    
    # 上传排序
    upload_sort: str = "s"  # --u2sort
    
    # 覆盖设置
    upload_overwrite: int = 0  # --u2ow
    
    # 日志
    write_upload_log: bool = False  # --write-uplog


@dataclass
class DatabaseConfig:
    """数据库配置 - 对应 add_db()"""

    # 基本数据库
    enable_database: bool = False  # -e2d
    scan_on_startup: bool = False  # -e2ds
    scan_all_on_startup: bool = False  # -e2dsa

    # 元数据
    enable_metadata: bool = False  # -e2t
    scan_metadata_on_startup: bool = False  # -e2ts
    rescan_metadata: bool = False  # -e2tsr

    # 完整性验证
    verify_integrity: bool = False  # -e2v
    update_on_mismatch: bool = False  # -e2vu
    panic_on_mismatch: bool = False  # -e2vp

    # 路径设置
    hist_path: str = ""  # --hist
    db_path: str = ""  # --db-path

    # 扫描设置
    rescan_interval: int = 0  # --re-scan
    db_activity_delay: float = 10.0  # --db-act
    search_timeout: int = 45  # --srch-to
    max_search_results: int = 7999  # --srch-lim

    # 哈希设置
    hash_threads: int = 5  # --hash-mt
    no_hash_pattern: str = ""  # --no-hash
    no_index_pattern: str = ""  # --no-idx

    # 数据保留
    no_forget: bool = False  # --no-forget
    forget_ip_minutes: int = 0  # --forget-ip
    no_db_ip: bool = False  # --no-db-ip


@dataclass
class ThumbnailConfig:
    """缩略图配置 - 对应 add_thumb()"""

    # 基本设置
    enable_thumbnails: bool = True  # 默认启用
    disable_video_thumbs: bool = False  # --no-vthumb
    disable_audio_thumbs: bool = False  # --no-athumb
    disable_image_thumbs: bool = False  # --no-ithumb

    # 缩略图尺寸和质量
    thumbnail_size: str = "320x240"  # --th-size
    crop_mode: str = "y"  # --th-crop
    high_res_3x: str = "n"  # --th-3x

    # 转换设置
    conversion_timeout: int = 60  # --th-to
    png_quantization: bool = False  # --th-pngq

    # 外部缩略图
    external_thumbs: Dict[str, str] = field(default_factory=dict)  # --th-ext

    # FFmpeg 设置
    ffmpeg_path: str = ""  # --ffmpeg
    ffprobe_path: str = ""  # --ffprobe
    use_swresample: bool = False  # --th-swr

    # 缓存管理
    poke_interval: int = 300  # --th-poke
    cleanup_interval: int = 43200  # --th-clean
    max_folder_age: int = 604800  # --th-maxage


@dataclass
class TranscodingConfig:
    """转码配置 - 对应 add_transcode()"""

    # 基本设置
    enable_transcoding: bool = False  # --tc

    # 音频转码
    audio_formats: Dict[str, str] = field(default_factory=dict)  # --tc-a-*
    audio_quality: str = "192k"  # --tc-aq
    audio_codec: str = "aac"  # --tc-ac

    # 视频转码
    video_formats: Dict[str, str] = field(default_factory=dict)  # --tc-v-*
    video_quality: str = "720p"  # --tc-vq
    video_codec: str = "h264"  # --tc-vc

    # 转码限制
    max_parallel_jobs: int = 2  # --tc-mt
    transcoding_timeout: int = 3600  # --tc-to

    # 缓存
    cache_transcoded: bool = True  # --tc-cache
    cache_path: str = ""  # --tc-cache-path


@dataclass
class ProtocolConfig:
    """协议配置 - 对应 add_ftp(), add_tftp(), add_smb()"""

    # FTP 设置
    enable_ftp: bool = False  # --ftp
    enable_ftps: bool = False  # --ftps
    ftp_port: int = 21  # --ftp-port
    ftp_passive_ports: tuple = (21000, 21099)  # --ftp-pr
    ftp_bind_ip: str = ""  # --ftp-ip

    # TFTP 设置
    enable_tftp: bool = False  # --tftp
    tftp_port: int = 69  # --tftp-port
    tftp_bind_ip: str = ""  # --tftp-ip

    # WebDAV 设置
    enable_webdav: bool = False  # --webdav
    webdav_auth: bool = False  # --webdav-auth

    # SMB 设置
    enable_smb: bool = False  # --smb
    smb_port: int = 445  # --smb-port


@dataclass
class SecurityConfig:
    """安全配置 - 对应 add_ban()"""

    # 密码策略
    ban_password_attempts: tuple = (9, 60, 1440)  # --ban-pw
    ban_password_changes: tuple = (5, 60, 1440)  # --ban-chpw
    ban_404_attempts: tuple = (50, 60, 1440)  # --ban-404
    ban_403_attempts: tuple = (9, 2, 1440)  # --ban-403
    ban_422_attempts: tuple = (9, 2, 1440)  # --ban-422
    ban_url_attempts: tuple = (9, 2, 1440)  # --ban-url

    # 其他安全选项
    logout_hours: float = 8086.0  # --logout
    early_ban: bool = False  # --early-ban
    vague_403: bool = False  # --vague-403
    force_js: bool = False  # --force-js
    no_robots: bool = False  # --no-robots

    # CORS 设置
    cors_origins: List[str] = field(default_factory=lambda: ["*"])  # --cors
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD"])  # --cors-methods

    # 访问控制
    allow_csrf: bool = False  # --allow-csrf
    cookie_lax: bool = False  # --cookie-lax
    getmod: bool = False  # --getmod


@dataclass
class UIConfig:
    """用户界面配置 - 对应各种 UI 选项"""

    # 基本UI设置
    server_name: str = "copyparty"  # --name
    document_title: str = "copyparty @ --name"  # 自动生成
    brand_name: str = "copyparty"  # 品牌名称
    theme: int = 0  # --theme

    # 显示选项
    no_title_hostname: bool = False  # --no-title-host
    no_info_hostname: bool = False  # --no-info-host
    no_disk_usage: bool = False  # --no-du
    no_branding: bool = False  # --no-brand

    # 功能开关
    enable_qr_code: bool = False  # --qr
    enable_rss: bool = False  # --rss
    enable_zip_download: bool = True  # 默认启用
    zip_max_files: int = 0  # --zip-max-files
    zip_max_size: int = 0  # --zip-max-size
    zip_timeout_response: str = "no"  # --zip-to
    zip_no_limit_for_auth: bool = False  # --zip-no-limit-auth

    # 访问控制
    upload_list_access: int = 2  # 1=管理员, 2=认证用户, 3=所有人
    zip_access: int = 2  # 同上

    # 其他选项
    disable_pipe: bool = False  # --no-pipe
    expensive_mimetype: bool = False  # --rmagic

    # 文件重命名/删除重试(Windows)
    move_retry_timeout: int = 0  # --mv-to
    remove_retry_timeout: int = 0  # --rm-to


@dataclass
class LoggingConfig:
    """日志配置 - 对应 add_log()"""

    # 基本日志设置
    log_file: str = ""  # --lo
    log_level: int = 1  # --lv
    log_utc: bool = False  # --log-utc
    log_time_decimals: int = 3  # --log-td

    # 访问日志
    access_log: str = ""  # --access-log
    access_log_format: str = ""  # --access-log-fmt

    # 错误日志
    error_log: str = ""  # --error-log

    # 调试选项
    debug_mode: bool = False  # --debug
    verbose_mode: bool = False  # --verbose


# 先定义所有新增的配置类
@dataclass
class AdminConfig:
    """管理员配置 - 对应 add_admin()"""

    # 管理员功能
    enable_admin: bool = False  # --admin
    admin_password: str = ""  # --admin-pwd
    admin_users: List[str] = field(default_factory=list)  # --admin-usr

    # 管理员权限
    admin_can_restart: bool = True  # --admin-restart
    admin_can_shutdown: bool = True  # --admin-shutdown
    admin_can_reload: bool = True  # --admin-reload


@dataclass
class HandlersConfig:
    """处理器配置 - 对应 add_handlers()"""

    # 错误处理器
    error_handlers: Dict[str, str] = field(default_factory=dict)  # --handler-*

    # 自定义错误页面
    custom_404_page: str = ""  # --handler-404
    custom_403_page: str = ""  # --handler-403
    custom_500_page: str = ""  # --handler-500


@dataclass
class HooksConfig:
    """钩子配置 - 对应 add_hooks()"""

    # 钩子脚本
    hooks: Dict[str, str] = field(default_factory=dict)  # --hook-*

    # 常用钩子
    upload_hook: str = ""  # --hook-upload
    delete_hook: str = ""  # --hook-delete
    move_hook: str = ""  # --hook-move
    mkdir_hook: str = ""  # --hook-mkdir


@dataclass
class StatsConfig:
    """统计配置 - 对应 add_stats()"""

    # 统计功能
    enable_stats: bool = False  # --stats
    stats_interval: int = 60  # --stats-int
    stats_file: str = ""  # --stats-file

    # 统计选项
    stats_include_ip: bool = False  # --stats-ip
    stats_include_user: bool = False  # --stats-user


@dataclass
class YoloConfig:
    """YOLO 配置 - 对应 add_yolo()"""

    # 危险选项
    yolo_mode: bool = False  # --yolo
    disable_safety: bool = False  # --no-safety
    allow_dangerous_operations: bool = False  # --dangerous


@dataclass
class OptoutsConfig:
    """退出选项配置 - 对应 add_optouts()"""

    # 功能退出
    no_scandir: bool = False  # --no-scandir
    no_sendfile: bool = False  # --no-sendfile
    no_atime: bool = False  # --no-atime
    no_hash: bool = False  # --no-hash


@dataclass
class SafetyConfig:
    """安全配置 - 对应 add_safety()"""

    # 安全选项
    safety_level: int = 1  # --safety
    paranoid_mode: bool = False  # --paranoid
    strict_mode: bool = False  # --strict


@dataclass
class SaltConfig:
    """盐值配置 - 对应 add_salt()"""

    # 盐值设置
    salt: str = ""  # --salt
    pepper: str = ""  # --pepper
    hash_rounds: int = 12  # --hash-rounds


@dataclass
class ShutdownConfig:
    """关闭配置 - 对应 add_shutdown()"""

    # 关闭选项
    shutdown_timeout: int = 30  # --shutdown-to
    graceful_shutdown: bool = True  # --graceful
    force_shutdown: bool = False  # --force-shutdown


@dataclass
class CompleteLoggingConfig:
    """完整日志配置 - 对应 add_logging()"""

    # 基本日志设置
    log_file: str = ""  # --log
    log_level: str = "info"  # --log-level
    log_format: str = ""  # --log-fmt

    # 访问日志
    access_log: str = ""  # --access-log
    access_log_format: str = ""  # --access-log-fmt

    # 错误日志
    error_log: str = ""  # --error-log

    # 日志轮转
    log_rotate_size: int = 0  # --log-rotate-size
    log_rotate_count: int = 5  # --log-rotate-count


@dataclass
class TailConfig:
    """尾随配置 - 对应 add_tail()"""

    # 尾随功能
    enable_tail: bool = True  # 默认启用
    tail_fd_check: int = 1  # --tail-fd-chk
    tail_rate: float = 0.2  # --tail-rate
    tail_timeout: int = 30  # --tail-to
    tail_access: int = 2  # --tail-access


@dataclass
class RSSConfig:
    """RSS 配置 - 对应 add_rss()"""

    # RSS 功能
    enable_rss: bool = False  # --rss
    rss_title: str = ""  # --rss-title
    rss_description: str = ""  # --rss-desc
    rss_max_items: int = 100  # --rss-max


@dataclass
class DatabaseGeneralConfig:
    """数据库通用配置 - 对应 add_db_general()"""

    # 数据库通用设置
    db_vacuum: bool = False  # --db-vacuum
    db_analyze: bool = False  # --db-analyze
    db_integrity_check: bool = False  # --db-check


@dataclass
class DatabaseMetadataConfig:
    """数据库元数据配置 - 对应 add_db_metadata()"""

    # 元数据设置
    metadata_timeout: int = 30  # --meta-to
    metadata_workers: int = 2  # --meta-workers
    metadata_cache_size: int = 1000  # --meta-cache


@dataclass
class TextConfig:
    """文本配置 - 对应 add_txt()"""

    # 文本处理
    markdown_history: str = "s"  # --md-hist
    enable_expansion: bool = False  # --expand
    expansion_markdown: str = ""  # --expand-md
    expansion_prologue: str = ""  # --expand-pro


@dataclass
class OpenGraphConfig:
    """Open Graph 配置 - 对应 add_og()"""

    # Open Graph 设置
    og_title: str = ""  # --og-title
    og_description: str = ""  # --og-desc
    og_image: str = ""  # --og-img


@dataclass
class CompleteUIConfig:
    """完整 UI 配置 - 对应 add_ui()"""

    # UI 主题
    theme: int = 0  # --theme
    custom_css: str = ""  # --css
    custom_js: str = ""  # --js

    # 页面设置
    page_title: str = ""  # --title
    favicon: str = ""  # --favicon
    logo: str = ""  # --logo


@dataclass
class WebDAVConfig:
    """WebDAV 配置 - 对应 add_webdav()"""

    # WebDAV 设置
    enable_webdav: bool = False  # --webdav
    webdav_auth: bool = False  # --webdav-auth
    webdav_lock: bool = True  # --webdav-lock


@dataclass
class DebugConfig:
    """调试配置 - 对应 add_debug()"""

    # 调试选项
    debug_mode: bool = False  # --debug
    verbose_mode: bool = False  # --verbose
    trace_mode: bool = False  # --trace
    profile_mode: bool = False  # --profile


@dataclass
class CopyPartyCompleteConfig:
    """CopyParty 完整配置管理器 - 严格遵循源码"""

    # 所有配置模块
    general: GeneralConfig = field(default_factory=GeneralConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    tls: TLSConfig = field(default_factory=TLSConfig)
    cert: CertConfig = field(default_factory=CertConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    chpw: PasswordChangeConfig = field(default_factory=PasswordChangeConfig)
    qr: QRConfig = field(default_factory=QRConfig)
    zeroconf: ZeroconfConfig = field(default_factory=ZeroconfConfig)
    mdns: MDNSConfig = field(default_factory=MDNSConfig)
    ssdp: SSDPConfig = field(default_factory=SSDPConfig)
    filesystem: FilesystemConfig = field(default_factory=FilesystemConfig)
    share: ShareConfig = field(default_factory=ShareConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    thumbnail: ThumbnailConfig = field(default_factory=ThumbnailConfig)
    transcoding: TranscodingConfig = field(default_factory=TranscodingConfig)
    protocol: ProtocolConfig = field(default_factory=ProtocolConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # 新增的配置模块
    admin: AdminConfig = field(default_factory=AdminConfig)
    handlers: HandlersConfig = field(default_factory=HandlersConfig)
    hooks: HooksConfig = field(default_factory=HooksConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    yolo: YoloConfig = field(default_factory=YoloConfig)
    optouts: OptoutsConfig = field(default_factory=OptoutsConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    salt: SaltConfig = field(default_factory=SaltConfig)
    shutdown: ShutdownConfig = field(default_factory=ShutdownConfig)
    complete_logging: CompleteLoggingConfig = field(default_factory=CompleteLoggingConfig)
    tail: TailConfig = field(default_factory=TailConfig)
    rss: RSSConfig = field(default_factory=RSSConfig)
    db_general: DatabaseGeneralConfig = field(default_factory=DatabaseGeneralConfig)
    db_metadata: DatabaseMetadataConfig = field(default_factory=DatabaseMetadataConfig)
    text: TextConfig = field(default_factory=TextConfig)
    opengraph: OpenGraphConfig = field(default_factory=OpenGraphConfig)
    complete_ui: CompleteUIConfig = field(default_factory=CompleteUIConfig)
    webdav: WebDAVConfig = field(default_factory=WebDAVConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)

    # 工作目录
    working_directory: str = field(default_factory=lambda: os.getcwd())

    def to_args(self) -> List[str]:
        """转换为完整的命令行参数列表"""
        args = []

        # 通用配置
        if self.general.config_files:
            for config_file in self.general.config_files:
                args.extend(["-c", config_file])

        if self.general.max_clients != 1024:
            args.extend(["-nc", str(self.general.max_clients)])

        if self.general.cpu_cores != 1:
            args.extend(["-j", str(self.general.cpu_cores)])

        for account in self.general.accounts:
            args.extend(["-a", account])

        for volume in self.general.volumes:
            args.extend(["-v", volume])

        for group in self.general.groups:
            args.extend(["--grp", group])

        if self.general.enable_dots:
            args.append("-ed")

        if self.general.urlform != "print,xm":
            args.extend(["--urlform", self.general.urlform])

        if self.general.window_title != "cpp @ $pub":
            args.extend(["--wintitle", self.general.window_title])

        if self.general.server_name != "copyparty":
            args.extend(["--name", self.general.server_name])

        for mime_mapping in self.general.mime_mappings:
            args.extend(["--mime", mime_mapping])

        if self.general.list_mimes:
            args.append("--mimes")

        if self.general.expensive_mime:
            args.append("--rmagic")

        if self.general.show_license:
            args.append("--license")

        if self.general.show_version:
            args.append("--version")

        # 网络配置
        if self.network.listen_ips != "::":
            args.extend(["-i", self.network.listen_ips])

        if self.network.listen_ports != "3923":
            args.extend(["-p", self.network.listen_ports])

        if self.network.include_link_local:
            args.append("--ll")

        if self.network.reverse_proxy_depth != 1:
            args.extend(["--rproxy", str(self.network.reverse_proxy_depth)])

        if self.network.xff_header != "x-forwarded-for":
            args.extend(["--xff-hdr", self.network.xff_header])

        if self.network.xff_sources != "127.0.0.0/8, ::1/128":
            args.extend(["--xff-src", self.network.xff_sources])

        if self.network.ip_allowlist:
            args.extend(["--ipa", self.network.ip_allowlist])

        if self.network.reverse_proxy_location:
            args.extend(["--rp-loc", self.network.reverse_proxy_location])

        if self.network.reuseaddr:
            args.append("--reuseaddr")

        if self.network.freebind:
            args.append("--freebind")

        if self.network.write_endpoints:
            args.extend(["--wr-h-eps", self.network.write_endpoints])

        if self.network.write_accessible:
            args.extend(["--wr-h-aon", self.network.write_accessible])

        if self.network.socket_timeout_header != 120:
            args.extend(["--s-thead", str(self.network.socket_timeout_header)])

        if self.network.socket_timeout_body != 128.0:
            args.extend(["--s-tbody", str(self.network.socket_timeout_body)])

        if self.network.socket_read_size != 256 * 1024:
            args.extend(["--s-rd-sz", str(self.network.socket_read_size)])

        if self.network.socket_write_size != 256 * 1024:
            args.extend(["--s-wr-sz", str(self.network.socket_write_size)])

        if self.network.socket_write_sleep != 0.0:
            args.extend(["--s-wr-slp", str(self.network.socket_write_sleep)])

        if self.network.response_sleep != 0.0:
            args.extend(["--rsp-slp", str(self.network.response_sleep)])

        if self.network.response_jitter != 0.0:
            args.extend(["--rsp-jtr", str(self.network.response_jitter)])

        # TLS 配置
        if self.tls.http_only:
            args.append("--http-only")

        if self.tls.https_only:
            args.append("--https-only")

        if self.tls.cert_path:
            args.extend(["--cert", self.tls.cert_path])

        if self.tls.ssl_versions:
            args.extend(["--ssl-ver", self.tls.ssl_versions])

        if self.tls.ciphers:
            args.extend(["--ciphers", self.tls.ciphers])

        if self.tls.ssl_debug:
            args.append("--ssl-dbg")

        if self.tls.ssl_log_path:
            args.extend(["--ssl-log", self.tls.ssl_log_path])

        # 证书配置
        for domain in self.cert.cert_domains:
            args.extend(["--cert-dns", domain])

        if self.cert.cert_exact:
            args.append("--cert-exact")

        if self.cert.cert_no_ip:
            args.append("--cert-no-ip")

        if self.cert.cert_no_localhost:
            args.append("--cert-no-localhost")

        if self.cert.cert_no_hostname:
            args.append("--cert-no-hostname")

        if self.cert.cert_directory:
            args.extend(["--cert-dir", self.cert.cert_directory])

        if self.cert.ca_cert_days != 3650:
            args.extend(["--ca-days", str(self.cert.ca_cert_days)])

        if self.cert.server_cert_days != 365:
            args.extend(["--srv-days", str(self.cert.server_cert_days)])

        if self.cert.cert_common_name != "partyco":
            args.extend(["--cert-cn", self.cert.cert_common_name])

        if self.cert.cert_algorithm != "ecdsa-256":
            args.extend(["--cert-alg", self.cert.cert_algorithm])

        return args

    def save_to_file(self, file_path: str):
        """保存完整配置到文件"""
        import json
        from dataclasses import asdict

        config_dict = asdict(self)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

    def load_from_file(self, file_path: str):
        """从文件加载完整配置"""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        # 重新构建配置对象
        for section_name, section_data in config_dict.items():
            if hasattr(self, section_name) and isinstance(section_data, dict):
                section_obj = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
