#!/bin/bash
# CodeWhisper API 测试脚本

API_URL="http://localhost:8000"

echo "================================"
echo "CodeWhisper API 测试"
echo "================================"

# 1. 健康检查
echo -e "\n1. 健康检查..."
curl -s "${API_URL}/api/health" | python -m json.tool

# 2. 列出模型
echo -e "\n2. 列出模型..."
curl -s "${API_URL}/api/models" | python -m json.tool

# 3. 获取统计信息
echo -e "\n3. 获取统计信息..."
curl -s "${API_URL}/api/stats" | python -m json.tool

# 4. 转录文件（需要提供音频文件）
if [ -f "test.wav" ]; then
    echo -e "\n4. 转录文件..."
    curl -X POST "${API_URL}/api/transcribe" \
      -F "file=@test.wav" \
      -F "model=small" \
      -F "language=zh" \
      -F "verbose=true" \
      | python -m json.tool
else
    echo -e "\n4. 跳过文件转录（test.wav 不存在）"
fi

echo -e "\n================================"
echo "测试完成"
echo "================================"
