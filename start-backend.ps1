Set-Location $PSScriptRoot\back

$pythonCandidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "python"
)

$python = $pythonCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $python) {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if (-not $python) {
    Write-Host "Python을 찾을 수 없습니다. python.org 에서 3.10+ 설치 후 다시 실행하세요." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "back\.env 파일이 없습니다." -ForegroundColor Yellow
    Write-Host "back\.env.example 을 복사한 뒤 OPENAI_API_KEY 를 입력하세요." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    exit 1
}

# MongoDB (Docker) — 없으면 자동 기동
$mongoRunning = docker ps --filter "name=chatbot-mongo" --filter "status=running" -q 2>$null
if (-not $mongoRunning) {
    Write-Host "MongoDB Docker 컨테이너 시작 중..." -ForegroundColor Cyan
    docker start chatbot-mongo 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker run -d --name chatbot-mongo -p 27017:27017 mongo:7
    }
}

Write-Host "백엔드 시작 (http://127.0.0.1:8000)..." -ForegroundColor Cyan
& $python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
