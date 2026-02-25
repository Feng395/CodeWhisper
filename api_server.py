#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CodeWhisper API Server

提供 REST API 接口供外部调用语音转文字功能
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import base64

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from CodeWhisper.transcriber import CodeWhisper

# 创建 FastAPI 应用
app = FastAPI(
    title="CodeWhisper API",
    description="语音转文字 API 服务，支持中文优化和术语修正",
    version="1.0.0"
)

# 配置 CORS（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Whisper 实例（避免重复加载模型）
whisper_instances = {}


def get_whisper_instance(model_name: str = "small") -> CodeWhisper:
    """获取或创建 Whisper 实例（单例模式）"""
    if model_name not in whisper_instances:
        print(f"🔄 加载模型: {model_name}")
        whisper_instances[model_name] = CodeWhisper(model_name=model_name)
    return whisper_instances[model_name]


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "CodeWhisper API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "transcribe": "/api/transcribe",
            "health": "/api/health",
            "models": "/api/models"
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "loaded_models": list(whisper_instances.keys())
    }


@app.get("/api/models")
async def list_models():
    """列出支持的模型"""
    return {
        "models": ["tiny", "base", "small", "medium", "large"],
        "default": "small",
        "loaded": list(whisper_instances.keys())
    }


@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="音频文件"),
    model: str = Form("small", description="模型大小: tiny/base/small/medium/large"),
    language: str = Form("zh", description="语言代码，如 zh, en"),
    fix_terms: bool = Form(True, description="是否修正术语"),
    learn: bool = Form(True, description="是否学习用户习惯"),
    verbose: bool = Form(False, description="是否显示详细信息")
):
    """
    转录音频文件
    
    参数:
    - file: 音频文件（支持 wav, mp3, m4a, flac, ogg 等格式）
    - model: 模型大小，可选 tiny/base/small/medium/large（默认：small）
    - language: 语言代码（默认：zh）
    - fix_terms: 是否修正术语（默认：true）
    - learn: 是否学习用户习惯（默认：true）
    - verbose: 是否返回详细信息（默认：false）
    
    返回:
    - text: 转录文本
    - language: 检测到的语言
    - corrections: 术语修正详情（如果启用）
    - stats: 统计信息（如果启用详细模式）
    """
    temp_file = None
    
    try:
        # 验证模型
        if model not in ["tiny", "base", "small", "medium", "large"]:
            raise HTTPException(status_code=400, detail=f"不支持的模型: {model}")
        
        # 验证文件类型
        allowed_extensions = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 保存上传的文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file = tmp.name
            content = await file.read()
            tmp.write(content)
        
        # 获取 Whisper 实例
        whisper = get_whisper_instance(model)
        
        # 转录
        result = whisper.transcribe(
            temp_file,
            language=language,
            fix_programmer_terms=fix_terms,
            learn_user_terms=learn,
            verbose=verbose
        )
        
        # 构建响应
        response = {
            "success": True,
            "text": result.get("text", ""),
            "language": result.get("language", language)
        }
        
        # 添加术语修正信息
        if fix_terms:
            corrections = whisper.dict_manager.get_corrections()
            stats = whisper.get_dict_stats()
            
            response["corrections"] = {
                "count": stats.get("replacements_made", 0),
                "details": corrections if verbose else []
            }
        
        # 添加详细信息
        if verbose:
            response["stats"] = {
                "model": model,
                "file_size": len(content),
                "file_type": file_ext,
                "dict_rules": whisper.get_dict_stats().get("total_rules", 0)
            }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@app.post("/api/transcribe/url")
async def transcribe_from_url(
    url: str = Form(..., description="音频文件 URL"),
    model: str = Form("small", description="模型大小"),
    language: str = Form("zh", description="语言代码"),
    fix_terms: bool = Form(True, description="是否修正术语"),
    learn: bool = Form(True, description="是否学习用户习惯")
):
    """
    从 URL 转录音频文件
    
    参数:
    - url: 音频文件的 URL
    - model: 模型大小
    - language: 语言代码
    - fix_terms: 是否修正术语
    - learn: 是否学习用户习惯
    """
    import requests
    
    temp_file = None
    
    try:
        # 下载文件
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 从 URL 推断文件扩展名
        file_ext = Path(url).suffix.lower() or ".wav"
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file = tmp.name
            tmp.write(response.content)
        
        # 获取 Whisper 实例
        whisper = get_whisper_instance(model)
        
        # 转录
        result = whisper.transcribe(
            temp_file,
            language=language,
            fix_programmer_terms=fix_terms,
            learn_user_terms=learn
        )
        
        # 构建响应
        response_data = {
            "success": True,
            "text": result.get("text", ""),
            "language": result.get("language", language)
        }
        
        if fix_terms:
            corrections = whisper.dict_manager.get_corrections()
            stats = whisper.get_dict_stats()
            
            response_data["corrections"] = {
                "count": stats.get("replacements_made", 0),
                "details": corrections
            }
        
        return JSONResponse(content=response_data)
    
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"下载文件失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    if not whisper_instances:
        return {
            "message": "没有加载的模型",
            "loaded_models": []
        }
    
    # 使用第一个加载的模型获取统计
    whisper = list(whisper_instances.values())[0]
    
    return {
        "loaded_models": list(whisper_instances.keys()),
        "dict_stats": whisper.get_dict_stats(),
        "dict_categories": whisper.get_dict_categories()
    }


@app.post("/api/transcribe/stream")
async def transcribe_stream(
    audio_data: str = Form(..., description="Base64 编码的音频数据"),
    model: str = Form("small", description="模型大小"),
    language: str = Form("zh", description="语言代码"),
    fix_terms: bool = Form(True, description="是否修正术语"),
    format: str = Form("wav", description="音频格式")
):
    """
    转录 Base64 编码的音频流
    
    参数:
    - audio_data: Base64 编码的音频数据（必需）
    - model: 模型大小（默认：small）
    - language: 语言代码（默认：zh）
    - fix_terms: 是否修正术语（默认：true）
    - format: 音频格式（默认：wav）
    
    返回:
    - text: 转录文本
    - corrections: 术语修正详情
    """
    temp_file = None
    
    try:
        # 解码 Base64 音频数据
        audio_bytes = base64.b64decode(audio_data)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
            temp_file = tmp.name
            tmp.write(audio_bytes)
        
        # 获取 Whisper 实例
        whisper = get_whisper_instance(model)
        
        # 转录
        result = whisper.transcribe(
            temp_file,
            language=language,
            fix_programmer_terms=fix_terms
        )
        
        # 构建响应
        response = {
            "success": True,
            "text": result.get("text", ""),
            "language": result.get("language", language)
        }
        
        if fix_terms:
            corrections = whisper.dict_manager.get_corrections()
            stats = whisper.get_dict_stats()
            
            response["corrections"] = {
                "count": stats.get("replacements_made", 0),
                "details": corrections
            }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket 实时转录接口
    
    客户端发送 JSON 消息：
    {
        "action": "start",  // 开始会话
        "model": "small",
        "language": "zh"
    }
    
    {
        "action": "audio",  // 发送音频数据
        "data": "base64_encoded_audio"
    }
    
    {
        "action": "end"  // 结束会话并转录
    }
    
    服务器响应：
    {
        "type": "status",
        "message": "会话已开始"
    }
    
    {
        "type": "result",
        "text": "转录结果",
        "corrections": {...}
    }
    """
    await websocket.accept()
    
    # 会话状态
    session = {
        "model": "small",
        "language": "zh",
        "audio_chunks": [],
        "temp_file": None
    }
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "start":
                # 开始新会话
                session["model"] = message.get("model", "small")
                session["language"] = message.get("language", "zh")
                session["audio_chunks"] = []
                
                await websocket.send_json({
                    "type": "status",
                    "message": f"会话已开始，模型: {session['model']}"
                })
            
            elif action == "audio":
                # 接收音频数据
                audio_data = message.get("data")
                if audio_data:
                    session["audio_chunks"].append(audio_data)
                    
                    await websocket.send_json({
                        "type": "status",
                        "message": f"已接收音频块 {len(session['audio_chunks'])}"
                    })
            
            elif action == "end":
                # 结束会话并转录
                if not session["audio_chunks"]:
                    await websocket.send_json({
                        "type": "error",
                        "message": "没有音频数据"
                    })
                    continue
                
                try:
                    # 合并所有音频块
                    combined_audio = b"".join([
                        base64.b64decode(chunk)
                        for chunk in session["audio_chunks"]
                    ])
                    
                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        session["temp_file"] = tmp.name
                        tmp.write(combined_audio)
                    
                    # 转录
                    whisper = get_whisper_instance(session["model"])
                    result = whisper.transcribe(
                        session["temp_file"],
                        language=session["language"],
                        fix_programmer_terms=True
                    )
                    
                    # 发送结果
                    corrections = whisper.dict_manager.get_corrections()
                    stats = whisper.get_dict_stats()
                    
                    await websocket.send_json({
                        "type": "result",
                        "text": result.get("text", ""),
                        "language": result.get("language", session["language"]),
                        "corrections": {
                            "count": stats.get("replacements_made", 0),
                            "details": corrections
                        }
                    })
                    
                    # 清理
                    session["audio_chunks"] = []
                    if session["temp_file"] and os.path.exists(session["temp_file"]):
                        os.remove(session["temp_file"])
                        session["temp_file"] = None
                
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"转录失败: {str(e)}"
                    })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"未知操作: {action}"
                })
    
    except WebSocketDisconnect:
        print("WebSocket 连接已断开")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        # 清理临时文件
        if session.get("temp_file") and os.path.exists(session["temp_file"]):
            try:
                os.remove(session["temp_file"])
            except:
                pass


def main():
    """
    启动 CodeWhisper API 服务器
    
    支持的命令行参数：
    =================
    
    1. --host
       - 说明：服务器绑定的 IP 地址
       - 默认值：0.0.0.0（监听所有网络接口）
       - 可选值：
         * 0.0.0.0 - 监听所有网卡，允许外部访问
         * 127.0.0.1 - 仅本地访问
         * 192.168.x.x - 局域网特定 IP
       - 使用示例：
         # 允许外部访问
         python api_server.py --host 0.0.0.0
         
         # 仅本地访问
         python api_server.py --host 127.0.0.1
         
         # 指定局域网 IP
         python api_server.py --host 192.168.1.100
    
    2. --port
       - 说明：服务器监听的端口号
       - 默认值：8000
       - 可选值：1-65535 之间的任意端口
       - 使用示例：
         # 使用默认端口
         python api_server.py
         
         # 指定端口
         python api_server.py --port 8080
         
         # 使用 80 端口（HTTP 默认端口）
         sudo python api_server.py --port 80
         
         # 使用 443 端口（HTTPS 默认端口，需要 SSL 证书）
         sudo python api_server.py --port 443
       - 注意事项：
         * 端口 < 1024 需要管理员权限
         * 确保端口未被占用
         * 防火墙需要允许该端口
    
    3. --reload
       - 说明：启用开发模式，代码修改后自动重载
       - 默认值：False（禁用）
       - 类型：布尔开关（指定即启用）
       - 使用示例：
         # 启用自动重载（开发环境）
         python api_server.py --reload
         
         # 禁用自动重载（生产环境）
         python api_server.py
       - 适用场景：
         * 开发调试时：启用，方便实时测试修改
         * 生产环境：禁用，避免不必要的性能开销
       - 注意事项：
         * 自动重载会增加内存占用
         * 可能导致意外的连接中断
         * 生产环境建议关闭
    
    4. --model
       - 说明：预加载的 Whisper 模型
       - 默认值：small
       - 可选值：tiny, base, small, medium, large
       - 模型对比：
         | 模型   | 大小   | 速度   | 准确率 | 显存占用  |
         |--------|--------|--------|--------|-----------|
         | tiny   | ~39 MB | 最快   | 较低   | ~1 GB     |
         | base   | ~74 MB | 很快   | 一般   | ~1-2 GB   |
         | small  | ~244 MB| 较快   | 较高   | ~2-4 GB   |
         | medium | ~769 MB| 中等   | 高     | ~4-8 GB   |
         | large  | ~1550 MB| 较慢   | 最高   | ~8-16 GB  |
       - 使用示例：
         # 使用小模型（最快）
         python api_server.py --model tiny
         
         # 使用中等模型（平衡）
         python api_server.py --model medium
         
         # 使用大模型（最准确）
         python api_server.py --model large
         
         # 不预加载模型（首次请求时加载）
         python api_server.py
       - 选择建议：
         * 实时应用：tiny 或 base
         * 一般应用：small（推荐）
         * 高准确率：medium 或 large
         * 根据硬件配置选择
       - 注意事项：
         * 大模型需要更多显存和内存
         * 首次加载需要较长时间
         * 预加载可以减少首次请求延迟
    
    完整使用示例：
    ==============
    
    # 开发环境（自动重载、本地访问）
    python api_server.py --reload --host 127.0.0.1 --port 8000
    
    # 生产环境（无重载、外部访问）
    python api_server.py --host 0.0.0.0 --port 8000 --model medium
    
    # 高性能服务器（使用大模型）
    python api_server.py --host 0.0.0.0 --port 8000 --model large
    
    # 资源受限环境（使用小模型）
    python api_server.py --host 0.0.0.0 --port 8000 --model tiny

    python api_server.py --host 192.168.1.143 --port 8888 --model medium
    
    # 查看帮助信息
    python api_server.py --help
    """
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="CodeWhisper API Server - 语音转文字 API 服务",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加命令行参数
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器绑定的 IP 地址 (默认: 0.0.0.0，监听所有网卡)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器监听的端口号 (默认: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用开发模式，代码修改后自动重载 (默认: 禁用)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="预加载的 Whisper 模型大小 (默认: small)"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 预加载指定模型
    print(f"🚀 启动 CodeWhisper API Server")
    print(f"📦 预加载模型: {args.model}")
    whisper = get_whisper_instance(args.model)
    
    # 显示服务器信息
    print(f"\n🌐 服务器配置:")
    print(f"   地址: http://{args.host}:{args.port}")
    print(f"   自动重载: {'启用' if args.reload else '禁用'}")
    print(f"   模型: {args.model}")
    
    print(f"\n📖 访问地址:")
    print(f"   API 文档: http://{args.host}:{args.port}/docs")
    print(f"   交互式文档: http://{args.host}:{args.port}/redoc")
    print(f"   健康检查: http://{args.host}:{args.port}/api/health")
    
    print(f"\n💡 提示: 按 Ctrl+C 停止服务器")
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
