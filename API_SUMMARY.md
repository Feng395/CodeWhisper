# API 功能总结

## ✅ 已完成

CodeWhisper 现在提供完整的 REST API 接口，支持外部调用！

## 📦 新增文件

### 核心文件
- `api_server.py` - FastAPI 服务器主文件
- `API_README.md` - API 快速入门

### 文档
- `docs/API_DOCUMENTATION.md` - 完整 API 文档（详细）
- `docs/API_QUICKSTART.md` - API 快速开始指南

### 示例代码
- `examples/api_client.py` - Python 客户端库
- `examples/test_api.sh` - Linux/Mac 测试脚本
- `examples/test_api.ps1` - Windows 测试脚本

### 依赖更新
- `requirements.txt` - 添加 FastAPI 相关依赖

## 🚀 主要功能

### 1. REST API 端点

#### 转录音频文件
```
POST /api/transcribe
```
- 上传音频文件
- 支持多种格式（wav, mp3, m4a, flac, ogg, webm）
- 自动术语修正
- 学习用户习惯

#### 从 URL 转录
```
POST /api/transcribe/url
```
- 从 URL 下载音频
- 自动转录

#### 健康检查
```
GET /api/health
```
- 检查服务器状态
- 查看已加载的模型

#### 列出模型
```
GET /api/models
```
- 查看支持的模型
- 查看已加载的模型

#### 获取统计
```
GET /api/stats
```
- 字典统计信息
- 模型信息

### 2. 客户端支持

#### Python 客户端
```python
from examples.api_client import CodeWhisperClient

client = CodeWhisperClient("http://localhost:8000")
result = client.transcribe_file("audio.wav")
print(result["text"])
```

#### cURL
```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.wav" \
  -F "model=small"
```

#### JavaScript
```javascript
fetch('http://localhost:8000/api/transcribe', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data.text));
```

### 3. 交互式文档

启动服务器后自动提供：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

可以直接在网页上测试 API！

## 📊 功能特性

✅ **多格式支持**：wav, mp3, m4a, flac, ogg, webm  
✅ **多语言支持**：支持 99 种语言  
✅ **术语修正**：自动修正专业术语  
✅ **自主学习**：学习用户常用术语  
✅ **详细统计**：提供修正详情和统计  
✅ **GPU 加速**：自动使用 CUDA 加速  
✅ **模型预加载**：避免首次请求延迟  
✅ **CORS 支持**：支持跨域请求  
✅ **错误处理**：友好的错误信息  

## 🎯 使用场景

### 1. Web 应用集成
```javascript
// 前端上传音频，后端转录
const formData = new FormData();
formData.append('file', audioBlob);

fetch('http://api.example.com/api/transcribe', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  // 显示转录结果
  document.getElementById('result').textContent = data.text;
});
```

### 2. 移动应用集成
```python
# iOS/Android 应用通过 HTTP 调用
import requests

def transcribe_audio(audio_file):
    with open(audio_file, 'rb') as f:
        response = requests.post(
            'http://api.example.com/api/transcribe',
            files={'file': f},
            data={'model': 'small', 'language': 'zh'}
        )
    return response.json()['text']
```

### 3. 批量处理
```python
# 批量转录音频文件
from examples.api_client import CodeWhisperClient

client = CodeWhisperClient("http://localhost:8000")

audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
results = []

for audio_file in audio_files:
    result = client.transcribe_file(audio_file)
    results.append({
        'file': audio_file,
        'text': result['text'],
        'corrections': result['corrections']['count']
    })

print(f"处理完成，共 {len(results)} 个文件")
```

### 4. 微服务架构
```yaml
# docker-compose.yml
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
```

## 🔧 部署选项

### 开发环境
```bash
python api_server.py --reload
```

### 生产环境（Gunicorn）
```bash
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker 部署
```bash
docker build -t codewhisper-api .
docker run -p 8000:8000 codewhisper-api
```

### Kubernetes 部署
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
```

## 📈 性能优化

1. **模型预加载**：启动时加载模型
2. **多进程部署**：使用多个 worker
3. **GPU 加速**：自动使用 CUDA
4. **异步处理**：FastAPI 原生支持
5. **连接池**：复用 HTTP 连接

## 🔒 安全建议

1. **CORS 限制**：生产环境限制域名
2. **文件大小限制**：限制上传文件大小
3. **请求频率限制**：使用 nginx 或 slowapi
4. **HTTPS**：生产环境使用 HTTPS
5. **认证**：添加 API Key 或 OAuth

## 📚 文档资源

- [API 快速开始](docs/API_QUICKSTART.md) - 5 分钟上手
- [完整 API 文档](docs/API_DOCUMENTATION.md) - 详细参考
- [Python 客户端](examples/api_client.py) - 客户端库
- [测试脚本](examples/) - 测试示例

## 🎉 总结

CodeWhisper 现在不仅是一个桌面应用，还是一个强大的 API 服务！

你可以：
- 在 Web 应用中集成语音转文字
- 在移动应用中调用转录功能
- 批量处理音频文件
- 构建自己的语音应用

所有功能都通过简单的 HTTP 请求即可使用！

## 🚀 快速测试

```bash
# 1. 安装依赖
pip install fastapi uvicorn python-multipart requests

# 2. 启动服务器
python api_server.py

# 3. 测试 API
python examples/api_client.py

# 或使用浏览器访问
# http://localhost:8000/docs
```

开始使用吧！🎤
