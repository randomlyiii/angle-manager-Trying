import json
import time
import logging
from datetime import datetime
from pathlib import Path


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, adb_controller, image_matcher, config_path="config/task_config.json"):
        self.adb = adb_controller
        self.matcher = image_matcher
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path):
        """加载任务配置"""
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"tasks": []}
    
    def _setup_logger(self):
        """设置日志"""
        Path("data").mkdir(exist_ok=True)
        log_file = f"data/task_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def execute_step(self, step):
        """执行单个步骤"""
        action = step.get("action")
        
        if action == "find_and_click":
            return self._find_and_click(step)
        elif action == "wait":
            time.sleep(step.get("duration", 1))
            return True
        elif action == "screenshot":
            return self.adb.screenshot()
        
        return False
    
    def _find_and_click(self, step):
        """查找并点击"""
        template = step.get("template")
        timeout = step.get("timeout", 10)
        max_retry = step.get("max_retry", self.config.get("max_retry", 3))
        
        start_time = time.time()
        retry_count = 0
        
        while time.time() - start_time < timeout and retry_count < max_retry:
            if not self.adb.screenshot():
                self.logger.error("截图失败")
                retry_count += 1
                time.sleep(1)
                continue
            
            result = self.matcher.find_template(
                self.adb.screenshot_path,
                template
            )
            
            if result and result.get("found"):
                x, y = result["position"]
                self.logger.info(f"找到模板 {template}，位置: ({x}, {y}), 置信度: {result['confidence']:.2f}")
                
                if self.adb.tap(x, y):
                    self.logger.info(f"点击成功: ({x}, {y})")
                    return True
                else:
                    self.logger.error(f"点击失败: ({x}, {y})")
            
            retry_count += 1
            time.sleep(self.config.get("task_interval", 1))
        
        self.logger.warning(f"未找到模板 {template}")
        return False
    
    def execute_task(self, task_name):
        """执行指定任务"""
        tasks = self.config.get("tasks", [])
        task = next((t for t in tasks if t["name"] == task_name), None)
        
        if not task:
            self.logger.error(f"任务不存在: {task_name}")
            return False
        
        if not task.get("enabled", True):
            self.logger.info(f"任务已禁用: {task_name}")
            return False
        
        self.logger.info(f"开始执行任务: {task_name}")
        
        for i, step in enumerate(task.get("steps", [])):
            self.logger.info(f"执行步骤 {i+1}/{len(task['steps'])}")
            
            if not self.execute_step(step):
                self.logger.error(f"步骤执行失败: {step}")
                return False
        
        self.logger.info(f"任务执行完成: {task_name}")
        return True
    
    def execute_all_tasks(self):
        """执行所有启用的任务"""
        tasks = self.config.get("tasks", [])
        enabled_tasks = [t for t in tasks if t.get("enabled", True)]
        
        self.logger.info(f"共有 {len(enabled_tasks)} 个任务待执行")
        
        for task in enabled_tasks:
            self.execute_task(task["name"])
            time.sleep(self.config.get("task_interval", 1))
