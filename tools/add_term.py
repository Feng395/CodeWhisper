#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速添加术语工具

使用方法:
    python tools/add_term.py

交互式添加新术语到字典
"""

import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def list_categories(data):
    """列出所有分类"""
    print("\n可用的分类:")
    for i, (key, value) in enumerate(data['categories'].items(), 1):
        name = value.get('name', key)
        desc = value.get('description', '')
        print(f"  {i}. {key} - {name}")
        if desc:
            print(f"     {desc}")
    return list(data['categories'].keys())


def add_term_interactive():
    """交互式添加术语"""
    dict_file = 'dictionaries/programmer_terms.json'
    
    if not os.path.exists(dict_file):
        print(f"❌ 字典文件不存在: {dict_file}")
        return
    
    # 读取字典
    with open(dict_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("CodeWhisper 术语添加工具")
    print("=" * 60)
    
    # 选择分类
    categories = list_categories(data)
    
    while True:
        category_input = input("\n请选择分类编号或输入分类名称 (q 退出): ").strip()
        
        if category_input.lower() == 'q':
            print("已取消")
            return
        
        # 尝试作为编号
        try:
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category = categories[idx]
                break
        except ValueError:
            pass
        
        # 尝试作为分类名
        if category_input in categories:
            category = category_input
            break
        
        print("❌ 无效的分类，请重新输入")
    
    print(f"\n✓ 选择的分类: {category}")
    
    # 输入术语信息
    correct = input("\n请输入正确的术语: ").strip()
    if not correct:
        print("❌ 术语不能为空")
        return
    
    description = input("请输入术语描述: ").strip()
    
    # 输入错误变体
    variants = []
    print("\n请输入可能的错误识别形式 (每行一个，输入空行结束):")
    
    while True:
        wrong = input("  错误形式: ").strip()
        if not wrong:
            break
        
        reason = input("  错误原因: ").strip() or "误识别"
        
        variants.append({
            "wrong": wrong,
            "description": reason
        })
        
        print(f"  ✓ 已添加: {wrong} → {correct}")
    
    if not variants:
        print("\n⚠️  未添加任何错误变体，术语将不会进行修正")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    
    # 构建术语数据
    term_data = {
        "correct": correct,
        "description": description,
        "variants": variants
    }
    
    # 显示预览
    print("\n" + "=" * 60)
    print("术语预览:")
    print("=" * 60)
    print(f"分类: {category}")
    print(f"术语: {correct}")
    print(f"描述: {description}")
    if variants:
        print("错误变体:")
        for v in variants:
            print(f"  - {v['wrong']} ({v['description']})")
    print("=" * 60)
    
    # 确认
    confirm = input("\n确认添加? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 添加到字典
    if correct in data['categories'][category]['terms']:
        print(f"\n⚠️  术语 '{correct}' 已存在，将被覆盖")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    
    data['categories'][category]['terms'][correct] = term_data
    
    # 保存
    with open(dict_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 成功添加术语 '{correct}' 到分类 '{category}'")
    print(f"总规则数: {sum(len(term.get('variants', [])) for cat in data['categories'].values() for term in cat['terms'].values())}")


def main():
    try:
        add_term_interactive()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
