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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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


def main():
    """启动 API 服务器"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeWhisper API Server")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    parser.add_argument("--model", default="small", help="预加载的模型")
    
    args = parser.parse_args()
    
    # 预加载模型
    print(f"🚀 启动 CodeWhisper API Server")
    print(f"📦 预加载模型: {args.model}")
    get_whisper_instance(args.model)
    
    print(f"🌐 服务器地址: http://{args.host}:{args.port}")
    print(f"📖 API 文档: http://{args.host}:{args.port}/docs")
    print(f"🔧 交互式文档: http://{args.host}:{args.port}/redoc")
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
