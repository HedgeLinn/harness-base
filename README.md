# harness-base

> 让 AI 编码智能体**可靠**工作的通用运行底座。
> A reusable harness that makes AI coding agents work *reliably*.

中文 · [English](#english-version) · TypeScript · Node · Python

---

## 问题 The Problem

用 AI 写代码，瓶颈往往不是模型能力，而是**环境**：

- 规则散落在聊天记录里，每个新会话都要从零解释上下文；
- 进度无法跨会话，上一次做到哪、卡在哪，没有记录；
- 智能体说「做完了」，却没有客观证据，无法求证；
- 智能体可以随手改任意文件，越界了也没人拦。

模型决定**写什么代码**；harness 决定**何时、何地、如何写**。harness 不改变模型的聪明程度，而是让模型的产出**可靠**。

## 做法 The Approach

把「让智能体可靠工作」需要的东西，抽象成**五个子系统**，固化成仓库内的文件契约：

| 子系统 Subsystem | 文件 Files | 管什么 What it governs |
|---|---|---|
| **Instructions** 规则 | `AGENTS.md` / `CLAUDE.md` | 启动流程、边界、完成标准 |
| **State** 状态 | `feature_list.json` / `progress.md` | 功能状态、会话连续性 |
| **Verification** 验证 | `init.sh` / `init.ps1` | 一键跑通前端 check/test/build + 后端 pytest |
| **Scope** 范围 | `feature_list.json` dependencies | 一次只做一个功能，防越界与半成品 |
| **Lifecycle** 交接 | `session-handoff.md` | 收尾流程，保证下次会话可重启 |

核心机制是**底座 + 场景分层**：

```
harness-base/
├── (底座根 = 纯 harness 模板，不承载业务)
├── backend/         # Python 内核最小自证骨架
├── frontend/        # Node/TypeScript 界面最小自证骨架
├── scripts/         # 派生与自审计工具
├── templates/       # 派生模板
└── scenarios/
    └── code-assistant/    # 第一个落地场景：自主智能体对话框（自包含）
```

底座根保持**纯净**，具体业务作为**自包含场景**放进 `scenarios/<name>/`——自带依赖、自带验证、可独立复制、多场景可并列共存。验证是唯一的完成证据，不跑验证不算做完。

## 亮点 Highlights

- **验证 = 唯一证据。** `./init.sh` 通过才算功能完成；测试、类型检查、构建的证据必须记录。
- **自审计给 harness 自己打分。** `node scripts/validate-harness.mjs --target .` 按五子系统给底座本身打分——当前 **100/100**（每个检查项都能在 `scripts/lib/harness-utils.mjs` 里看到它怎么打分，避免「关键词凑分」只统计结构化条）。
- **契约先行。** 接口合同与运行文档（`AGENTS.md`、`docs/ARCHITECTURE.md`）是事实来源，改了要同步，不允许悄悄漂移。
- **把原理跑在明处。** 能用清晰的 while 循环说清的事，不引入框架遮蔽它。

## 快速开始 Quick Start

```bash
# 完整验证（底座健康自检：安装依赖 + 前端 check/test/build + 后端 pytest）
./init.sh                          # Windows: powershell -ExecutionPolicy Bypass -File .\init.ps1

# harness 自审计
node scripts/validate-harness.mjs --target .
```

### 启动第一个场景 code-assistant

`scenarios/code-assistant/` 是一个**小型自主智能体对话框**：识别意图 → 编排计划 → 分步执行 → 归因审计，并受边界白名单约束。

```bash
# 后端（FastAPI）
cd scenarios/code-assistant/backend && python -m uvicorn core.agent.server:app --port 8000

# 前端（Vite，新的终端）
cd scenarios/code-assistant/frontend && npm install && npm run dev
```

浏览器打开 Vite 地址（默认 `http://localhost:5173`），输入「列出 backend 下的文件」「运行 git status」等指令，右侧「执行链 · 归因审计」面板展示每一步归因链；越界命令（如 `rm -rf`）会被拒绝并记录。

## 如何加一个功能 How to Add a Feature

1. 在 `feature_list.json` 新增一条 feature（含 `dependencies` 与完成标准）。
2. 在 `backend/` 实现内核逻辑，补 pytest 测试。
3. 在 `frontend/` 实现界面，补 `npm test`。
4. 跑 `./init.sh` 验证，证据记录到 `feature_list.json`，更新 `progress.md`。

> 一次只做一个功能；不跑验证不声称完成；留干净状态让下次会话能直接重启。

## 复制底座到新项目 Derive a New Project

```bash
node scripts/create-harness.mjs --target <新项目目录>                 # 纯底座骨架
node scripts/create-harness.mjs --target <新项目目录> --with-scenario code-assistant  # 带场景一起复制
```

`scripts/` 里的派生工具会自动按目标目录的工程形态（TypeScript / React / Python / Go / Rust / Java / .NET…）探测验证命令并生成对应的 `init.sh`。

## 目录结构 Repository Layout

```
harness-base/
├── AGENTS.md / CLAUDE.md          # 智能体操作手册（启动流程、边界、完成定义）
├── feature_list.json              # 功能状态追踪（事实来源）
├── progress.md                    # 会话连续性日志
├── session-handoff.md             # 会话交接模板
├── init.sh / init.ps1             # 标准启动与验证入口
├── docs/                          # ARCHITECTURE.md（分层边界）/ PRODUCT.md（需求）
├── backend/                       # 底座最小自证骨架（Python，math_ops）
├── frontend/                      # 底座最小自证骨架（Node/TS，greeting.ts）
├── scripts/ + templates/          # 派生工具（create-harness / validate-harness）与模板
└── scenarios/                     # 落地场景（自包含应用）
    └── code-assistant/            # 第一个场景：自主智能体对话框
```

## 设计原则 Principles

- **前端与后端仅通过接口通信**，不得直接共享内存或跨层 import（前端 Node / 内核 Python 边界不可跨越）。
- **验证是唯一证据**：只有 `./init.sh`（或等价命令）通过才算功能完成。
- **harness 文件不被业务代码依赖**：它们是给智能体读的，不是运行时依赖。
- **底座保持纯净**：具体业务放 `scenarios/<name>/`，底座根不承载场景代码。

## 相关文档 Related Docs

- `docs/ARCHITECTURE.md` — 分层边界与数据流
- `docs/PRODUCT.md` — 需求与设计动机
- `scenarios/code-assistant/README.md` — 第一个场景的使用与配置

---

## English Version

A reusable *harness base* — the reliability infrastructure around the code, not the code itself.

**Problem.** When AI writes code, the bottleneck is usually the environment, not the model: rules live in chat history, progress doesn't survive sessions, "done" claims have no evidence, and the agent can edit any file unrestrained.

**Approach.** Abstract what it takes to make an agent reliable into five subsystems — **Instructions, State, Verification, Scope, Lifecycle** — and freeze them as file contracts in the repo. Verification is the only evidence of completion. The base stays *pure*; concrete applications live as self-contained **scenarios** under `scenarios/<name>/`, each with its own dependencies, validation, and the ability to be copied out.

**Highlights.**

- `./init.sh` is the single entrypoint: frontend check/test/build + backend pytest. Nothing is "done" until it passes.
- **Self-audit for the harness itself**: `node scripts/validate-harness.mjs` scores the repo across the five subsystems — currently **100/100** (every check is inspectable in `scripts/lib/harness-utils.mjs`).
- **Contracts first.** `AGENTS.md` and `docs/ARCHITECTURE.md` are the source of truth; drift is not allowed silently.
- **Run the principle in the open.** If a plain loop can express it, don't bury it under a framework.

**First scenario** — `scenarios/code-assistant/`: a small autonomous agent chat window that runs intent → plan → execute → trace under a boundary whitelist. Out-of-scope commands (e.g. `rm -rf`) are rejected and logged.

**To add a feature**: add it to `feature_list.json` → implement in `backend/` + pytest → UI in `frontend/` + `npm test` → run `./init.sh` → record evidence.

**To derive a new project**: `node scripts/create-harness.mjs --target <dir> [--with-scenario code-assistant]`.
