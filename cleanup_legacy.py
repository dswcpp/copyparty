#!/usr/bin/env python3
"""
清理旧架构文件，为新架构让路
"""

import os
import sys
import shutil
from pathlib import Path

def get_legacy_files():
    """获取需要清理的旧文件列表"""
    
    # 旧的主要文件
    legacy_files = [
        "copyparty_ultimate_gui.py",
        "copyparty_complete_config.py", 
        "copyparty_complete_widgets.py",
        "run_ultimate_gui.py",
        "install_gui_deps.py",
        "create_architecture.py",
        "cleanup_legacy.py"  # 清理完成后删除自己
    ]
    
    # 旧的文档文件
    legacy_docs = [
        "README_ULTIMATE.md",
        "COPYPARTY_COMPLETENESS_ANALYSIS.md"
    ]
    
    # 配置文件
    legacy_configs = [
        "copyparty_config.json"
    ]
    
    return {
        "main_files": legacy_files,
        "docs": legacy_docs, 
        "configs": legacy_configs
    }

def backup_important_files():
    """备份重要文件到backup目录"""
    
    backup_dir = Path("backup_legacy")
    backup_dir.mkdir(exist_ok=True)
    
    important_files = [
        "copyparty_ultimate_gui.py",  # 主要实现
        "copyparty_complete_config.py",  # 配置系统
        "copyparty_complete_widgets.py",  # UI组件
        "copyparty_config.json"  # 用户配置
    ]
    
    print("备份重要文件...")
    for file_path in important_files:
        if os.path.exists(file_path):
            backup_path = backup_dir / file_path
            shutil.copy2(file_path, backup_path)
            print(f"✓ 备份: {file_path} -> {backup_path}")
    
    print(f"\n✓ 重要文件已备份到 {backup_dir}")

def clean_pycache():
    """清理Python缓存文件"""
    
    print("清理Python缓存...")
    
    # 清理 __pycache__ 目录
    pycache_dirs = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_dirs.append(os.path.join(root, dir_name))
    
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"✓ 删除缓存目录: {pycache_dir}")
        except Exception as e:
            print(f"⚠ 无法删除 {pycache_dir}: {e}")
    
    # 清理 .pyc 文件
    pyc_files = []
    for root, dirs, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".pyc"):
                pyc_files.append(os.path.join(root, file_name))
    
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"✓ 删除缓存文件: {pyc_file}")
        except Exception as e:
            print(f"⚠ 无法删除 {pyc_file}: {e}")

def remove_legacy_files(file_categories, dry_run=False):
    """删除旧文件"""
    
    action = "将删除" if dry_run else "删除"
    
    for category, files in file_categories.items():
        print(f"\n{action} {category}:")
        
        for file_path in files:
            if os.path.exists(file_path):
                if dry_run:
                    print(f"  - {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"✓ 删除: {file_path}")
                    except Exception as e:
                        print(f"✗ 无法删除 {file_path}: {e}")
            else:
                if not dry_run:
                    print(f"⚠ 文件不存在: {file_path}")

def show_new_structure():
    """显示新的项目结构"""
    
    print("\n📁 新的项目结构:")
    print("=" * 50)
    
    structure = """
copyparty_desktop/
├── main.py                 # 新的应用入口
├── requirements.txt        # 依赖管理
├── README_NEW.md          # 新架构说明
│
├── core/                  # 核心模块
│   ├── application.py     # 主应用程序
│   ├── config_manager.py  # 配置管理
│   ├── server_manager.py  # 服务器管理
│   └── plugin_manager.py  # 插件管理
│
├── config/                # 配置模块
├── protocols/             # 协议模块
├── features/              # 功能模块
├── security/              # 安全模块
├── monitoring/            # 监控模块
├── ui/                    # 用户界面
├── plugins/               # 插件系统
├── utils/                 # 工具模块
├── resources/             # 资源文件
├── tests/                 # 测试模块
└── docs/                  # 文档

备份目录:
└── backup_legacy/         # 旧文件备份
    ├── copyparty_ultimate_gui.py
    ├── copyparty_complete_config.py
    ├── copyparty_complete_widgets.py
    └── copyparty_config.json
"""
    
    print(structure)

def main():
    """主函数"""
    
    print("CopyParty Desktop 旧架构清理工具")
    print("=" * 50)
    
    # 获取要清理的文件
    legacy_files = get_legacy_files()
    
    # 显示将要删除的文件
    print("📋 将要清理的文件:")
    remove_legacy_files(legacy_files, dry_run=True)
    
    # 确认清理
    print("\n⚠️  警告: 此操作将删除旧架构文件!")
    print("重要文件将先备份到 backup_legacy/ 目录")
    
    response = input("\n是否继续清理? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("❌ 清理已取消")
        return 1
    
    try:
        # 备份重要文件
        backup_important_files()
        
        # 清理Python缓存
        clean_pycache()
        
        # 删除旧文件
        print("\n开始清理旧文件...")
        remove_legacy_files(legacy_files, dry_run=False)
        
        # 显示新结构
        show_new_structure()
        
        print("\n" + "=" * 50)
        print("✅ 旧架构清理完成!")
        
        print("\n📋 清理总结:")
        print("1. ✅ 重要文件已备份到 backup_legacy/")
        print("2. ✅ Python缓存已清理")
        print("3. ✅ 旧架构文件已删除")
        print("4. ✅ 新架构目录已就绪")
        
        print("\n🚀 下一步:")
        print("1. 查看新架构: README_NEW.md")
        print("2. 查看迁移计划: MIGRATION_PLAN.md")
        print("3. 开始开发: python main.py")
        print("4. 如需恢复旧版本，请从 backup_legacy/ 目录恢复")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 清理过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
