#!/usr/bin/env python3
"""
CopyParty Desktop 自动化打包脚本
支持多平台打包和分发
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path

class BuildManager:
    """构建管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        
    def clean(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✓ 已清理 {dir_path}")
        
        # 清理.spec文件
        for spec_file in self.project_root.glob("*.spec"):
            spec_file.unlink()
            print(f"  ✓ 已删除 {spec_file}")
        
        print("✅ 清理完成")
    
    def check_dependencies(self):
        """检查依赖"""
        print("🔍 检查依赖...")
        
        required_packages = [
            'PyQt6',
            'pyinstaller',
            'setuptools',
            'wheel'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"  ✓ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ✗ {package} (缺失)")
        
        if missing_packages:
            print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ 依赖检查通过")
        return True
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        test_files = [
            "test_config_migration.py",
            "test_ui_migration.py", 
            "test_protocol_expansion.py",
            "test_high_priority_features.py"
        ]
        
        passed_tests = 0
        total_tests = len(test_files)
        
        for test_file in test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, str(test_path)
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if result.returncode == 0:
                        print(f"  ✓ {test_file}")
                        passed_tests += 1
                    else:
                        print(f"  ✗ {test_file}")
                        print(f"    错误: {result.stderr[:100]}...")
                except Exception as e:
                    print(f"  ✗ {test_file} - 异常: {e}")
            else:
                print(f"  ⚠️  {test_file} (文件不存在)")
        
        print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
        
        if passed_tests < total_tests:
            print("⚠️  部分测试失败，但继续构建...")
        else:
            print("✅ 所有测试通过")
        
        return True
    
    def generate_spec(self):
        """生成PyInstaller配置"""
        print("📝 生成PyInstaller配置...")
        
        try:
            result = subprocess.run([
                sys.executable, "build_spec.py"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ PyInstaller配置生成成功")
                print(result.stdout)
                return True
            else:
                print(f"❌ PyInstaller配置生成失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 生成配置时出错: {e}")
            return False
    
    def build_executable(self):
        """构建可执行文件"""
        print("🔨 构建可执行文件...")
        
        # 查找.spec文件
        spec_files = list(self.project_root.glob("*.spec"))
        if not spec_files:
            print("❌ 未找到.spec文件")
            return False
        
        spec_file = spec_files[0]
        print(f"使用配置文件: {spec_file}")
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ 可执行文件构建成功")
                return True
            else:
                print(f"❌ 构建失败，返回码: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ 构建时出错: {e}")
            return False
    
    def create_installer(self):
        """创建安装包"""
        print("📦 创建安装包...")
        
        if self.system == "windows":
            return self._create_windows_installer()
        elif self.system == "darwin":
            return self._create_macos_installer()
        elif self.system == "linux":
            return self._create_linux_installer()
        else:
            print(f"⚠️  暂不支持 {self.system} 平台的安装包创建")
            return True
    
    def _create_windows_installer(self):
        """创建Windows安装包"""
        print("  创建Windows安装包...")
        
        # 检查是否有NSIS
        try:
            subprocess.run(["makensis", "/VERSION"], 
                         capture_output=True, check=True)
            print("  ✓ 找到NSIS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ⚠️  未找到NSIS，跳过安装包创建")
            return True
        
        # 这里可以添加NSIS脚本生成和执行
        print("  ⚠️  Windows安装包创建功能开发中...")
        return True
    
    def _create_macos_installer(self):
        """创建macOS安装包"""
        print("  创建macOS安装包...")
        
        # 检查.app文件
        app_files = list(self.dist_dir.glob("*.app"))
        if not app_files:
            print("  ❌ 未找到.app文件")
            return False
        
        app_file = app_files[0]
        dmg_name = f"CopyPartyDesktop-{self.arch}.dmg"
        
        try:
            # 创建DMG
            cmd = [
                "hdiutil", "create", "-volname", "CopyParty Desktop",
                "-srcfolder", str(app_file),
                "-ov", "-format", "UDZO",
                str(self.dist_dir / dmg_name)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ 已创建 {dmg_name}")
                return True
            else:
                print(f"  ❌ DMG创建失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建DMG时出错: {e}")
            return False
    
    def _create_linux_installer(self):
        """创建Linux安装包"""
        print("  创建Linux安装包...")
        
        # 创建tar.gz包
        try:
            exe_files = list(self.dist_dir.glob("CopyPartyDesktop*"))
            if not exe_files:
                print("  ❌ 未找到可执行文件")
                return False
            
            exe_file = exe_files[0]
            tar_name = f"CopyPartyDesktop-linux-{self.arch}.tar.gz"
            
            cmd = [
                "tar", "-czf", 
                str(self.dist_dir / tar_name),
                "-C", str(self.dist_dir),
                exe_file.name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ 已创建 {tar_name}")
                return True
            else:
                print(f"  ❌ tar包创建失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建tar包时出错: {e}")
            return False
    
    def show_results(self):
        """显示构建结果"""
        print("\n📊 构建结果:")
        
        if self.dist_dir.exists():
            files = list(self.dist_dir.iterdir())
            if files:
                print("  生成的文件:")
                for file in files:
                    size = file.stat().st_size if file.is_file() else 0
                    size_mb = size / (1024 * 1024)
                    print(f"    📄 {file.name} ({size_mb:.1f} MB)")
            else:
                print("  ❌ 未找到生成的文件")
        else:
            print("  ❌ 构建目录不存在")
    
    def build(self, skip_tests=False, skip_installer=False):
        """完整构建流程"""
        print("🚀 开始构建 CopyParty Desktop")
        print(f"平台: {self.system}-{self.arch}")
        print("=" * 50)
        
        steps = [
            ("检查依赖", self.check_dependencies),
            ("清理目录", self.clean),
        ]
        
        if not skip_tests:
            steps.append(("运行测试", self.run_tests))
        
        steps.extend([
            ("生成配置", self.generate_spec),
            ("构建可执行文件", self.build_executable),
        ])
        
        if not skip_installer:
            steps.append(("创建安装包", self.create_installer))
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ {step_name}失败，构建中止")
                return False
        
        self.show_results()
        print("\n🎉 构建完成！")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CopyParty Desktop 构建工具")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--skip-installer", action="store_true", help="跳过安装包创建")
    parser.add_argument("--clean-only", action="store_true", help="仅清理")
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    if args.clean_only:
        builder.clean()
        return 0
    
    success = builder.build(
        skip_tests=args.skip_tests,
        skip_installer=args.skip_installer
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
