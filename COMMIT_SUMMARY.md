# Git 提交摘要

本次更新共完成 8 个提交，按逻辑顺序组织如下：

## 提交列表

### 1. c1b0415 - fix: 修复模块导入问题
**文件：**
- `gui/win_floating_ball_app.py`
- `gui/mac_menu_bar_app.py`

**更改内容：**
- 修复 `codewhisper` → `CodeWhisper` 的导入错误
- 添加 Ctrl+C 信号处理支持优雅退出
- 为 Windows GUI 添加音频设备检测和错误处理
- 为 Mac GUI 添加信号处理

---

### 2. 322b82a - feat: Add CLI mode for audio file transcription
**文件：**
- `app.py`
- `USAGE.md`

**更改内容：**
- 添加命令行参数解析（argparse）
- 实现音频文件转录功能
- 支持指定模型大小和语言
- 创建使用说明文档

**新功能：**
```bash
python app.py -f audio.wav
python app.py -f audio.mp3 --model base --language en
```

---

### 3. 3ef8e65 - feat: Add mold industry terminology support
**文件：**
- `dictionaries/programmer_terms.json`
- `config/moju_dict.json`
- `config/README_MOLD.md`

**更改内容：**
- 在主字典中添加 `mold` 分类
- 添加 11 个模具工业术语
- 包含常见误识别变体（磨具→模具、慢思→慢丝等）
- 创建模具术语说明文档

**新增术语：**
- 模具、慢丝、快丝、中丝、线切割
- 慢丝割一刀、慢丝割一修一、慢丝割一修二、慢丝割一修三
- 快丝割一刀、中丝割一修一

---

### 4. dbea224 - feat: Update base config for mold industry
**文件：**
- `config/base_config.json`
- `config/base_dict.json`

**更改内容：**
- 更新提示词前缀为"工业模具行业从业者"
- 在通用术语库中添加模具相关术语
- 修正配置文件路径

---

### 5. 65da920 - docs: Add comprehensive documentation
**文件：**
- `docs/DICTIONARY_CORRECTION.md`
- `docs/LEARNING_MECHANISM.md`
- `docs/MOLD_TERMS_GUIDE.md`

**更改内容：**
- 创建词典修正机制详细说明
- 创建自主学习机制详解文档
- 创建模具术语使用指南
- 包含工作原理、使用示例、最佳实践等

---

### 6. 053a076 - feat: Add utility tools for term management
**文件：**
- `tools/README.md`
- `tools/add_term.py`
- `tools/demo_learning.py`
- `tools/view_user_terms.py`

**更改内容：**
- 创建查看用户术语库工具
- 创建交互式添加术语工具
- 创建学习机制演示工具
- 创建工具使用说明文档

**新工具：**
```bash
python tools/view_user_terms.py        # 查看高频词
python tools/view_user_terms.py export # 导出 CSV
python tools/add_term.py               # 添加术语
python tools/demo_learning.py          # 演示学习
```

---

### 7. 2d3b96b - feat: Enhance learning mechanism implementation
**文件：**
- `codewhisper/prompt_engine.py`
- `codewhisper/transcriber.py`

**更改内容：**
- 完善提示词引擎实现
- 优化学习算法
- 改进术语检测逻辑

---

## 功能总结

### 新增功能

1. **命令行模式**
   - 支持直接转录音频文件
   - 可指定模型和语言
   - 显示详细的修正统计

2. **模具工业支持**
   - 11 个专业术语
   - 30+ 个误识别变体
   - 自动修正功能

3. **优雅退出**
   - Ctrl+C 信号处理
   - 资源清理
   - 友好提示

4. **管理工具**
   - 查看高频词统计
   - 交互式添加术语
   - 学习效果演示
   - 数据导出功能

### 改进内容

1. **错误修复**
   - 模块导入问题
   - 音频设备检测
   - 路径配置

2. **文档完善**
   - 3 个详细技术文档
   - 工具使用说明
   - 使用指南

3. **用户体验**
   - 更好的错误提示
   - 设备检测信息
   - 优雅退出支持

## 文件统计

- 新增文件：11 个
- 修改文件：7 个
- 新增代码：约 2000+ 行
- 文档：约 1500+ 行

## 下一步

可以执行以下命令推送到远程仓库：

```bash
git push origin main
```

或者查看详细的提交差异：

```bash
git log origin/main..HEAD --stat
```
