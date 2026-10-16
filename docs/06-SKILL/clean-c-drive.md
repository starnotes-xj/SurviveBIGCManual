# C盘清理 Skill

**下载完整 Skill 包：** [clean-c-drive-skill.zip](downloads/clean-c-drive-skill.zip)（含 SKILL.md 与 PowerShell 脚本。）

也可直接浏览仓库中的[完整源文件](https://github.com/starnotes-xj/SurviveBIGCManual/tree/main/tools/clean-c-drive)。

**快速跳转：** [用途](#purpose) · [工作流程](#workflow) · [安全边界](#safety) · [安装](#install)

## 用途 { #purpose }

Windows C 盘空间清理的 Agent Skill，适用于 Claude Code / ZCode 等编码代理。当用户说"清理C盘"、"释放C盘空间"、"C盘满了"、"clean c drive"、"清理磁盘"这类话时自动触发，无需明确说"用 skill"。

支持扫描预览、按模块选择清理目标（用户 Temp、系统 Temp、JetBrains 旧版缓存、休眠文件等），并报告实际释放的空间。

## 工作流程 { #workflow }

1. **扫描并展示预览**：运行 `scripts/scan.ps1`，列出各清理目标的当前占用大小，先给用户看数字。
2. **用户确认模块**：由用户勾选要清理的模块；未经确认不删除任何东西。
3. **执行清理并汇报**：运行 `scripts/clean.ps1` 执行所选模块，最后报告实际释放的空间。

## 安全边界 { #safety }

- 所有删除操作在用户**确认后**才执行，扫描本身只读、不改动系统。
- 只清理列出的模块路径，不触碰用户目录之外的其他数据。
- 清理前展示每项占用，清理后汇报释放量，过程可核对。

## 安装 { #install }

把 `tools/clean-c-drive/` 整个目录复制到对应工具的技能目录：

```powershell
# ZCode（用户级）
Copy-Item -Recurse tools/clean-c-drive ~/.zcode/skills/clean-c-drive

# Claude Code（项目级）
Copy-Item -Recurse tools/clean-c-drive .claude/skills/clean-c-drive
```

脚本为 PowerShell，Windows 内置即可运行，无额外依赖。
