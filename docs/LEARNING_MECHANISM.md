# 自主学习机制详解

## 概述

CodeWhisper 实现了智能的自主学习机制，能够：
1. 检测你常用的术语
2. 构建个人词库
3. 动态识别你的专业方向
4. 持续优化识别率

## 工作原理

### 整体流程

```
语音输入 → Whisper识别 → 词典修正 → 术语检测 → 更新用户词库 → 优化提示词
   ↓                                                              ↑
   └──────────────────── 下次使用更优的提示词 ──────────────────────┘
```

### 核心组件

#### 1. PromptEngine (提示词引擎)

位置：`CodeWhisper/prompt_engine.py`

功能：
- 维护通用术语库（base_dict）
- 维护个性化术语库（user_dict）
- 根据使用频次动态构建最优提示词
- 自动淘汰低频术语

#### 2. DictionaryManager (词典管理器)

位置：`CodeWhisper/dict_manager.py`

功能：
- 检测转录文本中的术语
- 从修正记录中提取术语
- 提供术语统计信息

## 学习过程详解

### 第一步：术语检测

每次转录完成后，系统会通过两种方式检测术语：

#### 方法 1：从修正记录中获取（优先，更精准）

```python
# 例如：修正了 "磨具" → "模具"
detected_terms = dict_manager.get_detected_terms_from_corrections()
# 结果：{'模具'}
```

这种方法最准确，因为用户确实说了这个术语（虽然被误识别了）。

#### 方法 2：从最终文本中检测（补充）

```python
# 在转录文本中查找字典中的所有术语
detected_terms = dict_manager.detect_terms_in_text(result["text"])
# 例如文本："使用慢丝割一刀加工模具"
# 结果：{'慢丝割一刀', '模具'}
```

### 第二步：更新用户词库

检测到的术语会更新到用户词库：

```python
prompt_engine.update_user_terms(detected_terms)
```

#### 用户词库结构

文件位置：`config/user_dict.json`

```json
{
  "terms": [
    {
      "term": "模具",
      "freq": 15,
      "last_used": "2024-02-24T10:30:00"
    },
    {
      "term": "慢丝割一刀",
      "freq": 8,
      "last_used": "2024-02-24T10:25:00"
    },
    {
      "term": "线切割",
      "freq": 5,
      "last_used": "2024-02-23T15:20:00"
    }
  ]
}
```

#### 更新规则

1. **术语已存在**：
   - `freq` 频次 +1
   - `last_used` 更新为当前时间

2. **术语不存在**：
   - 添加新术语
   - `freq` 初始化为 1
   - `last_used` 设为当前时间

3. **容量控制**：
   - 最多保留 20 个术语（可配置）
   - 按频次和最后使用时间排序
   - 自动淘汰低频术语

### 第三步：构建优化的提示词

基于用户词库，动态构建下次转录使用的提示词：

```python
prompt = prompt_engine.build_prompt()
```

#### 提示词构建策略

配置文件：`config/base_config.json`

```json
{
  "prompt_prefix": "工业模具行业从业者：",
  "prompt_total_terms": 10,
  "prompt_base_terms": 5,
  "user_term_min_freq": 3,
  "max_user_terms": 20
}
```

#### 构建算法

1. **取通用术语**（5个）：
   ```
   从 base_dict 取前 5 个固定术语
   例如：提测、联调、排期、上线、复盘
   ```

2. **取个性化术语**（5个）：
   ```
   从 user_dict 取频次 >= 3 的高频术语
   按 freq DESC, last_used DESC 排序
   例如：模具、慢丝割一刀、线切割、快丝、中丝
   ```

3. **补齐不足**：
   ```
   如果个性化术语不足 5 个，用 base_dict 后续术语补齐
   ```

4. **拼接成提示词**：
   ```
   工业模具行业从业者：提测、联调、排期、上线、复盘、模具、慢丝割一刀、线切割、快丝、中丝。
   ```

### 第四步：下次转录使用优化的提示词

Whisper 在转录时会参考提示词，提高相关术语的识别准确率。

## 高频词体现

### 1. 频次统计

在 `config/user_dict.json` 中：

```json
{
  "term": "模具",
  "freq": 15,  // ← 这里就是频次
  "last_used": "2024-02-24T10:30:00"
}
```

### 2. 查看高频词

#### 方法 1：直接查看文件

```bash
cat config/user_dict.json
```

#### 方法 2：使用 Python 脚本

```python
from CodeWhisper.prompt_engine import PromptEngine

engine = PromptEngine()
stats = engine.get_stats()

print(f"用户术语数: {stats['user_terms_count']}")
print(f"高频术语数: {stats['qualified_user_terms']}")
print(f"当前提示词: {stats['current_prompt']}")

# 查看所有用户术语（按频次排序）
sorted_terms = sorted(
    engine.user_dict,
    key=lambda x: x['freq'],
    reverse=True
)

print("\n高频术语排行:")
for i, term in enumerate(sorted_terms[:10], 1):
    print(f"{i}. {term['term']}: {term['freq']}次")
```

#### 方法 3：创建查看工具

我会为你创建一个专门的工具来查看高频词。

## 配置参数说明

### config/base_config.json

```json
{
  "prompt_prefix": "工业模具行业从业者：",
  // 提示词前缀，描述你的专业领域
  
  "user_dict_path": "config/user_dict.json",
  // 用户词库文件路径
  
  "base_dict_path": "config/base_dict.json",
  // 通用术语库文件路径
  
  "max_user_terms": 20,
  // 用户词库最大容量
  
  "prompt_total_terms": 10,
  // 提示词中总术语数
  
  "prompt_base_terms": 5,
  // 提示词中通用术语数
  
  "user_term_min_freq": 3
  // 术语进入提示词的最低频次
}
```

### 参数调优建议

1. **prompt_total_terms**：
   - 太少：覆盖不全
   - 太多：可能影响识别速度
   - 推荐：8-12

2. **user_term_min_freq**：
   - 太低：低频词干扰
   - 太高：新术语难进入
   - 推荐：2-5

3. **max_user_terms**：
   - 太少：学习能力受限
   - 太多：淘汰不及时
   - 推荐：15-30

## 学习效果示例

### 初次使用

```
提示词: 计算机行业从业者：提测、联调、排期、上线、复盘、接口、缓存、数据库、日志、MySQL。

转录: "我需要一个磨具来做慢思割一道"
修正: "我需要一个模具来做慢丝割一刀"
检测术语: {模具, 慢丝割一刀}
```

### 使用 5 次后

```
用户词库:
- 模具: 5次
- 慢丝割一刀: 4次
- 线切割: 3次

提示词: 工业模具行业从业者：提测、联调、排期、上线、复盘、模具、慢丝割一刀、线切割、快丝、中丝。
```

### 使用 20 次后

```
用户词库:
- 模具: 20次
- 慢丝割一刀: 15次
- 线切割: 12次
- 快丝: 8次
- 中丝: 6次
- 慢丝割一修一: 5次

提示词: 工业模具行业从业者：提测、联调、模具、慢丝割一刀、线切割、快丝、中丝、慢丝割一修一、排期、上线。

识别准确率显著提升！
```

## 优势

1. **自动适应**：无需手动配置，自动学习你的专业方向
2. **持续优化**：使用越多，识别越准确
3. **动态调整**：自动淘汰不常用的术语
4. **轻量高效**：只保留高频术语，不占用过多资源

## 局限性

1. **需要积累**：初期效果不明显，需要一定使用量
2. **依赖字典**：只能学习字典中已有的术语
3. **频次阈值**：低频术语可能被忽略

## 最佳实践

1. **持续使用**：多次使用才能建立有效的个人词库
2. **完善字典**：及时添加新术语到主字典
3. **定期查看**：检查用户词库，了解学习效果
4. **调整配置**：根据实际情况调整参数

## 隐私说明

- 所有数据存储在本地
- 不会上传到任何服务器
- 用户词库文件可以随时删除重置
