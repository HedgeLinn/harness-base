# Architecture -- 通用 Harness 底座

## 系统概览

本仓库是"通用 harness 底座"：为后续任意 AI 编码智能体项目提供可靠运行环境。它本身不绑定具体业务，而是定义了混合栈的分层边界与验证管道。

技术栈：前端界面用 Node/TypeScript，内核逻辑用 Python，二者通过进程间通信（IPC / HTTP / stdio）解耦。

## 底座 + 场景分层

底座根保持**纯 harness 模板**，不承载具体业务；落地应用作为**场景**放进 `scenarios/<name>/`，自包含、可独立运行、可独立复制。

```
chat/  (底座根 = 纯 harness)
├── AGENTS.md / CLAUDE.md / feature_list.json / progress.md / session-handoff.md
├── init.sh / init.ps1                     # 只验证底座最小骨架
├── docs/ (ARCHITECTURE.md / PRODUCT.md)
├── scripts/ + templates/                  # 派生工具（create-harness --with-scenario）
├── backend/                               # 底座最小自证骨架（greeting / math_ops）
├── frontend/                              # 底座最小自证骨架（greeting.ts）
└── scenarios/                             # 落地场景（自包含）
    └── code-assistant/                    # 第一个场景：自主智能体对话框
        ├── README.md / feature_list.json / scenario.json
        ├── backend/  frontend/  docs/  init.sh / init.ps1
```

- **底座**只提供五子系统 + 派生工具 + 最小自证示例，证明「验证管道可跑通」。
- **场景**自带独立的 `requirements.txt` / `package.json` / `init.sh`，不依赖底座根的 frontend/backend；每个场景内部仍遵守「frontend 只走 HTTP 调 backend」的边界。

## 分层图

```
+-----------------------------------------------------------+
|                      frontend/ (Node)                      |
|  TypeScript 界面层，只通过接口调后端，不直接读内核数据      |
+-----------------------------------------------------------+
         |  定义好的接口（HTTP / IPC / stdio / 函数调用）
+-----------------------------------------------------------+
|                      backend/ (Python)                     |
|  内核业务逻辑层，纯计算，不 import 前端代码                 |
+-----------------------------------------------------------+
         |
+-----------------------------------------------------------+
|   harness 层（与业务无关）                                 |
|   AGENTS.md / CLAUDE.md / feature_list.json / progress.md  |
|   session-handoff.md / init.sh / scripts/ 审计工具          |
+-----------------------------------------------------------+
```

## 各层职责

### `frontend/`（Node/TypeScript）

- 界面与交互层。
- 只通过定义好的接口调用后端能力。
- 不直接读写内核数据存储，不 import 任何 `backend/` 代码。
- 验证：`npm run check`（类型）、`npm test`（单测）、`npm run build`（构建）。

### `backend/`（Python）

- 内核业务逻辑层（计算、数据、算法）。
- 纯逻辑，不依赖前端，不 import `frontend/` 代码。
- 验证：`python -m pytest`。

### harness 层

- 与业务代码无关的可靠性环境。
- 五子系统：Instructions（AGENTS.md/CLAUDE.md）、State（feature_list.json/progress.md）、Verification（init.sh + 各层验证命令）、Scope（feature 的 dependencies 与 done 标准）、Lifecycle（session-handoff.md + 收尾流程）。

## 关键不变量

- **前端与后端仅通过接口通信**，不得直接共享内存或跨层 import。
- **验证是唯一证据**：只有 `./init.sh` 通过（或等价命令）才算功能完成。
- **文档是事实来源**：改动架构或产品行为需同步 `docs/`。
- **harness 文件不被业务代码依赖**：它们是给智能体读的，不是运行时依赖。
- **底座保持纯净**：具体业务/落地应用放 `scenarios/<name>/`，底座根不承载场景代码。

## 场景如何接入

1. 在 `scenarios/<name>/` 下新建自包含目录（backend + frontend + 自己的 requirements.txt / package.json / init.sh）。
2. 场景内部仍遵守本文件的 frontend/backend 边界（前端只走 HTTP 调后端）。
3. 用派生工具复制：`node scripts/create-harness.mjs --target <目标> --with-scenario <name>`，会把底座元文件 + 指定场景一起复制过去。

## 数据流（示例）

1. 用户在 `frontend/` 触发操作。
2. `frontend/` 通过定义好的接口调用 `backend/` 能力。
3. `backend/` 执行内核逻辑，返回结果。
4. `frontend/` 更新界面状态并渲染。

（后续业务落地时在此补充具体协议与数据存储结构。）
