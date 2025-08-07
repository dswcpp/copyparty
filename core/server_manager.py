"""
服务器管理器
管理 CopyParty 服务器进程
"""

import os
import sys
import subprocess
import signal
import time
import threading
from typing import Optional, List
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class ServerManager:
    """服务器管理器"""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.server_process: Optional[subprocess.Popen] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.start_time: Optional[float] = None

        # 查找 CopyParty 可执行文件
        self.copyparty_path = self.find_copyparty_executable()

    def find_copyparty_executable(self) -> Optional[str]:
        """查找 CopyParty 可执行文件"""
        # 优先检查是否安装了 copyparty 包
        try:
            import copyparty
            # 如果能导入，返回模块名，这样可以用 -m copyparty 运行
            return "copyparty"
        except ImportError:
            pass

        # 检查系统PATH中的copyparty
        import shutil
        copyparty_exe = shutil.which("copyparty")
        if copyparty_exe:
            return copyparty_exe

        # 最后检查当前目录下的 copyparty 模块（但这通常会有相对导入问题）
        current_dir = Path(__file__).parent.parent
        copyparty_module = current_dir / "copyparty" / "__main__.py"

        if copyparty_module.exists():
            print(f"警告: 找到本地CopyParty模块 {copyparty_module}，但可能有相对导入问题")
            return str(copyparty_module)

        return None

    def start_server(self):
        """启动服务器"""
        if self.is_running:
            raise RuntimeError("服务器已在运行")

        if not self.copyparty_path:
            raise RuntimeError("未找到 CopyParty 可执行文件")

        if not self.config_manager:
            raise RuntimeError("配置管理器未设置")

        try:
            # 生成命令行参数
            args = self.generate_command_args()

            # 启动服务器进程
            self.server_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config_manager.server_config.working_directory
            )

            self.is_running = True
            self.start_time = time.time()

            # 启动监控线程
            self.server_thread = threading.Thread(target=self._monitor_server, daemon=True)
            self.server_thread.start()

            print(f"服务器已启动，PID: {self.server_process.pid}")

        except Exception as e:
            self.is_running = False
            self.server_process = None
            raise RuntimeError(f"启动服务器失败: {str(e)}")

    def stop_server(self):
        """停止服务器"""
        if not self.is_running or not self.server_process:
            return

        try:
            # 尝试优雅关闭
            if os.name == 'nt':  # Windows
                self.server_process.terminate()
            else:  # Unix/Linux
                self.server_process.send_signal(signal.SIGTERM)

            # 等待进程结束
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # 强制杀死进程
                self.server_process.kill()
                self.server_process.wait()

            self.is_running = False
            self.server_process = None
            self.start_time = None

            print("服务器已停止")

        except Exception as e:
            print(f"停止服务器时出错: {str(e)}")
            # 强制重置状态
            self.is_running = False
            self.server_process = None

    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        time.sleep(1)  # 等待1秒
        self.start_server()

    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config_manager:
            raise RuntimeError("配置管理器未设置")

        args = []

        # Python 解释器和模块路径
        if self.copyparty_path == "copyparty":
            # 如果是模块名，使用 -m 运行
            args.extend([sys.executable, "-m", "copyparty"])
        elif self.copyparty_path.endswith(".py"):
            # 如果是Python文件，需要作为模块运行以避免相对导入问题
            copyparty_dir = os.path.dirname(self.copyparty_path)
            if os.path.basename(copyparty_dir) == "copyparty":
                # 运行copyparty模块
                args.extend([sys.executable, "-m", "copyparty"])
            else:
                # 直接运行Python文件
                args.extend([sys.executable, self.copyparty_path])
        else:
            # 可执行文件
            args.append(self.copyparty_path)

        # 添加配置参数
        config_args = self.config_manager.generate_copyparty_args()
        args.extend(config_args)

        return args

    def _monitor_server(self):
        """监控服务器进程"""
        if not self.server_process:
            return

        try:
            # 等待进程结束
            return_code = self.server_process.wait()

            if self.is_running:  # 如果不是主动停止
                print(f"服务器进程意外退出，返回码: {return_code}")

                # 读取错误输出
                if self.server_process.stderr:
                    stderr_output = self.server_process.stderr.read()
                    if stderr_output:
                        print(f"服务器错误输出: {stderr_output}")

                # 重置状态
                self.is_running = False
                self.server_process = None

        except Exception as e:
            print(f"监控服务器进程时出错: {str(e)}")

    def get_server_status(self) -> dict:
        """获取服务器状态"""
        status = {
            'running': self.is_running,
            'pid': self.server_process.pid if self.server_process else None,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'command': self.generate_command_args() if self.config_manager else []
        }

        return status

    def get_server_logs(self) -> tuple:
        """获取服务器日志"""
        if not self.server_process:
            return "", ""

        try:
            # 非阻塞读取输出
            stdout_data = ""
            stderr_data = ""

            if self.server_process.stdout:
                stdout_data = self.server_process.stdout.read()

            if self.server_process.stderr:
                stderr_data = self.server_process.stderr.read()

            return stdout_data, stderr_data

        except Exception as e:
            print(f"读取服务器日志失败: {str(e)}")
            return "", ""

    def is_server_running(self) -> bool:
        """检查服务器是否运行"""
        if not self.is_running or not self.server_process:
            return False

        # 检查进程是否仍在运行
        try:
            return self.server_process.poll() is None
        except:
            return False
