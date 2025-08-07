#!/usr/bin/env python3
"""
CopyParty Desktop Application
主应用程序入口点
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
        copyparty_app.show()
        return app.exec()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
