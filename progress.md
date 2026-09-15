# Session Progress Log

## Current State

**Last Updated:** 2026-09-11
**Session ID:** agent-framework-002
**Active Feature:** feat-011「场景化重构」— agent 框架已从底座剥离为 `scenarios/code-assistant/`，底座回归纯净可复用

## Status

### What's Done

- [x] 底座初始化（feat-001）：干净检出可安装依赖、跑通验证（validate 100/100）
- [x] 前端骨架（feat-002）：Node/TypeScript 最小界面骨架（greeting.ts）
- [x] 后端骨架（feat-003）：Python 内核骨架（math_ops.py）
- [x] 验证覆盖（feat-004）：底座验证 100/100；前后端测试全绿
- [x] 收尾与交接（feat-005）：progress.md + session-handoff.md 记录启动路径
- [x] 场景化重构（feat-011）：agent 框架整体移入 `scenarios/code-assistant/`，底座回归纯 harness

### What's In Progress

- 无

### What's Next

1. 场景端到端联调：场景 backend `uvicorn` + 场景 frontend `npm run dev` 浏览器验证对话框与执行链面板
2. 派生工具验证：`node scripts/create-harness.mjs --target <临时目录> --with-scenario code-assistant`
3. 派生第二个场景：在 `scenarios/` 下新建领域场景，验证「底座 + 多场景」可并列共存

## Blockers / Risks

- [ ] [环境] Windows 下 `init.sh` 需 Git Bash / WSL 运行；已提供 init.ps1 作为便利入口
- [ ] [依赖] 场景 LLM 调用依赖 `new-api.mypy.cn` 网络可达；不可用时自动降级规则计划（demo 离线可跑）
- [ ] [安全] 场景 demo 阶段边界为「配置 + 校验层」，不可信输入需按场景 `docs/SANDBOX.md` 升级沙箱/容器隔离

## Decisions Made

- **底座定位：通用 harness 工作区，而非跟随教程的 Electron 应用**
  - Context: 用户要"匹配后续 harness 项目的通用基础部分"

- **技术栈：前端界面 Node，内核逻辑 Python**
  - Context: 用户明确指定；边界不可跨越（前端只走 HTTP 调后端）

- **Agent 形态：小型、能力集中的 Claude Code / Codex**
  - Context: 用户"自主的完整对应任务 + 可设边界 + 动态执行链"

- **执行链 = 动态四段式**：意图识别(规则) → 计划编排(LLM，可降级) → 分步执行(白名单工具) → 归因审计(trace)

- **大脑 = 混合模式**：意图识别用规则分流，任务型再交给 LLM 做计划与执行

- **边界 = 操作白名单 + 资源白名单**；demo 用「配置 + 校验层」，沙箱/容器隔离只输出文档步骤

- **对话框 = Web 界面**：Vite + 原生 TS（不引 React，保持轻量）；后端 FastAPI

- **LLM 走 new-api.mypy.cn（deepseek-v4-pro，关思考）**，不可用时规则兜底

- **底座与场景分离（本轮关键）**：底座是纯 harness 模板，具体业务作为场景放 `scenarios/<name>/`，自包含、可独立复制
  - Context: 用户指出"要保证的是一个可复用的 harness 可以结合其余落地场景"，agent 框架不应污染底座根

## Files Modified This Session

**移动（底座根 → scenarios/code-assistant/）**

- `backend/core/agent/`（intent/planner/executor/boundary/trace/llm/server + tools/）→ 场景 `backend/core/agent/`
- `backend/config/scenario.json` → 场景 `scenario.json`
- `backend/tests/test_{intent,boundary,executor,trace}.py` → 场景 `backend/tests/`
- `frontend/index.html`、`vite.config.ts`、`src/{api.ts,main.ts,ui/}`、`test/render.test.ts` → 场景 `frontend/`
- `docs/SANDBOX.md` → 场景 `docs/SANDBOX.md`

**还原（底座回归纯净）**

- `backend/requirements.txt`：去掉 fastapi/uvicorn，只留 pytest>=7.0
- `frontend/package.json`：去 vite/dev 脚本，build 改 `tsc -p tsconfig.build.json`
- `frontend/tsconfig.json`：去 DOM libs
- `feature_list.json`：移除 feat-006~010，新增 feat-011

**新增（场景自包含）**

- `scenarios/code-assistant/README.md`、`feature_list.json`（feat-006~010）、`init.sh`、`init.ps1`
- `scenarios/code-assistant/backend/requirements.txt`、`pyproject.toml`
- `scenarios/code-assistant/frontend/package.json`、`tsconfig.json`、`tsconfig.build.json`

**修改（底座元文件与工具）**

- `docs/ARCHITECTURE.md`、`docs/PRODUCT.md`：补「底座 + 场景」分层与场景机制
- `AGENTS.md`、`CLAUDE.md`：补「落地场景放 scenarios/，底座保持纯净」边界
- `scripts/create-harness.mjs`：新增 `--with-scenario <name>`
- `scenarios/code-assistant/backend/core/agent/server.py`：`_SCENARIO_PATH` 改为场景根下的 `scenario.json`

## Evidence of Completion

- [x] 底座自审计：`node scripts/validate-harness.mjs --target .` → **100/100**
- [x] 底座后端：`python -m pytest`（math_ops）通过
- [x] 底座前端：`npm run check` / `npm test` / `npm run build` 通过（greeting 2 tests）
- [x] 场景后端：`python -m pytest` → **13 passed**（intent/boundary/executor/trace 全覆盖）
- [x] 场景前端：`npm run check` / `npm test`（3 passed）/ `npm run build` 通过
- [x] 派生工具：`node scripts/create-harness.mjs --target <临时目录> --with-scenario code-assistant` → 底座元文件（AGENTS/feature_list/progress/session-handoff/init.sh）+ `scenarios/code-assistant/` 完整复制

## Notes for Next Session

底座已回归纯净 harness，agent 框架作为第一个落地场景放在 `scenarios/code-assistant/`。启动路径：

1. 底座验证：`./init.sh`（或 `init.ps1`）→ 前端 greeting + 后端 math_ops 全绿
2. 底座自审计：`node scripts/validate-harness.mjs --target .` → 100/100
3. 场景验证：`cd scenarios/code-assistant && ./init.sh`（或 init.ps1）→ 后端 15 passed + 前端全绿
4. 场景端到端：场景 backend `python -m uvicorn core.agent.server:app --port 8000` + 场景 frontend `npm run dev`，浏览器输入「列出 backend 下的文件」「运行 git status」，观察执行链面板与越界拒绝
5. 派生新项目：`node scripts/create-harness.mjs --target <目标> --with-scenario code-assistant`
