# init.ps1 -- 代码仓库助手场景的验证入口（PowerShell 版）。
# 在 scenarios/code-assistant/ 下运行：powershell -ExecutionPolicy Bypass -File .\init.ps1
$ErrorActionPreference = 'Stop'

Write-Host "=== [code-assistant] Verification ==="

# --- 后端：Python（FastAPI + agent 执行链）---
if (Test-Path 'backend\requirements.txt') {
  Write-Host "`n=== [backend] Installing dependencies ==="
  python -m pip install -r backend\requirements.txt
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  Write-Host "`n=== [backend] Unit tests (pytest) ==="
  Push-Location backend
  python -m pytest
  $code = $LASTEXITCODE
  Pop-Location
  if ($code -ne 0 -and $code -ne 5) { exit $code }
} else {
  Write-Host "`n=== [backend] requirements.txt 不存在，跳过后端验证 ==="
}

# --- 前端：Node/TypeScript（Vite 对话框）---
if (Test-Path 'frontend\package.json') {
  Write-Host "`n=== [frontend] Installing dependencies (npm) ==="
  Push-Location frontend
  npm install
  if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }

  Write-Host "`n=== [frontend] Type check ==="
  npm run check
  if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }

  Write-Host "`n=== [frontend] Unit tests ==="
  npm test
  if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }

  Write-Host "`n=== [frontend] Build ==="
  npm run build
  if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
  Pop-Location
} else {
  Write-Host "`n=== [frontend] package.json 不存在，跳过前端验证 ==="
}

Write-Host "`n=== Verification Complete ==="
Write-Host "Next steps:"
Write-Host "1. Start backend: cd backend; python -m uvicorn core.agent.server:app --port 8000"
Write-Host "2. Start frontend: cd frontend; npm run dev"
Write-Host "3. Open the dialog and try commands like: 列出 backend 下的文件 / 运行 git status"
