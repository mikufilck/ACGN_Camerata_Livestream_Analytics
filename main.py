import os
import sys
import ctypes
import platform
import pandas as pd
import warnings

# ================= 强力静音区 =================
# 1. 关闭 CoW 警告
pd.options.mode.copy_on_write = False
# 2. 关闭赋值警告
pd.options.mode.chained_assignment = None
# 3. 过滤所有 FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# ============================================

# =========================================================================
# 1. 环境路径锚定 (防止相对路径错误)
# =========================================================================
# 获取 main.py 所在的绝对路径 (项目根目录)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 将根目录加入 Python 搜索路径，确保能 import src
sys.path.append(PROJECT_ROOT)


def setup_environment():
    """
    [系统初始化]
    自动检测并创建缺失的目录结构，确保程序即开即用。
    """
    print(f">>> 正在初始化运行环境...")
    print(f"    项目根目录: {PROJECT_ROOT}")

    # 需要预先存在的目录结构
    required_dirs = [
        os.path.join(PROJECT_ROOT, "config"),
        os.path.join(PROJECT_ROOT, "data", "streamers"),
        os.path.join(PROJECT_ROOT, "output"),
        os.path.join(PROJECT_ROOT, "logs")  # 预留给系统日志
    ]

    for d in required_dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d, exist_ok=True)
                print(f"    [+] 创建目录: {d}")
            except Exception as e:
                print(f"    [!] 创建目录失败 {d}: {e}")
                sys.exit(1)

    # Windows 高分屏 (High-DPI) 适配
    # 让字体和图标在缩放设置下不模糊
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            print("    [+] Windows High-DPI 适配已启用")
        except Exception:
            pass


def run_gui():
    """
    [启动入口] 拉起 GUI 主程序
    """
    try:
        # 延迟导入，确保环境 setup 之后再加载依赖
        import customtkinter as ctk
        from src.ui.app import App

        print(">>> 启动图形界面 (GUI)...")

        # 设置全局外观
        ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        app = App()
        app.mainloop()

    except ImportError as e:
        print("\n" + "=" * 50)
        print("❌ 启动失败: 缺少必要依赖库")
        print(f"错误详情: {e}")
        print("-" * 50)
        print("请在终端运行以下命令安装依赖:")
        print("pip install customtkinter pandas matplotlib mplcursors wordcloud jieba")
        print("=" * 50 + "\n")
        input("按 Enter 键退出...")  # 暂停防止窗口秒关

    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ 程序发生未知崩溃")
        print("-" * 50)
        import traceback
        traceback.print_exc()
        print("=" * 50 + "\n")
        input("按 Enter 键退出...")


if __name__ == "__main__":
    setup_environment()
    run_gui()