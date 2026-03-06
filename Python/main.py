"""
ADB模拟器自动连接工具
"""
import sys
from pathlib import Path

# 添加Python目录到路径
python_dir = Path(__file__).parent
sys.path.insert(0, str(python_dir))

from adb.adb_controller import ADBController


def main():
    """主函数"""
    print("=" * 50)
    print("ADB模拟器自动连接工具")
    print("=" * 50)
    
    # 初始化ADB控制器
    print("\n[1/2] 初始化ADB控制器...")
    adb = ADBController()
    
    # 启动模拟器
    print("[2/2] 检查并启动MuMu模拟器...")
    if not adb.start_emulator():
        print("警告: 模拟器启动失败，尝试连接现有设备...")
    
    # 连接设备
    print("\n连接设备...")
    if not adb.connect():
        print("\n错误: 无法连接到设备，请检查:")
        print("  - MuMu模拟器是否已启动")
        print("  - ADB工具是否正确配置")
        print("  - config/adb_config.json中的配置是否正确")
        return
    
    print("\n✓ 设备连接成功!")
    
    # 获取屏幕尺寸
    width, height = adb.get_screen_size()
    if width and height:
        print(f"✓ 屏幕尺寸: {width}x{height}")
    
    print("\n" + "=" * 50)
    print("模拟器已就绪")
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
