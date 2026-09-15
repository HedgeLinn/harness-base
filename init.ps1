# init.ps1 -- Windows 下的验证入口（PowerShell 版）。
# 用法：powershell -ExecutionPolicy Bypass -File .\init.ps1
$ErrorActionPreference = 'Stop'

Write-Host "=== Harness Initialization ==="

# --- 前端：Node/TypeScript ---
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

# --- 后端：Python ---
if ((Test-Path 'backend\pyproject.toml') -or (Test-Path 'backend\requirements.txt')) {
  Write-Host "`n=== [backend] Installing dependencies ==="
  if (Test-Path 'backend\requirements.txt') {
    python -m pip install -r backend\requirements.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }

  Write-Host "`n=== [backend] Unit tests (pytest) ==="
  Push-Location backend
  python -m pytest
  $code = $LASTEXITCODE
  Pop-Location
  # pytest 未收集到测试时退出码为 5，对空项目不算失败。
  if ($code -ne 0 -and $code -ne 5) { exit $code }
} else {
  Write-Host "`n=== [backend] pyproject.toml / requirements.txt 不存在，跳过后端验证 ==="
}

Write-Host "`n=== Verification Complete ==="
Write-Host "Next steps:"
Write-Host "1. Read feature_list.json to see current feature state"
Write-Host "2. Pick ONE unfinished feature to work on"
Write-Host "3. Implement only that feature"
Write-Host "4. Re-run verification before claiming done"
