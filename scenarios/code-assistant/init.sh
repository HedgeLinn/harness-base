#!/bin/bash
# init.sh -- 代码仓库助手场景的验证入口。
# 在 scenarios/code-assistant/ 下运行。Windows 用 Git Bash / WSL，或改用 init.ps1。
set -euo pipefail

echo "=== [code-assistant] Verification ==="
echo ""

# --- 后端：Python（FastAPI + agent 执行链）---
if [ -f backend/requirements.txt ]; then
  PY="$(command -v python3 || command -v python)"
  echo "=== [backend] Installing dependencies ==="
  "$PY" -m pip install -r backend/requirements.txt
  echo ""

  echo "=== [backend] Unit tests (pytest) ==="
  (cd backend && "$PY" -m pytest) || { code=$?; if [ "$code" -ne 5 ]; then exit "$code"; fi; }
  echo ""
else
  echo "=== [backend] requirements.txt 不存在，跳过后端验证 ==="
fi

# --- 前端：Node/TypeScript（Vite 对话框）---
if [ -f frontend/package.json ]; then
  echo "=== [frontend] Installing dependencies (npm) ==="
  (cd frontend && npm install)
  echo ""

  echo "=== [frontend] Type check ==="
  (cd frontend && npm run check)
  echo ""

  echo "=== [frontend] Unit tests ==="
  (cd frontend && npm test)
  echo ""

  echo "=== [frontend] Build ==="
  (cd frontend && npm run build)
  echo ""
else
  echo "=== [frontend] package.json 不存在，跳过前端验证 ==="
fi

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Start backend: cd backend && python -m uvicorn core.agent.server:app --port 8000"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Open the dialog and try commands like: 列出 backend 下的文件 / 运行 git status"
