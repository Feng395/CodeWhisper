#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CodeWhisper API 客户端示例

演示如何调用 CodeWhisper API
"""

import requests
from pathlib import Path


class CodeWhisperClient:
    """CodeWhisper API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API 服务器地址
        """
        self.base_url = base_url.rstrip("/")
    
    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()
    
    def list_models(self):
        """列出支持的模型"""
        response = requests.get(f"{self.base_url}/api/models")
        response.raise_for_status()
        return response.json()
    
    def transcribe_file(
        self,
        audio_file: str,
        model: str = "small",
        language: str = "zh",
        fix_terms: bool = True,
        learn: bool = True,
        verbose: bool = False
    ):
        """
        转录音频文件
        
        Args:
            audio_file: 音频文件路径
            model: 模型大小
            language: 语言代码
            fix_terms: 是否修正术语
            learn: 是否学习用户习惯
            verbose: 是否返回详细信息
        
        Returns:
            转录结果字典
        """
        with open(audio_file, "rb") as f:
            files = {"file": (Path(audio_file).name, f)}
            data = {
                "model": model,
                "language": language,
                "fix_terms": fix_terms,
                "learn": learn,
                "verbose": verbose
            }
            
            response = requests.post(
                f"{self.base_url}/api/transcribe",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    def transcribe_url(
        self,
        url: str,
        model: str = "small",
        language: str = "zh",
        fix_terms: bool = True,
        learn: bool = True
    ):
        """
        从 URL 转录音频文件
        
        Args:
            url: 音频文件 URL
            model: 模型大小
            language: 语言代码
            fix_terms: 是否修正术语
            learn: 是否学习用户习惯
        
        Returns:
            转录结果字典
        """
        data = {
            "url": url,
            "model": model,
            "language": language,
            "fix_terms": fix_terms,
            "learn": learn
        }
        
        response = requests.post(
            f"{self.base_url}/api/transcribe/url",
            data=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self):
        """获取统计信息"""
        response = requests.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()


def main():
    """示例用法"""
    # 创建客户端
    client = CodeWhisperClient("http://localhost:8000")
    
    # 健康检查
    print("🔍 健康检查...")
    health = client.health_check()
    print(f"   状态: {health['status']}")
    print(f"   已加载模型: {health['loaded_models']}")
    
    # 列出模型
    print("\n📦 支持的模型...")
    models = client.list_models()
    print(f"   可用模型: {models['models']}")
    print(f"   默认模型: {models['default']}")
    
    # 转录文件（示例）
    # audio_file = "test.wav"
    # if Path(audio_file).exists():
    #     print(f"\n🎵 转录文件: {audio_file}")
    #     result = client.transcribe_file(
    #         audio_file,
    #         model="small",
    #         language="zh",
    #         verbose=True
    #     )
    #     
    #     print(f"   文本: {result['text']}")
    #     print(f"   语言: {result['language']}")
    #     
    #     if 'corrections' in result:
    #         print(f"   修正次数: {result['corrections']['count']}")
    
    # 获取统计
    print("\n📊 统计信息...")
    stats = client.get_stats()
    print(f"   已加载模型: {stats.get('loaded_models', [])}")
    if 'dict_stats' in stats:
        print(f"   字典规则数: {stats['dict_stats'].get('total_rules', 0)}")


if __name__ == "__main__":
    main()
