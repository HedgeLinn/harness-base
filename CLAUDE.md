# CLAUDE.md

本文件是 Claude Code 的快捷参考。完整规则见 `AGENTS.md`（智能体必须先读它）。

## 项目概览

通用 harness 底座：前端界面 Node/TypeScript（`frontend/`），内核逻辑 Python（`backend/`），`docs/` 为架构与产品文档，`scripts/` 为 harness 审计工具。落地场景放 `scenarios/<name>/`（自包含应用），底座保持纯净。

## 命令

```bash
./init.sh          # 完整验证：安装依赖 + 前端检查/测试/构建 + 后端 pytest

# 前端（frontend/）
npm run check      # 类型检查
npm test           # 单元测试
npm run build      # 构建

# 后端（backend/）
python -m pytest   # 单元测试

# 场景（scenarios/<name>/，自包含，独立验证）
./init.sh          # 在场景目录下运行

# harness 自审计
node scripts/validate-harness.mjs --target .
node scripts/create-harness.mjs --target <某项目目录>
node scripts/create-harness.mjs --target <某项目目录> --with-scenario <场景名>
```

## 关键文件

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 智能体操作手册（启动流程、边界、完成定义） |
| `feature_list.json` | 功能状态追踪（事实来源） |
| `progress.md` | 会话连续性日志 |
| `session-handoff.md` | 会话交接模板 |
| `init.sh` | 标准启动与验证入口 |
| `docs/ARCHITECTURE.md` | 分层边界 |
| `docs/PRODUCT.md` | 需求 |
| `scenarios/<name>/` | 落地场景（自包含应用） |

## 分层规则

- `frontend/`（Node）只通过接口调 `backend/`，不直接读写内核数据。
- `backend/`（Python）纯逻辑，不 import 前端代码。
- 落地场景放 `scenarios/<name>/`，底座保持纯净；场景内部仍遵守 frontend/backend 边界。
- 边界细节见 `docs/ARCHITECTURE.md`。

## 如何加一个功能

1. 在 `feature_list.json` 里新增一条 feature（含 dependencies）。
2. 在 `backend/` 实现内核逻辑，补 pytest 测试。
3. 在 `frontend/` 实现界面，补 `npm test`。
4. 跑 `./init.sh` 验证。
5. 在 `feature_list.json` 记录 evidence，更新 `progress.md`。
