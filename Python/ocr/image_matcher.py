import cv2
import numpy as np
import json
import os
from pathlib import Path


class ImageMatcher:
    """图像匹配器"""
    
    def __init__(self, config_path="config/ocr_config.json"):
        self.config = self._load_config(config_path)
        self.threshold = self.config.get("template_match_threshold", 0.8)
        self.template_dir = self.config.get("template_dir", "resource/templates")
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def find_template(self, screenshot_path, template_name, threshold=None):
        """在截图中查找模板"""
        if threshold is None:
            threshold = self.threshold
        
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(screenshot_path):
            return None
        if not os.path.exists(template_path):
            return None
        
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screenshot is None or template is None:
            return None
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            return {
                "found": True,
                "confidence": float(max_val),
                "position": (center_x, center_y),
                "top_left": max_loc,
                "size": (w, h)
            }
        
        return None
    
    def find_all_templates(self, screenshot_path, template_name, threshold=None):
        """查找所有匹配的模板"""
        if threshold is None:
            threshold = self.threshold
        
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(screenshot_path) or not os.path.exists(template_path):
            return []
        
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screenshot is None or template is None:
            return []
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        matches = []
        h, w = template.shape[:2]
        
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            matches.append({
                "position": (center_x, center_y),
                "top_left": pt,
                "size": (w, h)
            })
        
        return matches
    
    def save_debug_image(self, screenshot_path, template_name, result, output_path="debug/match_result.png"):
        """保存调试图像"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None or result is None:
            return False
        
        if result.get("found"):
            top_left = result["top_left"]
            w, h = result["size"]
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
            center = result["position"]
            cv2.circle(screenshot, center, 5, (0, 0, 255), -1)
        
        cv2.imwrite(output_path, screenshot)
        return True
