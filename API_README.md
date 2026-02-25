# CodeWhisper API

## 概述

CodeWhisper 现在提供 REST API 接口，让你可以通过 HTTP 请求调用语音转文字功能。

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn python-multipart requests
```

### 2. 启动服务器

```bash
python api_server.py
```

### 3. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 简单示例

### Python

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

### cURL

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.wav" \
  -F "model=small" \
  -F "language=zh"
```

### JavaScript

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

## 主要功能

✅ 上传音频文件转录  
✅ 从 URL 转录音频  
✅ 术语自动修正  
✅ 自主学习用户习惯  
✅ 支持多种音频格式  
✅ 支持多种语言  
✅ 详细的修正统计  

## 文档

- [API 快速开始](docs/API_QUICKSTART.md)
- [完整 API 文档](docs/API_DOCUMENTATION.md)
- [Python 客户端示例](examples/api_client.py)

## 支持的端点

- `POST /api/transcribe` - 转录音频文件
- `POST /api/transcribe/url` - 从 URL 转录
- `GET /api/health` - 健康检查
- `GET /api/models` - 列出模型
- `GET /api/stats` - 获取统计信息

## 部署

### 开发环境

```bash
python api_server.py --reload
```

### 生产环境

```bash
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 性能

- 支持 GPU 加速
- 模型预加载
- 多进程部署
- 异步处理

## 安全

- CORS 配置
- 文件大小限制
- 请求频率限制
- HTTPS 支持

## 示例

查看 `examples/` 目录获取更多示例：

- `api_client.py` - Python 客户端库
- `test_api.sh` - Linux/Mac 测试脚本
- `test_api.ps1` - Windows 测试脚本
