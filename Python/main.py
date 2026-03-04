"""
自动化测试主程序入口
"""
import sys
import os
from pathlib import Path

# 添加Python目录到路径
python_dir = Path(__file__).parent
sys.path.insert(0, str(python_dir))

from adb.adb_controller import ADBController
from ocr.image_matcher import ImageMatcher
from task.task_executor import TaskExecutor


def main():
    """主函数"""
    print("=" * 50)
    print("自动化测试工具启动")
    print("=" * 50)
    
    # 初始化ADB控制器
    print("\n[1/5] 初始化ADB控制器...")
    adb = ADBController()
    
    # 启动模拟器
    print("[2/5] 检查并启动MuMu模拟器...")
    if not adb.start_emulator():
        print("警告: 模拟器启动失败，尝试连接现有设备...")
    
    # 连接设备
    print("[3/5] 连接设备...")
    if not adb.connect():
        print("错误: 无法连接到设备，请检查:")
        print("  - MuMu模拟器是否已启动")
        print("  - ADB工具是否正确配置")
        print("  - config/adb_config.json中的设备名称是否正确")
        return
    
    print("设备连接成功!")
    
    # 获取屏幕尺寸
    width, height = adb.get_screen_size()
    if width and height:
        print(f"屏幕尺寸: {width}x{height}")
    
    # 初始化图像匹配器
    print("\n[4/5] 初始化图像匹配器...")
    matcher = ImageMatcher()
    
    # 初始化任务执行器
    print("[5/5] 初始化任务执行器...")
    executor = TaskExecutor(adb, matcher)
    
    print("\n" + "=" * 50)
    print("初始化完成，开始执行任务")
    print("=" * 50 + "\n")
    
    # 执行所有任务
    executor.execute_all_tasks()
    
    print("\n" + "=" * 50)
    print("任务执行完毕")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
