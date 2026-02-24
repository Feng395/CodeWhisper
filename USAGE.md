# CodeWhisper 使用指南

## 快速开始

### 1. GUI 模式（推荐）

启动应用：
```bash
python app.py
```

#### Mac 菜单栏应用

点击菜单栏的 🎙️ 图标开始使用。

**快捷键**：
- `Command + M` 开始/停止录音

**退出应用**：
- 在终端按 `Ctrl+C` 优雅退出

#### Windows 悬浮球应用

启动后会出现桌面悬浮球：
- 点击开始录音，再次点击停止录音
- 转写完成后自动复制到剪贴板

**退出应用**：
- 在终端按 `Ctrl+C` 优雅退出

---

### 2. 命令行模式（转录音频文件）

直接转录已有的音频文件：

```bash
# 基本用法
python app.py -f audio.wav

# 指定模型大小
python app.py -f audio.mp3 --model base

# 指定语言
python app.py -f audio.m4a --language en

# 查看帮助
python app.py --help
```

**支持的音频格式**：wav, mp3, m4a, flac, ogg 等

**可选参数**：
- `-f, --file`：音频文件路径（必需）
- `-m, --model`：模型大小，可选 tiny/base/small/medium/large（默认：small）
- `-l, --language`：语言代码（默认：zh）

**示例输出**：
```
🎵 加载音频文件: test.wav
📦 使用模型: small
🔍 📚 加载字典管理器
...
📝 转录结果:
帮我用双指针解决这个 LeetCode 题目

词典修正统计:
  总规则数: 156
  修正次数: 1

修正详情:
  1. '力扣' -> 'LeetCode' (platform)
```

---

## 常见问题

### Windows 音频设备问题

如果遇到 "Error querying device -1" 错误：

1. 检查麦克风是否已连接
2. Windows 设置 > 隐私 > 麦克风 > 允许应用访问麦克风
3. 在设备管理器中检查音频设备状态
4. 在 Windows 声音设置中设置默认录音设备

### 模型配置

- Mac 默认使用 `medium` 模型
- Windows 默认使用 `small` 模型
- 命令行模式默认使用 `small` 模型

可以通过修改代码或命令行参数更改模型大小。

