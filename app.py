"""
CodeWhisper - 为中文社区开发者设计的语音转文字工具
"""

import os
import platform
import sys

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main() -> None:
    system = platform.system()

    if system == "Darwin":
        from gui.mac_menu_bar_app import main as mac_main

        mac_main()
    elif system == "Windows":
        from gui.win_floating_ball_app import main as win_main

        win_main()
    else:
        raise SystemExit(f"Unsupported platform: {system}. 目前只支持Mac和Windows❤")


if __name__ == "__main__":
    sys.exit(main())
