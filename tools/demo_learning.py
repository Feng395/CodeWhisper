#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
演示自主学习机制

模拟多次使用后的学习效果
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CodeWhisper.prompt_engine import PromptEngine


def simulate_learning():
    """模拟学习过程"""
    print("=" * 70)
    print("CodeWhisper 自主学习机制演示")
    print("=" * 70)
    
    # 初始化引擎
    engine = PromptEngine()
    
    print("\n📝 初始状态:")
    print(f"  提示词: {engine.build_prompt()}")
    
    # 模拟使用场景
    scenarios = [
        # 场景1：模具加工（5次）
        {
            "name": "模具加工场景",
            "times": 5,
            "terms": {"模具", "慢丝割一刀", "线切割"}
        },
        # 场景2：快丝加工（3次）
        {
            "name": "快丝加工场景",
            "times": 3,
            "terms": {"模具", "快丝", "线切割"}
        },
        # 场景3：修刀工艺（4次）
        {
            "name": "修刀工艺场景",
            "times": 4,
            "terms": {"慢丝割一修一", "慢丝割一修二", "模具"}
        },
        # 场景4：中丝加工（2次）
        {
            "name": "中丝加工场景",
            "times": 2,
            "terms": {"中丝", "中丝割一修一", "模具"}
        }
    ]
    
    base_time = datetime.now()
    
    print("\n🎬 开始模拟使用...")
    print("-" * 70)
    
    for scenario in scenarios:
        name = scenario["name"]
        times = scenario["times"]
        terms = scenario["terms"]
        
        print(f"\n场景: {name} (使用 {times} 次)")
        print(f"  涉及术语: {', '.join(terms)}")
        
        for i in range(times):
            # 模拟时间推移
            current_time = base_time + timedelta(hours=i)
            
            # 更新术语（模拟检测到的术语）
            engine.update_user_terms(terms)
            
            print(f"  第 {i+1} 次使用完成")
    
    print("\n" + "-" * 70)
    print("\n✅ 模拟完成！")
    
    # 显示学习结果
    print("\n📊 学习结果:")
    
    # 按频次排序
    sorted_terms = sorted(
        engine.user_dict,
        key=lambda x: x.get('freq', 0),
        reverse=True
    )
    
    print(f"\n用户术语库 (共 {len(sorted_terms)} 个):")
    for i, term_data in enumerate(sorted_terms, 1):
        term = term_data.get('term', '')
        freq = term_data.get('freq', 0)
        marker = "⭐" if freq >= engine.config.get('user_term_min_freq', 3) else "  "
        print(f"{marker} {i}. {term}: {freq}次")
    
    # 显示优化后的提示词
    print(f"\n💡 优化后的提示词:")
    print(f"  {engine.build_prompt()}")
    
    # 对比
    print(f"\n📈 效果对比:")
    print(f"  初始提示词: 工业模具行业从业者：模具、线切割、慢丝、快丝、中丝、提测、联调、排期、上线、复盘。")
    print(f"  优化提示词: {engine.build_prompt()}")
    
    print("\n说明:")
    print("  ⭐ 标记的术语已达到频次阈值，会被优先加入提示词")
    print("  提示词会根据你的使用习惯动态调整，提高识别准确率")
    
    print("\n" + "=" * 70)
    
    # 询问是否保存
    save = input("\n是否保存模拟的学习数据? (y/n): ").strip().lower()
    if save == 'y':
        engine._save_user_dict()
        print("✅ 已保存到 config/user_dict.json")
        print("   运行 'python tools/view_user_terms.py' 查看详情")
    else:
        print("未保存，模拟数据已丢弃")


def main():
    try:
        simulate_learning()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
