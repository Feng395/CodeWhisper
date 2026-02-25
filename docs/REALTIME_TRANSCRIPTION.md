# 实时语音转录功能

## 概述

CodeWhisper API 现在支持实时语音输入，客户端可以直接发送语音数据进行转录，无需先保存为文件。

## 三种方式

### 1. Base64 流式接口（推荐用于简单场景）

**POST /api/transcribe/stream**

直接发送 Base64 编码的音频数据。

**优点：**
- 简单易用
- 适合一次性转录
- 兼容性好

**示例：**

```python
import requests
import base64

# 读取音频数据
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()

# 编码为 Base64
audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# 发送请求
response = requests.post(
    "http://localhost:8000/api/transcribe/stream",
    data={
        "audio_data": audio_base64,
        "model": "small",
        "language": "zh",
        "format": "wav"
    }
)

result = response.json()
print(result["text"])
```

**JavaScript 示例：**

```javascript
// 从麦克风录音
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    
    mediaRecorder.onstop = async () => {
      // 合并音频
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      
      // 转换为 Base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        // 发送到 API
        const formData = new FormData();
        formData.append('audio_data', base64Audio);
        formData.append('model', 'small');
        formData.append('language', 'zh');
        
        const response = await fetch('http://localhost:8000/api/transcribe/stream', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        console.log(result.text);
      };
    };
    
    // 开始录音
    mediaRecorder.start();
    
    // 5 秒后停止
    setTimeout(() => mediaRecorder.stop(), 5000);
  });
```

---

### 2. WebSocket 接口（推荐用于实时场景）

**WS /ws/transcribe**

使用 WebSocket 进行双向通信，支持分块发送音频数据。

**优点：**
- 真正的实时通信
- 可以边录边发
- 支持长时间录音
- 低延迟

**协议：**

客户端发送：
```json
{
  "action": "start",
  "model": "small",
  "language": "zh"
}
```

```json
{
  "action": "audio",
  "data": "base64_encoded_audio_chunk"
}
```

```json
{
  "action": "end"
}
```

服务器响应：
```json
{
  "type": "status",
  "message": "会话已开始"
}
```

```json
{
  "type": "result",
  "text": "转录结果",
  "corrections": {...}
}
```

**Python 示例：**

```python
import asyncio
import websockets
import json
import base64

async def transcribe_realtime():
    uri = "ws://localhost:8000/ws/transcribe"
    
    async with websockets.connect(uri) as websocket:
        # 开始会话
        await websocket.send(json.dumps({
            "action": "start",
            "model": "small",
            "language": "zh"
        }))
        
        response = await websocket.recv()
        print(json.loads(response)['message'])
        
        # 发送音频数据（分块）
        with open("audio.wav", "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                
                encoded = base64.b64encode(chunk).decode('utf-8')
                await websocket.send(json.dumps({
                    "action": "audio",
                    "data": encoded
                }))
                
                response = await websocket.recv()
                print(json.loads(response)['message'])
        
        # 结束并获取结果
        await websocket.send(json.dumps({
            "action": "end"
        }))
        
        response = await websocket.recv()
        result = json.loads(response)
        print(f"转录结果: {result['text']}")

asyncio.run(transcribe_realtime())
```

**JavaScript 示例：**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

ws.onopen = () => {
  // 开始会话
  ws.send(JSON.stringify({
    action: 'start',
    model: 'small',
    language: 'zh'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'result') {
    console.log('转录结果:', data.text);
  } else if (data.type === 'status') {
    console.log('状态:', data.message);
  }
};

// 发送音频数据
function sendAudioChunk(audioData) {
  const base64 = btoa(String.fromCharCode(...new Uint8Array(audioData)));
  ws.send(JSON.stringify({
    action: 'audio',
    data: base64
  }));
}

// 结束会话
function endSession() {
  ws.send(JSON.stringify({
    action: 'end'
  }));
}
```

---

### 3. 文件上传接口（原有方式）

**POST /api/transcribe**

上传完整的音频文件。

**优点：**
- 最简单
- 适合已有音频文件
- 支持所有格式

**示例：**

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

---

## 网页录音示例

我们提供了一个完整的网页示例，展示如何在浏览器中直接录音并转录。

### 使用方法

1. 启动 API 服务器：
```bash
python api_server.py
```

2. 在浏览器中打开：
```
examples/web_recorder.html
```

3. 点击"开始录音"，说话，然后点击"停止录音"

4. 等待转录结果显示

### 功能特性

- ✅ 浏览器内录音
- ✅ 实时转录
- ✅ 术语自动修正
- ✅ 修正详情显示
- ✅ 模型和语言选择
- ✅ 美观的界面

---

## 实时录音集成

### 使用 sounddevice（Python）

```python
import sounddevice as sd
import numpy as np
import requests
import base64
import io
import wave

def record_and_transcribe(duration=5, samplerate=16000):
    """录音并转录"""
    print("开始录音...")
    
    # 录音
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("录音完成，正在转录...")
    
    # 转换为 WAV 格式
    audio_int16 = (audio * 32767).astype(np.int16)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_int16.tobytes())
    
    # 编码为 Base64
    audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 发送到 API
    response = requests.post(
        "http://localhost:8000/api/transcribe/stream",
        data={
            "audio_data": audio_base64,
            "model": "small",
            "language": "zh",
            "format": "wav"
        }
    )
    
    result = response.json()
    print(f"转录结果: {result['text']}")
    
    return result

# 使用
record_and_transcribe(duration=5)
```

### 使用 MediaRecorder（浏览器）

```javascript
class VoiceRecorder {
  constructor(apiUrl = 'http://localhost:8000') {
    this.apiUrl = apiUrl;
    this.mediaRecorder = null;
    this.audioChunks = [];
  }
  
  async start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);
    this.audioChunks = [];
    
    this.mediaRecorder.ondataavailable = (event) => {
      this.audioChunks.push(event.data);
    };
    
    this.mediaRecorder.start();
    console.log('录音开始');
  }
  
  async stop() {
    return new Promise((resolve) => {
      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        const result = await this.transcribe(audioBlob);
        resolve(result);
      };
      
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      console.log('录音停止');
    });
  }
  
  async transcribe(audioBlob) {
    const reader = new FileReader();
    
    return new Promise((resolve, reject) => {
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        const formData = new FormData();
        formData.append('audio_data', base64Audio);
        formData.append('model', 'small');
        formData.append('language', 'zh');
        
        try {
          const response = await fetch(`${this.apiUrl}/api/transcribe/stream`, {
            method: 'POST',
            body: formData
          });
          
          const result = await response.json();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.readAsDataURL(audioBlob);
    });
  }
}

// 使用
const recorder = new VoiceRecorder();

// 开始录音
await recorder.start();

// 停止录音并获取结果
const result = await recorder.stop();
console.log('转录结果:', result.text);
```

---

## 性能建议

### 1. 音频格式

- **推荐格式**: WAV (PCM)
- **采样率**: 16000 Hz
- **声道**: 单声道 (Mono)
- **位深度**: 16-bit

### 2. 分块大小

- **WebSocket**: 4KB - 8KB 每块
- **Base64**: 整个音频（< 10MB）

### 3. 延迟优化

- 使用 WebSocket 减少延迟
- 预加载模型
- 使用 GPU 加速

---

## 安全建议

### 1. HTTPS

生产环境必须使用 HTTPS：

```bash
uvicorn api_server:app \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem
```

### 2. 文件大小限制

```python
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB

if len(audio_data) > MAX_AUDIO_SIZE:
    raise HTTPException(400, "音频数据太大")
```

### 3. 速率限制

使用 slowapi 或 nginx 限制请求频率。

---

## 常见问题

### Q: 浏览器无法录音？

A: 需要 HTTPS 或 localhost。现代浏览器出于安全考虑，只允许在安全上下文中访问麦克风。

### Q: WebSocket 连接失败？

A: 检查防火墙设置，确保 WebSocket 端口开放。

### Q: 转录延迟很高？

A: 
1. 使用更小的模型（tiny/base）
2. 启用 GPU 加速
3. 减少音频分块大小

### Q: 支持实时流式转录吗？

A: 当前版本需要完整音频才能转录。真正的实时流式转录需要使用 Whisper 的流式模式，这是未来的改进方向。

---

## 示例代码

完整的示例代码位于 `examples/` 目录：

- `websocket_client.py` - WebSocket 客户端
- `web_recorder.html` - 网页录音示例

---

## 下一步

查看完整的 API 文档：[API_DOCUMENTATION.md](API_DOCUMENTATION.md)
