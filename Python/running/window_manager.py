import time
import cv2
import numpy as np


class WindowManager:
    """窗口管理器 - 负责检测和切换游戏窗口"""
    
    def __init__(self, adb_controller):
        self.adb = adb_controller
        
    def is_on_home_screen(self):
        """检测是否在模拟器主屏幕（未进入游戏）"""
        # 截取当前屏幕
        screenshot_path = self.adb.screenshot()
        if not screenshot_path:
            return False
        
        screen = cv2.imread(screenshot_path)
        if screen is None:
            return False
        
        # 检测主屏幕特征：
        # 1. 顶部状态栏的时间显示
        # 2. "每日新发现" 文字区域
        # 使用颜色和位置特征判断
        
        height, width = screen.shape[:2]
        
        # 检查顶部区域是否有深色背景（主屏幕特征）
        top_region = screen[0:int(height*0.1), :]
        avg_color = np.mean(top_region, axis=(0, 1))
        
        # 主屏幕顶部通常是深蓝色背景
        # BGR格式，深蓝色大约是 (高B, 低G, 低R)
        is_dark_blue = avg_color[0] > 80 and avg_color[1] < 80 and avg_color[2] < 80
        
        return is_dark_blue
    
    def switch_to_game(self):
        """切换到游戏窗口（通过点击返回键或最近任务）"""
        print("\n检测到在主屏幕，尝试切换到游戏...")
        
        # 方法1: 按返回键
        cmd = f'"{self.adb.adb_path}" shell input keyevent KEYCODE_BACK'
        success, _, _ = self.adb._execute_command(cmd)
        
        if success:
            time.sleep(1)
            # 检查是否成功切换
            if not self.is_on_home_screen():
                print("✓ 已切换到游戏窗口")
                return True
        
        # 方法2: 打开最近任务并切换
        print("尝试通过最近任务切换...")
        cmd = f'"{self.adb.adb_path}" shell input keyevent KEYCODE_APP_SWITCH'
        self.adb._execute_command(cmd)
        time.sleep(0.5)
        
        # 点击屏幕中央（通常是最近的应用）
        width, height = self.adb.get_screen_size()
        if width and height:
            cmd = f'"{self.adb.adb_path}" shell input tap {width//2} {height//2}'
            self.adb._execute_command(cmd)
            time.sleep(1)
            
            if not self.is_on_home_screen():
                print("✓ 已切换到游戏窗口")
                return True
        
        print("✗ 无法自动切换到游戏")
        return False
    
    def ensure_game_window(self):
        """确保当前在游戏窗口"""
        if self.is_on_home_screen():
            return self.switch_to_game()
        else:
            print("✓ 当前已在游戏窗口")
            return True
