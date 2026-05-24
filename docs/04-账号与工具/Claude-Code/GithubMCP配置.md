# Claude Code 配置 GitHub MCP

## 添加 GitHub MCP 服务

在终端执行以下命令，将 `YOUR_GITHUB_TOKEN` 替换为你自己的 GitHub Personal Access Token：

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN"
```

## 生成 GitHub Token

1. 访问 [![GitHub Tokens](https://img.shields.io/badge/GitHub-Personal_Access_Tokens-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/settings/tokens)
2. 点击 **Generate new token (classic)**
3. 勾选所需权限（`repo`、`read:org` 等）
4. 生成后复制，替换上方命令中的 `YOUR_GITHUB_TOKEN`

!!! warning "Token 安全"
    Token 相当于密码，**不要提交到任何公开仓库**。建议存入密码管理器或环境变量。
