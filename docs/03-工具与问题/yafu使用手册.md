# yafu 使用手册（离线整数分解）

> **版本对应**：YAFU 3.1.9（AVX2 构建，内置 GMP-ECM 7.0.5 / GMP 6.3.0）· 官方仓库 [bbuhrow/yafu](https://github.com/bbuhrow/yafu)
> **本机位置**：`D:\快捷方式\yafu.exe`（已改短名并入 PATH；`$PROFILE` 有包装函数固定工作目录到 `D:\yafu-work\`，任意目录直接敲 `yafu` 即可）
> **实测环境**：i9-13900HX（SSE41/AVX2/BMI2）· 全部数字为 2026-11-06 本机实跑

## 1. yafu 是干什么的

**离线大整数分解 + 素性判定**。比赛禁网时 FactorDB 不可用，yafu 就是"本地 FactorDB"：给一个合数吐出全部素因子。内置算法链：试除 → Pollard rho → P−1/P+1 → ECM → **SIQS（自研二次筛，主力）**；NFS 需外置 ggnfs（本 exe 未捆绑，见 §6）。

## 2. 快速上手（三条实测）

```powershell
cd C:\Users\星记\Downloads
# ① 一把梭分解（自动选算法链）
.\yafu-windows-avx2.exe "factor(10403)"
#   P3 = 101
#   P3 = 103
#   ans = 1                     ← 成功标志

# ② 50 位半素数 —— SIQS 实测 0.088 秒
.\yafu-windows-avx2.exe "factor(38496531895565156387230614535411605735840813349469)"
#   starting SIQS on c50: 3849...
#   SIQS elapsed time = 0.0884 seconds
#   P25 = 5099003768822373601419091
#   P25 = 7549814363925449124854159

# ③ 素性判定（数是素数时输出 P<位数> = 自身）
.\yafu-windows-avx2.exe "factor(1636007954745804602439513446189799023)"
#   P37 = 1636007954745804602439513446189799023   ← 真题的 r，素数实锤
```

命令行不传参则进入**交互模式**（`quit` 退出）；长命令写 `"factor(N)"` 时**引号必须**。

## 3. 命令速查

| 命令 | 用途 | 备注 |
|---|---|---|
| `factor(N)` | 全自动分解 | 先试除/rho/ECM 探路，再上 SIQS；日常只用它 |
| `siqs(N)` | 强制二次筛 | ≤~100 位十进制的绝对主力 |
| `ecm(N)` | 强制 ECM | 适合"有中等大小因子"的场景（因子 ≤~60 位） |
| `pm1(N)` / `pp1(N)` | P−1 / P+1 | 因子的 p−1/p+1 平滑时秒出，白捡的分 |
| `rho(N)` | Pollard rho | 小因子快筛 |
| `t(N)` | 纯试除 | 验证小素因子 |
| `factor(@文件)` | 批量分解 | 文件里一行一个数 |
| `threads=N` | 线程数 | 默认自动（识别到 13900HX 全核） |
| `tune` | 自校准 | 换机器时跑一次，写 yafu.ini |

## 4. 输出怎么读

- `P25 = 5099...`：**素因子**，数字 = 位数（P25 即 25 位素数）
- `C50 = ...`：还没分解开的**合数剩余**（c50 同义，出现在 "starting SIQS on c50"）
- `ans = 1`：本轮成功；`ans = 0`：失败/未完成
- `***factors found***\nP1 = ...`：factor() 的汇总块——**抄答案抄这里**
- 计时行 `SIQS elapsed time = ...`、ECM 曲线进度（B1=11e3…11e6 逐档跑）

## 5. CTF 实战定位（何时用 yafu）

比赛拿到 n 的检查顺序（手册样题知识库的标准套路）：

```
小素数试除 → 多公钥 gcd 共享素数 → 费马(p,q 相近) → 维纳(d 小) → dp/dq 泄露 → 【yafu 蛮力】
```

yafu 上场的典型场景：

1. **n ≤ ~70 位十进制**（RSA 里即 ≤232 bit 的小课题）：秒~分钟出，闭眼 `factor(n)`
2. **n 有结构线索但缺一角**：如已知 p+q 或 φ(n) 的部分场景，先 Python 推出候选再 yafu 验证
3. **快速素性判定**：比 sympy.isprime 更省心的整数黑盒（P<位数>=自身 即素数）
4. **真题联动**：ISCC 真题卷的 `nb = q·r`——gcd 拿到 q 后，`factor(r)` 立即验证 r 是 37 位素数（0.1 秒）

**速度预期**（i9-13900HX 实测/推算）：c50 ≈ 0.1s · c60 ≈ 数秒 · c70 ≈ 分钟级 · c80 ≈ 十分钟~小时 · c100+ 需 NFS，比赛改思路别硬磨。

## 6. 边界与坑

- **NFS 未捆绑**：`nfs()` 会找 `ggnfs_dir`（外置 GGNFS 二进制），本裸 exe 没有——c100+ 的比赛题通常另有漏洞（共享因子/小指数/结构），轮不到蛮力
- **`warning: could not open yafu.ini`**：无害；想消除就在工作目录建 `yafu.ini`（`tune` 会自动生成）
- **从只读目录调用报 `fopen error`**：yafu 往 CWD 写 session.log/factor.log——本机已用 `$PROFILE` 包装函数固定到 `D:\yafu-work\`，直接敲 `yafu` 不受影响；日志/中间产物去那里找
- **纯 CPU 工具**：吃满所有核但用不上 GPU；别和 GPU hashcat 抢机器——正好互补分兵
- **内存**：c80+ 的 SIQS 数十亿关系表可能吃 GB 级内存，虚拟机慎跑大数
- **Kali 上没有**：Windows exe 不通用，Linux 需源码编译（比赛用 Windows 这台即可，快得多）
- 输出里的 `Cached 664579 primes` 等启动日志是正常信息流，stderr 混着 stdout，管道取结果用 `grep "P[0-9]* =\|ans"`

## 7. 与本手册其他工具的配合

- **Python**：构造/验算（`sympy.randprime` 造测试数、`int(n)**` 传参）、从 pcap/文档提数后交给 yafu
- **hashcat / tshark**：各管一段——口令爆破、流量解析、整数分解，三件套凑齐离线工具链
- **EBCTFCodeBox**：RSA op 是"给定 p,q,e 算 d"的正向计算；**反向（给 n 分解）只有 yafu 能干**
