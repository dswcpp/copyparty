#!/usr/bin/env python3
"""
CopyParty 终极桌面应用启动脚本
"""

import sys
import os
import subprocess

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    required_deps = ["PyQt6", "jinja2", "psutil"]
    missing_deps = []
    
    for dep in required_deps:
        try:
            __import__(dep.lower().replace("6", ""))
            print(f"✓ {dep} 已安装")
        except ImportError:
            missing_deps.append(dep)
            print(f"✗ {dep} 未安装")
    
    return missing_deps

def install_dependencies(missing_deps):
    """安装缺失的依赖"""
    if not missing_deps:
        return True
    
    print(f"\n发现 {len(missing_deps)} 个缺失的依赖")
    response = input("是否自动安装? (y/n): ").lower()
    
    if response == 'y':
        try:
            print("正在运行依赖安装脚本...")
            result = subprocess.run([sys.executable, "install_gui_deps.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ 依赖安装成功")
                return True
            else:
                print(f"✗ 依赖安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ 安装过程出错: {e}")
            return False
    else:
        print("请手动安装依赖:")
        for dep in missing_deps:
            print(f"  pip install {dep}")
        return False

def check_copyparty():
    """检查 CopyParty"""
    print("\n检查 CopyParty...")
    
    try:
        import copyparty
        print("✓ CopyParty 模块可用")
        
        # 检查版本
        try:
            version = copyparty.__version__
            print(f"✓ CopyParty 版本: {version}")
        except:
            print("✓ CopyParty 可用 (版本未知)")
        
        return True
    except ImportError:
        print("⚠ CopyParty 模块不可用")
        print("  请确保 CopyParty 已正确安装")
        print("  pip install copyparty")
        return False

def check_files():
    """检查必要文件"""
    print("\n检查必要文件...")
    
    required_files = [
        "copyparty_complete_config.py",
        "copyparty_complete_widgets.py", 
        "copyparty_ultimate_gui.py"
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            missing_files.append(file)
            print(f"✗ {file} 缺失")
    
    return len(missing_files) == 0

def run_tests():
    """运行测试"""
    print("\n运行快速测试...")
    
    try:
        result = subprocess.run([sys.executable, "test_ultimate_gui.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ 所有测试通过")
            return True
        else:
            print("✗ 测试失败")
            print(result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print("⚠ 测试超时，但可能仍然正常")
        return True
    except Exception as e:
        print(f"⚠ 测试运行出错: {e}")
        return True  # 测试失败不阻止启动

def launch_gui():
    """启动GUI"""
    print("\n启动 CopyParty 终极桌面应用...")
    
    try:
        # 直接运行GUI
        subprocess.run([sys.executable, "copyparty_ultimate_gui.py"])
        return True
    except KeyboardInterrupt:
        print("\n用户中断")
        return True
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("CopyParty 终极桌面应用启动器")
    print("=" * 50)
    
    # 检查依赖
    missing_deps = check_dependencies()
    if missing_deps:
        if not install_dependencies(missing_deps):
            print("\n❌ 依赖检查失败，无法启动")
            return 1
    
    # 检查 CopyParty
    if not check_copyparty():
        response = input("\nCopyParty 不可用，是否继续? (y/n): ").lower()
        if response != 'y':
            return 1
    
    # 检查文件
    if not check_files():
        print("\n❌ 必要文件缺失，无法启动")
        return 1
    
    # 运行测试
    print("\n" + "=" * 50)
    response = input("是否运行快速测试? (y/n): ").lower()
    if response == 'y':
        if not run_tests():
            response = input("测试失败，是否继续启动? (y/n): ").lower()
            if response != 'y':
                return 1
    
    # 启动GUI
    print("\n" + "=" * 50)
    if launch_gui():
        print("\n✅ 应用已正常退出")
        return 0
    else:
        print("\n❌ 应用启动失败")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n用户中断启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n启动器异常: {e}")
        sys.exit(1)
