# 沙箱 / 容器隔离升级路径

本文档说明如何把 agent 内核从 demo 阶段的「配置 + 校验层」边界，升级为真正的**沙箱 / 容器隔离**。当前 `boundary.py` 只做白名单校验（操作 + 资源），不隔离进程；生产或不可信输入场景应按本文档逐级硬化。

## 为什么需要升级

| 维度 | 配置 + 校验层（当前） | 沙箱 / 容器隔离（目标） |
|------|----------------------|------------------------|
| 文件系统 | 路径白名单，越界抛异常 | 物理隔离，越界不可见 |
| 进程执行 | 命令白名单 + subprocess | 容器内执行，主机无副作用 |
| 网络 | 无限制 | 按需屏蔽 / 白名单出口 |
| 逃逸风险 | 依赖 `Path.resolve` 正确性 | 内核级隔离 |

## 升级步骤（由浅入深）

### 第 1 级：进程级资源限制（轻量，可立即做）

在执行命令前用 Python 限制子进程资源，不改架构：

- 用 `subprocess.run(..., timeout=...)` 限制单步耗时（已做，30s）。
- 用 `preexec_fn`（POSIX）或 `CREATE_NEW_PROCESS_GROUP`（Windows）限制信号传播。
- 用 `resource.setrlimit`（POSIX）限制 CPU / 内存 / 文件描述符。
- 拒绝 `shell=True`，改用参数列表 `subprocess.run(["git", "status"])` 避免命令注入。

### 第 2 级：Docker 容器隔离（推荐，跨平台）

把 `executor.py` 的 `run_cmd` 改为在容器内执行：

1. 为 agent 写 `backend/Dockerfile`，挂载白名单目录为只读卷：
   ```dockerfile
   FROM python:3.13-slim
   WORKDIR /workspace
   RUN useradd -m -s /bin/bash agent
   USER agent
   ```
2. 用 Docker SDK 或 `docker run --rm --network none -v <allowed_dir>:/workspace:ro <image> <command>` 执行每一步。
3. `boundary.py` 保留白名单校验（容器是第二道防线，校验是第一道防线）。
4. 命令白名单映射为容器内允许的入口脚本，不给 `shell`。

### 第 3 级：进程级沙箱（更细粒度，适合 Linux）

- 用 `bubblewrap`（`bwrap --ro-bind / --tmpfs /tmp --unshare-net ...`）包裹每个工具调用。
- 用 `seccomp` / `landlock`（Linux 5.13+）限制系统调用与文件访问。
- 用 `nsjail` 组合 namespace + cgroup + seccomp，提供更强隔离。

### 第 4 级：远程隔离执行

- 把「计划」发给独立的 worker 进程 / 远程机器执行，agent 主进程只编排不执行。
- 适合需要完全信任边界、多租户或不可信模型的场景。

## 落地建议（结合本仓库）

1. **先做第 1 级**：把 `tools/__init__.py` 的 `run_cmd` 改成参数列表 + 资源限制，成本最低、立竿见影。
2. **再上第 2 级**：给 `backend/` 加 `Dockerfile`，`run_cmd` 走容器，`boundary.py` 的 `allow_dirs` 映射为 `-v` 只读挂载。
3. **保留校验层**：容器是兜底，白名单是语义层；两层叠加才既安全又可解释。
4. **记录到归因链**：容器/沙箱的每次拦截同样写入 `trace.py`，保证审计链不因隔离升级而断裂。

## 边界：本仓库不默认引入

- 本仓库 demo 阶段**不引入 Docker / 沙箱依赖**，保持「最小可运行」。
- 需要时再按本文档第 2 级引入，并在 `feature_list.json` 里新增 feature 追踪。
