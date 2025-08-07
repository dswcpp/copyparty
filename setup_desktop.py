#!/usr/bin/env python3
"""
CopyParty Desktop 专用安装配置
支持多平台打包和分发
"""

import sys
import os
from setuptools import setup, find_packages

# 读取版本信息
def get_version():
    """获取版本号"""
    return "2.0.0"

# 读取README
def get_long_description():
    """获取长描述"""
    return """
# CopyParty Desktop v2.0

专业级文件服务器桌面管理工具，基于CopyParty构建的现代化GUI应用程序。

## 功能特性

- 🏗️ 模块化架构设计
- 🌐 多协议支持 (HTTP/HTTPS, FTP/FTPS, WebDAV, SMB)
- 🔐 完整的用户认证和权限管理
- 📁 高级文件索引和搜索功能
- 📊 实时性能监控
- ⚙️ 直观的配置管理界面
- 🔧 插件化扩展系统

## 功能覆盖率

根据COPYPARTY_COMPLETENESS_ANALYSIS.md分析：
- 总体功能覆盖率: 80%
- 高优先级功能: 100% 完成
- 中优先级功能: 60% 完成

## 系统要求

- Python 3.8+
- PyQt6
- 支持 Windows, macOS, Linux
"""

# 读取依赖
def get_requirements():
    """获取依赖列表"""
    return [
        # GUI框架
        'PyQt6>=6.5.0',
        
        # 网络和HTTP
        'requests>=2.31.0',
        'urllib3>=2.0.0',
        
        # 文件和系统操作
        'psutil>=5.9.0',
        'watchdog>=3.0.0',
        
        # 配置和数据
        'PyYAML>=6.0',
        'toml>=0.10.2',
        
        # 安全和认证
        'cryptography>=41.0.0',
        'bcrypt>=4.0.0',
        
        # 媒体处理
        'Pillow>=10.0.0',
    ]

# 平台特定依赖
def get_platform_requirements():
    """获取平台特定依赖"""
    platform_deps = []
    
    if sys.platform.startswith('win'):
        platform_deps.extend([
            'pywin32>=306',
            'wmi>=1.5.1'
        ])
    elif sys.platform.startswith('linux'):
        platform_deps.extend([
            'python-dbus>=1.2.18'
        ])
    elif sys.platform.startswith('darwin'):
        platform_deps.extend([
            'pyobjc-framework-Cocoa>=9.0'
        ])
    
    return platform_deps

# 主要设置
setup(
    name="copyparty-desktop",
    version=get_version(),
    description="CopyParty Desktop - 专业级文件服务器桌面管理工具",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="CopyParty Desktop Team",
    author_email="support@copyparty-desktop.com",
    url="https://github.com/copyparty/copyparty-desktop",
    license="MIT",
    
    # 包配置
    packages=[
        'core',
        'config',
        'protocols',
        'features',
        'security',
        'monitoring',
        'ui',
        'ui.widgets',
        'ui.dialogs',
        'ui.themes',
        'plugins',
        'utils',
        'tests'
    ],
    
    package_data={
        'resources': ['*'],
        'ui': ['themes/*.qss'],
    },
    
    include_package_data=True,
    zip_safe=False,
    
    # 依赖配置
    python_requires=">=3.8",
    install_requires=get_requirements() + get_platform_requirements(),
    
    # 可选依赖
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-qt>=4.2.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0'
        ],
        'media': [
            'ffmpeg-python>=0.2.0'
        ],
        'monitoring': [
            'prometheus-client>=0.17.0'
        ]
    },
    
    # 入口点
    entry_points={
        'console_scripts': [
            'copyparty-desktop=main:main',
        ],
        'gui_scripts': [
            'copyparty-desktop-gui=main:main'
        ]
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Filesystems",
        "Topic :: Desktop Environment",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X"
    ],
    
    # 关键词
    keywords=[
        "copyparty", "file-server", "desktop-application",
        "gui", "qt", "cross-platform", "http-server", "ftp-server"
    ]
)
