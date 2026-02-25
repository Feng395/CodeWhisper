# 命令行参数详解

## 概述

CodeWhisper API 服务器支持 4 个命令行参数，用于灵活配置服务器的运行方式。

## 参数列表

### 1. --host

**功能：** 指定服务器绑定的 IP 地址

**默认值：** `0.0.0.0`（监听所有网络接口）

**可选值：**
- `0.0.0.0` - 监听所有网卡，允许外部访问
- `127.0.0.1` - 仅本地访问
- 特定 IP 地址，如 `192.168.1.100`

**使用示例：**

```bash
# 允许外部访问（默认）
python api_server.py
# 或
python api_server.py --host 0.0.0.0

# 仅本地访问
python api_server.py --host 127.0.0.1

# 指定局域网 IP
python api_server.py --host 192.168.1.100
```

**使用场景：**

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 开发测试 | 127.0.0.1 | 仅本地访问，更安全 |
| 局域网共享 | 192.168.x.x | 允许局域网内其他设备访问 |
| 公网部署 | 0.0.0.0 | 允许外部访问 |

**注意事项：**
- 监听 `0.0.0.0` 时，确保防火墙允许外部访问
- 生产环境建议使用反向代理（如 Nginx）

---

### 2. --port

**功能：** 指定服务器监听的端口号

**默认值：** `8000`

**可选值：** 1-65535 之间的任意端口

**使用示例：**

```bash
# 使用默认端口
python api_server.py

# 指定端口
python api_server.py --port 8080

# 使用 80 端口（HTTP 默认端口）
sudo python api_server.py --port 80

# 使用 443 端口（HTTPS 默认端口）
sudo python api_server.py --port 443
```

**常用端口：**
- `80` - HTTP 默认端口（需要 sudo）
- `443` - HTTPS 默认端口（需要 sudo）
- `8000` - 常用开发端口
- `8080` - 备用 HTTP 端口
- `3000` - Node.js 常用端口

**注意事项：**
- 端口 < 1024 需要管理员权限
- 确保端口未被其他程序占用
- 防火墙需要允许该端口

**检查端口占用：**
```bash
# Linux/Mac
netstat -tuln | grep 8000

# Windows
netstat -ano | findstr 8000
```

---

### 3. --reload

**功能：** 启用开发模式，代码修改后自动重载

**默认值：** `False`（禁用）

**类型：** 布尔开关（指定即启用）

**使用示例：**

```bash
# 启用自动重载（开发环境）
python api_server.py --reload

# 禁用自动重载（生产环境）
python api_server.py
```

**对比：**

| 模式 | 命令 | 适用场景 | 优点 | 缺点 |
|------|------|----------|------|------|
| 开发模式 | `--reload` | 开发调试 | 代码修改自动生效 | 消耗更多资源 |
| 生产模式 | 无参数 | 生产部署 | 稳定、性能好 | 需要手动重启 |

**注意事项：**
- 自动重载会增加内存占用
- 可能导致意外的连接中断
- 生产环境强烈建议关闭

---

### 4. --model

**功能：** 预加载 Whisper 模型

**默认值：** `small`

**可选值：** `tiny`, `base`, `small`, `medium`, `large`

**模型对比：**

| 模型 | 文件大小 | 相对速度 | 准确率 | 显存占用 | 适用场景 |
|------|----------|----------|--------|----------|----------|
| tiny | ~39 MB | 最快 | 较低 | ~1 GB | 实时应用、资源受限 |
| base | ~74 MB | 很快 | 一般 | ~1-2 GB | 快速原型、一般应用 |
| small | ~244 MB | 较快 | 较高 | ~2-4 GB | **推荐日常使用** |
| medium | ~769 MB | 中等 | 高 | ~4-8 GB | 高准确率需求 |
| large | ~1550 MB | 较慢 | 最高 | ~8-16 GB | 最高准确率 |

**使用示例：**

```bash
# 使用小模型（最快）
python api_server.py --model tiny

# 使用基础模型
python api_server.py --model base

# 使用小模型（推荐）
python api_server.py --model small

# 使用中等模型
python api_server.py --model medium

# 使用大模型（最准确）
python api_server.py --model large
```

**选择建议：**

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 实时对话 | tiny / base | 延迟最低 |
| 日常转录 | small | 平衡速度和准确率 |
| 会议记录 | medium | 高准确率 |
| 专业转录 | large | 最高准确率 |
| GPU 显存有限 | tiny / base | 显存占用小 |
| GPU 显存充足 | medium / large | 准确率更高 |

**显存要求：**

| 模型 | 最低显存 | 推荐显存 |
|------|----------|----------|
| tiny | 1 GB | 2 GB |
| base | 2 GB | 4 GB |
| small | 4 GB | 6 GB |
| medium | 8 GB | 12 GB |
| large | 16 GB | 24 GB |

**检查显存：**
```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi
```

---

## 完整使用示例

### 开发环境

```bash
# 本地开发，自动重载
python api_server.py \
  --host 127.0.0.1 \
  --port 8000 \
  --reload \
  --model small
```

### 生产环境（标准配置）

```bash
# 允许外部访问，不自动重载
python api_server.py \
  --host 0.0.0.0 \
  --port 8000 \
  --model small
```

### 生产环境（高性能）

```bash
# 使用大模型，高准确率
python api_server.py \
  --host 0.0.0.0 \
  --port 8000 \
  --model medium
```

### 资源受限环境

```bash
# 使用小模型，减少资源占用
python api_server.py \
  --host 0.0.0.0 \
  --port 8000 \
  --model tiny
```

### 局域网共享

```bash
# 允许局域网访问
python api_server.py \
  --host 192.168.1.143 \
  --port 8888 \
  --model medium
```

---

## 组合使用

### 使用环境变量

```bash
# 设置默认参数
export HOST=0.0.0.0
export PORT=8000
export MODEL=small

# 启动服务器
python api_server.py
```

### 使用配置文件

创建 `api_config.json`：

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "model": "small",
  "reload": false
}
```

然后修改 `api_server.py` 加载配置：

```python
import json

config = {}
if os.path.exists("api_config.json"):
    with open("api_config.json") as f:
        config = json.load(f)

parser.add_argument("--host", default=config.get("host", "0.0.0.0"))
parser.add_argument("--port", type=int, default=config.get("port", 8000))
parser.add_argument("--model", default=config.get("model", "small"))
```

---

## 查看帮助

```bash
# 查看帮助信息
python api_server.py --help
```

输出：

```
usage: api_server.py [-h] [--host HOST] [--port PORT] [--reload] [--model {tiny,base,small,medium,large}]

CodeWhisper API Server - 语音转文字 API 服务

options:
  -h, --help            显示帮助信息
  --host HOST           服务器绑定的 IP 地址 (默认: 0.0.0.0，监听所有网卡)
  --port PORT           服务器监听的端口号 (默认: 8000)
  --reload              启用开发模式，代码修改后自动重载 (默认: 禁用)
  --model {tiny,base,small,medium,large}
                        预加载的 Whisper 模型大小 (默认: small)
```

---

## 常见问题

### Q: 端口被占用怎么办？

A: 使用其他端口
```bash
python api_server.py --port 8080
```

### Q: 如何让外网访问？

A: 设置 host 为 0.0.0.0
```bash
python api_server.py --host 0.0.0.0
```

### Q: 显存不够怎么办？

A: 使用更小的模型
```bash
python api_server.py --model tiny
```

### Q: 首次请求太慢？

A: 预加载模型
```bash
python api_server.py --model small
```

### Q: 代码修改后需要重启吗？

A: 启用自动重载
```bash
python api_server.py --reload
```

---

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000", "--model", "small"]
```

### Docker Compose

```yaml
version: '3'
services:
  codewhisper-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL=small
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 性能优化建议

### 1. 选择合适的模型

根据需求选择模型，不要盲目使用大模型。

### 2. 使用 GPU 加速

确保安装了 GPU 版本的 PyTorch：

```bash
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 3. 多进程部署

使用 Gunicorn：

```bash
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --model small
```

### 4. 使用反向代理

使用 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 总结

| 参数 | 作用 | 默认值 | 重要程度 |
|------|------|--------|----------|
| --host | 服务器地址 | 0.0.0.0 | ⭐⭐⭐ |
| --port | 端口号 | 8000 | ⭐⭐⭐ |
| --reload | 自动重载 | False | ⭐⭐ |
| --model | 模型大小 | small | ⭐⭐⭐ |

根据实际需求灵活配置这些参数，可以获得最佳的使用体验！