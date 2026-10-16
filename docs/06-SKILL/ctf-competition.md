# CTF 比赛解题 Skill（授权比赛）

> 本 Skill 仅用于主办方明确授权的比赛平台和靶场。使用前先确认本场授权范围、目标和时间窗口；不要把方法扩展到范围外的系统。

**下载完整 Skill 包：** [ctf-competition-skill.zip](downloads/ctf-competition-skill.zip)（含 SKILL.md、参考文档、Cairn 适配器与脚本。）

也可直接浏览仓库中的[完整源文件](https://github.com/starnotes-xj/SurviveBIGCManual/tree/main/tools/ctf-competition)。

**快速跳转：** [用途](#purpose) · [并行工作方式](#parallel) · [安全边界](#safety) · [安装](#install) · [CTF 是什么](../02-技术方向/CTF竞技/CTF是什么.md) · [CTF 学习资源](../02-技术方向/CTF竞技/学习资源.md)

## 用途 { #purpose }

这是一个面向 AI 编码代理（Claude Code / ZCode / Codex CLI / OpenCode，另附 Cairn 提示适配器）的 CTF 比赛 Skill，把一场比赛的完整生命周期整理成证据驱动的工作流：

1. **范围与规则**：从官方页面和规则确认赛事、轮次、分类和提交方式；AI 辅助被禁止时立即停止。
2. **安全认证**：只通过一个已授权的浏览器进程完成登录，凭据和 Cookie 不进入提示词或文件。
3. **捕获题目**：记录分类、标题、题面、分值、附件名和官方下载链接。
4. **下载与解压**：只用官方附件链接；内置 `safe_extract.py` 拒绝路径穿越、特殊文件和超限压缩包。
5. **证据分析**：按分类选用方法（如 Crypto 从 `file`、hex 视图、字符串、源码入手），不凭猜测假设算法或 flag 格式。
6. **求解与验证**：保留假设日志，独立复核恢复出的明文/密钥/flag，未通过验证不得当作已解出。
7. **谨慎提交**：规则允许且验证通过后才提交，每题一个提交者、串行提交，避免重复猜测。
8. **报告**：区分观察到的事实、推断和未解决项，不暗示覆盖未测试的分类。

## 并行工作方式 { #parallel }

- **默认串行**：用户没有明确要求并行时，当前会话按方向逐个推进，不会自作主张派出其他代理。
- **会话内编排**：用户明确要求并行时，主会话作为协调者——先把所有分类 scope 一遍、建好共享任务台账（`ledger`），再每个分类派一个子代理；子代理只操作自己分到的页面和题目，返回已验证的 flag 候选，提交统一由主会话串行执行。子代理与主会话共享同一个宿主浏览器连接，天然满足"同一已认证浏览器上下文"的要求。
- **多独立会话**：也支持多个独立 AI 会话并行，但必须 attach 到同一个已登录浏览器进程，每个会话持有唯一页面 ID 和题目分配；VNC 场景用每台机器一把的 `vnc_gate.py` 锁串行输入。
- **题量规则**：真实比赛没有"每类一题"的上限，每个方向尽力清完；只有在用户明确把这次运行定性为 scoped 测试时（如 DataCon 214 预选赛测试），才限制每类一题并跳过 Theory/理论。

## 安全边界 { #safety }

- 每次使用都需要针对该场比赛的明确授权；授权只覆盖主办方列出的平台、分类、时间段和动作，不扫描基础设施、不攻击平台本身。
- 不查看/导出 Chrome Cookie 数据库、密码、认证头或浏览器存储状态；MFA 和验证码由用户处理。
- 不执行题目附件里自带的文件或命令；先检查，只执行经过审阅的求解脚本。
- 原始下载保持不变，每题独立目录并记录来源与哈希。
- 赛后提交冒烟测试只在用户明确要求时进行：一个已验证 flag 通过可见 UI 提交一次，提交控件不可用时不绕过 UI 直接调 API。

## 安装 { #install }

把 `tools/ctf-competition/` 整个目录复制到对应工具的技能目录：

```powershell
# ZCode（用户级）
Copy-Item -Recurse tools/ctf-competition ~/.zcode/skills/ctf-competition

# Claude Code（项目级）
Copy-Item -Recurse tools/ctf-competition .claude/skills/ctf-competition

# Codex CLI / OpenCode（项目级）
Copy-Item -Recurse tools/ctf-competition .agents/skills/ctf-competition
```

脚本只需 Python 3 标准库，无第三方依赖。触发方式：在比赛场景下让代理使用 `ctf-competition` 技能即可。

## 页面范围

Skill 包中的参考文档（工作流、Crypto 分流、浏览器与 VNC 约束、Cairn 集成限制）随 ZIP 一起分发。下载和使用都只限于主办方明确授权的比赛平台与靶机；下载本身不构成对其他系统的授权。
