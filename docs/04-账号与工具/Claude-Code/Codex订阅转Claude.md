# 用 Codex 订阅驱动 Claude Code

Claude Pro 每月 $20，而 OpenAI 的 Codex 订阅价格更低，且同样提供 OpenAI Responses API 接口。[claude-code-proxy](https://github.com/starnotes-xj/claude-code-proxy) 是一个本地代理，把 Claude Code 发出的 Anthropic Messages 请求实时转换成 OpenAI Responses 格式，转发给 Codex 后端，让你用更便宜的 Codex 订阅驱动 Claude Code。

```
Claude Code → claude-code-proxy（本地 8787）→ Codex / 任意 OpenAI 兼容后端
```

---

## 前置条件

- 已有可用的 **Codex（OpenAI）订阅**及对应 API Key
- 本机安装了 **Docker**（推荐部署方式）或 **Go 1.21+**（本地直接运行）

---

## 快速启动

### 第一步：克隆项目

```bash
git clone https://github.com/starnotes-xj/claude-code-proxy.git
cd claude-code-proxy
```

### 第二步：配置环境变量

**方式 A：从已有的 `~/.codex` 配置自动生成（推荐）**

已经在本机配置过 Codex 的用户，运行对应脚本即可自动生成 `.env.local`：

```powershell
# Windows PowerShell
.\scripts\write-env-from-config.ps1
```

```bash
# macOS / Linux
bash scripts/write-env-from-config.sh
```

**方式 B：手动填写**

```bash
cp env.example .env.local
```

打开 `.env.local`，至少填写以下三项：

```bash
# Codex 后端地址（OpenAI Responses API）
CLAUDE_CODE_PROXY_BACKEND_BASE_URL=https://api.openai.com

# Codex API Key
CLAUDE_CODE_PROXY_BACKEND_API_KEY=sk-...

# 客户端鉴权密钥（Docker 模式必填，自己随意设置一个）
CLAUDE_CODE_PROXY_CLIENT_API_KEY=my-secret-key

# 固定后端模型（推荐），例如 codex-mini-latest
CLAUDE_CODE_PROXY_BACKEND_MODEL=codex-mini-latest
```

### 第三步：启动代理

```bash
docker build -t claude-codex-proxy:latest .

docker run -d --name claude-codex-proxy \
  -p 127.0.0.1:8787:8787 \
  -v "${PWD}/.env.local:/app/.env.local:ro" \
  claude-codex-proxy:latest
```

验证是否正常运行：

```bash
curl http://127.0.0.1:8787/healthz
# 返回 {"ok":true,...} 即成功
```

### 第四步：配置 Claude Code

在 Claude Code 中将 API 后端指向本地代理：

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 ANTHROPIC_API_KEY=my-secret-key claude
```

或者写入 shell 配置文件（`~/.zshrc` / `~/.bashrc` / PowerShell profile）使其永久生效：

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=my-secret-key   # 与 CLIENT_API_KEY 保持一致
```

---

## 注意事项

!!! warning "这不是官方支持的用法"
    代理依赖格式转换，部分高级特性（如 `thinking` 块、`stop_sequences`）在跨后端传递时行为可能与原生 Claude 有差异。

!!! info "token 计数为估算值"
    `/v1/messages/count_tokens` 端点使用字符长度近似估算，不代表 Codex 后端实际消耗的 token 数。

---

## 可选：本地直接运行（不用 Docker）

```bash
go run .
```

启用 SQLite 用量统计（可在 `http://127.0.0.1:8787/v1/usage/dashboard` 查看）：

```bash
go build -tags sqlite -o claude-codex-proxy && ./claude-codex-proxy
```
