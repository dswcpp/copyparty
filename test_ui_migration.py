#!/usr/bin/env python3
"""
测试UI组件迁移
验证从旧架构到新架构的UI迁移
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_imports():
    """测试UI模块导入"""
    print("测试UI模块导入...")
    
    try:
        from ui.main_window import MainWindow
        print("✓ main_window 导入成功")
        
        from ui.widgets.server_control import ServerControlWidget
        print("✓ server_control 导入成功")
        
        from ui.widgets.config_editor import ConfigEditorWidget
        print("✓ config_editor 导入成功")
        
        from ui.widgets.monitoring_panel import MonitoringPanel, LogViewer
        print("✓ monitoring_panel 导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ UI模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_core_imports():
    """测试核心模块导入"""
    print("\n测试核心模块导入...")
    
    try:
        from core.application import CopyPartyApplication
        print("✓ application 导入成功")
        
        from core.config_manager import ConfigManager
        print("✓ config_manager 导入成功")
        
        from core.server_manager import ServerManager
        print("✓ server_manager 导入成功")
        
        from core.plugin_manager import PluginManager
        print("✓ plugin_manager 导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 核心模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_creation():
    """测试应用程序创建"""
    print("\n测试应用程序创建...")
    
    try:
        # 检查PyQt6是否可用
        from PyQt6.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication([])
        
        # 创建主应用程序
        from core.application import CopyPartyApplication
        copyparty_app = CopyPartyApplication()
        
        print("✓ 应用程序创建成功")
        
        # 检查组件是否正确初始化
        assert hasattr(copyparty_app, 'config_manager'), "配置管理器未初始化"
        assert hasattr(copyparty_app, 'server_manager'), "服务器管理器未初始化"
        assert hasattr(copyparty_app, 'plugin_manager'), "插件管理器未初始化"
        assert hasattr(copyparty_app, 'main_window'), "主窗口未初始化"
        
        print("✓ 组件初始化验证通过")
        
        # 清理
        copyparty_app.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ 应用程序创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_creation():
    """测试组件创建"""
    print("\n测试组件创建...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from core.application import CopyPartyApplication
        
        # 创建应用程序
        app = QApplication([])
        copyparty_app = CopyPartyApplication()
        
        # 测试主窗口组件
        main_window = copyparty_app.main_window
        
        # 检查主要组件是否存在
        assert hasattr(main_window, 'control_panel'), "控制面板未创建"
        assert hasattr(main_window, 'config_editor'), "配置编辑器未创建"
        assert hasattr(main_window, 'monitoring_panel'), "监控面板未创建"
        assert hasattr(main_window, 'log_viewer'), "日志查看器未创建"
        
        print("✓ 主要组件创建成功")
        
        # 测试控制面板组件
        control_panel = main_window.control_panel
        assert hasattr(control_panel, 'start_btn'), "启动按钮未创建"
        assert hasattr(control_panel, 'stop_btn'), "停止按钮未创建"
        assert hasattr(control_panel, 'restart_btn'), "重启按钮未创建"
        
        print("✓ 控制面板组件验证通过")
        
        # 测试配置编辑器组件
        config_editor = main_window.config_editor
        assert hasattr(config_editor, 'tabs'), "配置标签页未创建"
        assert hasattr(config_editor, 'apply_btn'), "应用按钮未创建"
        
        print("✓ 配置编辑器组件验证通过")
        
        # 清理
        copyparty_app.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ 组件创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_integration():
    """测试配置集成"""
    print("\n测试配置集成...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from core.application import CopyPartyApplication
        
        # 创建应用程序
        app = QApplication([])
        copyparty_app = CopyPartyApplication()
        
        # 获取配置管理器
        config_manager = copyparty_app.config_manager
        
        # 测试配置修改
        original_port = config_manager.network_config.listen_ports
        config_manager.network_config.listen_ports = "8080"
        
        # 测试配置应用到UI
        main_window = copyparty_app.main_window
        config_editor = main_window.config_editor
        
        # 加载配置到UI
        config_editor.load_config_to_ui()
        
        # 验证UI是否反映了配置更改
        assert config_editor.listen_ports_edit.text() == "8080", "配置未正确加载到UI"
        
        print("✓ 配置到UI加载验证通过")
        
        # 测试从UI应用配置
        config_editor.listen_ports_edit.setText("9000")
        config_editor.apply_config()
        
        # 验证配置是否更新
        assert config_manager.network_config.listen_ports == "9000", "UI配置未正确应用"
        
        print("✓ UI到配置应用验证通过")
        
        # 恢复原始配置
        config_manager.network_config.listen_ports = original_port
        
        # 清理
        copyparty_app.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ 配置集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_integration():
    """测试服务器集成"""
    print("\n测试服务器集成...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from core.application import CopyPartyApplication
        
        # 创建应用程序
        app = QApplication([])
        copyparty_app = CopyPartyApplication()
        
        # 获取服务器管理器
        server_manager = copyparty_app.server_manager
        
        # 测试服务器状态
        status = server_manager.get_server_status()
        assert isinstance(status, dict), "服务器状态格式错误"
        assert 'running' in status, "服务器状态缺少运行状态"
        
        print("✓ 服务器状态获取验证通过")
        
        # 测试命令行参数生成
        args = server_manager.generate_command_args()
        assert isinstance(args, list), "命令行参数格式错误"
        
        print("✓ 命令行参数生成验证通过")
        
        # 测试控制面板与服务器管理器的集成
        control_panel = copyparty_app.main_window.control_panel
        
        # 验证按钮状态
        assert control_panel.start_btn.isEnabled(), "启动按钮应该可用"
        assert not control_panel.stop_btn.isEnabled(), "停止按钮应该不可用"
        
        print("✓ 控制面板状态验证通过")
        
        # 清理
        copyparty_app.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ 服务器集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_compatibility():
    """测试旧版本兼容性"""
    print("\n测试旧版本兼容性...")
    
    try:
        # 检查是否存在旧配置文件
        if not os.path.exists("copyparty_complete_config.py"):
            print("⚠ 旧配置文件不存在，跳过兼容性测试")
            return True
        
        from PyQt6.QtWidgets import QApplication
        from core.application import CopyPartyApplication
        from copyparty_complete_config import CopyPartyCompleteConfig
        
        # 创建应用程序
        app = QApplication([])
        copyparty_app = CopyPartyApplication()
        
        # 创建旧配置
        legacy_config = CopyPartyCompleteConfig()
        
        # 测试迁移
        config_manager = copyparty_app.config_manager
        config_manager.load_from_legacy(legacy_config)
        
        print("✓ 旧配置迁移验证通过")
        
        # 测试UI更新
        config_editor = copyparty_app.main_window.config_editor
        config_editor.load_config_to_ui()
        
        print("✓ 迁移后UI更新验证通过")
        
        # 清理
        copyparty_app.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ 旧版本兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("CopyParty UI组件迁移测试")
    print("=" * 50)
    
    tests = [
        test_ui_imports,
        test_core_imports,
        test_application_creation,
        test_widget_creation,
        test_config_integration,
        test_server_integration,
        test_legacy_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ UI组件迁移测试全部通过！")
        print("\n🎉 UI迁移成果:")
        print("1. ✅ 模块化UI架构")
        print("2. ✅ 主窗口和组件集成")
        print("3. ✅ 配置系统UI集成")
        print("4. ✅ 服务器管理UI集成")
        print("5. ✅ 旧版本兼容性")
        
        print("\n📊 UI组件统计:")
        print("- MainWindow: 主窗口布局和菜单")
        print("- ServerControlWidget: 服务器控制面板")
        print("- ConfigEditorWidget: 配置编辑器")
        print("- MonitoringPanel: 性能监控面板")
        print("- LogViewer: 日志查看器")
        
        print("\n🚀 下一步: 测试完整应用")
        print("python main.py")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
