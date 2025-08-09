#!/usr/bin/env python3
"""
CopyParty WebDeps 设置工具
自动下载和设置Web依赖文件
"""

import os
import sys
import urllib.request
import tempfile
import zipfile
import shutil
from pathlib import Path

def check_webdeps():
    """检查webdeps是否存在"""
    webdeps_path = Path("copyparty/web/deps")
    mini_fa_path = webdeps_path / "mini-fa.woff"
    
    if mini_fa_path.exists():
        print("✅ WebDeps已存在")
        return True
    else:
        print("❌ WebDeps缺失")
        return False

def download_webdeps():
    """从GitHub下载webdeps"""
    print("📦 正在下载CopyParty WebDeps...")
    
    # GitHub releases URL
    url = "https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py"
    
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "copyparty-sfx.py")
            
            print(f"📥 下载: {url}")
            urllib.request.urlretrieve(url, temp_file)
            print("✅ 下载完成")
            
            # 运行sfx文件获取临时目录
            print("🔍 提取WebDeps...")
            import subprocess
            result = subprocess.run([
                sys.executable, temp_file, "--version"
            ], capture_output=True, text=True)
            
            # 查找sfxdir路径
            sfx_dir = None
            for line in result.stdout.split('\n'):
                if 'sfxdir:' in line:
                    sfx_dir = line.split('sfxdir:')[1].strip()
                    break
            
            if not sfx_dir:
                print("❌ 无法找到sfx临时目录")
                return False
            
            print(f"📂 找到sfx目录: {sfx_dir}")
            
            # 复制webdeps
            source_deps = Path(sfx_dir) / "copyparty" / "web" / "deps"
            target_deps = Path("copyparty/web/deps")
            
            if source_deps.exists():
                # 删除现有的deps目录
                if target_deps.exists():
                    shutil.rmtree(target_deps)
                
                # 复制新的deps
                shutil.copytree(source_deps, target_deps)
                print("✅ WebDeps复制完成")
                
                # 验证关键文件
                key_files = [
                    "mini-fa.woff",
                    "mini-fa.css", 
                    "marked.js",
                    "prism.js",
                    "easymde.js"
                ]
                
                missing_files = []
                for file in key_files:
                    if not (target_deps / file).exists():
                        missing_files.append(file)
                
                if missing_files:
                    print(f"⚠️ 缺少文件: {missing_files}")
                else:
                    print("✅ 所有关键文件都已就位")
                
                return True
            else:
                print(f"❌ 源目录不存在: {source_deps}")
                return False
                
    except Exception as e:
        print(f"❌ 下载WebDeps失败: {e}")
        return False

def create_webdeps_info():
    """创建webdeps信息文件"""
    info_content = """# CopyParty WebDeps

这个目录包含CopyParty的Web依赖文件，包括：

- mini-fa.woff/css: FontAwesome图标字体
- marked.js: Markdown解析器
- prism.js/css: 代码语法高亮
- easymde.js/css: Markdown编辑器
- sha512.*.js: 哈希计算库

这些文件是从官方CopyParty发布版本中提取的。

如果需要重新下载，请运行：
python setup_webdeps.py
"""
    
    info_path = Path("copyparty/web/deps/README.md")
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_content)

def main():
    """主函数"""
    print("🔧 CopyParty WebDeps 设置工具")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("copyparty").exists():
        print("❌ 错误: 请在CopyParty项目根目录运行此脚本")
        return 1
    
    # 检查webdeps状态
    if check_webdeps():
        print("💡 WebDeps已存在，无需重新下载")
        
        # 询问是否重新下载
        try:
            response = input("是否要重新下载WebDeps? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("👋 保持现有WebDeps")
                return 0
        except KeyboardInterrupt:
            print("\n👋 操作取消")
            return 0
    
    # 下载webdeps
    if download_webdeps():
        create_webdeps_info()
        
        print("\n🎉 WebDeps设置完成！")
        print("📋 现在您可以:")
        print("1. ✅ 使用完整的CopyParty Web界面")
        print("2. ✅ 享受所有前端功能")
        print("3. ✅ 正常的图标和样式显示")
        print("4. ✅ Markdown编辑和预览")
        print("5. ✅ 代码语法高亮")
        
        print("\n💡 提示:")
        print("• WebDeps只需要设置一次")
        print("• 文件存储在 copyparty/web/deps/")
        print("• 如有问题可重新运行此脚本")
        
        return 0
    else:
        print("\n❌ WebDeps设置失败")
        print("💡 可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 手动从GitHub下载copyparty-sfx.py")
        print("3. 使用pip安装完整版: pip install copyparty")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
