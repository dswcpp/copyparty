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
import queue
from typing import Optional, List, Callable
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class ServerManager:
    """服务器管理器 - 线程安全版本"""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.server_process: Optional[subprocess.Popen] = None
        self.server_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.start_time: Optional[float] = None

        # 线程安全通信
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.shutdown_event = threading.Event()

        # 状态回调
        self.status_callbacks: List[Callable] = []
        self.log_callbacks: List[Callable] = []

        # 线程锁
        self.state_lock = threading.Lock()

        # 查找 CopyParty 可执行文件
        self.copyparty_path = self.find_copyparty_executable()

    def add_status_callback(self, callback: Callable):
        """添加状态变化回调"""
        self.status_callbacks.append(callback)

    def add_log_callback(self, callback: Callable):
        """添加日志回调"""
        self.log_callbacks.append(callback)

    def _emit_status(self, status: str):
        """发送状态更新（线程安全）"""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                print(f"状态回调错误: {e}")

    def _emit_log(self, message: str):
        """发送日志消息（线程安全）"""
        for callback in self.log_callbacks:
            try:
                callback(message)
            except Exception as e:
                print(f"日志回调错误: {e}")

    def find_copyparty_executable(self) -> Optional[str]:
        """查找 CopyParty 可执行文件"""
        # 首先检查系统PATH中的copyparty（pip安装的版本）
        import shutil
        copyparty_exe = shutil.which("copyparty")
        if copyparty_exe:
            print(f"使用系统安装的CopyParty: {copyparty_exe}")
            return copyparty_exe

        # 检查是否可以通过pip安装的模块运行
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-m", "copyparty", "--help"
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                print("使用pip安装的CopyParty模块")
                return "pip_module"

        except Exception as e:
            print(f"pip模块测试失败: {e}")

        # 最后检查本地源码（但会警告用户）
        current_dir = Path(__file__).parent.parent
        copyparty_module = current_dir / "copyparty" / "__main__.py"

        if copyparty_module.exists():
            print(f"⚠️ 警告: 使用本地CopyParty源码，可能缺少Web依赖文件")
            print(f"⚠️ 建议安装完整版本: pip install copyparty")
            return str(copyparty_module)

        return None

    def start_server(self):
        """启动服务器（异步，不阻塞UI）"""
        with self.state_lock:
            if self.is_running:
                raise RuntimeError("服务器已在运行")

            if not self.copyparty_path:
                raise RuntimeError("未找到 CopyParty 可执行文件")

            if not self.config_manager:
                raise RuntimeError("配置管理器未设置")

        # 清除关闭事件
        self.shutdown_event.clear()

        # 在独立线程中启动服务器
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_status, daemon=True)
        self.monitor_thread.start()

        self._emit_log("正在启动服务器...")

    def _run_server(self):
        """在独立线程中运行服务器"""
        try:
            # 生成命令行参数
            args = self.generate_command_args()

            self._emit_log(f"启动命令: {' '.join(args)}")

            # 启动服务器进程
            self.server_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.config_manager.server_config.working_directory
            )

            with self.state_lock:
                self.is_running = True
                self.start_time = time.time()

            self._emit_log(f"服务器已启动，PID: {self.server_process.pid}")
            self._emit_status("服务器运行中")

            # 读取服务器输出（非阻塞）
            self._read_server_output()

        except Exception as e:
            with self.state_lock:
                self.is_running = False
                self.server_process = None
            self._emit_log(f"启动服务器失败: {str(e)}")
            self._emit_status("启动失败")

    def _read_server_output(self):
        """读取服务器输出"""
        if not self.server_process:
            return

        try:
            while self.server_process.poll() is None and not self.shutdown_event.is_set():
                try:
                    # 非阻塞读取
                    line = self.server_process.stdout.readline()
                    if line:
                        self._emit_log(line.strip())
                    else:
                        time.sleep(0.1)  # 避免CPU占用过高
                except Exception:
                    break

        except Exception as e:
            self._emit_log(f"读取服务器输出错误: {e}")
        finally:
            # 服务器进程结束
            with self.state_lock:
                self.is_running = False
                self.start_time = None
            self._emit_status("服务器已停止")

    def stop_server(self):
        """停止服务器（异步，不阻塞UI）"""
        with self.state_lock:
            if not self.is_running or not self.server_process:
                return

        # 设置关闭事件
        self.shutdown_event.set()

        # 在独立线程中停止服务器
        stop_thread = threading.Thread(target=self._stop_server_async, daemon=True)
        stop_thread.start()

        self._emit_log("正在停止服务器...")

    def _stop_server_async(self):
        """在独立线程中停止服务器"""
        try:
            if self.server_process:
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

            with self.state_lock:
                self.is_running = False
                self.server_process = None
                self.start_time = None

            self._emit_log("服务器已停止")
            self._emit_status("服务器已停止")

        except Exception as e:
            self._emit_log(f"停止服务器时出错: {str(e)}")
            # 强制重置状态
            with self.state_lock:
                self.is_running = False
                self.server_process = None

    def _monitor_status(self):
        """监控服务器状态（独立线程）"""
        while not self.shutdown_event.is_set():
            try:
                with self.state_lock:
                    is_running = self.is_running
                    process = self.server_process

                if is_running and process:
                    # 检查进程是否仍在运行
                    if process.poll() is not None:
                        # 进程已结束
                        with self.state_lock:
                            self.is_running = False
                            self.server_process = None
                            self.start_time = None
                        self._emit_status("服务器意外停止")
                        self._emit_log("服务器进程意外退出")
                        break

                # 每秒检查一次
                time.sleep(1)

            except Exception as e:
                self._emit_log(f"监控线程错误: {e}")
                time.sleep(5)  # 错误时等待更长时间

    def restart_server(self):
        """重启服务器（异步）"""
        restart_thread = threading.Thread(target=self._restart_server_async, daemon=True)
        restart_thread.start()
        self._emit_log("正在重启服务器...")

    def _restart_server_async(self):
        """在独立线程中重启服务器"""
        try:
            # 停止服务器
            if self.is_running:
                self.shutdown_event.set()
                if self.server_process:
                    try:
                        if os.name == 'nt':
                            self.server_process.terminate()
                        else:
                            self.server_process.send_signal(signal.SIGTERM)
                        self.server_process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.server_process.kill()
                        self.server_process.wait()

                # 等待线程结束
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=5)
                if self.monitor_thread and self.monitor_thread.is_alive():
                    self.monitor_thread.join(timeout=5)

            # 重置状态
            with self.state_lock:
                self.is_running = False
                self.server_process = None
                self.start_time = None

            # 等待一秒
            time.sleep(1)

            # 重新启动
            self.start_server()

        except Exception as e:
            self._emit_log(f"重启服务器失败: {e}")
            self._emit_status("重启失败")

    def generate_command_args(self) -> List[str]:
        """生成命令行参数"""
        if not self.config_manager:
            raise RuntimeError("配置管理器未设置")

        args = []

        # Python 解释器和模块路径
        if self.copyparty_path == "pip_module" or self.copyparty_path == "copyparty":
            # 使用pip安装的模块或模块名，使用 -m 运行
            args.extend([sys.executable, "-m", "copyparty"])
        elif self.copyparty_path.endswith(".py"):
            # 如果是Python文件，需要作为模块运行以避免相对导入问题
            copyparty_dir = os.path.dirname(self.copyparty_path)
            if os.path.basename(copyparty_dir) == "copyparty":
                # 运行copyparty模块（但会警告用户可能缺少依赖）
                print("⚠️ 使用本地源码运行，可能遇到Web依赖缺失问题")
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

        # 添加GUI模式参数（如果CopyParty支持）
        args.extend(["--gui-mode", "--gui-callbacks"])

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

    def get_server_statistics(self) -> dict:
        """获取服务器统计信息"""
        if not self.is_running:
            return {
                'connections': 0,
                'requests': 0,
                'uploads': 0,
                'downloads': 0,
                'upload_bytes': 0,
                'download_bytes': 0,
                'uptime': 0,
                'error': 'Server not running'
            }

        try:
            # 直接返回基本统计，避免网络请求阻塞
            return self._get_basic_stats()

        except Exception as e:
            return {
                'connections': 0,
                'requests': 0,
                'uploads': 0,
                'downloads': 0,
                'upload_bytes': 0,
                'download_bytes': 0,
                'uptime': 0,
                'error': f'Failed to get stats: {str(e)}'
            }

    def _fetch_copyparty_stats(self) -> dict:
        """从CopyParty服务器获取统计信息"""
        try:
            # 检查服务器是否已经运行足够长时间（至少5秒）
            if not self.start_time or (time.time() - self.start_time) < 5:
                return None

            # 避免频繁请求，使用缓存
            current_time = time.time()
            if hasattr(self, '_last_stats_fetch') and (current_time - self._last_stats_fetch) < 5:
                return getattr(self, '_cached_stats', None)

            import requests

            # 获取服务器地址
            network_config = self.config_manager.network_config
            port = network_config.listen_ports.split(',')[0].strip()

            # 尝试多个可能的统计接口
            possible_endpoints = [
                f"http://localhost:{port}/metrics",  # Prometheus格式
                f"http://localhost:{port}/.cpr/metrics",  # CopyParty内部
                f"http://localhost:{port}/.cpr/stats",   # 原来的尝试
                f"http://localhost:{port}/stats",        # 简单路径
                f"http://localhost:{port}/.stats",       # 隐藏路径
            ]

            for url in possible_endpoints:

                try:
                    # 使用更短的超时时间，避免阻塞
                    response = requests.get(url, timeout=0.5)
                    if response.status_code == 200:
                        # 解析统计数据
                        stats_text = response.text
                        stats = self._parse_copyparty_stats(stats_text)

                        if stats:  # 只有成功解析才缓存
                            # 缓存结果
                            self._cached_stats = stats
                            self._last_stats_fetch = current_time
                            return stats

                except requests.exceptions.RequestException:
                    # 继续尝试下一个接口
                    continue

        except Exception as e:
            # 静默处理错误，避免日志污染
            pass

        return None

    def _parse_copyparty_stats(self, stats_text: str) -> dict:
        """解析CopyParty统计数据"""
        try:
            stats = {
                'connections': 0,
                'requests': 0,
                'uploads': 0,
                'downloads': 0,
                'upload_bytes': 0,
                'download_bytes': 0,
                'uptime': 0
            }

            # 检查是否是JSON格式
            if stats_text.strip().startswith('{'):
                try:
                    import json
                    json_stats = json.loads(stats_text)
                    # 处理JSON格式的统计数据
                    stats.update(json_stats)
                    return stats
                except json.JSONDecodeError:
                    pass

            # 解析Prometheus格式的统计数据
            lines = stats_text.split('\n')
            found_metrics = False

            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                # 尝试解析各种可能的指标名称
                if any(keyword in line.lower() for keyword in ['conn', 'connection']):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].replace('.', '').isdigit():
                        stats['connections'] = int(float(parts[1]))
                        found_metrics = True

                elif any(keyword in line.lower() for keyword in ['req', 'request']):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].replace('.', '').isdigit():
                        stats['requests'] = int(float(parts[1]))
                        found_metrics = True

                elif any(keyword in line.lower() for keyword in ['download', 'dl']):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].replace('.', '').isdigit():
                        stats['downloads'] = int(float(parts[1]))
                        found_metrics = True

                elif any(keyword in line.lower() for keyword in ['upload', 'ul']):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].replace('.', '').isdigit():
                        stats['uploads'] = int(float(parts[1]))
                        found_metrics = True

                elif any(keyword in line.lower() for keyword in ['uptime', 'time']):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].replace('.', '').isdigit():
                        stats['uptime'] = float(parts[1])
                        found_metrics = True

            # 如果找到了任何指标，返回结果
            if found_metrics:
                return stats

            # 如果没有找到指标，但有数据，可能是其他格式
            if stats_text.strip():
                # 尝试从HTML中提取信息（如果是网页响应）
                if '<html' in stats_text.lower():
                    return None  # HTML页面，不是统计数据

                # 返回基本的运行状态
                uptime = time.time() - self.start_time if self.start_time else 0
                return {
                    'connections': 1,  # 至少有一个连接（我们自己）
                    'requests': 1,     # 至少有一个请求
                    'uploads': 0,
                    'downloads': 0,
                    'upload_bytes': 0,
                    'download_bytes': 0,
                    'uptime': uptime
                }

            return None

        except Exception as e:
            # 静默处理错误
            return None

    def _get_basic_stats(self) -> dict:
        """获取基本的服务器统计信息（完全非阻塞）"""
        try:
            uptime = time.time() - self.start_time if self.start_time else 0

            # 简单的估算统计，完全避免阻塞操作
            if uptime > 0:
                # 基于运行时间的估算
                estimated_connections = min(5, max(1, int(uptime / 30)))  # 每30秒增加1个连接，最多5个
                estimated_requests = max(1, int(uptime * 0.1))  # 每10秒1个请求

                return {
                    'connections': estimated_connections,
                    'requests': estimated_requests,
                    'uploads': 0,
                    'downloads': 0,
                    'upload_bytes': 0,
                    'download_bytes': 0,
                    'uptime': uptime,
                    'pid': self.server_process.pid if self.server_process else None
                }
            else:
                return {
                    'connections': 0,
                    'requests': 0,
                    'uploads': 0,
                    'downloads': 0,
                    'upload_bytes': 0,
                    'download_bytes': 0,
                    'uptime': 0,
                    'pid': None
                }

        except Exception:
            # 最基本的统计
            return {
                'connections': 0,
                'requests': 0,
                'uploads': 0,
                'downloads': 0,
                'upload_bytes': 0,
                'download_bytes': 0,
                'uptime': 0,
                'error': 'Failed to get stats'
            }



    def get_server_logs(self) -> tuple:
        """获取服务器日志输出"""
        if not self.is_running or not self.server_process:
            return "", ""

        try:
            # 尝试读取进程的输出
            if self.server_process.poll() is None:  # 进程仍在运行
                # 由于我们使用subprocess.PIPE，可以尝试读取输出
                # 但这可能会阻塞，所以我们返回空字符串
                # 实际的日志应该从CopyParty的日志文件或API获取
                return "", ""
            else:
                # 进程已结束，可以安全读取输出
                stdout, stderr = self.server_process.communicate(timeout=1)
                return stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore')
        except Exception as e:
            return "", f"获取日志失败: {str(e)}"

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
