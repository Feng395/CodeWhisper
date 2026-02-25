# CodeWhisper 完整使用指南

## 目录

1. [项目简介](#项目简介)
2. [快速开始](#快速开始)
3. [使用方式](#使用方式)
4. [API 服务](#api-服务)
5. [实时语音输入](#实时语音输入)
6. [术语修正](#术语修正)
7. [自主学习](#自主学习)
8. [部署指南](#部署指南)
9. [常见问题](#常见问题)

---

## 项目简介

**CodeWhisper** 是一款针对中文语境优化的语音转文字工具，支持：

- 🎤 语音转文字
- 🔧 专业术语自动修正
- 🧠 自主学习用户习惯
- 🌐 提供 REST API 接口
- 📦 支持多种部署方式

### 核心特性

✅ **中文优化** - 针对中文语境优化，支持专业术语修正  
✅ **本地运行** - 不依赖网络，保护隐私  
✅ **多平台支持** - Mac 菜单栏应用、Windows 悬浮球应用  
✅ **API 服务** - 提供 REST API，支持外部调用  
✅ **实时转录** - 支持直接输入语音数据  
✅ **自主学习** - 自动学习用户常用术语，持续优化  

---

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-repo/codewhisper.git
cd codewhisper

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 启动 GUI 应用
python app.py

# 启动 API 服务
python api_server.py
```

### 3. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 使用方式

### 1. GUI 模式（推荐）

#### Mac 菜单栏应用

```bash
python app.py
```

**功能：**
- 点击菜单栏 🎙️ 图标开始录音
- 快捷键 `Command + M` 开始/停止录音
- 自动复制转录结果到剪贴板

#### Windows 悬浮球应用

```bash
python app.py
```

**功能：**
- 桌面悬浮球显示状态
- 点击开始/停止录音
- 自动复制转录结果到剪贴板

**退出应用：** 在终端按 `Ctrl+C`

### 2. 命令行模式

转录音频文件：

```bash
# 基本用法
python app.py -f audio.wav

# 指定模型
python app.py -f audio.mp3 --model base

# 指定语言
python app.py -f audio.m4a --language en

# 查看帮助
python app.py --help
```

**支持的音频格式：** wav, mp3, m4a, flac, ogg 等

**参数说明：**
- `-f, --file`：音频文件路径（必需）
- `-m, --model`：模型大小（默认：small）
- `-l, --language`：语言代码（默认：zh）

**输出示例：**
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

## API 服务

CodeWhisper 提供 REST API 接口，支持外部调用。

### 1. 启动 API 服务器

```bash
# 基本启动
python api_server.py

# 指定端口
python api_server.py --port 8080

# 开发模式（自动重载）
python api_server.py --reload

# 预加载模型
python api_server.py --model medium
```

**命令行参数：**

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| --host | 服务器地址 | 0.0.0.0 | --host 127.0.0.1 |
| --port | 端口号 | 8000 | --port 8080 |
| --reload | 自动重载 | False | --reload |
| --model | 模型大小 | small | --model medium |

### 2. API 端点

#### 转录音频文件

**POST /api/transcribe**

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.wav" \
  -F "model=small" \
  -F "language=zh"
```

**Python：**
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/transcribe",
        files={"file": f},
        data={"model": "small", "language": "zh"}
    )

result = response.json()
print(result["text"])
```

**JavaScript：**
```javascript
const formData = new FormData();
formData.append('file', audioFile);
formData.append('model', 'small');

fetch('http://localhost:8000/api/transcribe', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data.text));
```

#### 从 URL 转录

**POST /api/transcribe/url**

```bash
curl -X POST "http://localhost:8000/api/transcribe/url" \
  -F "url=https://example.com/audio.wav" \
  -F "model=small"
```

#### 健康检查

**GET /api/health**

```bash
curl http://localhost:8000/api/health
```

**响应：**
```json
{
  "status": "healthy",
  "loaded_models": ["small"]
}
```

#### 列出模型

**GET /api/models**

```bash
curl http://localhost:8000/api/models
```

**响应：**
```json
{
  "models": ["tiny", "base", "small", "medium", "large"],
  "default": "small",
  "loaded": ["small"]
}
```

#### 获取统计

**GET /api/stats**

```bash
curl http://localhost:8000/api/stats
```

**响应：**
```json
{
  "loaded_models": ["small"],
  "dict_stats": {
    "total_rules": 316,
    "replacements_made": 0
  }
}
```

### 3. 客户端库

我们提供了 Python 客户端库：

```python
from examples.api_client import CodeWhisperClient

# 创建客户端
client = CodeWhisperClient("http://localhost:8000")

# 健康检查
health = client.health_check()
print(f"状态: {health['status']}")

# 转录文件
result = client.transcribe_file(
    "audio.wav",
    model="small",
    language="zh",
    verbose=True
)

print(f"转录结果: {result['text']}")
print(f"修正次数: {result['corrections']['count']}")
```

---

## 实时语音输入

CodeWhisper API 支持直接输入语音数据，无需先保存为文件！

### 1. Base64 流式接口 ⭐ 推荐用于简单场景

**POST /api/transcribe/stream**

直接发送 Base64 编码的音频数据。

**Python：**
```python
import requests
import base64

with open("audio.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    "http://localhost:8000/api/transcribe/stream",
    data={
        "audio_data": audio_base64,
        "model": "small",
        "language": "zh"
    }
)

result = response.json()
print(result["text"])
```

**JavaScript：**
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks);
      const reader = new FileReader();
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        const formData = new FormData();
        formData.append('audio_data', base64Audio);
        formData.append('model', 'small');
        
        const response = await fetch('http://localhost:8000/api/transcribe/stream', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        console.log(result.text);
      };
      
      reader.readAsDataURL(audioBlob);
    };
    
    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 5000);
  });
```

**特点：**
- ✅ 简单易用
- ✅ 一次性转录
- ✅ 兼容性好
- ✅ 适合网页应用

### 2. WebSocket 接口 ⭐⭐ 推荐用于实时场景

**WS /ws/transcribe**

使用 WebSocket 进行双向通信，支持分块发送音频数据。

**Python：**
```python
import asyncio
import websockets
import json
import base64

async def transcribe():
    async with websockets.connect("ws://localhost:8000/ws/transcribe") as ws:
        # 开始会话
        await ws.send(json.dumps({
            "action": "start",
            "model": "small",
            "language": "zh"
        }))
        
        # 发送音频数据（分块）
        with open("audio.wav", "rb") as f:
            while chunk := f.read(4096):
                await ws.send(json.dumps({
                    "action": "audio",
                    "data": base64.b64encode(chunk).decode()
                }))
        
        # 结束并获取结果
        await ws.send(json.dumps({"action": "end"}))
        result = json.loads(await ws.recv())
        
        if result["type"] == "result":
            print(result["text"])

asyncio.run(transcribe())
```

**协议：**

```json
// 客户端发送
{"action": "start", "model": "small", "language": "zh"}
{"action": "audio", "data": "base64_encoded_audio"}
{"action": "end"}

// 服务器响应
{"type": "status", "message": "会话已开始"}
{"type": "result", "text": "转录结果", "corrections": {...}}
```

**特点：**
- ✅ 真正的实时通信
- ✅ 可以边录边发
- ✅ 支持长时间录音
- ✅ 低延迟
- ✅ 双向通信

### 3. 网页录音示例

我们提供了完整的 HTML 网页示例：`examples/web_recorder.html`

可以直接在浏览器中录音并转录！

**使用方法：**
1. 启动服务器：`python api_server.py`
2. 打开网页：`examples/web_recorder.html`
3. 点击"开始录音" → 说话 → 点击"停止录音"
4. 查看转录结果！

**功能：**
- 🎤 浏览器内录音
- 🚀 实时转录
- 🔧 术语自动修正
- 📊 修正详情显示
- ⚙️ 模型和语言选择
- 🎨 美观的界面

### 4. 三种方式对比

| 方式 | 延迟 | 复杂度 | 适用场景 |
|------|------|--------|----------|
| 文件上传 | 高 | 低 | 已有音频文件 |
| Base64 流 | 中 | 低 | 网页应用、简单场景 |
| WebSocket | 低 | 中 | 实时对话、长时间录音 |

---

## 术语修正

CodeWhisper 内置术语修正功能，自动修正语音识别中的常见错误。

### 支持的术语类型

- **职场术语**：提测、联调、排期、上线、复盘等
- **编程术语**：MySQL、Redis、Docker、API 等
- **模具术语**：慢丝割一刀、快丝割一刀等
- **自定义术语**：用户可添加专业术语

### 示例

```
输入: "我需要一个磨具来做慢思割一道"
输出: "我需要一个模具来做慢丝割一刀"

修正:
- 磨具 → 模具 (模具术语)
- 慢思 → 慢丝 (模具术语)
- 一道 → 一刀 (通用术语)
```

### 添加自定义术语

编辑 `dictionaries/programmer_terms.json`：

```json
{
  "categories": {
    "your_category": {
      "terms": {
        "正确术语": {
          "correct": "正确术语",
          "description": "术语说明",
          "variants": [
            {
              "wrong": "错误形式1",
              "description": "错误原因"
            }
          ]
        }
      }
    }
  }
}
```

---

## 自主学习

CodeWhisper 具有自主学习功能，自动学习用户常用术语，持续优化识别率。

### 工作原理

1. **术语检测**：每次转录后检测文本中的术语
2. **频次累积**：常用术语频次增加
3. **动态提示词**：根据频次构建优化的提示词
4. **自动淘汰**：低频术语自动淘汰

### 查看学习效果

```bash
# 查看用户术语库
python tools/view_user_terms.py

# 导出为 CSV
python tools/view_user_terms.py export
```

**输出示例：**
```
📊 统计信息:
  通用术语数: 19
  用户术语数: 8
  高频术语数: 6 (频次 >= 3)

💡 当前提示词:
  工业模具行业从业者：模具、线切割、慢丝、快丝、中丝、慢丝割一刀、慢丝割一修一、慢丝割一修二。

📈 用户术语排行:
  ⭐ 1. 模具: 14次
  ⭐ 2. 线切割: 8次
  ⭐ 3. 慢丝割一刀: 5次
```

### 配置文件

编辑 `config/base_config.json`：

```json
{
  "prompt_prefix": "工业模具行业从业者：",
  "prompt_total_terms": 10,
  "prompt_base_terms": 5,
  "user_term_min_freq": 3,
  "max_user_terms": 20
}
```

**参数说明：**
- `prompt_total_terms`：提示词中总术语数
- `prompt_base_terms`：提示词中通用术语数
- `user_term_min_freq`：术语进入提示词的最低频次
- `max_user_terms`：用户词库最大容量

---

## 部署指南

### 1. 开发环境

```bash
# 启动 API 服务（自动重载）
python api_server.py --reload --host 127.0.0.1 --port 8000
```

### 2. 生产环境

#### 使用 Gunicorn

```bash
pip install gunicorn

gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --model small
```

#### 使用 Docker

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py", "--host", "0.0.0.0"]
```

```bash
# 构建
docker build -t codewhisper-api .

# 运行
docker run -p 8000:8000 codewhisper-api
```

#### 使用 Docker Compose

```yaml
version: '3'
services:
  codewhisper-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL=small
    volumes:
      - ./config:/app/config
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codewhisper-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: codewhisper-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MODEL
          value: "small"
```

### 4. 模型选择

| 模型 | 大小 | 速度 | 准确率 | 显存占用 |
|------|------|------|--------|----------|
| tiny | ~39 MB | 最快 | 较低 | ~1 GB |
| base | ~74 MB | 很快 | 一般 | ~1-2 GB |
| small | ~244 MB | 较快 | 较高 | ~2-4 GB |
| medium | ~769 MB | 中等 | 高 | ~4-8 GB |
| large | ~1550 MB | 较慢 | 最高 | ~8-16 GB |

**选择建议：**
- 实时应用：tiny / base
- 日常转录：small（推荐）
- 高准确率：medium / large

---

## 常见问题

### 1. Windows 音频设备问题

如果遇到 "Error querying device -1" 错误：

1. 检查麦克风是否已连接
2. Windows 设置 > 隐私 > 麦克风 > 允许应用访问麦克风
3. 在设备管理器中检查音频设备状态
4. 在 Windows 声音设置中设置默认录音设备

### 2. 首次请求很慢

首次请求需要加载模型，可以使用 `--model` 参数预加载：

```bash
python api_server.py --model small
```

### 3. 显存不足

使用更小的模型：

```bash
python api_server.py --model tiny
```

### 4. 端口被占用

使用其他端口：

```bash
python api_server.py --port 8080
```

### 5. 浏览器无法录音

浏览器录音需要 HTTPS 或 localhost：

```bash
# 开发环境（localhost）
python api_server.py

# 生产环境（需要 SSL 证书）
uvicorn api_server:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### 6. 如何添加自定义术语

编辑 `dictionaries/programmer_terms.json`，添加新的术语和错误变体。

### 7. 如何重置学习数据

```bash
python tools/view_user_terms.py reset
```

### 8. 支持哪些语言

Whisper 支持 99 种语言，通过 `language` 参数指定：

```bash
# 中文
python app.py -f audio.wav --language zh

# 英文
python app.py -f audio.wav --language en

# 日文
python app.py -f audio.wav --language ja
```

---

## 文档资源

- [API 快速开始](docs/API_QUICKSTART.md)
- [完整 API 文档](docs/API_DOCUMENTATION.md)
- [命令行参数](docs/COMMAND_LINE_ARGS.md)
- [词典修正机制](docs/DICTIONARY_CORRECTION.md)
- [自主学习机制](docs/LEARNING_MECHANISM.md)
- [模具术语指南](docs/MOLD_TERMS_GUIDE.md)

## 示例代码

- `examples/api_client.py` - Python 客户端库
- `examples/websocket_client.py` - WebSocket 客户端
- `examples/web_recorder.html` - 网页录音示例
- `examples/test_api.sh` - Linux/Mac 测试脚本
- `examples/test_api.ps1` - Windows 测试脚本

## 工具

- `tools/view_user_terms.py` - 查看/导出/重置用户术语库
- `tools/add_term.py` - 交互式添加术语
- `tools/demo_learning.py` - 演示学习机制

---

## 总结

CodeWhisper 是一款功能强大的语音转文字工具，支持：

- 🎤 多平台 GUI 应用
- 🌐 REST API 服务
- 🔧 实时语音输入
- 🧠 自主学习优化
- 📦 多种部署方式

开始使用吧！🎤

```bash
# 快速开始
pip install -r requirements.txt
python api_server.py

# 访问文档
# http://localhost:8000/docs
```