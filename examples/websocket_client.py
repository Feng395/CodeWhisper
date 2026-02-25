#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CodeWhisper WebSocket 客户端示例

演示如何使用 WebSocket 实时发送语音数据
"""

import asyncio
import base64
import json
import wave
from pathlib import Path

try:
    import websockets
except ImportError:
    print("请安装 websockets: pip install websockets")
    exit(1)


async def transcribe_with_websocket(audio_file: str, server_url: str = "ws://localhost:8000/ws/transcribe"):
    """
    使用 WebSocket 转录音频文件
    
    Args:
        audio_file: 音频文件路径
        server_url: WebSocket 服务器地址
    """
    async with websockets.connect(server_url) as websocket:
        print(f"✅ 已连接到服务器: {server_url}")
        
        # 1. 开始会话
        await websocket.send(json.dumps({
            "action": "start",
            "model": "small",
            "language": "zh"
        }))
        
        response = await websocket.recv()
        print(f"📝 {json.loads(response)['message']}")
        
        # 2. 读取并发送音频数据
        print(f"🎵 读取音频文件: {audio_file}")
        
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        # 分块发送（模拟实时流）
        chunk_size = 4096  # 每次发送 4KB
        total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            encoded_chunk = base64.b64encode(chunk).decode('utf-8')
            
            await websocket.send(json.dumps({
                "action": "audio",
                "data": encoded_chunk
            }))
            
            response = await websocket.recv()
            msg = json.loads(response)
            print(f"📤 {msg['message']}")
            
            # 模拟实时发送延迟
            await asyncio.sleep(0.1)
        
        # 3. 结束会话并获取结果
        print("\n⏳ 正在转录...")
        await websocket.send(json.dumps({
            "action": "end"
        }))
        
        response = await websocket.recv()
        result = json.loads(response)
        
        if result["type"] == "result":
            print("\n" + "=" * 60)
            print("✅ 转录完成！")
            print("=" * 60)
            print(f"\n📝 转录结果:\n{result['text']}\n")
            print(f"🌐 语言: {result['language']}")
            print(f"🔧 修正次数: {result['corrections']['count']}")
            
            if result['corrections']['details']:
                print("\n修正详情:")
                for correction in result['corrections']['details']:
                    print(f"  • {correction['wrong']} → {correction['correct']} ({correction['category']})")
        else:
            print(f"\n❌ 错误: {result.get('message', '未知错误')}")


async def transcribe_realtime_simulation():
    """
    模拟实时语音转录
    
    这个示例展示如何在实际应用中使用 WebSocket
    """
    server_url = "ws://localhost:8000/ws/transcribe"
    
    async with websockets.connect(server_url) as websocket:
        print("🎤 模拟实时语音转录")
        print("=" * 60)
        
        # 开始会话
        await websocket.send(json.dumps({
            "action": "start",
            "model": "small",
            "language": "zh"
        }))
        
        response = await websocket.recv()
        print(f"✅ {json.loads(response)['message']}")
        
        # 模拟从麦克风捕获音频
        print("\n🎙️  正在录音...")
        print("   (实际应用中，这里会从麦克风实时捕获音频)")
        
        # 这里应该是实时音频捕获的循环
        # 示例：使用 sounddevice 或 pyaudio 捕获音频
        # while recording:
        #     audio_chunk = capture_audio()
        #     encoded = base64.b64encode(audio_chunk).decode('utf-8')
        #     await websocket.send(json.dumps({
        #         "action": "audio",
        #         "data": encoded
        #     }))
        
        print("   按 Enter 停止录音...")
        # input()  # 实际应用中可能是按钮或其他触发方式
        
        # 结束并获取结果
        await websocket.send(json.dumps({
            "action": "end"
        }))
        
        response = await websocket.recv()
        result = json.loads(response)
        
        if result["type"] == "result":
            print(f"\n✅ 转录结果: {result['text']}")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if not Path(audio_file).exists():
            print(f"❌ 文件不存在: {audio_file}")
            return
        
        print(f"🚀 使用 WebSocket 转录音频文件")
        asyncio.run(transcribe_with_websocket(audio_file))
    else:
        print("用法:")
        print("  python websocket_client.py <audio_file>")
        print("\n示例:")
        print("  python websocket_client.py test.wav")
        print("\n或者查看实时转录模拟:")
        print("  # 取消注释 transcribe_realtime_simulation() 调用")


if __name__ == "__main__":
    main()
