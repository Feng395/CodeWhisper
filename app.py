"""
CodeWhisper - 为中文社区开发者设计的语音转文字工具
"""

import argparse
import os
import platform
import sys

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def transcribe_file(audio_file: str, model: str = "small", language: str = "zh") -> None:
    """转录音频文件"""
    from CodeWhisper.transcriber import CodeWhisper
    
    if not os.path.exists(audio_file):
        print(f"❌ 文件不存在: {audio_file}")
        sys.exit(1)
    
    print(f"🎵 加载音频文件: {audio_file}")
    print(f"📦 使用模型: {model}")
    
    whisper = CodeWhisper(model_name=model)
    result = whisper.transcribe(
        audio_file,
        language=language,
        fix_programmer_terms=True,
        verbose=True
    )
    
    text = result.get("text", "")
    print(f"\n📝 转录结果:\n{text}\n")
    
    # 显示词典修正统计
    stats = whisper.get_dict_stats()
    corrections = whisper.dict_manager.get_corrections()
    
    print("词典修正统计:")
    print(f"  总规则数: {stats.get('total_rules')}")
    print(f"  修正次数: {stats.get('replacements_made')}")
    
    if corrections:
        print("\n修正详情:")
        for i, correction in enumerate(corrections, 1):
            wrong = correction.get('wrong', '')
            correct = correction.get('correct', '')
            category = correction.get('category', 'unknown')
            print(f"  {i}. '{wrong}' -> '{correct}' ({category})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CodeWhisper - 语音转文字工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  启动 GUI:
    python app.py
  
  转录音频文件:
    python app.py -f audio.wav
    python app.py --file audio.mp3 --model base
    python app.py -f audio.m4a --language en
        """
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="音频文件路径 (支持 wav, mp3, m4a 等格式)"
    )
    
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型大小 (默认: small)"
    )
    
    parser.add_argument(
        "-l", "--language",
        type=str,
        default="zh",
        help="音频语言代码 (默认: zh)"
    )
    
    args = parser.parse_args()
    
    # 如果指定了文件，则进行文件转录
    if args.file:
        transcribe_file(args.file, args.model, args.language)
        return
    
    # 否则启动 GUI
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
