#!/usr/bin/env python3
"""
简化的应用测试
验证基础功能是否正常
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """测试基础导入"""
    print("测试基础导入...")
    
    try:
        # 测试配置系统
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        print("✓ ConfigManager 创建成功")
        
        # 测试服务器管理器
        from core.server_manager import ServerManager
        server_manager = ServerManager(config_manager)
        print("✓ ServerManager 创建成功")
        
        # 测试配置操作
        config_manager.server_config.working_directory = "/test"
        config_manager.network_config.listen_ports = "8080"
        print("✓ 配置修改成功")
        
        # 测试配置验证
        result = config_manager.validate_all()
        print(f"✓ 配置验证: {'通过' if result.is_valid else '有错误'}")
        
        # 测试命令行参数生成
        args = config_manager.generate_copyparty_args()
        print(f"✓ 命令行参数生成: {len(args)} 个参数")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_basic():
    """测试基础GUI功能"""
    print("\n测试基础GUI功能...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        # 创建应用
        app = QApplication([])
        print("✓ QApplication 创建成功")
        
        # 测试配置管理器
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        # 测试简化的UI组件
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
        
        class SimpleTestWidget(QWidget):
            def __init__(self):
                super().__init__()
                layout = QVBoxLayout()
                
                layout.addWidget(QLabel("CopyParty Desktop v2.0 测试"))
                layout.addWidget(QLabel(f"工作目录: {config_manager.server_config.working_directory}"))
                layout.addWidget(QLabel(f"监听端口: {config_manager.network_config.listen_ports}"))
                
                test_btn = QPushButton("测试按钮")
                test_btn.clicked.connect(lambda: print("按钮点击测试成功"))
                layout.addWidget(test_btn)
                
                self.setLayout(layout)
                self.setWindowTitle("CopyParty Desktop 测试")
                self.resize(400, 200)
        
        # 创建测试窗口
        test_widget = SimpleTestWidget()
        test_widget.show()
        print("✓ 测试窗口创建成功")
        
        # 清理
        test_widget.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_manager():
    """测试服务器管理器"""
    print("\n测试服务器管理器...")
    
    try:
        from core.config_manager import ConfigManager
        from core.server_manager import ServerManager
        
        # 创建管理器
        config_manager = ConfigManager()
        server_manager = ServerManager(config_manager)
        
        # 测试状态获取
        status = server_manager.get_server_status()
        print(f"✓ 服务器状态: {status}")
        
        # 测试命令行生成
        args = server_manager.generate_command_args()
        print(f"✓ 命令行参数: {' '.join(args[:5])}...")
        
        # 测试CopyParty可执行文件查找
        copyparty_path = server_manager.find_copyparty_executable()
        print(f"✓ CopyParty路径: {copyparty_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ 服务器管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_serialization():
    """测试配置序列化"""
    print("\n测试配置序列化...")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 修改配置
        config_manager.server_config.working_directory = "/test/path"
        config_manager.server_config.max_clients = 2048
        config_manager.network_config.listen_ports = "8080,8081"
        
        # 测试JSON序列化
        json_str = config_manager.to_json()
        print(f"✓ JSON序列化: {len(json_str)} 字符")
        
        # 测试反序列化
        new_config = ConfigManager()
        new_config.from_json(json_str)
        print("✓ JSON反序列化成功")
        
        # 验证数据
        assert new_config.server_config.working_directory == "/test/path"
        assert new_config.server_config.max_clients == 2048
        assert new_config.network_config.listen_ports == "8080,8081"
        print("✓ 数据一致性验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置序列化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("CopyParty Desktop 简化测试")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config_serialization,
        test_server_manager,
        test_gui_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 异常: {e}")
    
    print("\n" + "=" * 40)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 基础功能测试全部通过！")
        print("\n🎉 核心功能验证:")
        print("1. ✅ 配置系统正常")
        print("2. ✅ 服务器管理正常")
        print("3. ✅ 序列化功能正常")
        print("4. ✅ 基础GUI正常")
        
        print("\n🚀 可以继续完善复杂功能")
    else:
        print("❌ 部分基础功能有问题，需要修复")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
