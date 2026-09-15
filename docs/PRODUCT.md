# Product Description -- 通用 Harness 底座

## 这是什么

一个可复用的项目底座：为后续 AI 编码智能体项目提供"可靠运行环境"（harness）与混合栈骨架。前端界面用 Node/TypeScript，内核逻辑用 Python。

## 要解决的问题

让智能体在真实仓库里、跨多个会话、无需人工持续监督地可靠完成工程任务。核心理念来自 learn-harness-engineering 教程：

> 模型决定写什么代码；harness 决定何时、何地、如何写。harness 不改变模型聪明程度，而是让模型的产出可靠。

## 核心能力（底座提供）

1. **Instructions**：`AGENTS.md`/`CLAUDE.md` 定义启动流程、边界、完成标准。
2. **State**：`feature_list.json` 追踪功能状态，`progress.md` 记录会话连续性。
3. **Verification**：`init.sh`/`init.ps1` 一键跑通前端 check/test/build + 后端 pytest。
4. **Scope**：feature 的 dependencies 与 Definition of Done 防止越界与半成品。
5. **Lifecycle**：`session-handoff.md` + 收尾流程，保证下次会话可重启。

## 后续项目如何用它

- **直接在此骨架上新增业务 feature**：先 `backend/` 内核 + pytest，再 `frontend/` 界面 + npm test。
- **作为场景接入**：在 `scenarios/<name>/` 下新建自包含落地场景（自带 backend/frontend/requirements/package.json/init），底座保持纯净，多个场景可并列共存。
- **复制底座到新项目**：`node scripts/create-harness.mjs --target <新项目>` 生成纯底座骨架；`--with-scenario <name>` 可连同某个落地场景一起复制。
- 每个功能都遵循"一次只做一个 → 验证 → 记录证据"的循环。

## 场景机制

底座是通用 harness 模板，`scenarios/<name>/` 是落地应用实例：

- 底座只提供五子系统 + 派生工具 + 最小自证骨架（`greeting.ts` / `math_ops.py`），证明验证管道可跑通。
- 场景自包含：独立依赖、独立验证、独立复制；真实业务代码由场景自带，不污染底座。
- 第一个场景 `scenarios/code-assistant/`（自主智能体对话框）演示了完整的「底座 + 场景」组合。

## 约束

- 前端 Node/TypeScript，后端 Python，边界不可跨越（详见 `docs/ARCHITECTURE.md`）。
- 验证是唯一完成证据，无验证不完成。
- harness 文件是给智能体读的，不是运行时依赖。
