# 词典修正机制说明

## 工作原理

CodeWhisper 的词典修正机制通过预定义的错误变体（variants）来识别和修正语音识别中的常见错误。

### 修正流程

```
语音输入 → Whisper 识别 → 词典修正 → 最终结果
   "磨具"  →    "磨具"    →   "模具"   →  "模具"
```

## 词典结构

词典文件位于 `dictionaries/programmer_terms.json`，采用以下结构：

```json
{
  "categories": {
    "mold": {
      "name": "模具术语",
      "description": "模具工业领域的专业术语",
      "terms": {
        "模具": {
          "correct": "模具",
          "description": "制造业中用于成型产品的工具",
          "variants": [
            {
              "wrong": "磨具",
              "description": "同音误识别，最常见"
            },
            {
              "wrong": "摸具",
              "description": "音韵误识别"
            }
          ]
        }
      }
    }
  }
}
```

## 修正规则

### 1. 基于正则表达式匹配

- 短词（≤3字符）：使用边界匹配，避免子串误匹配
  - 例如：`TPR` 不会匹配 `TPRS`
  
- 长词：灵活匹配，支持格式不固定的内容
  - 例如：`Spring Boot` 可以匹配 `Spring Boat`

### 2. 优先级排序

按错误文本长度降序排序，先匹配长的术语，避免短词覆盖长词：

```
"慢丝割一刀" (5字) → 优先匹配
"慢丝" (2字)       → 后匹配
```

### 3. 防止重复替换

已替换的文本位置会被标记，避免同一位置被多次替换。

## 添加新术语

### 方法 1：直接编辑 JSON 文件

编辑 `dictionaries/programmer_terms.json`，在相应分类下添加术语：

```json
{
  "术语名称": {
    "correct": "正确形式",
    "description": "术语说明",
    "variants": [
      {
        "wrong": "错误形式1",
        "description": "错误原因"
      },
      {
        "wrong": "错误形式2",
        "description": "错误原因"
      }
    ]
  }
}
```

### 方法 2：使用 Python 脚本

```python
import json

# 读取字典
with open('dictionaries/programmer_terms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 添加新术语
data['categories']['mold']['terms']['新术语'] = {
    "correct": "新术语",
    "description": "术语说明",
    "variants": [
        {"wrong": "错误形式", "description": "错误原因"}
    ]
}

# 保存
with open('dictionaries/programmer_terms.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 常见误识别类型

### 1. 同音字

- 模具 → 磨具
- 慢丝 → 慢思
- 一刀 → 一道

### 2. 音韵相近

- 模具 → 摸具、膜具
- 线切割 → 线切个、线切格

### 3. 数字与中文

- 一修一 → 一修1、1修一、1修1
- 一刀 → 1刀

## 测试修正效果

创建测试脚本：

```python
from CodeWhisper.dict_manager import DictionaryManager

dict_manager = DictionaryManager()

# 测试
input_text = "我需要一个磨具"
result = dict_manager.fix_text(input_text)
print(f"输入: {input_text}")
print(f"输出: {result}")
print(f"修正: {dict_manager.corrections}")
```

## 最佳实践

1. **收集真实错误**：记录实际使用中的识别错误
2. **优先级排序**：常见错误优先添加
3. **避免过度匹配**：确保不会误伤正确的词
4. **定期更新**：根据使用反馈持续优化
5. **分类管理**：按领域分类，便于维护

## 性能考虑

- 规则数量：当前支持 300+ 规则
- 匹配速度：使用正则表达式，性能良好
- 内存占用：字典加载到内存，占用很小

## 局限性

1. **需要预定义**：只能修正字典中已记录的错误
2. **上下文无关**：不考虑语义，纯文本替换
3. **顺序依赖**：复杂情况可能需要调整规则顺序

## 未来改进方向

1. **智能学习**：自动学习用户的常见错误
2. **上下文感知**：结合语义进行更智能的修正
3. **动态更新**：支持运行时添加新规则
4. **统计分析**：分析最常见的错误类型
