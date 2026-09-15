# AGENTS.md

这是本仓库的智能体操作手册。任何 AI 编码智能体（Claude Code、Codex、Cursor 等）在动手前都必须先读本文件。

## 项目概览

通用 harness 工作区：为后续任意 AI 编码智能体项目提供可靠运行环境（底座）。前端界面用 Node/TypeScript，内核逻辑用 Python，二者通过进程间通信（IPC / HTTP / stdio）解耦。

## Startup Workflow（启动流程）

Before writing code（动手前，按顺序执行）：

1. **确认工作目录**：运行 `pwd`（或 `Get-Location`）。
2. **读完本文件**：它定义了边界、约定和完成标准。
3. **读架构与产品文档**：`docs/ARCHITECTURE.md`（分层边界）、`docs/PRODUCT.md`（需求）。
4. **运行 `./init.sh`**：验证环境健康（安装依赖 + 前端检查 + 后端测试）。失败则先修复再继续。
5. **读 `feature_list.json`**：了解当前功能状态。
6. **回顾最近提交**：`git log --oneline -5`。

## Working Rules（工作规则）

- **One feature at a time（一次只做一个功能）**：从 `feature_list.json` 里挑恰好一个未完成功能，只做它。
- **Stay in scope（守边界）**：不修改与当前功能无关的文件，不顺手重构。
- **Verification required（必须验证）**：没跑验证命令前不得声称"完成"。
- **Update artifacts（更新工件）**：会话结束前更新 `progress.md` 和 `feature_list.json`。
- **Leave clean state（留干净状态）**：下次会话必须能直接 `./init.sh` 成功。

## 分层边界

本项目是混合栈，边界不可跨越：

- **`frontend/`**：Node/TypeScript 界面层，只通过定义好的接口调用后端，不直接读写内核数据。
- **`backend/`**：Python 内核逻辑层，纯业务计算，不依赖前端，不 import 前端代码。
- **`docs/`**：架构与产品文档，是事实来源，代码改动需同步更新。
- **`scripts/`**：harness 自身的脚手架与审计工具，与业务代码无关。
- **`scenarios/<name>/`**：落地场景（自包含应用）。底座保持纯净，具体业务放这里；场景内部仍遵守 frontend/backend 边界。

## Definition of Done（完成定义）

一个功能只有在**全部**满足以下条件时才算 done：

- [ ] 目标行为已实现
- [ ] 验证命令实际跑过（前端 `npm run check`/`test`/`build`，后端 `pytest`）
- [ ] 证据记录在 `feature_list.json` 或 `progress.md` 中
- [ ] 仓库仍能从标准启动路径重启（`./init.sh` 通过）

## Verification Commands（验证命令）

```bash
# 完整验证（推荐）
./init.sh
```

前端（在 `frontend/` 目录）：

- `npm run check` — 类型检查
- `npm test` — 单元测试
- `npm run build` — 构建

后端（在 `backend/` 目录）：

- `python -m pytest` — 单元测试

## End of Session（会话收尾）

Before ending（结束前）：

1. 更新 `progress.md` 记录当前状态。
2. 更新 `feature_list.json` 的功能状态。
3. 记录未解决的风险或阻塞。
4. 工作处于安全状态时用描述性信息提交。
5. 留下足够干净的状态，让下次会话能立即 `./init.sh`。

## 升级路径

遇到以下情况时：

- **架构决策**：查 `docs/ARCHITECTURE.md`，没有则问用户。
- **需求不清晰**：查 `docs/PRODUCT.md`，没有则问用户。
- **反复测试失败**：更新 progress，标记为人工复核。
- **范围模糊**：重读 `feature_list.json` 的完成定义。
