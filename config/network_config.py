"""
网络配置模块
迁移自 copyparty_complete_config.py 中的 NetworkConfig
"""

import ipaddress
import socket
from typing import List, Dict, Any, Optional
from .base_config import BaseConfig, ValidationResult


class NetworkConfig(BaseConfig):
    """网络配置 - 迁移自 NetworkConfig"""
    
    def __init__(self):
        super().__init__()
        
        # 基本网络
        self.listen_ips: str = "::"  # -i
        self.listen_ports: str = "3923"  # -p
        self.include_link_local: bool = False  # --ll
        
        # 反向代理
        self.reverse_proxy_depth: int = 1  # --rproxy
        self.xff_header: str = "x-forwarded-for"  # --xff-hdr
        self.xff_sources: str = "127.0.0.0/8, ::1/128"  # --xff-src
        self.ip_allowlist: str = ""  # --ipa
        self.reverse_proxy_location: str = ""  # --rp-loc
        
        # 系统选项
        self.reuseaddr: bool = False  # --reuseaddr (Windows)
        self.freebind: bool = False  # --freebind (Linux)
        
        # 文件输出
        self.write_endpoints: str = ""  # --wr-h-eps
        self.write_accessible: str = ""  # --wr-h-aon
        
        # 超时设置
        self.socket_timeout_header: int = 120  # --s-thead
        self.socket_timeout_body: float = 128.0  # --s-tbody
        self.socket_read_size: int = 256 * 1024  # --s-rd-sz
        self.socket_write_size: int = 256 * 1024  # --s-wr-sz
        self.socket_write_sleep: float = 0.0  # --s-wr-slp
        
        # 调试选项
        self.response_sleep: float = 0.0  # --rsp-slp
        self.response_jitter: float = 0.0  # --rsp-jtr

        # 高优先级网络功能 (根据COPYPARTY_COMPLETENESS_ANALYSIS.md)
        self.max_connections: int = 1024  # 最大连接数

        # WebDAV 配置
        self.webdav_enabled: bool = True  # 默认启用WebDAV
        self.webdav_auth_required: bool = False  # --dav-auth 强制WebDAV认证

        # TFTP 服务器配置
        self.tftp_enabled: bool = False  # --tftp 启用TFTP服务器
        self.tftp_port: int = 3969  # TFTP端口（默认非特权端口）
        self.tftp_port_range: str = ""  # TFTP回复端口范围

        # SMB/CIFS 服务器配置
        self.smb_enabled: bool = False  # --smb 启用SMB只读
        self.smb_write_enabled: bool = False  # --smbw 启用SMB读写
        self.smb_port: int = 3945  # SMB端口（默认非特权端口）
        self.smb_version: int = 2  # SMB版本（1或2）
        self.smb_disable_workaround: bool = False  # --smb-nwa-1 禁用文件数量限制解决方案
        self.max_connections_per_ip: int = 64  # 每IP最大连接数
        self.connection_timeout: int = 30  # 连接超时
        self.keep_alive_timeout: int = 5  # Keep-Alive超时
        self.max_keep_alive_requests: int = 100  # 最大Keep-Alive请求数

        # 带宽控制 (高优先级功能)
        self.upload_rate_limit: int = 0  # 上传速率限制 (KB/s, 0=无限制)
        self.download_rate_limit: int = 0  # 下载速率限制 (KB/s, 0=无限制)
        self.global_rate_limit: int = 0  # 全局速率限制 (KB/s, 0=无限制)

        # IPv6/IPv4控制
        self.no_ipv6: bool = False  # --no-ipv6: 禁用IPv6
        self.no_ipv4: bool = False  # --no-ipv4: 禁用IPv4
        self.prefer_ipv6: bool = False  # --prefer-ipv6: 优先IPv6

        # 缓冲区设置
        self.send_buffer_size: int = 65536  # 发送缓冲区大小
        self.recv_buffer_size: int = 65536  # 接收缓冲区大小
        self.tcp_nodelay: bool = True  # TCP_NODELAY选项
        self.tcp_keepalive: bool = True  # TCP_KEEPALIVE选项

        # 设置验证规则
        self._required_fields = ['listen_ips', 'listen_ports']
        self._type_rules = {
            'listen_ips': str,
            'listen_ports': str,
            'include_link_local': bool,
            'reverse_proxy_depth': int,
            'xff_header': str,
            'xff_sources': str,
            'ip_allowlist': str,
            'reverse_proxy_location': str,
            'reuseaddr': bool,
            'freebind': bool,
            'write_endpoints': str,
            'write_accessible': str,
            'socket_timeout_header': int,
            'socket_timeout_body': float,
            'socket_read_size': int,
            'socket_write_size': int,
            'socket_write_sleep': float,
            'response_sleep': float,
            'response_jitter': float
        }
        self._value_rules = {
            'reverse_proxy_depth': {'min': 0, 'max': 10},
            'socket_timeout_header': {'min': 1, 'max': 3600},
            'socket_timeout_body': {'min': 0.1, 'max': 3600.0},
            'socket_read_size': {'min': 1024, 'max': 10 * 1024 * 1024},
            'socket_write_size': {'min': 1024, 'max': 10 * 1024 * 1024},
            'socket_write_sleep': {'min': 0.0, 'max': 10.0},
            'response_sleep': {'min': 0.0, 'max': 10.0},
            'response_jitter': {'min': 0.0, 'max': 10.0}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'listen_ips': self.listen_ips,
            'listen_ports': self.listen_ports,
            'include_link_local': self.include_link_local,
            'reverse_proxy_depth': self.reverse_proxy_depth,
            'xff_header': self.xff_header,
            'xff_sources': self.xff_sources,
            'ip_allowlist': self.ip_allowlist,
            'reverse_proxy_location': self.reverse_proxy_location,
            'reuseaddr': self.reuseaddr,
            'freebind': self.freebind,
            'write_endpoints': self.write_endpoints,
            'write_accessible': self.write_accessible,
            'socket_timeout_header': self.socket_timeout_header,
            'socket_timeout_body': self.socket_timeout_body,
            'socket_read_size': self.socket_read_size,
            'socket_write_size': self.socket_write_size,
            'socket_write_sleep': self.socket_write_sleep,
            'response_sleep': self.response_sleep,
            'response_jitter': self.response_jitter
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.listen_ips = data.get('listen_ips', "::")
        self.listen_ports = data.get('listen_ports', "3923")
        self.include_link_local = data.get('include_link_local', False)
        self.reverse_proxy_depth = data.get('reverse_proxy_depth', 1)
        self.xff_header = data.get('xff_header', "x-forwarded-for")
        self.xff_sources = data.get('xff_sources', "127.0.0.0/8, ::1/128")
        self.ip_allowlist = data.get('ip_allowlist', "")
        self.reverse_proxy_location = data.get('reverse_proxy_location', "")
        self.reuseaddr = data.get('reuseaddr', False)
        self.freebind = data.get('freebind', False)
        self.write_endpoints = data.get('write_endpoints', "")
        self.write_accessible = data.get('write_accessible', "")
        self.socket_timeout_header = data.get('socket_timeout_header', 120)
        self.socket_timeout_body = data.get('socket_timeout_body', 128.0)
        self.socket_read_size = data.get('socket_read_size', 256 * 1024)
        self.socket_write_size = data.get('socket_write_size', 256 * 1024)
        self.socket_write_sleep = data.get('socket_write_sleep', 0.0)
        self.response_sleep = data.get('response_sleep', 0.0)
        self.response_jitter = data.get('response_jitter', 0.0)
        self.mark_changed()
    
    def get_command_args(self) -> List[str]:
        """生成命令行参数"""
        args = []
        
        # 监听IP
        if self.listen_ips != "::":
            args.extend(['-i', self.listen_ips])
        
        # 监听端口
        if self.listen_ports != "3923":
            args.extend(['-p', self.listen_ports])
        
        # 链路本地
        if self.include_link_local:
            args.append('--ll')
        
        # 反向代理
        if self.reverse_proxy_depth != 1:
            args.extend(['--rproxy', str(self.reverse_proxy_depth)])
        
        # XFF 头
        if self.xff_header != "x-forwarded-for":
            args.extend(['--xff-hdr', self.xff_header])
        
        # XFF 源
        if self.xff_sources != "127.0.0.0/8, ::1/128":
            args.extend(['--xff-src', self.xff_sources])
        
        # IP 允许列表
        if self.ip_allowlist:
            args.extend(['--ipa', self.ip_allowlist])
        
        # 反向代理位置
        if self.reverse_proxy_location:
            args.extend(['--rp-loc', self.reverse_proxy_location])
        
        # 系统选项
        if self.reuseaddr:
            args.append('--reuseaddr')
        
        if self.freebind:
            args.append('--freebind')
        
        # 文件输出
        if self.write_endpoints:
            args.extend(['--wr-h-eps', self.write_endpoints])
        
        if self.write_accessible:
            args.extend(['--wr-h-aon', self.write_accessible])
        
        # 超时设置
        if self.socket_timeout_header != 120:
            args.extend(['--s-thead', str(self.socket_timeout_header)])
        
        if self.socket_timeout_body != 128.0:
            args.extend(['--s-tbody', str(self.socket_timeout_body)])
        
        if self.socket_read_size != 256 * 1024:
            args.extend(['--s-rd-sz', str(self.socket_read_size)])
        
        if self.socket_write_size != 256 * 1024:
            args.extend(['--s-wr-sz', str(self.socket_write_size)])
        
        if self.socket_write_sleep != 0.0:
            args.extend(['--s-wr-slp', str(self.socket_write_sleep)])
        
        # 调试选项
        if self.response_sleep != 0.0:
            args.extend(['--rsp-slp', str(self.response_sleep)])

        if self.response_jitter != 0.0:
            args.extend(['--rsp-jtr', str(self.response_jitter)])

        # 高优先级网络功能
        if self.max_connections != 1024:
            args.extend(['--max-conn', str(self.max_connections)])

        if self.max_connections_per_ip != 64:
            args.extend(['--max-conn-ip', str(self.max_connections_per_ip)])

        if self.connection_timeout != 30:
            args.extend(['--conn-timeout', str(self.connection_timeout)])

        # 带宽控制
        if self.upload_rate_limit > 0:
            args.extend(['--upload-limit', str(self.upload_rate_limit)])

        if self.download_rate_limit > 0:
            args.extend(['--download-limit', str(self.download_rate_limit)])

        if self.global_rate_limit > 0:
            args.extend(['--rate-limit', str(self.global_rate_limit)])

        # IPv6/IPv4控制
        if self.no_ipv6:
            args.append('--no-ipv6')

        if self.no_ipv4:
            args.append('--no-ipv4')

        if self.prefer_ipv6:
            args.append('--prefer-ipv6')

        # WebDAV 配置
        if self.webdav_auth_required:
            args.append('--dav-auth')

        # TFTP 服务器配置
        if self.tftp_enabled:
            args.extend(['--tftp', str(self.tftp_port)])
            if self.tftp_port_range:
                args.extend(['--tftp-port-range', self.tftp_port_range])

        # SMB/CIFS 服务器配置
        if self.smb_enabled and not self.smb_write_enabled:
            args.append('--smb')
        elif self.smb_write_enabled:
            args.append('--smbw')

        if (self.smb_enabled or self.smb_write_enabled) and self.smb_port != 445:
            args.extend(['--smb-port', str(self.smb_port)])

        if (self.smb_enabled or self.smb_write_enabled) and self.smb_version == 1:
            args.append('--smb1')

        if (self.smb_enabled or self.smb_write_enabled) and self.smb_disable_workaround:
            args.append('--smb-nwa-1')

        return args
    
    def _custom_validation(self, result: ValidationResult):
        """自定义验证"""
        # 验证监听IP
        if self.listen_ips:
            ips = [ip.strip() for ip in self.listen_ips.split(',')]
            for ip in ips:
                if ip not in ['::', '0.0.0.0']:
                    try:
                        ipaddress.ip_address(ip)
                    except ValueError:
                        result.add_error(f"无效的IP地址: {ip}")
        
        # 验证端口
        if self.listen_ports:
            ports = self.listen_ports.replace(',', ' ').split()
            for port_str in ports:
                if '-' in port_str:
                    # 端口范围
                    try:
                        start, end = port_str.split('-')
                        start_port = int(start)
                        end_port = int(end)
                        if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                            result.add_error(f"端口范围超出有效范围: {port_str}")
                        if start_port > end_port:
                            result.add_error(f"端口范围起始大于结束: {port_str}")
                    except ValueError:
                        result.add_error(f"无效的端口范围: {port_str}")
                else:
                    # 单个端口
                    try:
                        port = int(port_str)
                        if not (1 <= port <= 65535):
                            result.add_error(f"端口超出有效范围: {port}")
                    except ValueError:
                        result.add_error(f"无效的端口: {port_str}")
        
        # 验证XFF源
        if self.xff_sources:
            sources = [source.strip() for source in self.xff_sources.split(',')]
            for source in sources:
                try:
                    ipaddress.ip_network(source, strict=False)
                except ValueError:
                    result.add_error(f"无效的XFF源网络: {source}")
        
        # 验证IP允许列表
        if self.ip_allowlist:
            ips = [ip.strip() for ip in self.ip_allowlist.split(',')]
            for ip in ips:
                try:
                    ipaddress.ip_network(ip, strict=False)
                except ValueError:
                    result.add_error(f"无效的IP允许列表项: {ip}")
    
    def get_listen_ports_list(self) -> List[int]:
        """获取监听端口列表"""
        ports = []
        if self.listen_ports:
            port_parts = self.listen_ports.replace(',', ' ').split()
            for port_str in port_parts:
                if '-' in port_str:
                    # 端口范围
                    try:
                        start, end = port_str.split('-')
                        start_port = int(start)
                        end_port = int(end)
                        ports.extend(range(start_port, end_port + 1))
                    except ValueError:
                        pass  # 忽略无效的端口范围
                else:
                    # 单个端口
                    try:
                        port = int(port_str)
                        ports.append(port)
                    except ValueError:
                        pass  # 忽略无效的端口
        return ports
    
    def get_listen_ips_list(self) -> List[str]:
        """获取监听IP列表"""
        if self.listen_ips:
            return [ip.strip() for ip in self.listen_ips.split(',')]
        return []
    
    def is_port_available(self, port: int, ip: str = "127.0.0.1") -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                return result != 0  # 0 表示连接成功，即端口被占用
        except Exception:
            return False
    
    def get_available_port(self, start_port: int = 3923, end_port: int = 4000) -> Optional[int]:
        """获取可用端口"""
        for port in range(start_port, end_port + 1):
            if self.is_port_available(port):
                return port
        return None
