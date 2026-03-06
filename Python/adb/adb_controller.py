import subprocess
import json
import os
import time
from pathlib import Path


class ADBController:
    """ADB设备控制器"""
    
    def __init__(self, config_path="config/adb_config.json"):
        self.config = self._load_config(config_path)
        self.adb_path = self.config.get("adb_path", "adb")
        self.mumu_path = self.config.get("mumu_path", "")
        self.mumu_index = self.config.get("mumu_index", 0)
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _execute_command(self, command):
        """执行ADB命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.get("connection_timeout", 30)
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def start_emulator(self):
        """启动MuMu模拟器"""
        if not self.mumu_path or not os.path.exists(self.mumu_path):
            print("错误: MuMu模拟器路径未配置或不存在")
            print(f"配置路径: {self.mumu_path}")
            return False
        
        # 计算端口号（16384 + index * 32）
        port = 16384 + self.mumu_index * 32
        device_address = f"127.0.0.1:{port}"
        
        # 检查模拟器是否已经运行
        cmd = f'"{self.adb_path}" devices'
        success, stdout, _ = self._execute_command(cmd)
        
        if success and device_address in stdout and "device" in stdout:
            print(f"MuMu模拟器已在运行 (端口: {port})")
            self._hide_mumu_manager()
            return True
        
        print(f"正在启动MuMu模拟器 #{self.mumu_index} (端口: {port})...")
        try:
            # 使用Popen启动模拟器，传入索引参数
            # MuMuNxDevice.exe 启动命令格式
            subprocess.Popen([self.mumu_path], shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("模拟器启动命令已发送，等待模拟器启动...")
            
            # 从配置读取等待时间
            max_wait = self.config.get("emulator_start_timeout", 90)
            wait_interval = self.config.get("emulator_start_check_interval", 3)
            elapsed = 0
            
            while elapsed < max_wait:
                time.sleep(wait_interval)
                elapsed += wait_interval
                
                cmd = f'"{self.adb_path}" devices'
                success, stdout, _ = self._execute_command(cmd)
                
                if success and device_address in stdout and "device" in stdout:
                    print(f"模拟器启动成功！(端口: {port}, 耗时 {elapsed} 秒)")
                    time.sleep(5)  # 额外等待确保完全启动
                    
                    # 隐藏管理器窗口到托盘
                    self._hide_mumu_manager()
                    return True
                
                if elapsed % 9 == 0:  # 每9秒显示一次
                    print(f"等待中... ({elapsed}/{max_wait}秒)")
            
            print("警告: 模拟器启动超时")
            return False
            
        except Exception as e:
            print(f"启动模拟器失败: {e}")
            return False
    
    def _hide_mumu_manager(self):
        """隐藏MuMu管理器窗口到托盘"""
        try:
            import win32gui
            import win32con
            
            # 查找MuMu管理器窗口
            def find_window_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "MuMu" in title and "模拟器" in title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(find_window_callback, windows)
            
            # 隐藏找到的窗口
            for hwnd in windows:
                title = win32gui.GetWindowText(hwnd)
                # 只隐藏管理器窗口，不隐藏模拟器窗口
                if "MuMu模拟器" == title or "MuMu" in title:
                    # 检查是否是管理器窗口（通常管理器窗口标题不包含具体游戏名）
                    if "12" not in title or len(title) < 15:
                        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                        print(f"已隐藏窗口: {title}")
            
        except ImportError:
            print("提示: 需要安装 pywin32 才能自动隐藏管理器窗口")
            print("运行: pip install pywin32")
        except Exception as e:
            print(f"隐藏窗口时出错: {e}")
    
    def connect(self, device_ip=None):
        """连接设备"""
        # 根据配置的索引计算端口号
        if device_ip is None:
            port = 16384 + self.mumu_index * 32
            device_ip = f"127.0.0.1:{port}"
        
        # 先尝试连接MuMu模拟器
        print(f"正在连接设备: {device_ip}")
        cmd = f'"{self.adb_path}" connect {device_ip}'
        success, stdout, stderr = self._execute_command(cmd)
        
        if success:
            print(f"连接命令执行成功: {stdout.strip()}")
        else:
            print(f"连接失败: {stderr}")
        
        # 等待连接建立
        time.sleep(2)
        
        # 检查设备列表
        cmd = f'"{self.adb_path}" devices'
        success, stdout, stderr = self._execute_command(cmd)
        
        print(f"设备列表:\n{stdout}")
        
        # 检查是否有设备连接
        if success and "device" in stdout.lower() and device_ip in stdout:
            # 尝试唤醒设备
            self.wake_device()
            return True
        
        return False
    
    def wake_device(self):
        """唤醒设备屏幕"""
        # 检查屏幕状态
        cmd = f'"{self.adb_path}" shell dumpsys power | findstr "mWakefulness"'
        success, stdout, _ = self._execute_command(cmd)
        
        # 如果屏幕是休眠状态，则唤醒
        if success and ("Asleep" in stdout or "Dozing" in stdout):
            print("检测到设备休眠，正在唤醒...")
            # 按电源键唤醒
            cmd = f'"{self.adb_path}" shell input keyevent KEYCODE_WAKEUP'
            self._execute_command(cmd)
            time.sleep(1)
            
            # 滑动解锁（如果有锁屏）
            cmd = f'"{self.adb_path}" shell input swipe 500 1000 500 300'
            self._execute_command(cmd)
            time.sleep(0.5)
            print("设备已唤醒")
        else:
            print("设备屏幕已激活")
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        cmd = f'"{self.adb_path}" shell wm size'
        success, stdout, _ = self._execute_command(cmd)
        
        if success and "Physical size:" in stdout:
            size_str = stdout.split("Physical size:")[1].strip()
            width, height = map(int, size_str.split('x'))
            return width, height
        return None, None
    
    def run(self):
        """运行完整的启动和连接流程"""
        print("=" * 50)
        print("ADB模拟器自动连接工具")
        print("=" * 50)
        
        print("\n[1/2] 初始化ADB控制器...")
        print("[2/2] 检查并启动MuMu模拟器...")
        
        if not self.start_emulator():
            print("警告: 模拟器启动失败，尝试连接现有设备...")
        
        print("\n连接设备...")
        if not self.connect():
            print("\n错误: 无法连接到设备，请检查:")
            print("  - MuMu模拟器是否已启动")
            print("  - ADB工具是否正确配置")
            print("  - config/adb_config.json中的配置是否正确")
            return False
        
        print("\n✓ 设备连接成功!")
        
        width, height = self.get_screen_size()
        if width and height:
            print(f"✓ 屏幕尺寸: {width}x{height}")
        
        print("\n" + "=" * 50)
        print("模拟器已就绪")
        print("=" * 50)
        return True
