---
name: clean-c-drive
description: >
  Windows C盘空间清理工具。当用户说"清理C盘"、"释放C盘空间"、"C盘满了"、
  "clean c drive"、"清理磁盘"、"磁盘空间不足"、"帮我清一下C盘"时立即触发本技能。
  支持扫描预览、模块选择（临时文件、JetBrains旧版、休眠文件等）、并报告实际释放空间。
  只要用户提到 C盘空间、清理缓存、释放磁盘，就应主动使用本技能，无需等待用户明确说"用skill"。
---

# C盘清理 Skill

本技能帮助用户安全清理 Windows C盘，所有操作在用户**确认后**才执行。

## 工作流程

### 第一步：扫描并展示预览

运行扫描脚本，展示各清理目标的当前占用大小：

```powershell
# 脚本路径（相对于本 SKILL.md 所在目录）
scripts\scan.ps1
```

输出示例：
```
模块                          路径                                          占用
----                          ----                                          ----
[1] 用户 Temp 临时文件        %USERPROFILE%\AppData\Local\Temp             3.2 GB
[2] Windows 系统 Temp         C:\Windows\Temp                              0.8 GB
[3] NVIDIA DXCache            %USERPROFILE%\AppData\Local\NVIDIA\DXCache   1.1 GB
[4] npm 缓存                  %USERPROFILE%\AppData\Local\npm-cache         0.4 GB
[5] pip 缓存                  %USERPROFILE%\AppData\Local\pip              0.2 GB
[6] 程序崩溃转储              %USERPROFILE%\AppData\Local\CrashDumps       0.0 GB
[7] 回收站                    C:\$Recycle.Bin                              0.1 GB
[8] JetBrains 旧版本数据      (多个路径)                                   2.3 GB
[9] 休眠文件 hiberfil.sys     C:\hiberfil.sys                             ~25.0 GB
```

### 第二步：询问用户选择

向用户展示扫描结果后，询问：
- 要清理哪些模块（可全选，或按编号选择）
- 是否禁用休眠（会永久关闭休眠功能，提醒用户影响）

**关于休眠的重要提示**：禁用休眠会删除 hiberfil.sys（约等于内存大小，通常 16-32 GB），
但会**永久失去快速启动和睡眠恢复**功能，执行前务必告知用户这一权衡。

### 第三步：执行清理

根据用户选择运行清理脚本：

```powershell
scripts\clean.ps1 -Modules <逗号分隔的模块编号或"all"> -DisableHibernation <$true/$false>
```

**管理员权限**：清理 `C:\Windows\Temp` 和禁用休眠需要管理员权限。
如果当前 PowerShell 不是管理员，提示用户以管理员身份重新运行，
或使用以下命令启动管理员 PowerShell：
```powershell
Start-Process powershell -Verb RunAs
```

### 第四步：报告结果

清理完成后，汇报：
- 每个模块实际释放的空间
- 本次清理总计释放空间
- C盘当前剩余空间

## 模块说明

| 编号 | 模块 | 安全性 | 说明 |
|------|------|--------|------|
| 1 | 用户 Temp | 安全 | 临时文件，程序正常运行后不需要 |
| 2 | Windows Temp | 安全* | 需要管理员权限 |
| 3 | NVIDIA DXCache | 安全 | 着色器缓存，会自动重建 |
| 4 | npm 缓存 | 安全 | 重新 install 时会重下 |
| 5 | pip 缓存 | 安全 | 重新 install 时会重下 |
| 6 | 崩溃转储 | 安全 | 除非在排查崩溃问题 |
| 7 | 回收站 | 安全 | 确认不需要恢复文件后 |
| 8 | JetBrains 旧版 | 安全 | 旧版本遗留数据，当前版本不受影响 |
| 9 | 休眠文件 | **不可逆** | 禁用后失去睡眠/快速启动功能 |

## JetBrains 版本配置

脚本默认清理以下旧版本（当前年份 -1 之前视为旧版）：
```
IntelliJIdea2025.2/2025.3, CLion2025.2/2025.3
PyCharm2025.2/2025.3, WebStorm2025.2/2025.3
PhpStorm2025.2/2025.3, GoLand2025.3
```
如用户有特殊需求（保留某版本或清理更多版本），在运行前询问并调整脚本参数。
