#!/bin/bash
# init.sh -- 验证底座能干净构建并跑通验证。
# 克隆后或恢复工作时运行。Windows 用 Git Bash / WSL 运行，或改用 init.ps1。
set -euo pipefail

echo "=== Harness Initialization ==="
echo ""

# --- 前端：Node/TypeScript ---
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

# --- 后端：Python ---
if [ -f backend/pyproject.toml ] || [ -f backend/requirements.txt ]; then
  PY="$(command -v python3 || command -v python)"
  echo "=== [backend] Installing dependencies ==="
  if [ -f backend/requirements.txt ]; then
    "$PY" -m pip install -r backend/requirements.txt
  fi
  echo ""

  echo "=== [backend] Unit tests (pytest) ==="
  # pytest 未收集到测试时退出码为 5，对空项目不算失败。
  (cd backend && "$PY" -m pytest) || { code=$?; if [ "$code" -ne 5 ]; then exit "$code"; fi; }
  echo ""
else
  echo "=== [backend] pyproject.toml / requirements.txt 不存在，跳过后端验证 ==="
fi

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Read feature_list.json to see current feature state"
echo "2. Pick ONE unfinished feature to work on"
echo "3. Implement only that feature"
echo "4. Re-run verification before claiming done"
