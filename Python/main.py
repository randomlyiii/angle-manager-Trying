"""ADB模拟器自动连接工具"""
from adb.adb_controller import ADBController
from running.window_manager import WindowManager
from logic.logic_controller import LogicController


def main():
    """主函数"""
    adb = ADBController()
    
    # 运行启动流程
    if not adb.run():
        return
    
    # # 检查并切换到游戏窗口
    # window_mgr = WindowManager(adb)
    # window_mgr.ensure_game_window()
    
    # 检查并同意条例
    logic = LogicController(adb)
    logic.check_and_accept_regulation()
    
    print("\n游戏启动流程完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
