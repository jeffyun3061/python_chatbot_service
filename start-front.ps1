Set-Location $PSScriptRoot\front

if (-not (Test-Path "node_modules")) {
    Write-Host "의존성 설치 중..." -ForegroundColor Cyan
    npm install
}

Write-Host "프론트 시작 (Parcel)..." -ForegroundColor Cyan
npm start
