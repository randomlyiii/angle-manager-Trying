"""ADB模拟器自动连接工具"""
from adb.adb_controller import ADBController


def main():
    """主函数"""
    adb = ADBController()
    adb.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
