# 代码仓库助手（code-assistant）

「底座 + 场景」组合里的第一个落地场景：一个**小型自主智能体对话框**，能识别意图、编排计划、分步执行、归因审计，并受边界白名单约束。

> 底座（`../../`）是通用 harness 模板；本目录是自包含的落地应用，可独立运行、独立验证、独立复制到其他项目。

## 能力

- **意图识别**（规则）：把输入分流为 `command` / `file` / `search` / `chat` 四类。
- **计划编排**（LLM + 规则降级）：LLM 生成分步计划，LLM 不可用时降级为规则计划。
- **分步执行**（白名单工具）：`read_file` / `list_dir` / `run_cmd` / `search`。
- **归因审计**（trace）：记录每一步 intent → plan → tool → boundary → result。
- **边界控制**（boundary）：操作白名单 + 资源白名单（目录/命令/扩展名），越界拒绝并记录归因链。

## 目录结构

```
code-assistant/
├── scenario.json        # 场景配置：意图规则 / 工具集 / 边界 / LLM
├── backend/             # Python 内核（FastAPI + agent 执行链）
├── frontend/            # Node/TypeScript 对话框（Vite + 原生 TS）
├── docs/SANDBOX.md      # 沙箱/容器隔离升级路径
├── feature_list.json    # 场景功能追踪
├── init.sh / init.ps1   # 场景验证入口
```

## 启动方式

### 1. 后端（FastAPI）

```bash
cd backend
python -m uvicorn core.agent.server:app --port 8000
```

### 2. 前端（Vite）

```bash
cd frontend
npm install
npm run dev
```

Vite 已把 `/api` 代理到 `http://127.0.0.1:8000`。浏览器打开 Vite 输出的地址（默认 `http://localhost:5173`），输入指令，如：

- 「列出 backend 下的文件」
- 「读取 core/agent/intent.py」
- 「运行 git status」
- 「搜索 classify_intent」

观察右侧「执行链 · 归因审计」面板展示每一步归因链，越界命令（如 `rm -rf`）会被拒绝并记录。

## 验证

```bash
./init.sh      # 或 Windows: powershell -ExecutionPolicy Bypass -File .\init.ps1
```

后端 `python -m pytest`（intent/boundary/executor/trace 覆盖），前端 `npm run check` / `npm test` / `npm run build`。

## 配置

- **边界与场景**：`scenario.json`（allow_dirs / allow_commands / allow_extensions / deny_commands）。
- **LLM**：走 `new-api.mypy.cn`，默认 `deepseek-v4-pro`（关思考）。API key 需通过环境变量 `AGENT_LLM_API_KEY` 提供（`AGENT_LLM_MODEL` 可选覆盖模型名）；未提供 key 时 LLM 调用失败，自动降级为规则计划。
- **沙箱升级**：demo 阶段边界为「配置 + 校验层」，生产环境按 `docs/SANDBOX.md` 升级为进程/容器隔离。
