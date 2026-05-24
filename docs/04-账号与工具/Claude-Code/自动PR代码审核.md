还能自动修复错误，优化代码

```yaml
name: Claude Code Review & Auto Fix

on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
  issue_comment:
    types: [created]

jobs:
  claude-review:
    # 在 PR 事件时自动运行，或在 PR 评论中包含 @claude 或 /review 时运行
    if: |
      github.event_name == 'pull_request' ||
      (github.event_name == 'issue_comment' &&
       github.event.issue.pull_request &&
       (contains(github.event.comment.body, '@claude') || contains(github.event.comment.body, '/review')))

    runs-on: ubuntu-latest
    permissions:
      contents: write      # ✨ 允许修改文件并提交
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    env:
      # 配置 Aliyun DashScope Anthropic API 端点
      ANTHROPIC_BASE_URL: https://dashscope.aliyuncs.com/apps/anthropic
      ANTHROPIC_DEFAULT_HAIKU_MODEL: qwen3-coder-plus
      ANTHROPIC_DEFAULT_OPUS_MODEL: qwen3-coder-plus
      ANTHROPIC_DEFAULT_SONNET_MODEL: qwen3-coder-plus

    steps:
      - name: Checkout PR branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref || github.event.issue.pull_request.head.ref }}
          fetch-depth: 0
          token: ${{ secrets.USER_TOKEN }}

      - name: 配置 Git
        run: |
          git config user.name "Claude Code Bot"
          git config user.email "claude-code-bot@users.noreply.github.com"

      - name: 运行 Claude 代码审查与自动修复
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          github_token: ${{ secrets.USER_TOKEN }}
          track_progress: true
          prompt: |
            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number || github.event.issue.number }}

            ## 任务说明

            使用 `/pr-review-toolkit:review-pr` 插件对这个 PR 进行全面的代码审查。

            ### 审查重点

            请关注以下方面（参考 `.claude/CLAUDE.md` 项目规范）：

            1. **代码质量和可读性**
               - 变量命名是否清晰
               - 函数职责是否单一
               - 代码逻辑是否清晰

            2. **潜在的 Bug 或安全问题**
               - 空指针引用、数组越界
               - SQL 注入、XSS 等安全漏洞
               - 并发安全问题
               - 资源泄漏（文件句柄、数据库连接等）

            3. **性能优化建议**
               - 不必要的循环嵌套
               - 可以优化的算法
               - 内存使用问题

            4. **Go 语言最佳实践**
               - 错误处理是否正确
               - defer 使用是否合理
               - goroutine 和 channel 使用是否安全
               - 是否遵循 Go 命名约定

            5. **项目规范**
               - 是否符合 `.claude/CLAUDE.md` 中的规范
               - 提交信息格式是否正确
               - 文档是否需要更新

            ### 自动修复流程

            对于发现的可以安全自动修复的问题，请直接修复：

            **可自动修复的问题类型**：
            - ✅ 代码格式问题（gofmt、行尾空格、缩进）
            - ✅ 明显的语法错误
            - ✅ 简单的逻辑错误
            - ✅ 缺少的基本错误处理
            - ✅ 拼写错误
            - ✅ 未使用的变量和导入
            - ✅ 简单的性能优化（如预分配切片容量）

            **不要自动修复的问题**（仅在审查报告中指出）：
            - ❌ 需要架构调整的问题
            - ❌ 可能影响业务逻辑的修改
            - ❌ 复杂的重构
            - ❌ 不确定的安全问题

            ### 修复步骤

            如果发现可修复的问题：
            1. 使用 Read 工具读取需要修改的文件
            2. 使用 Edit 工具进行精确修改
            3. 所有修复完成后，使用 Bash 工具创建提交：
               ```bash
               git add -A
               git commit -m "🤖 Claude 自动修复: [简要说明]

               基于 pr-review-toolkit 审查结果自动修复：
               - 列出修复的问题

               Co-Authored-By: Claude Code Bot <claude-code-bot@users.noreply.github.com>"
               git push
               ```

            ### 审查报告格式

            在 PR 中发布审查报告，在开头添加 Claude 标识，格式如下：

            ```markdown
            <div align="center">
              <img src="https://mintlify.s3-us-west-1.amazonaws.com/anthropic/logo/light.svg" alt="Claude" width="120" />

              # Claude Code 审查报告

              **🔮 Powered by Claude Code** | 使用 pr-review-toolkit 专业审查
            </div>

            ---

            ### ✅ 已自动修复的问题

            - [x] 问题描述（文件:行号）

            ### ⚠️ 需要手动处理的问题

            #### 🔴 高优先级
            - [ ] 问题描述（文件:行号）

            #### 🟡 中优先级
            - [ ] 问题描述（文件:行号）

            ### 💡 优化建议

            - 建议描述

            ### 📊 总结

            - 检查了 X 个文件
            - 自动修复了 Y 个问题
            - 发现 Z 个需要手动处理的问题
            ```

            ## 重要提示

            - 所有回复使用中文，除非在当前对话中用户明确要求使用其他语言
            - 如果没有发现需要修复的问题，只发布审查报告，不要创建空提交
            - 修复时要谨慎，确保不会破坏现有功能
            - 使用内联评论指出具体代码位置的问题（如果适用）

          # 允许的工具：读写文件、执行所有 Bash 命令、GitHub 操作、调用插件
          claude_args: |
            --allowedTools "Read,Edit,Write,Glob,Grep,Bash,mcp__github__*,Skill"
            --max-turns 100
