# 文件哈希校验与 HashMyFiles

下载完一个文件，先算一遍 SHA-256 再运行——能排除下载损坏、网盘替换、别人二次打包这几类问题。本文给三条系统自带的命令，再给一个带中文界面的图形工具 HashMyFiles。

---

## 1. 什么时候需要算 hash

| 场景 | 做法 |
|---|---|
| 网盘 / 群里拿到工具、镜像、样本 | 先算 hash 和发布方公布的比对，不一致就别运行 |
| 队友之间传 exe / jar / 固件 | 传完核一次，排除传输损坏或被换包 |
| 写复盘、交报告 | 把样本 SHA-256 写进去，别人能复现、能去查 |
| 比赛下发附件 | 和题目页给出的 hash 对齐，确认没下错 |

!!! warning "压缩包的 hash ≠ 里面文件的 hash"
    官方公布的通常是**压缩包本体**（如 ZIP）的 hash。如果你拿到的是别人重新打包的 `.rar` / `.7z`，包本身的 hash **一定**对不上——容器格式、压缩级别、时间戳都会改变结果。这种情况要解压后核对里面 payload（如 exe）的 hash，而不是断定文件坏了。

---

## 2. 系统自带的三种算法入口

| 方式 | 命令 | 支持算法 | 备注 |
|---|---|---|---|
| certutil（cmd 原生） | `certutil -hashfile "文件" SHA256` | MD2/MD4/MD5/SHA1/SHA256/SHA384/SHA512 | Vista 起自带；输出是中文句子，要自己截取 |
| PowerShell | `Get-FileHash "文件" -Algorithm SHA256` | MD5/SHA1/SHA256/SHA384/SHA512 | 返回对象，可批量、可导出 CSV |
| Git Bash（coreutils） | `sha256sum "文件"` | SHA-256，另有 `sha1sum` / `md5sum` / `b2sum` | 与 Linux 语义完全一致，支持 `-c` 批量校验 |

同一个文件用三种方式算，结果必须一致（下表 hash 仅为示意）：

```text
C:\> certutil -hashfile D:\demo\README.txt SHA256
SHA256 的 D:\demo\README.txt 哈希:
a429a4577b044d6c69705ca074789305e2a0fb9533f837705dfb702c79247599
CertUtil: -hashfile 命令成功完成。

PS> (Get-FileHash D:\demo\README.txt -Algorithm SHA256).Hash
A429A4577B044D6C69705CA074789305E2A0FB9533F837705DFB702C79247599

$ sha256sum /d/demo/README.txt
a429a4577b044d6c69705ca074789305e2a0fb9533f837705dfb702c79247599 */d/demo/README.txt
```

几个顺手的写法：

- certutil 只要纯 hash：`certutil -hashfile D:\a.exe SHA256 | findstr /v ":"`（哈希行没有冒号）
- Get-FileHash 直接取值：`(Get-FileHash D:\a.exe -Algorithm SHA256).Hash`
- 比较时**忽略大小写**（hash 是十六进制），建议统一转小写
- `sha256sum` 输出里的 `*` 表示二进制模式，正常现象
- Windows 11 资源管理器"属性"里**没有** hash 页签，别找了

### 2.1 批量

PowerShell 递归整目录、导出 CSV：

```powershell
Get-ChildItem D:\demo -Recurse -File |
  Get-FileHash -Algorithm SHA256 |
  Select-Object Hash, @{n='File';e={$_.Path}} |
  Export-Csv D:\hashes.csv -NoTypeInformation -Encoding UTF8
```

生成能跨平台校验的清单（Git Bash 与 Linux 通用）：

```bash
sha256sum *.exe > SHA256SUMS   # 生成清单
sha256sum -c SHA256SUMS        # 逐行校验，输出 OK / FAILED
```

cmd 里对当前目录所有 exe 批量算：

```bat
for %F in (*.exe) do @certutil -hashfile "%F" SHA256 | findstr /v ":"
```

---

## 3. HashMyFiles：图形化批量算

NirSoft 出品，免费、免安装，拖进窗口就出结果，适合一次算几十个文件，或者懒得敲命令的时候。

| 项目 | 值 |
|---|---|
| 官网 | [nirsoft.net/utils/hash_my_files.html](https://www.nirsoft.net/utils/hash_my_files.html) |
| 版本 | v2.52（2026） |
| 下载（通用 32 位） | [hashmyfiles.zip](https://www.nirsoft.net/utils/hashmyfiles.zip)（约 64 KB） |
| 下载（64 位） | [hashmyfiles-x64.zip](https://www.nirsoft.net/utils/hashmyfiles-x64.zip)（约 84 KB） |
| 算法 | MD5、SHA1、SHA-256、SHA-384、SHA-512、CRC32 |

解压到固定目录（例如 `D:\tools\HashMyFiles\`）后直接运行 `HashMyFiles.exe`，没有安装步骤，卸载就是删目录。

### 3.1 上手

1. **加文件**：把文件或文件夹直接拖进窗口；或用 `文件 → 添加文件` / `添加文件夹`（对话框里可勾"添加子文件夹下的文件"）/ `按通配符添加`（如 `D:\tools\*.exe`）。
2. **打开要算的算法**：`选项 → Hash 类型` 里勾上 `SHA-256`。默认只算 MD5/SHA1，SHA-256 要手动勾；不勾的话后面查 VirusTotal 也会提示"为了打开 VirusTotal 网页，你必须激活 SHA-256 校验"。
3. **加一列 SHA-256**：`查看 → 选择列`，在"列设置"里勾选并决定顺序（同一个对话框里能左右调整列的显示/隐藏和宽度）。
4. **复制**：选中行 `Ctrl+C`；或 `编辑 → 复制 SHA256` 只复制该列。
5. **比对（它没有"验签"按钮）**：HashMyFiles 不像校验工具那样让你粘贴期望值打勾，做法是——
    - 把官方公布的 hash 复制到剪贴板；
    - `选项 → 标记与剪贴板内复制的散列值相同的项`；
    - 列表里和剪贴板一致的行会被**标绿**，扫一眼就知道谁对上了。
    - 反过来查"列表里有没有重复"用 `选项 → 标记相同的散列值`。
6. **查信誉**：右键 → `打开VirusTotal 网站`（用 hash 拼 URL 打开，不上传文件本体）。
7. **导出**：`文件 → 保存选择的项目`，可选 文本 / 制表符分隔 / 表格文本 / HTML / XML / CSV，交报告直接贴表。
8. **右键菜单（需手动开）**：`选项 → 启用资源管理器右键菜单`，之后资源管理器里右键文件/文件夹就有 HashMyFiles 项。

!!! tip "命令行也能用"
    `HashMyFiles.exe /file "D:\a.zip" /SHA256`、`/folder "D:\下载"`、`/wildcard "*.iso"`、`/virustotal`，适合塞进脚本里批量跑。

### 3.2 装简体中文语言包（重点）

官方语言包**只有界面文本，不含程序本体**，别把 ini 当绿色软件使。

| 步骤 | 操作 |
|---|---|
| 1 | 下载 [hashmyfiles_schinese.zip](https://www.nirsoft.net/utils/trans/hashmyfiles_schinese.zip)（约 2 KB，译者 Qiang） |
| 2 | 解压，里面只有一个文件 `hashmyfiles_lng.ini` |
| 3 | 把这个 ini **放进 `HashMyFiles.exe` 所在目录**（和 exe 同级，不是桌面、不是 `%APPDATA%`） |
| 4 | **关掉正在运行的 HashMyFiles**（它启动时才读语言文件），重新打开 → 菜单、列名、对话框都变中文 |
| 5 | 想还原英文：把 ini 改名（如 `hashmyfiles_lng.ini.bak`）或移到别的目录，再重启程序 |

放好后目录长这样：

```text
D:\tools\HashMyFiles\
├─ HashMyFiles.exe
├─ hashmyfiles_lng.ini     ← 语言包放这里
└─ HashMyFiles.chm
```

装好后菜单变成：`文件 / 编辑 / 查看 / 选项 / 帮助`，其中 `选项 → Hash 类型 → SHA-256`、`查看 → 选择列`、`编辑 → 复制 SHA256` 就是上面 3.1 里说的位置。

!!! warning "语言包是 v2.43 时代的，程序是 v2.52"
    语言包里 `Version=2.43`，而程序已到 v2.52。v2.50 之后新增的少数文字（如"哈希开始时间 / 结束时间 / 计算耗时"几列）没有译文，会保持英文——属正常现象，不影响使用。想补全可以自己加，见下面的做法。

!!! note "自己生成或补翻译语言文件"
    在程序目录打开 cmd，执行

    ```bat
    HashMyFiles.exe /savelangfile
    ```

    会在同目录生成 `HashMyFiles_lng.ini`（内容是**当前正在使用**的语言），把 `=` 右边逐条改掉即可。

    - **会覆盖**同目录的中文语言包，动手前先改名备份。
    - 这个 ini 是 **ANSI（GBK）编码**，用记事本编辑后必须选"另存为 → 编码：ANSI"；存成 UTF-8 会乱码。
    - 改完重启程序生效；顺手按 `选项 → 查看` 之类逐项检查有没有漏翻。

---

## 4. 常见坑

1. **只从官网下**。NirSoft 的 zip 不带数字签名，下载完先给 zip 本身算一次 hash，必要时拿 hash 去 VirusTotal 查；别用"软件下载站"的镜像包。
2. **hash 对得上 ≠ 文件安全**。它只说明你和别人拿到的是同一份；样本类文件先丢沙箱/VT 看行为，再决定要不要运行，别用管理员权限裸跑。
3. **中文提示乱码**。cmd 里 `certutil` 的"哈希:"那行在代码页不匹配时可能显示成乱码，**hash 值本身不受影响**；语言包 ini 的编码问题见 3.2。
4. **大文件要等**。算 hash 要读完整文件，瓶颈在磁盘；v2.50 起列表里会显示计算耗时，别以为卡死了。
5. **算 hash ≠ 破 hash**。HashMyFiles / certutil 算的是文件摘要；爆破口令哈希是另一回事，看 [hashcat 使用手册](hashcat使用手册.md)。

---

## 5. 速查

| 需求 | 就用 |
|---|---|
| 单个文件，一条命令 | `certutil -hashfile "文件" SHA256` |
| 脚本里取 hash 字符串 | `(Get-FileHash "文件" -Algorithm SHA256).Hash` |
| 递归算整个目录 | `Get-ChildItem -Recurse -File \| Get-FileHash` |
| 批量生成/校验清单 | `sha256sum *.exe > SHA256SUMS` / `sha256sum -c SHA256SUMS` |
| 图形界面 + 中文 + 导出表格 | HashMyFiles（ini 丢到 exe 同级目录） |
| 核对别人公布的 hash | 复制到剪贴板 → `选项 → 标记与剪贴板内复制的散列值相同的项` |

---

*工具会更新，界面文字以实际版本为准；相关：[必备工具清单](../01-入门/必备工具清单.md)、[PowerShell 执行策略](Windows常见问题/PowerShell执行策略.md)。*
