# CodeWhisper API 测试脚本 (PowerShell)

$API_URL = "http://localhost:8000"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "CodeWhisper API 测试" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. 健康检查
Write-Host "`n1. 健康检查..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/health" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

# 2. 列出模型
Write-Host "`n2. 列出模型..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/models" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

# 3. 获取统计信息
Write-Host "`n3. 获取统计信息..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/stats" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

# 4. 转录文件（需要提供音频文件）
if (Test-Path "test.wav") {
    Write-Host "`n4. 转录文件..." -ForegroundColor Yellow
    try {
        $form = @{
            file = Get-Item -Path "test.wav"
            model = "small"
            language = "zh"
            verbose = "true"
        }
        $response = Invoke-RestMethod -Uri "$API_URL/api/transcribe" -Method Post -Form $form
        $response | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "错误: $_" -ForegroundColor Red
    }
} else {
    Write-Host "`n4. 跳过文件转录（test.wav 不存在）" -ForegroundColor Gray
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
