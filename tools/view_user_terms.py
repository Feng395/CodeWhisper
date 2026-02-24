#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看用户术语库和高频词统计

使用方法:
    python tools/view_user_terms.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CodeWhisper.prompt_engine import PromptEngine


def format_datetime(iso_string):
    """格式化时间字符串"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string


def view_user_terms():
    """查看用户术语库"""
    print("=" * 70)
    print("CodeWhisper 用户术语库查看工具")
    print("=" * 70)
    
    # 初始化引擎
    try:
        engine = PromptEngine()
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return
    
    # 获取统计信息
    stats = engine.get_stats()
    
    print(f"\n📊 统计信息:")
    print(f"  通用术语数: {stats['base_terms_count']}")
    print(f"  用户术语数: {stats['user_terms_count']}")
    print(f"  高频术语数: {stats['qualified_user_terms']} (频次 >= {engine.config.get('user_term_min_freq', 3)})")
    
    # 显示当前提示词
    print(f"\n💡 当前提示词:")
    print(f"  {stats['current_prompt']}")
    
    # 显示用户术语列表
    if not engine.user_dict:
        print("\n⚠️  用户术语库为空")
        print("   提示：多次使用后会自动学习你常用的术语")
        return
    
    # 按频次排序
    sorted_terms = sorted(
        engine.user_dict,
        key=lambda x: (x.get('freq', 0), x.get('last_used', '')),
        reverse=True
    )
    
    print(f"\n📈 用户术语排行 (共 {len(sorted_terms)} 个):")
    print("-" * 70)
    print(f"{'排名':<6} {'术语':<20} {'频次':<8} {'最后使用时间':<20}")
    print("-" * 70)
    
    min_freq = engine.config.get('user_term_min_freq', 3)
    
    for i, term_data in enumerate(sorted_terms, 1):
        term = term_data.get('term', '')
        freq = term_data.get('freq', 0)
        last_used = term_data.get('last_used', '')
        
        # 高频术语标记
        marker = "⭐" if freq >= min_freq else "  "
        
        formatted_time = format_datetime(last_used)
        
        print(f"{marker} {i:<4} {term:<20} {freq:<8} {formatted_time:<20}")
    
    print("-" * 70)
    print(f"\n说明:")
    print(f"  ⭐ 标记的术语会被加入提示词，提高识别准确率")
    print(f"  频次阈值: {min_freq} (可在 config/base_config.json 中调整)")
    
    # 显示配置信息
    print(f"\n⚙️  配置参数:")
    print(f"  提示词总术语数: {engine.config.get('prompt_total_terms', 10)}")
    print(f"  通用术语数: {engine.config.get('prompt_base_terms', 5)}")
    print(f"  个性化术语数: {engine.config.get('prompt_total_terms', 10) - engine.config.get('prompt_base_terms', 5)}")
    print(f"  最低频次要求: {min_freq}")
    print(f"  最大用户术语数: {engine.config.get('max_user_terms', 20)}")
    
    # 显示文件路径
    user_dict_path = Path(__file__).parent.parent / engine.config.get('user_dict_path', 'config/user_dict.json')
    print(f"\n📁 用户词库文件:")
    print(f"  {user_dict_path}")
    
    print("\n" + "=" * 70)


def export_user_terms():
    """导出用户术语库为 CSV"""
    try:
        engine = PromptEngine()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    if not engine.user_dict:
        print("⚠️  用户术语库为空，无法导出")
        return
    
    # 按频次排序
    sorted_terms = sorted(
        engine.user_dict,
        key=lambda x: x.get('freq', 0),
        reverse=True
    )
    
    # 导出为 CSV
    output_file = "user_terms_export.csv"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("排名,术语,频次,最后使用时间\n")
        for i, term_data in enumerate(sorted_terms, 1):
            term = term_data.get('term', '')
            freq = term_data.get('freq', 0)
            last_used = format_datetime(term_data.get('last_used', ''))
            f.write(f"{i},{term},{freq},{last_used}\n")
    
    print(f"✅ 已导出到: {output_file}")


def reset_user_terms():
    """重置用户术语库"""
    confirm = input("⚠️  确认要重置用户术语库吗？所有学习数据将被清空 (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("已取消")
        return
    
    try:
        engine = PromptEngine()
        user_dict_path = Path(__file__).parent.parent / engine.config.get('user_dict_path', 'config/user_dict.json')
        
        # 清空用户词库
        with open(user_dict_path, 'w', encoding='utf-8') as f:
            json.dump({"terms": []}, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 用户术语库已重置")
        print(f"   文件: {user_dict_path}")
    except Exception as e:
        print(f"❌ 重置失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            export_user_terms()
        elif command == "reset":
            reset_user_terms()
        else:
            print(f"未知命令: {command}")
            print("\n可用命令:")
            print("  python tools/view_user_terms.py         # 查看用户术语")
            print("  python tools/view_user_terms.py export  # 导出为 CSV")
            print("  python tools/view_user_terms.py reset   # 重置用户术语库")
    else:
        view_user_terms()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
