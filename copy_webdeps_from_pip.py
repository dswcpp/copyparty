#!/usr/bin/env python3
"""
从pip安装的CopyParty复制WebDeps
"""

import os
import sys
import shutil
from pathlib import Path

def find_pip_copyparty():
    """查找pip安装的CopyParty位置"""
    try:
        import copyparty
        copyparty_path = Path(copyparty.__file__).parent
        print(f"📍 找到pip安装的CopyParty: {copyparty_path}")
        return copyparty_path
    except ImportError:
        print("❌ 未找到pip安装的CopyParty")
        return None

def copy_webdeps():
    """复制webdeps"""
    # 查找pip安装的CopyParty
    pip_copyparty = find_pip_copyparty()
    if not pip_copyparty:
        return False
    
    # 源webdeps路径
    source_deps = pip_copyparty / "web" / "deps"
    if not source_deps.exists():
        print(f"❌ 源webdeps不存在: {source_deps}")
        return False
    
    # 目标webdeps路径
    target_deps = Path("copyparty/web/deps")
    
    print(f"📂 源路径: {source_deps}")
    print(f"📂 目标路径: {target_deps}")
    
    try:
        # 删除现有的deps目录
        if target_deps.exists():
            print("🗑️ 删除现有webdeps...")
            shutil.rmtree(target_deps)
        
        # 复制新的deps
        print("📦 复制webdeps...")
        shutil.copytree(source_deps, target_deps)
        
        # 验证关键文件
        key_files = [
            "mini-fa.woff",
            "mini-fa.css", 
            "marked.js",
            "prism.js"
        ]
        
        print("🔍 验证关键文件...")
        missing_files = []
        existing_files = []
        
        for file in key_files:
            file_path = target_deps / file
            if file_path.exists():
                size = file_path.stat().st_size
                existing_files.append(f"{file} ({size} bytes)")
            else:
                missing_files.append(file)
        
        print("✅ 存在的文件:")
        for file in existing_files:
            print(f"  • {file}")
        
        if missing_files:
            print("⚠️ 缺少的文件:")
            for file in missing_files:
                print(f"  • {file}")
        
        # 列出所有文件
        all_files = list(target_deps.glob("*"))
        print(f"\n📋 总共复制了 {len(all_files)} 个文件:")
        for file in sorted(all_files):
            if file.is_file():
                size = file.stat().st_size
                print(f"  • {file.name} ({size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False

def main():
    """主函数"""
    print("📦 从pip安装的CopyParty复制WebDeps")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("copyparty").exists():
        print("❌ 错误: 请在CopyParty项目根目录运行此脚本")
        return 1
    
    # 复制webdeps
    if copy_webdeps():
        print("\n🎉 WebDeps复制完成！")
        print("📋 现在您可以:")
        print("1. ✅ 使用完整的CopyParty Web界面")
        print("2. ✅ 享受所有前端功能")
        print("3. ✅ 正常的图标和样式显示")
        
        print("\n💡 提示:")
        print("• WebDeps已从pip安装版本复制")
        print("• 文件存储在 copyparty/web/deps/")
        print("• 重启应用程序以生效")
        
        return 0
    else:
        print("\n❌ WebDeps复制失败")
        print("💡 可能的解决方案:")
        print("1. 确保已安装CopyParty: pip install copyparty")
        print("2. 检查文件权限")
        print("3. 手动复制webdeps文件")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
