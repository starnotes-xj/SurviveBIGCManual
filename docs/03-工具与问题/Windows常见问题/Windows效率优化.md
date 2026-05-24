# Windows 效率优化

几个一劳永逸的系统设置，装机后建议第一时间完成。

---

## Win+R 快速启动程序

Win+R 打开「运行」窗口后，可以直接输入程序名启动，无需找图标。实现方法是把程序的快捷方式统一放入一个 PATH 文件夹，Windows 会自动识别。

### 第一步：创建快捷方式文件夹

在任意位置创建一个固定文件夹，例如：

```
D:\AppShortcuts\
```

### 第二步：将文件夹加入 PATH

详见 [添加环境变量 PATH](添加环境变量PATH.md)，把 `D:\AppShortcuts` 加入系统变量的 Path。

### 第三步：将程序快捷方式复制进去

找到程序的快捷方式（`.lnk` 文件，通常在桌面或开始菜单），**重命名为简短的名字**后复制到 `D:\AppShortcuts\` 中。

**示例：**

| 快捷方式文件名 | Win+R 输入 | 打开的程序 |
|---|---|---|
| `ev.lnk` | `ev` | Everything |
| `geek.lnk` | `geek` | Geek Uninstaller |
| `bz.lnk` | `bz` | Bandizip |

!!! tip "快捷方式在哪找"
    右键桌面图标 →「打开文件位置」即可跳转到快捷方式所在目录。或直接将桌面图标复制到文件夹后重命名。

### 第四步：验证

重新打开运行窗口（`Win+R`），输入快捷方式的名字（不含 `.lnk`）回车，程序正常启动即配置成功。

---

## 关闭快速启动

快速启动本质上是把内核状态写入休眠文件 `hiberfil.sys`，加快下次开机速度。但这个文件会随使用时间增长，**最终可能占据 10 GB 甚至 25 GB 以上的 C 盘空间**，是 C 盘悄悄变满的常见元凶之一。

除了占空间，快速启动还会带来：

- **双系统**：Windows 分区保持「脏」状态，Linux 无法正常挂载，强行挂载可能损坏文件
- **USB 设备**：重新插拔后有时不被识别，需完整重启
- **驱动更新**：装完驱动必须完整重启才生效，快速启动会绕过这一步

### 关闭方法

1. 打开「控制面板」→「系统和安全」→「电源选项」
2. 左侧点击「**选择电源按钮的功能**」
3. 点击「**更改当前不可用的设置**」（需要管理员权限）
4. 取消勾选「**启用快速启动（推荐）**」
5. 点击「保存修改」

### 彻底删除 hiberfil.sys（推荐）

关闭快速启动后 `hiberfil.sys` 不会自动消失。用管理员权限运行 PowerShell，执行以下命令**彻底禁用休眠**，同时删除该文件：

```powershell
powercfg /hibernate off
```

执行后 `hiberfil.sys` 立即从 C 盘消失，通常可以回收数 GB 至数十 GB 的空间。

!!! warning "双系统用户必须关闭"
    安装 Kali 等 Linux 系统前务必先执行以上步骤，否则 Linux 下挂载 Windows 分区时会报错或无法写入。

---

## 清理 C 盘

C 盘满了会导致系统变慢，甚至无法正常运行。以下是几个有效的清理方向。

### 方法一：系统自带磁盘清理

按 ++win+s++ 搜索「**磁盘清理**」，选择 C 盘后勾选所有项目，再点击「清理系统文件」获取更多可清理空间（包括旧版 Windows 更新）。

### 方法二：清理临时文件

按 ++win+r++ 输入 `%TEMP%` 打开临时文件夹，全选删除（删不掉的跳过即可）。

```powershell
# PowerShell 批量清理临时文件
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
```

### 方法三：使用 Claude Code Skill 自动清理

本手册提供了一个 Claude Code Skill，输入 `/clean-c-drive` 即可触发：自动扫描各清理目标并展示占用大小，**你选择后才执行**，不会盲目删文件。

**支持的清理模块：**

| 模块 | 说明 |
|---|---|
| 用户 Temp / Windows Temp | 临时文件 |
| NVIDIA DXCache | 着色器缓存（可自动重建） |
| npm / pip 缓存 | 重新安装时会自动重下 |
| 程序崩溃转储 | 崩溃日志 |
| 回收站 | 一键清空 |
| JetBrains 旧版本数据 | 老版本遗留缓存 |
| 休眠文件 hiberfil.sys | 禁用休眠，彻底释放（不可逆） |

**安装方法：**

1. 下载 Skill 文件包（三个文件）：

    [![SKILL.md](https://img.shields.io/badge/下载-SKILL.md-181717?style=flat&logo=github&logoColor=white)](https://github.com/starnotes-xj/SurviveBIGCManual/raw/main/tools/clean-c-drive/SKILL.md)
    [![scan.ps1](https://img.shields.io/badge/下载-scan.ps1-181717?style=flat&logo=github&logoColor=white)](https://github.com/starnotes-xj/SurviveBIGCManual/raw/main/tools/clean-c-drive/scripts/scan.ps1)
    [![clean.ps1](https://img.shields.io/badge/下载-clean.ps1-181717?style=flat&logo=github&logoColor=white)](https://github.com/starnotes-xj/SurviveBIGCManual/raw/main/tools/clean-c-drive/scripts/clean.ps1)

2. 按以下结构放置文件：

    ```
    C:\Users\你的用户名\.claude\skills\clean-c-drive\
    ├── SKILL.md
    └── scripts\
        ├── scan.ps1
        └── clean.ps1
    ```

3. 在 Claude Code 中输入 `/clean-c-drive` 即可使用，或直接说「清理 C 盘」「C 盘满了」也会自动触发。

### 方法四：软件迁移到 D 盘

C 盘空间不足的根本解决方案是**把大型软件装到 D 盘**。安装时选择自定义路径，改为 `D:\Program Files\` 或 `D:\Software\`。

已安装的软件可以用 Geek Uninstaller 卸载后重装到 D 盘，或使用「软件搬家」类工具（如 Steam 游戏可在 Steam 设置中直接移动）。

!!! info "哪些必须留在 C 盘"
    系统组件、驱动、.NET 运行时等不要动。用户数据、游戏、开发工具、IDE 都可以迁移到 D 盘。

### 方法五：符号链接（迁移无法自选路径的应用）

部分应用强制安装到 C 盘且无法更改路径（如 JetBrains 数据目录、npm 全局包等）。可以把实际数据移到 D 盘，再在原位置创建一个**符号链接**指向新位置，应用感知不到变化。

**以 JetBrains 数据目录为例（需管理员 PowerShell）：**

```powershell
# 1. 将数据目录移到 D 盘
Move-Item "$env:APPDATA\JetBrains" "D:\AppData\JetBrains"

# 2. 在原位置创建符号链接
New-Item -ItemType SymbolicLink `
    -Path "$env:APPDATA\JetBrains" `
    -Target "D:\AppData\JetBrains"
```

**其他常见目录：**

| 应用 | 原路径 | 建议迁移到 |
|---|---|---|
| npm 全局包 | `%APPDATA%\npm` | `D:\AppData\npm` |
| JetBrains 数据 | `%APPDATA%\JetBrains` | `D:\AppData\JetBrains` |
| Gradle 缓存 | `%USERPROFILE%\.gradle` | `D:\AppData\.gradle` |
| Go 模块缓存 | `%USERPROFILE%\go` | `D:\AppData\go` |

!!! warning "创建符号链接需要管理员权限"
    以管理员身份运行 PowerShell：右键开始菜单 → Windows PowerShell（管理员）。

### 方法六：提前设置环境变量再安装

部分工具在安装前可通过**环境变量**指定数据存放路径，一次设置永久生效，比符号链接更干净。

**在系统环境变量中添加以下变量（详见 [添加环境变量 PATH](添加环境变量PATH.md)）：**

| 变量名 | 建议值 | 作用 |
|---|---|---|
| `NPM_CONFIG_PREFIX` | `D:\npm-global` | npm 全局包安装路径 |
| `NPM_CONFIG_CACHE` | `D:\npm-cache` | npm 缓存路径 |
| `PIP_CACHE_DIR` | `D:\pip-cache` | pip 缓存路径 |
| `GRADLE_USER_HOME` | `D:\AppData\.gradle` | Gradle 依赖缓存 |
| `GOPATH` | `D:\go` | Go 工作目录 |
| `GOMODCACHE` | `D:\go\pkg\mod` | Go 模块缓存 |

设置后**重新安装或首次运行**对应工具，数据会自动写入 D 盘，无需手动迁移。
