# PowerShell 提示"在此系统上禁止运行脚本"

运行 `.ps1` 脚本或在安装命令里管道执行脚本时（例如 `irm https://claude.ai/install.ps1 | iex`），报错：

```
无法加载文件 xxx.ps1，因为在此系统上禁止运行脚本。有关详细信息，请参阅
https://go.microsoft.com/fwlink/?LinkID=135170 中的 about_Execution_Policies。
+ CategoryInfo          : SecurityError: (:) []，ParentContainsErrorRecordException
+ FullyQualifiedErrorId : UnauthorizedAccess
```

这不是脚本有问题，而是 Windows 的 **PowerShell 执行策略**默认为 `Restricted`——禁止运行任何脚本。这是防止恶意脚本的默认防护，放开即可。

---

## 解决：改为 RemoteSigned（推荐）

在 PowerShell 窗口执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

提示确认时输入 `Y` 回车。**无需管理员权限**，只影响当前用户，不动系统全局设置。

[![about_Execution_Policies](https://img.shields.io/badge/MS_Learn-about__Execution__Policies-0078D4?style=plastic&logo=microsoft&logoColor=white)](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.core/about/about_execution_policies)

!!! warning "pwsh 和 powershell 是分开的"
    执行策略按程序分别存储：在 `pwsh`（PowerShell 7）里设置只对 pwsh 生效，系统自带的 `powershell`（5.1）里仍保持原策略。在哪个窗口跑脚本，就在哪个窗口设置。

!!! tip "改完不生效？"
    已打开的窗口读取的是设置生效前的策略，**关掉重开**再试。

---

## 策略级别速查

| 策略 | 本地脚本 | 下载的脚本 | 适用场景 |
|---|---|---|---|
| `Restricted` | 禁止 | 禁止 | **Windows 客户端默认**，报错就是它 |
| `RemoteSigned` | 直接运行 | 需签名或解除标记 | 个人机推荐 |
| `AllSigned` | 需签名 | 需签名 | 高安全要求 |
| `Unrestricted` | 直接运行 | 运行前提示 | 不推荐 |
| `Bypass` | 全部放行 | 全部放行 | 仅用于单次任务（见下） |

查看当前策略：

```powershell
Get-ExecutionPolicy -List
```

---

## 下载的脚本还是被拦？

`RemoteSigned` 下，从网上下载的文件带有"来自网络"标记（Mark of the Web），仍会被拦截。两种处理方式：

**方式一：解除文件标记后运行（推荐）**

```powershell
Unblock-File "$env:USERPROFILE\Downloads\bootstrap.ps1"
& "$env:USERPROFILE\Downloads\bootstrap.ps1"
```

**方式二：单次放行，不改任何设置**

```powershell
pwsh -ExecutionPolicy Bypass -File "脚本完整路径.ps1"
```

`Bypass` 只对这一次进程生效，窗口关闭即失效，适合运行一次性安装脚本。

---

## 恢复默认

想改回系统默认（禁止脚本）：

```powershell
Set-ExecutionPolicy -ExecutionPolicy Default -Scope CurrentUser
```

---

## 相关页面

- [Claude Code 快速入门](../../04-账号与工具/Claude-Code/快速入门.md) — 安装 Claude Code 时会用到本文的解决方法
