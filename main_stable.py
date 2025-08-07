#!/usr/bin/env python3
"""
CopyParty Desktop Application - 稳定版本
主应用程序入口点 (禁用了有问题的定时器功能)
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt6.QtWidgets import QApplication
    from core.application import CopyPartyApplication
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装 PyQt6: pip install PyQt6")
    sys.exit(1)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("CopyParty Desktop")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("CopyParty")
    
    try:
        copyparty_app = CopyPartyApplication()
        
        # 禁用有问题的定时器
        if hasattr(copyparty_app, 'main_window'):
            main_window = copyparty_app.main_window
            
            # 禁用监控面板的定时器
            if hasattr(main_window, 'monitoring_panel'):
                monitoring_panel = main_window.monitoring_panel
                if hasattr(monitoring_panel, 'performance_timer'):
                    monitoring_panel.performance_timer.stop()
                if hasattr(monitoring_panel, 'log_timer'):
                    monitoring_panel.log_timer.stop()
                print("已禁用监控面板定时器")
            
            # 禁用主窗口的UI更新定时器
            if hasattr(main_window, 'ui_update_timer'):
                main_window.ui_update_timer.stop()
                print("已禁用UI更新定时器")
        
        copyparty_app.show()
        print("应用程序启动成功")
        
        return app.exec()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
