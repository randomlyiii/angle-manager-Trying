"""游戏逻辑控制器"""
import time
import os
import cv2


class LogicController:
    """游戏逻辑控制器"""
    
    def __init__(self, adb_controller):
        """
        初始化逻辑控制器
        
        Args:
            adb_controller: ADB控制器实例
        """
        self.adb = adb_controller
        
        # 模板图片路径
        self.template_dir = "resource/template/imgs"
        self.regulation_unchecked = os.path.join(self.template_dir, "yuedu0.png")  # 未同意按钮
        self.regulation_checked = os.path.join(self.template_dir, "yuedu1.png")    # 已同意按钮
        self.login_qq = os.path.join(self.template_dir, "login_qq.png")            # QQ登录按钮
        self.login_wechat = os.path.join(self.template_dir, "logic_weixing.png")   # 微信登录按钮
        
        # 获取当前屏幕分辨率
        self.screen_width, self.screen_height = self.adb.get_screen_size()
        if self.screen_width and self.screen_height:
            print(f"当前屏幕分辨率: {self.screen_width}x{self.screen_height}")
        else:
            print("警告: 无法获取屏幕分辨率，将使用默认值")
            self.screen_width, self.screen_height = 1600, 900
    
    def check_and_accept_regulation(self, max_attempts=5, check_interval=2, threshold=0.75):
        """
        检查并自动同意游戏条例
        
        工作流程：
        1. 检测是否存在登录按钮（QQ或微信），确认在登录界面
        2. 检查条例是否已同意（yuedu1.png），如果已同意则无需操作
        3. 如果未同意，查找未同意按钮（yuedu0.png）并点击
        4. 点击后验证是否成功切换到已同意状态
        
        Args:
            max_attempts: 最大尝试次数
            check_interval: 每次检查的间隔时间（秒）
            threshold: 图像匹配阈值（0-1之间，越高越严格）
        
        Returns:
            bool: 是否成功处理条例
        """
        print("\n" + "="*50)
        print("开始检查游戏条例")
        print("="*50)
        
        # 检查模板文件是否存在
        if not self._check_template_files():
            return False
        
        for attempt in range(max_attempts):
            print(f"\n第 {attempt + 1}/{max_attempts} 次检查...")
            
            # 截取当前屏幕
            screenshot_path = self.adb.screenshot()
            if not screenshot_path:
                print("错误: 截图失败")
                time.sleep(check_interval)
                continue
            
            # 检查是否在登录界面（检测登录按钮）
            is_login_screen = self._check_login_screen(screenshot_path, threshold)
            if not is_login_screen:
                print("未检测到登录界面，可能已进入游戏或界面未加载完成")
                if attempt < max_attempts - 1:
                    print(f"{check_interval}秒后重试...")
                    time.sleep(check_interval)
                continue
            
            print("✓ 确认在登录界面")
            
            # 检查条例是否已同意
            if self._is_regulation_accepted(screenshot_path, threshold):
                print("✓ 条例已同意，无需操作")
                return True
            
            # 查找并点击未同意按钮
            if self._click_regulation_checkbox(screenshot_path, threshold):
                print("✓ 已点击条例同意按钮")
                time.sleep(1.5)  # 等待界面响应
                
                # 验证是否成功切换到已同意状态
                screenshot_path = self.adb.screenshot()
                if screenshot_path and self._is_regulation_accepted(screenshot_path, threshold):
                    print("✓ 条例已成功同意")
                    print("="*50)
                    return True
                else:
                    print("警告: 点击后未检测到已同意状态，将重试...")
            else:
                print("未检测到条例复选框")
            
            # 等待后重试
            if attempt < max_attempts - 1:
                print(f"{check_interval}秒后重试...")
                time.sleep(check_interval)
        
        print("\n未能完成条例同意操作")
        print("="*50)
        return False
    
    def _check_template_files(self):
        """
        检查所需的模板文件是否存在
        
        Returns:
            bool: 所有必需文件是否存在
        """
        required_files = [
            (self.regulation_unchecked, "未同意按钮"),
            (self.regulation_checked, "已同意按钮")
        ]
        
        optional_files = [
            (self.login_qq, "QQ登录按钮"),
            (self.login_wechat, "微信登录按钮")
        ]
        
        all_exist = True
        
        # 检查必需文件
        for file_path, description in required_files:
            if not os.path.exists(file_path):
                print(f"错误: {description}模板不存在: {file_path}")
                all_exist = False
            else:
                print(f"✓ {description}模板: {file_path}")
        
        # 检查可选文件
        for file_path, description in optional_files:
            if not os.path.exists(file_path):
                print(f"警告: {description}模板不存在: {file_path}")
            else:
                print(f"✓ {description}模板: {file_path}")
        
        return all_exist
    
    def _check_login_screen(self, screenshot_path, threshold=0.6):
        """
        检查是否在登录界面（通过检测登录按钮）
        
        Args:
            screenshot_path: 屏幕截图路径
            threshold: 匹配阈值
        
        Returns:
            bool: 是否在登录界面
        """
        # 检查QQ登录按钮
        if os.path.exists(self.login_qq):
            if self._find_image_location(screenshot_path, self.login_qq, threshold):
                print("  检测到QQ登录按钮")
                return True
        
        # 检查微信登录按钮
        if os.path.exists(self.login_wechat):
            if self._find_image_location(screenshot_path, self.login_wechat, threshold):
                print("  检测到微信登录按钮")
                return True
        
        return False
    
    def _is_regulation_accepted(self, screenshot_path, threshold=0.75):
        """
        检查条例是否已同意
        
        Args:
            screenshot_path: 屏幕截图路径
            threshold: 匹配阈值
        
        Returns:
            bool: 条例是否已同意
        """
        if not os.path.exists(self.regulation_checked):
            return False
        
        match_result = self._find_image_location(screenshot_path, self.regulation_checked, threshold)
        if match_result:
            max_val, _, _, _, _ = match_result
            print(f"  检测到已同意状态 (匹配度: {max_val:.2f})")
            return True
        
        return False
    
    def _click_regulation_checkbox(self, screenshot_path, threshold=0.75):
        """
        查找并点击条例复选框
        
        Args:
            screenshot_path: 屏幕截图路径
            threshold: 匹配阈值
        
        Returns:
            bool: 是否成功点击
        """
        match_result = self._find_image_location(screenshot_path, self.regulation_unchecked, threshold)
        if not match_result:
            return False
        
        max_val, match_x, match_y, template_w, template_h = match_result
        print(f"  检测到未同意状态 (匹配度: {max_val:.2f})")
        print(f"  匹配区域: 位置({match_x}, {match_y}), 大小({template_w}x{template_h})")
        
        # 计算点击位置
        # 复选框图片本身就是复选框，点击中心即可
        click_x = match_x + template_w // 2
        click_y = match_y + template_h // 2
        
        print(f"  点击位置: ({click_x}, {click_y})")
        
        # 保存调试图像
        self._save_debug_image(screenshot_path, match_x, match_y, template_w, template_h, 
                              click_x, click_y)
        
        # 执行点击
        return self._click_position(click_x, click_y)
    
    def _find_image_location(self, screenshot_path, template_path, threshold=0.75):
        """
        在屏幕截图中查找目标图像的位置
        
        Args:
            screenshot_path: 屏幕截图路径
            template_path: 模板图像路径
            threshold: 匹配阈值
        
        Returns:
            tuple: (匹配度, 左上角x, 左上角y, 模板宽度, 模板高度) 或 None
        """
        if not os.path.exists(screenshot_path) or not os.path.exists(template_path):
            return None
        
        # 读取图像
        screen = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screen is None or template is None:
            return None
        
        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # 返回匹配位置和模板尺寸
            h, w = template.shape[:2]
            return (max_val, max_loc[0], max_loc[1], w, h)
        
        return None
    
    def _save_debug_image(self, screenshot_path, match_x, match_y, template_w, template_h, 
                         click_x, click_y, save_path="debug/regulation_debug.png"):
        """
        保存调试图像，标注匹配区域和点击位置
        
        Args:
            screenshot_path: 屏幕截图路径
            match_x: 匹配区域左上角x坐标
            match_y: 匹配区域左上角y坐标
            template_w: 模板宽度
            template_h: 模板高度
            click_x: 点击位置x坐标
            click_y: 点击位置y坐标
            save_path: 保存路径
        """
        try:
            screen = cv2.imread(screenshot_path)
            if screen is None:
                return
            
            # 绘制匹配区域（绿色矩形）
            cv2.rectangle(screen, (match_x, match_y), 
                         (match_x + template_w, match_y + template_h), 
                         (0, 255, 0), 2)
            
            # 绘制点击位置（红色圆点和十字）
            cv2.circle(screen, (click_x, click_y), 10, (0, 0, 255), -1)
            cv2.line(screen, (click_x - 20, click_y), (click_x + 20, click_y), (0, 0, 255), 2)
            cv2.line(screen, (click_x, click_y - 20), (click_x, click_y + 20), (0, 0, 255), 2)
            
            # 添加文字标注
            cv2.putText(screen, f"Click: ({click_x}, {click_y})", 
                       (click_x + 15, click_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # 保存图像
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, screen)
            print(f"  调试图像已保存: {save_path}")
        except Exception as e:
            print(f"  保存调试图像失败: {e}")
    
    def _click_position(self, x, y):
        """
        点击指定位置
        
        Args:
            x: x坐标
            y: y坐标
        
        Returns:
            bool: 是否点击成功
        """
        cmd = f'"{self.adb.adb_path}" shell input tap {x} {y}'
        success, _, _ = self.adb._execute_command(cmd)
        return success
    
    def click_by_ratio(self, x_ratio, y_ratio):
        """
        根据屏幕比例点击位置（适配不同分辨率）
        
        Args:
            x_ratio: x坐标比例（0-1之间）
            y_ratio: y坐标比例（0-1之间）
        
        Returns:
            bool: 是否点击成功
        
        Example:
            # 点击屏幕中心
            click_by_ratio(0.5, 0.5)
            # 点击屏幕左上角1/4位置
            click_by_ratio(0.25, 0.25)
        """
        if not (0 <= x_ratio <= 1 and 0 <= y_ratio <= 1):
            print(f"错误: 比例值必须在0-1之间 (x_ratio={x_ratio}, y_ratio={y_ratio})")
            return False
        
        # 计算实际坐标
        x = int(self.screen_width * x_ratio)
        y = int(self.screen_height * y_ratio)
        
        print(f"点击位置: ({x}, {y}) [比例: {x_ratio:.2f}, {y_ratio:.2f}]")
        return self._click_position(x, y)
    
    def wait_for_main_menu(self, timeout=30, check_interval=2):
        """
        等待游戏进入主菜单
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
        
        Returns:
            bool: 是否成功进入主菜单
        """
        print(f"\n等待游戏加载进入主菜单 (超时: {timeout}秒)...")
        elapsed = 0
        
        while elapsed < timeout:
            # 这里可以添加主菜单特征检测逻辑
            # 目前简单等待
            time.sleep(check_interval)
            elapsed += check_interval
            
            if elapsed % 10 == 0:
                print(f"等待中... ({elapsed}/{timeout}秒)")
        
        print("✓ 等待完成")
        return True
