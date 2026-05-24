# Cowork 报错 RPC pipe closed 修复

在 Claude Desktop 中点击 Cowork 标签页时出现以下报错：

```
Failed to start Claude's workspace
RPC pipe closed
```

---

## 原因

Cowork 功能依赖一个 Linux 虚拟机（VM），启动时需要四个文件：`rootfs.vhdx`、`smol-bin.vhdx`、`vmlinuz`、`initrd`。

问题出在路径不匹配：MSIX 安装包的文件系统虚拟化将 `vm_bundles` 放在 `LocalCache\Packages\...` 路径下，而负责启动 VM 的 CoworkVMService（以 LocalSystem 身份运行的 Windows 服务）却从标准的 `%APPDATA%\Claude\vm_bundles` 查找文件。

文件找不到 → VM 启动失败 → RPC 通道关闭 → 报出上述错误。

!!! info "已知 Bug"
    这是一个活跃的 GitHub Issue（#61559、#60809、#61113、#60631），截至 2026/05 尚无官方修复。

---

## 关键发现

- VM Bundle SHA（版本哈希）：`5680b11bcdab215cccf07e0c0bd1bd9213b0c25d`，从 Claude Desktop v1.1.9669 起稳定未变
- 下载 URL 路径是 `vms/linux/x64/`（不是 `win32/x64/`），即使在 Windows 上也用 Linux 路径 — 这是最容易踩坑的地方
- `smol-bin.vhdx` 不从 CDN 下载，而是从 MSIX 包内的 `app\resources\smol-bin.x64.vhdx` 复制

---

## 下载链接（当前版本 1.8555.2.0）

三个文件需要从 CDN 下载（均为 `.zst` 压缩格式）：

| 文件 | 大小 | 下载地址 |
|---|---|---|
| `rootfs.vhdx.zst` | ~2.2 GB | [下载](https://downloads.claude.ai/vms/linux/x64/5680b11bcdab215cccf07e0c0bd1bd9213b0c25d/rootfs.vhdx.zst) |
| `vmlinuz.zst` | ~14 MB | [下载](https://downloads.claude.ai/vms/linux/x64/5680b11bcdab215cccf07e0c0bd1bd9213b0c25d/vmlinuz.zst) |
| `initrd.zst` | ~166 MB | [下载](https://downloads.claude.ai/vms/linux/x64/5680b11bcdab215cccf07e0c0bd1bd9213b0c25d/initrd.zst) |

!!! warning "版本更新后 SHA 可能变化"
    如果 Claude Desktop 升级后链接失效，参见文末「附录」提取最新 SHA 的方法。

---

## 手动修复步骤

以管理员身份打开 PowerShell，依次执行：

**第一步：创建目标目录**

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude\vm_bundles\claudevm.bundle"
```

**第二步：安装 zstd 解压工具**

```powershell
Invoke-WebRequest -Uri "https://github.com/facebook/zstd/releases/latest/download/zstd-v1.5.7-win64.zip" -OutFile "$env:TEMP\zstd.zip"
Expand-Archive -Path "$env:TEMP\zstd.zip" -DestinationPath "$env:LOCALAPPDATA\zstd" -Force
```

**第三步：将上面 3 个 `.zst` 文件下载到目标目录**

用浏览器下载后移动到：

```
%APPDATA%\Claude\vm_bundles\claudevm.bundle\
```

**第四步：解压所有 .zst 文件**

```powershell
$zstd   = "$env:LOCALAPPDATA\zstd\zstd-v1.5.7-win64\zstd.exe"
$bundle = "$env:APPDATA\Claude\vm_bundles\claudevm.bundle"
& $zstd -d -f --rm "$bundle\rootfs.vhdx.zst" -o "$bundle\rootfs.vhdx"
& $zstd -d -f --rm "$bundle\vmlinuz.zst"      -o "$bundle\vmlinuz"
& $zstd -d -f --rm "$bundle\initrd.zst"       -o "$bundle\initrd"
```

**第五步：从 MSIX 包复制 smol-bin.vhdx**

```powershell
$src = (Get-ChildItem "C:\Program Files\WindowsApps\Claude_*\app\resources" -Filter "smol-bin*" -Recurse).FullName
Copy-Item $src "$env:APPDATA\Claude\vm_bundles\claudevm.bundle\smol-bin.vhdx"
```

**第六步：重启 Claude Desktop，切换到 Cowork 标签页测试**

---

## 最终文件清单

修复完成后，目录 `%APPDATA%\Claude\vm_bundles\claudevm.bundle\` 下应有以下四个文件：

| 文件 | 大小 | 来源 |
|---|---|---|
| `smol-bin.vhdx` | 36 MB | 从 MSIX 包复制 |
| `vmlinuz` | 14.3 MB | CDN 下载 + 解压 |
| `initrd` | 169 MB | CDN 下载 + 解压 |
| `rootfs.vhdx` | 8.8 GB | CDN 下载 + 解压 |

---

## 附录：版本更新后如何提取最新 SHA

如果 Claude Desktop 升级后 SHA 发生变化导致下载链接失效，可以用以下 Python 脚本从 `app.asar` 中提取最新配置：

```python
import re, glob

asar_path = glob.glob(r"C:\Program Files\WindowsApps\Claude_*\app\resources\app.asar")[0]

with open(asar_path, 'rb') as f:
    data = f.read()

# 提取 bundle SHA
match = re.search(rb'sha:"([a-f0-9]{40})"', data)
if match:
    print(f"SHA: {match.group(1).decode()}")

# 提取下载 URL 模板
match = re.search(rb'downloads\.claude\.ai/vms/[^"]+', data)
if match:
    print(f"URL 模板: https://{match.group(0).decode()}")
```

将输出的 SHA 替换到上述下载链接中即可。
