#!/usr/bin/env python3
"""
CopyParty Desktop GUI 依赖安装脚本
"""

import subprocess
import sys
import os

def install_package(package):
    """安装 Python 包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package} 安装失败: {e}")
        return False

def check_package(package):
    """检查包是否已安装"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """主函数"""
    print("CopyParty Desktop GUI 依赖安装脚本")
    print("=" * 50)
    
    # 需要安装的包
    packages = [
        "PyQt6",
        "jinja2",  # CopyParty 依赖
        "psutil",  # 性能监控依赖
    ]
    
    # 检查并安装包
    failed_packages = []
    
    for package in packages:
        if check_package(package):
            print(f"✓ {package} 已安装")
        else:
            if not install_package(package):
                failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if failed_packages:
        print("以下包安装失败:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\n请手动安装这些包:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return 1
    else:
        print("所有依赖已成功安装!")
        print("\n现在可以运行 CopyParty Desktop GUI:")
        print("  python copyparty_gui.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
