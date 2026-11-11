# PowerShell 设置代理（临时代理 / 每次开窗口自动设置）

命令行工具（`git clone`、`curl`、`pip install`、`npm install`……）不会自动走系统代理，需要给它们设置 `HTTP_PROXY` / `HTTPS_PROXY` 两个环境变量。本文给两种用法：

- **临时代理**：当前窗口敲两条命令，关窗即失效，偶尔用一次选它
- **永久代理**：写进 PowerShell 配置文件（`$PROFILE`），以后每次打开 PowerShell 自动设置好，一劳永逸

!!! info "端口 7897 是哪来的"
    `7897` 是 Clash Verge 的默认**混合端口**（HTTP/SOCKS 共用）。如果你用的是 Clash for Windows（默认 `7890`）或其他软件，去软件设置里确认自己的端口号，下文照改。

---

## 一、临时代理：当前窗口有效

### 设置

打开 PowerShell（`pwsh` 或系统自带 `powershell` 都行），执行：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
```

没有任何输出就是成功——环境变量不需要回显。

### 验证已生效

**方法一：查变量本身**

```powershell
$env:HTTP_PROXY
```

```
http://127.0.0.1:7897
```

原样打印出刚设的值，说明变量已就位。

**方法二：查出口 IP（更彻底，能确认代理真的通了）**

```powershell
curl http://ipinfo.io/ip
```

```
66.90.xx.xx
```

返回的是**代理节点的出口 IP**。想确认它和直连不同，可以对照直连的出口：

```powershell
curl --noproxy '*' http://ipinfo.io/ip
```

```
1.203.xx.xx
```

两个 IP 不一样，说明 curl 确实走了代理。（IP 已打码，以实际输出为准。）

### 取消临时代理

代理软件关了、或者这个窗口暂时不想走代理时：

```powershell
Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY
```

验证取消成功（输出为空行 / 不打印任何内容即已删除）：

```powershell
$env:HTTP_PROXY          # 此时无输出
```

### 为什么叫"临时"

`$env:XXX=` 设置的是**当前 PowerShell 进程**的环境变量——只存在于这个窗口里，窗口一关就没了；其他已打开的窗口、新开的窗口都不受影响。所以它适合"偶尔救个急"，要天天用就往下看永久方案。

---

## 二、永久代理：写进配置文件，每次开窗口自动设置

PowerShell 有个启动脚本机制：每次打开新窗口，会先自动执行一遍当前用户的**配置文件**（`$PROFILE` 指向的那个 `.ps1`）。把设代理的命令写进去，就等于每次开机开窗口都自动帮你敲一遍——这正是本站主力的做法。

### 第 1 步：查看自己的配置文件路径

```powershell
$PROFILE
```

```
C:\Users\星记\Documents\PowerShell\Microsoft.PowerShell_profile.ps1
```

（路径里的用户名是你自己的。）看看它现在存不存在：

```powershell
Test-Path $PROFILE
```

```
True
```

`True` 说明已有配置文件，直接编辑追加；`False` 也没关系，下一步保存时会自动创建。

### 第 2 步：编辑配置文件

```powershell
notepad $PROFILE
```

在文件里加入下面这段（本站主力实际在用的配置，含内网排除）：

```powershell
# 设置代理
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"

# 设置不用代理的地址
$env:NO_PROXY="localhost,127.*,192.168.*,10.*,172.16.*,172.17.*,172.18.*,172.19.*,172.20.*,172.21.*,172.22.*,172.23.*,172.24.*,172.25.*,172.26.*,172.27.*,172.28.*,172.29.*,172.30.*,172.31.*"

Write-Host "代理已设置: 127.0.0.1:7897" -ForegroundColor Green
Write-Host "排除内网地址: localhost, 127.*, 192.168.*, 10.*, 172.16-31.*" -ForegroundColor Gray
```

保存关闭。最后两行 `Write-Host` 不是必须的，但强烈建议保留——每次开窗口有绿字提示，一眼知道"这个窗口的代理是设好的"，省得猜。

`NO_PROXY` 的作用：匹配这些地址的请求**不走代理直连**。访问本机开发服务器（`localhost:8000`）、路由器管理页（`192.168.1.1`）之类的内网地址时不被代理劫持。没有内网需求可以不设这段。

### 第 3 步：让它生效

**已经打开的窗口不会自动重读配置文件**，两种方式二选一：

- 简单粗暴：关掉窗口，重新开一个
- 不想关：在当前窗口手动执行一遍配置文件

    ```powershell
    . $PROFILE
    ```

### 第 4 步：验证

新开一个 PowerShell 窗口，应该直接看到绿字提示，变量也已就位：

```
代理已设置: 127.0.0.1:7897
排除内网地址: localhost, 127.*, 192.168.*, 10.*, 172.16-31.*
```

```powershell
$env:HTTP_PROXY
```

```
http://127.0.0.1:7897
```

看到这两样，永久代理就配好了——以后每个新窗口都自动带代理。

!!! tip "配置文件里还能放什么"
    `$PROFILE` 就是普通的 PowerShell 脚本，除了代理，还可以放自定义函数、别名等。比如本站主力的配置文件里还定义了 `hashcat`、`yafu` 的直调函数和 tshark 补全。

---

## 三、常见坑

!!! warning "pwsh 和 powershell 的配置文件是两个文件"
    PowerShell 7（`pwsh`）和系统自带的 Windows PowerShell 5.1（`powershell`）各有各的配置文件，**互不相通**：

    | 窗口 | 配置文件 |
    |---|---|
    | `pwsh`（PowerShell 7） | `Documents\PowerShell\Microsoft.PowerShell_profile.ps1` |
    | `powershell`（5.1） | `Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` |

    只配了 pwsh 的文件，那 5.1 窗口里 `$env:HTTP_PROXY` 就是空的（本机实测如此）。两个都用的话，要么两个文件各写一份，要么把代理写进两者共用的 `profile.ps1`（`$PROFILE.CurrentUserAllHosts`）。

!!! warning "配置文件根本没执行？先查执行策略"
    如果新开窗口**看不到绿字提示**，多半是 `.ps1` 脚本被执行策略拦下了（Windows 默认禁止运行脚本）。解决方法见 [PowerShell 执行策略](PowerShell执行策略.md)。

!!! warning "代理软件没开，设了也白设"
    环境变量只是"告诉工具去连 127.0.0.1:7897"，代理软件本身没运行的话，请求会直接失败：

    ```
    curl: (7) Failed to connect to 127.0.0.1 port 7898 after 2041 ms: Couldn't connect to server
    ```

    （端口没在监听就是这个报错。）此时要么打开代理软件，要么按上文"取消临时代理"清掉变量。

---

## 四、速查

| 需求 | 命令 |
|---|---|
| 临时设代理 | `$env:HTTP_PROXY="http://127.0.0.1:7897"` + `$env:HTTPS_PROXY="http://127.0.0.1:7897"` |
| 临时取消代理 | `Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY` |
| 查看当前代理 | `$env:HTTP_PROXY` |
| 查配置文件路径 | `$PROFILE` |
| 编辑配置文件 | `notepad $PROFILE` |
| 重载配置文件 | `. $PROFILE` |
| 查出口 IP 验证 | `curl http://ipinfo.io/ip` |

---

## 相关页面

- [PowerShell 执行策略](PowerShell执行策略.md) — 配置文件不执行（看不到绿字提示）时先看这篇
- [添加环境变量 PATH](添加环境变量PATH.md) — 同为环境变量，PATH 管"去哪找程序"，代理变量管"流量走哪出去"
- [梯子获取](../../04-账号与工具/梯子获取.md) — 代理端口背后的软件从哪来
