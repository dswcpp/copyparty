#!/usr/bin/env python3
"""
CopyParty Desktop 快速打包脚本
用于开发和测试阶段的快速打包
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """主函数"""
    print("🚀 CopyParty Desktop 快速打包")
    print("=" * 40)
    
    # 获取平台信息
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"平台: {system}-{arch}")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return 1
    
    # 检查PyQt6
    try:
        import PyQt6
        print("✓ PyQt6 已安装")
    except ImportError:
        print("❌ PyQt6 未安装")
        print("请运行: pip install PyQt6")
        return 1
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 单文件模式
        "--windowed",  # GUI模式 (无控制台)
        "--name", "CopyPartyDesktop",
        "--add-data", "COPYPARTY_COMPLETENESS_ANALYSIS.md;.",
        "--add-data", "README.md;.",
        "--add-data", "CHANGELOG.md;.",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "core.application",
        "--hidden-import", "core.config_manager",
        "--hidden-import", "protocols.base_protocol",
        "--hidden-import", "protocols.http_server",
        "--hidden-import", "protocols.ftp_server",
        "--hidden-import", "protocols.webdav_server",
        "--hidden-import", "protocols.smb_server",
        "--hidden-import", "features.file_indexing",
        "--hidden-import", "security.authentication",
        "--clean",
        "--noconfirm",
        "main.py"
    ]
    
    # 添加平台特定选项
    if system == "windows":
        # Windows图标 (如果存在)
        icon_path = project_root / "resources" / "icons" / "app.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
    elif system == "darwin":
        # macOS图标 (如果存在)
        icon_path = project_root / "resources" / "icons" / "app.icns"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
    
    print("\n🔨 开始构建...")
    print(f"命令: {' '.join(cmd[:5])}...")
    
    try:
        # 执行构建
        result = subprocess.run(
            cmd,
            cwd=project_root,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ 构建成功！")
            
            # 显示结果
            dist_dir = project_root / "dist"
            if dist_dir.exists():
                files = list(dist_dir.iterdir())
                if files:
                    print("\n📦 生成的文件:")
                    for file in files:
                        if file.is_file():
                            size_mb = file.stat().st_size / (1024 * 1024)
                            print(f"  📄 {file.name} ({size_mb:.1f} MB)")
                
                # 运行测试
                exe_files = [f for f in files if f.name.startswith("CopyPartyDesktop")]
                if exe_files:
                    exe_file = exe_files[0]
                    print(f"\n🧪 测试可执行文件: {exe_file.name}")
                    
                    # 简单测试 (显示版本信息)
                    try:
                        test_result = subprocess.run(
                            [str(exe_file), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if test_result.returncode == 0:
                            print("✓ 可执行文件测试通过")
                        else:
                            print("⚠️  可执行文件测试失败，但文件已生成")
                    except subprocess.TimeoutExpired:
                        print("⚠️  可执行文件测试超时，但文件已生成")
                    except Exception as e:
                        print(f"⚠️  可执行文件测试异常: {e}")
            
            print("\n🎉 快速打包完成！")
            print(f"输出目录: {dist_dir}")
            
            return 0
        else:
            print(f"\n❌ 构建失败，返回码: {result.returncode}")
            return 1
            
    except Exception as e:
        print(f"\n❌ 构建过程出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
