# CodeWhisper 工具集

本目录包含了一系列实用工具，帮助你管理术语、查看学习效果和优化识别率。

## 工具列表

### 1. 查看用户术语库

查看自主学习的高频词和统计信息。

```bash
# 查看用户术语和高频词
python tools/view_user_terms.py

# 导出为 CSV 文件
python tools/view_user_terms.py export

# 重置用户术语库
python tools/view_user_terms.py reset
```

**输出示例：**
```
📊 统计信息:
  通用术语数: 19
  用户术语数: 8
  高频术语数: 6 (频次 >= 3)

💡 当前提示词:
  工业模具行业从业者：模具、线切割、慢丝、快丝、中丝、慢丝割一刀、慢丝割一修一、慢丝割一修二。

📈 用户术语排行 (共 8 个):
排名   术语                   频次     最后使用时间        
----------------------------------------------------------------------
⭐ 1    模具                   14       2024-02-24 10:30:00
⭐ 2    线切割                 8        2024-02-24 10:25:00
⭐ 3    慢丝割一刀             5        2024-02-24 10:20:00
```

### 2. 添加新术语

交互式添加新术语到字典。

```bash
python tools/add_term.py
```

**使用流程：**
1. 选择术语分类（如 mold、work_terms 等）
2. 输入正确的术语
3. 输入术语描述
4. 添加可能的错误识别形式
5. 确认并保存

### 3. 学习机制演示

演示自主学习的工作过程。

```bash
python tools/demo_learning.py
```

**功能：**
- 模拟多次使用场景
- 展示术语频次累积
- 对比优化前后的提示词
- 可选择保存模拟数据

## 文件说明

### 用户词库文件

**位置：** `config/user_dict.json`

**结构：**
```json
{
  "terms": [
    {
      "term": "模具",
      "freq": 14,
      "last_used": "2024-02-24T10:30:00"
    }
  ]
}
```

**字段说明：**
- `term`: 术语名称
- `freq`: 使用频次（越高越重要）
- `last_used`: 最后使用时间（ISO 格式）

### 配置文件

**位置：** `config/base_config.json`

**参数说明：**
```json
{
  "prompt_prefix": "工业模具行业从业者：",
  // 提示词前缀，描述你的专业领域
  
  "user_dict_path": "config/user_dict.json",
  // 用户词库文件路径
  
  "base_dict_path": "config/base_dict.json",
  // 通用术语库文件路径
  
  "max_user_terms": 20,
  // 用户词库最大容量（超过会自动淘汰低频词）
  
  "prompt_total_terms": 10,
  // 提示词中总术语数
  
  "prompt_base_terms": 5,
  // 提示词中通用术语数（剩余为个性化术语）
  
  "user_term_min_freq": 3
  // 术语进入提示词的最低频次
}
```

## 使用场景

### 场景 1：查看学习效果

使用一段时间后，想了解系统学到了什么：

```bash
python tools/view_user_terms.py
```

### 场景 2：添加专业术语

发现某个专业术语经常被误识别：

```bash
python tools/add_term.py
```

按提示添加术语及其可能的错误形式。

### 场景 3：重置学习数据

切换到新的专业领域，需要重新学习：

```bash
python tools/view_user_terms.py reset
```

### 场景 4：导出数据分析

想分析自己最常用的术语：

```bash
python tools/view_user_terms.py export
```

会生成 `user_terms_export.csv` 文件，可用 Excel 打开。

## 高频词工作原理

### 1. 术语检测

每次转录后，系统会检测文本中的术语：

```python
# 方法1：从修正记录中获取（最准确）
detected_terms = dict_manager.get_detected_terms_from_corrections()

# 方法2：从文本中检测（补充）
detected_terms_from_text = dict_manager.detect_terms_in_text(text)
```

### 2. 频次累积

检测到的术语会更新到用户词库：

```python
prompt_engine.update_user_terms(detected_terms)
```

- 已存在的术语：`freq += 1`
- 新术语：`freq = 1`

### 3. 动态提示词

根据频次构建优化的提示词：

```python
prompt = prompt_engine.build_prompt()
```

**策略：**
1. 取 5 个通用术语（固定）
2. 取 5 个高频个性化术语（freq >= 3）
3. 如果不足，用通用术语补齐

### 4. 自动淘汰

当用户词库超过 20 个术语时：
- 按频次和最后使用时间排序
- 保留前 20 个
- 淘汰低频术语

## 最佳实践

### 1. 定期查看

每周查看一次用户术语库：

```bash
python tools/view_user_terms.py
```

了解学习效果，发现需要优化的地方。

### 2. 及时添加

发现新的误识别，立即添加到字典：

```bash
python tools/add_term.py
```

### 3. 调整配置

根据实际情况调整 `config/base_config.json`：

- 如果高频词太少：降低 `user_term_min_freq`
- 如果提示词太长：减少 `prompt_total_terms`
- 如果淘汰太快：增加 `max_user_terms`

### 4. 导出备份

定期导出用户词库：

```bash
python tools/view_user_terms.py export
```

### 5. 切换领域

切换专业领域时，重置用户词库：

```bash
python tools/view_user_terms.py reset
```

然后修改 `config/base_config.json` 中的 `prompt_prefix`。

## 常见问题

### Q: 为什么用户词库是空的？

A: 用户词库需要通过实际使用来积累。多次使用语音转录后，系统会自动学习你常用的术语。

### Q: 高频词多久会生效？

A: 立即生效。每次转录后，系统会更新用户词库并重新构建提示词，下次转录就会使用新的提示词。

### Q: 如何查看某个术语的频次？

A: 运行 `python tools/view_user_terms.py`，会显示所有术语及其频次。

### Q: 可以手动编辑用户词库吗？

A: 可以，直接编辑 `config/user_dict.json` 文件。但建议使用工具，避免格式错误。

### Q: 频次阈值如何设置？

A: 在 `config/base_config.json` 中调整 `user_term_min_freq`：
- 设为 2：更容易进入提示词，但可能包含低频词
- 设为 5：只有高频词才能进入，更精准但覆盖面小
- 推荐：3-4

## 技术细节

详细的技术说明请参考：

- [自主学习机制详解](../docs/LEARNING_MECHANISM.md)
- [词典修正机制说明](../docs/DICTIONARY_CORRECTION.md)
- [模具术语使用指南](../docs/MOLD_TERMS_GUIDE.md)

## 贡献

欢迎贡献新的工具和改进建议！
