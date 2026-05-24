# 用 GitHub Copilot 订阅驱动 Claude Code

GitHub Copilot Individual 每月 $10，远低于 Claude Pro 的 $20。[copilot-api](https://github.com/caozhiyuan/copilot-api) 是一个本地网关，将 Claude Code 的 Anthropic Messages 请求转发给 GitHub Copilot，让你用更便宜的 Copilot 订阅驱动 Claude Code。

```
Claude Code → copilot-api（本地 4141）→ GitHub Copilot
```

[![GitHub](https://img.shields.io/badge/GitHub-caozhiyuan%2Fcopilot--api-181717?style=plastic&logo=github&logoColor=white)](https://github.com/caozhiyuan/copilot-api)
[![Stars](https://img.shields.io/github/stars/caozhiyuan/copilot-api?style=plastic&logo=github)](https://github.com/caozhiyuan/copilot-api)
[![Release](https://img.shields.io/badge/最新版本-v1.10.12-blue?style=plastic)](https://github.com/caozhiyuan/copilot-api/releases/latest)

---

## 前置条件

- **GitHub Copilot 订阅**（Individual $10/月 即可）
- **Node.js ≥ 18**（推荐 ≥ 22.13.0 以启用用量统计）

---

## 方式一：npx（推荐，无需安装）

### 第一步：登录 GitHub Copilot

```bash
npx @jeffreycao/copilot-api@latest auth
```

按提示完成 GitHub OAuth 授权，凭据会自动保存，后续无需重复登录。

### 第二步：启动网关

```bash
npx @jeffreycao/copilot-api@latest start
```

默认监听 `http://localhost:4141`。启动成功后保持终端开启。

### 第三步：配置 Claude Code

```bash
ANTHROPIC_BASE_URL=http://localhost:4141 ANTHROPIC_API_KEY=any claude
```

或写入 shell 配置文件永久生效：

```bash
export ANTHROPIC_BASE_URL=http://localhost:4141
export ANTHROPIC_API_KEY=any
```

!!! warning "必须指定模型为 claude-opus-4-6"
    使用时须在 Claude Code 的 `settings.json` 中固定模型 ID，**不要带 `[1m]` 后缀**，否则超出 Copilot 上下文窗口限制可能导致账号被封。

    ```json
    {
      "model": "claude-opus-4-6"
    }
    ```

---

## 方式二：桌面 Electron App（适合不熟悉命令行的同学）

从 [Releases 页面](https://github.com/caozhiyuan/copilot-api/releases) 下载对应平台的安装包，安装后：

1. 打开 App，点击「Sign in with GitHub」完成授权
2. 选择端口（默认 4141），点击「Start Server」
3. App 界面会显示本地端点地址，复制后填入 Claude Code 的 `ANTHROPIC_BASE_URL`

App 内置用量仪表板，可以直观看到 token 消耗情况。

---

## 方式三：Docker

```bash
mkdir -p ./copilot-data
docker run -d --name copilot-api \
  -p 4141:4141 \
  -v $(pwd)/copilot-data:/root/.local/share/copilot-api \
  ghcr.io/caozhiyuan/copilot-api:latest
```

首次运行后进入容器完成 auth：

```bash
docker exec -it copilot-api npx @jeffreycao/copilot-api@latest auth
```

---

## 注意事项

!!! warning "这不是官方支持的用法"
    通过 Copilot 代理使用 Claude，属于对 GitHub Copilot 服务条款的边缘用法，存在账号风险。建议个人开发机使用，不要用于生产环境。

!!! info "多 Agent 模式"
    使用 Codex via Copilot 时，建议在 Claude Code 中禁用 multi-agent 模式，避免异常计费。
