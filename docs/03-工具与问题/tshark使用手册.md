# tshark 使用手册（Wireshark 命令行 · 离线速查）

> **面向线下赛**：全程本地命令，不依赖联网。基准版本 Wireshark 4.6.x（tshark 语法 3.x/4.x 通用，本文所有命令均在 Kali + Wireshark 4.6.9 实测）。
> 配套阅读：[国密算法入门](../02-技术方向/国密算法入门.md)、[ISCC 真题复盘卷](../02-技术方向/ISCC密码安全赛真题卷.md)（国密 SSL VPN 流量实战）。

## 1. tshark 是什么、在哪

Wireshark 安装时自带，同一套解析引擎——**GUI 过滤框里能写的表达式，`-Y` 里原样能用**。

- Windows：`C:\Program Files\Wireshark\tshark.exe`（建议把该目录加入 PATH）
- Kali/Linux：`apt install tshark wireshark`（装 wireshark 元包即可）
- 同目录的兄弟工具：`capinfos`（文件信息）、`editcap`（转格式/裁剪）、`mergecap`（合并）、`text2pcap`、`rawshark`

## 2. 命令骨架：一条万能公式

```bash
tshark -r 文件.pcap -Y "显示过滤器" -T fields -e 字段1 -e 字段2
```

| 参数 | 作用 | 备注 |
|---|---|---|
| `-r 文件` | 读 pcap/pcapng | 也可读改过魔数的 modified pcap（4.x） |
| `-Y "表达式"` | 显示过滤器 | 与 GUI 过滤框语法完全相同 |
| `-f "表达式"` | 捕获过滤器 | BPF 语法（如 `tcp port 443`），仅抓包时用 |
| `-T fields` | 输出模式 | 配 `-e` 抽字段；另有 `-T json` / `-T ek` |
| `-e 字段名` | 要抽取的字段 | 可多个，Tab 分隔输出 |
| `-c N` | 只处理前 N 包 | 快速预览 |
| `-V` | 单包全展开 | 配 `-Y` 精挑包后看细节 |
| `-x` | 附十六进制转储 | 配 `-Y` 用 |
| `-q` | 安静模式 | 专配 `-z` 统计模块 |
| `-z 模块` | 统计 | 见第 5 节 |
| `-w out.pcap` | 写出原始文件 | 抓包或过滤后另存 |
| `-i eth0` | 在线抓包 | `-i any` 抓所有接口 |
| `-n` | 禁止名字解析 | 取证必加（MAC/IP 不反查主机名） |
| `-t ad` | 显示绝对时间 | 取证常用；`-tt` unix 时间戳 |
| `-2` | 两遍分析 | 需要完整 TCP 会话信息时加 |

## 3. 两种过滤器别搞混

| | 显示过滤器 `-Y` | 捕获过滤器 `-f` |
|---|---|---|
| 语法 | Wireshark 表达式（`ip.addr == 10.0.0.2`） | BPF（`host 10.0.0.2`） |
| 用途 | 读文件/抓包后筛选 | 只在 `-i` 在线抓包时用 |
| 示例 | `-Y "tls.handshake.type == 16"` | `-f "tcp port 443"` |

## 4. 显示过滤器字段速查

按协议分层背，字段名全部小写、点号分级：

| 协议 | 常用字段 / 表达式 |
|---|---|
| 通用列 | `_ws.col.Protocol`（协议列）`_ws.col.Info`（Info 摘要列——任何协议的"人话"描述） |
| frame | `frame.number` `frame.len` `frame.time` `frame contains "pass"` |
| eth | `eth.src` `eth.dst` `eth.type == 0x0800` |
| ip | `ip.addr` `ip.src` `ip.dst` `ip.ttl < 10` `ip.proto == 6` |
| tcp | `tcp.port` `tcp.stream` `tcp.len` `tcp.payload` `tcp.flags.syn == 1 && tcp.flags.ack == 1` `tcp.analysis.retransmission` |
| udp | `udp.port == 53` |
| http | `http.request.method == "POST"` `http.request.full_uri contains "login"` `http.response.code == 200` |
| dns | `dns.qry.name contains "flag"` |
| icmp | `icmp.type == 8`（ping 请求，经典 covert channel） |
| tls | `tls.handshake.type` `tls.handshake.ciphersuite` `tls.record.version == 0x0101` |
| wlan | `wlan.sa` `wlan.fc.type == 2` |

运算符：`==` `!=` `<` `>` `>=` `<=` `contains`（字节串包含）`matches`（正则）；逻辑用 `and` `or` `not`。字符串值要带引号：`http.request.method == "POST"`。

## 5. `-z` 统计模块速查（都配 `-q`）

| 命令 | 用途 |
|---|---|
| `tshark -r f.pcap -q -z conv,tcp` | TCP 会话总览：谁和谁、多少字节、多久 |
| `tshark -r f.pcap -q -z conv,ip` | IP 会话总览 |
| `tshark -r f.pcap -q -z endpoints,ip` | 各 IP 收发总量（一眼找出刷流量的人） |
| `tshark -r f.pcap -q -z io,phs` | 协议分层占比（判断流量类型） |
| `tshark -r f.pcap -q -z follow,tcp,ascii,0` | 完整跟读 0 号流（`raw` 为十六进制） |
| `tshark -r f.pcap -q -z expert` | 专家警告汇总（重传/校验和错等） |

## 6. 输出、导出与兄弟工具

```bash
tshark -r f.pcap -T fields -e frame.number -e ip.src -e tcp.payload > out.tsv
tshark -r f.pcap -T json > out.json                  # 完整结构化（文件大，配 -Y 先筛）
tshark -r f.pcap --export-objects http,httpdir       # 取证神器：把 HTTP 传输的文件全导出
tshark -r f.pcap -w filtered.pcap -Y "tcp.port==443" # 过滤结果另存为新 pcap
```

| 工具 | 一句话用途 |
|---|---|
| capinfos | 文件信息：类型/包数/时长（**识别魔改 pcap 第一步**） |
| editcap | 转格式（`-F pcap`）、裁剪（`-A/-B` 时间区间）、去重（`-d`） |
| mergecap | 合并多份 pcap |
| text2pcap | 把文本 hex 重组回 pcap（自己造样本时用） |
| rawshark | 直接喂原始字节流 |

## 7. 国密 TLCP 流量解析（国内比赛重点）

Wireshark 4.0+ **原生支持 TLCP**（GB/T 38636-2020，record 版本 `0x0101`；GM/T 0024-2014 同结构）。实测基准：Wireshark 4.6.9 + ISCC 真题 SSL VPN 抓包。

### 第一步：找服务端端口（decode-as 的参数从这来）

ClientHello（握手第一条消息）的**目的端口 = 服务端端口**，一行定位：

```bash
tshark -r f.pcap -Y "tls.handshake.type == 1" -T fields -e tcp.dstport   # 真题数据1 → 10443
```

已装 GMSSL.lua 时，443 流量会被插件接管（原生 `tls.*` 字段不存在），换插件字段查：

```bash
tshark -r f.pcap -Y "GMSSL.Hello.Type == 1" -T fields -e tcp.dstport     # 真题数据2 → 443
```

通用兜底（与插件无关、永远可用）——会话统计表，端口就在冒号后面：

```bash
tshark -r f.pcap -q -z conv,tcp
# 10.0.0.100:59813 <-> 10.0.0.2:443   ← 服务端 = 熟知端口那一侧(443/10443...)
```

默认包列表不显示端口，想知道每一帧的端口方向就抽字段：`-T fields -e tcp.srcport -e tcp.dstport -e _ws.col.Protocol`。拿到端口后的规则：443 → GMSSL 插件自动生效；其他端口 → `-d "tcp.port==该端口,gmssl"`。

### 7.1 认出它是国密

```
capinfos -t f.pcap                              # 先看类型
tshark -r f.pcap -Y "tls.record.version == 0x0101" -c 3
tshark -r f.pcap -Y "tls.handshake" -T fields -e frame.number -e tls.handshake.type -e tls.record.version
```

实测输出（ISCC 真题数据 1）：

```
1  1      0x0101     ClientHello
2  2      0x0101     ServerHello
3  11     0x0101     Certificate
4  12     0x0101     ServerKeyExchange
5  13,14  0x0101     CertificateRequest + ServerHelloDone
6  11     0x0101     客户端 Certificate        ← 出现 = 双向认证
7  16     0x0101     ClientKeyExchange
8  15     0x0101     CertVerify
```

**单向/双向判定不靠背规范，数三个消息**：服务端 `CertificateRequest(13)`、客户端 `Certificate(11)`、`CertVerify(15)`——出现即双向。

> 上表第 4 列的名字是**注释**，不是 `-T fields` 的输出——`-T fields` 只输出 `-e` 指定的字段（所以你的终端只有三列数字）。要 tshark 直接报消息名，加 **Info 列字段** `_ws.col.Info`：
>
> ```bash
> tshark -r f.pcap -Y "tls.handshake" -T fields -e frame.number -e tls.handshake.type -e _ws.col.Info
> # 1  1      Client Hello
> # 2  2      Server Hello
> # 3  11     Certificate
> # 4  12     Server Key Exchange
> # 5  13,14  Certificate Request, Server Hello Done
> # 7  16     Client Key Exchange
> # 8  15     Certificate Verify, Change Cipher Spec, Encrypted Handshake Message
> ```

**type 对照与"为什么写 2 / 写 16"**：`tls.handshake.type` 是协议常量（写死在规范里，任何 pcap 都一样）——1=ClientHello、**2=ServerHello**、11=Certificate、12=ServerKeyExchange、13=CertificateRequest、14=ServerHelloDone、**16=ClientKeyExchange**、15=CertVerify、20=Finished。**套件号没有 type**：它是协商结果，藏在 ServerHello（type 2）的载荷里，每个 pcap 可能不同。所以——想知道**用了什么算法** → 过滤 `type == 2` 读套件；想拿**预主密钥原料**（65 字节临时 SM2 公钥）→ 过滤 `type == 16` 切载荷；判**单向/双向** → 数 13/11/15 是否出现。理论推导见知识库 [#589](https://bigcctf.org.cn/wiki/589) 第 5–7 节。

### 7.2 套件号（ECDHE 还是 ECC）

```
tshark -r f.pcap -Y "tls.handshake.type == 2" -T fields -e tls.handshake.ciphersuite
```

| 值 | 含义 |
|---|---|
| `0xe011` | ECDHE_SM4_CBC_SM3（真题数据 1，双向） |
| `0xe013` | ECC_SM4_CBC_SM3——SM2 密钥交换协议（真题数据 2） |
| `0xe033` | ECCC_SM4_CBC_SM3（SM2 加密证书） |

### 7.3 抽 ClientKeyExchange 里的临时公钥（预主密钥核心数据）

字段层**拿不到**载荷——`-V` 展开会提示 `Ciphersuite not implemented`（这是"手工接棒"的信号，不是解密失败）。退一档用 `tcp.payload` 报原始 hex，再按结构切片：

```
tshark -r f.pcap -Y "tls.handshake.type == 16" -T fields -e tcp.payload
# 1601010049 10000045 03000041 04fc57e6dbc6...
#   │record头  │hs头：type=0x10 len=0x45(69)
#   │                    └ 04fc57e6... = 65 字节临时 SM2 公钥(04‖X‖Y)
#   └ type=0x16 ver=0x0101 len=0x49(73)
```

一条命令离线切出（Kali/任何 Linux 自带 python3）：

```bash
tshark -r f.pcap -Y "tls.handshake.type == 16" -T fields -e tcp.payload | head -1 | python3 -c "
import sys
b = bytes.fromhex(sys.stdin.read().strip())
print(b[13:13+65].hex())   # 跳过 record头5B + hs头4B + 前缀4B
"
```

实测输出与手工逐字节解析完全一致（真题答案 `04fc57e6…21dace6d`）。

**"去前 4 字节前缀"换个好记的说法**：hex 里 1 字节 = 2 个字符，所以就是**掐掉开头 8 个字符（`03000041`，其中 0x41 = 65 是长度声明），留下后面 130 个字符（`04` 开头 = 65 字节公钥）**。校验：8 + 130 = 138 = 69 字节 × 2。

### 不想手工？把切片逻辑存成脚本，一条命令

上面的 record/握手两级头只需理解一次，之后交给现成脚本：本仓库 `03-工具与问题/scripts/tlcp_cke.py`（纯 Python、无第三方依赖）。它自动识别 modified 魔数（内置跳 8 字节）、重组 TCP 流、按两级头列出全部握手消息、自动抽出 65 字节临时公钥、自动报套件号（有 Wireshark 环境时也可直接用 §9 的 GMSSL.lua 插件，效果等价）：

```bash
python tlcp_cke.py f.pcap
```

真题实测节选（数据 2 是 modified pcap，脚本直接读、无需修复）：

```
== 流 3.3.3.4:49374 -> 3.3.3.3:10443
  [ClientHello] ver=0x0101 len=41
  [ClientKeyExchange] ver=0x0101 len=69
      临时公钥候选(65B): 04fc57e6dbc62d06...21dace6d
== 流 3.3.3.3:10443 -> 3.3.3.4:49374
  [ServerHello] ver=0x0101 len=38
      选定/出现套件: 0xe011(ECDHE_SM4_CBC_SM3) @偏移35
  [CertificateRequest] ver=0x0101 len=6      ← 出现 = 双向认证
```

**顺带分清三个密码工具的分工**：GmSSL / Tongsuo / Python gmssl 是**算法与协议库**（自己发起 TLCP 连接、验签、拿密钥后的加解密）——它们不解析 pcap；抓包抽字段 = tshark（字段层）+ 这个脚本（载荷层）。CKE 里的临时公钥在 ChangeCipherSpec 之前，本来就是明文，所以这件事从头到尾不需要密码库。

### 7.4 预主密钥速记

RSA 类套件 = 客户端生成 48 字节；ECC 套件 = SM2 密钥协商 **16 字节、双方共同产生**；ECDHE = 双临时密钥协商（具备前向安全）。

## 8. 魔改 pcap：Wireshark 能不能读？

Wireshark 4.x 内置多种 90 年代魔改 libpcap 的**历史布局**，打开时逐个候选解释、读前 3 条记录打分择优。实测矩阵（真题数据逐一构造验证）：

| 魔数 | 每包附加字节 | Wireshark 识别为 | 结果 |
|---|---|---|---|
| 标准 `d4c3b2a1` | 0 | 标准 pcap | ✓ |
| 标准 `d4c3b2a1` | 4 | Nokia tcpdump - pcap | ✓ |
| 标准 `d4c3b2a1` | 8 | RedHat 6.1 tcpdump - pcap | ✓ |
| `34cdb2a1` | 8 | Modified tcpdump - pcap | ✓（真题数据 2） |
| `34cdb2a1` | 12 | SuSE 6.3 tcpdump - pcap | ✓ |
| `34cdb2a1` | 0 / 4 | 无对应变体 | ✗ 报损坏 / 乱码假包 |

**用法**：先 `capinfos -t`——报出 "Modified/SuSE/RedHat/Nokia" 等名字就是能读，直接 `tshark -r` 上；scapy 拒读这些格式（只实现标准 pcap）。对于不在表内的自造 N，或要走 scapy 路线时，手工切包：按"16B 包头 + N 附加 + incl 数据"循环走文件（推导方法见真题卷思路回放），或用 scapy 前先修魔数重建：

```python
import struct, io
from scapy.all import PcapReader
raw = open('data2.pcap', 'rb').read()
fixed = bytearray(raw); fixed[0:4] = bytes.fromhex('d4c3b2a1')
body = bytearray(); off = 24
while off + 24 <= len(raw):
    incl = int.from_bytes(raw[off+8:off+12], 'little')
    body += raw[off:off+16] + raw[off+16+8:off+16+8+incl]   # 跳过 8B 附加
    off += 16 + 8 + incl
pkts = list(PcapReader(io.BytesIO(bytes(fixed[:24]) + bytes(body))))
```

## 9. 现成 Lua 插件：GMSSL.lua（国密握手直接字段化）

不想写脚本也不想手工？用 **GMSSL.lua 插件**——⚠️ **只使用本仓库的修补版** `03-工具与问题/scripts/GMSSL.lua`（上游 [leavesth/gmssl_wireshark](https://github.com/leavesth/gmssl_wireshark) 的原版存在五处缺陷：拼写错误、接管 443 后原生 `tls.*` 字段失效、Info 列描述拼接、跨段 record 不解析、丢消息——修补版已全部修复，文件头有 10 条 patch 说明，**勿直接从 GitHub 下载原版使用**）。**安装**：修补版放进 `%APPDATA%\Wireshark\plugins\`（Windows）；Linux/Kali 建议放全局目录 `/usr/lib/x86_64-linux-gnu/wireshark/plugins/`（全局目录不受"root 下禁用 Lua"限制，root 直跑也可用），重启 Wireshark/tshark 即加载（`tshark -G plugins` 可确认）。

插件默认只挂 **tcp.port 443**：443 端口的国密流量自动按 GMSSL 协议解析（协议列变 GMSSL，消息名直接可见，CKE/SKE 载荷字段化）。其他端口用 decode-as 强制：

```bash
# 注意大小写：decode-as 的名字是小写 gmssl，字段名前缀是大写 GMSSL.*
tshark -r f.pcap -d "tcp.port==10443,gmssl" -Y "GMSSL.Hello.ClientKeyExchangeData" \
  -T fields -e GMSSL.Hello.ClientKeyExchangeData
# 输出 CKE 完整载荷（含 65 字节临时 SM2 公钥）：0300004104fc57e6...
```

实测（4.6.9 + 真题两份）：数据 2（443 端口）自动触发，数据 1（10443 端口）加 `-d` 后同样出 CKE 数据。

**插件字段清单**（前缀 `GMSSL.`，全部实测可用）：

| 字段（省略前缀） | 内容 | 真题实测 |
|---|---|---|
| `Hello.CipherSuite` | 套件**可读名**（字符串） | ClientHello 上 = `(2) Suites 57363,57395`（报出 offered 列表） |
| `Hello.CipherSuite.CipherSuiteValue` | 套件数值（**十六进制显示**） | ClientHello = `0xe011`；数据 2 = `0xe013,0xe033`；ServerHello 拍板 = `0xe013` |
| `Hello.KeyExchange` | ServerKeyExchange 载荷 | `0300004104cf4b4a…`（65 字节点在偏移 13 起） |
| `Hello.ClientKeyExchangeData` | ClientKeyExchange 载荷 | 数据 1：`0300004104fc57e6…`；数据 2：`009b308198…` |
| `Hello.Random` / `Hello.SesId` | 随机数 / 会话 ID | ServerHello 实测 ✓ |
| `Hello.CertReq` / `Hello.CertVerifyData` / `Hello.ApplicationData` | 证书请求 / 验证 / 加密数据 | 同前缀用法 |

套件一眼速查（offered 与拍板同屏）：`tshark -r f.pcap -Y "GMSSL.Hello.CipherSuite.CipherSuiteValue" -T fields -e frame.number -e _ws.col.Info -e GMSSL.Hello.CipherSuite.CipherSuiteValue`，输出如 `1 Client Hello 0xe011`、`2 Server Hello 0xe011`。

GUI 用法（不想敲命令）：打开抓包 → 443 流量自动按 GMSSL 解析；非标端口选中任意相关包 → **Analyze → Decode As** → 加一条 `TCP(port) == 10443 → GMSSL` → 确定，之后协议列与字段过滤器同上。

**存档副本是修补版**（文件头有 10 条 patch 说明；上游原版问题全部修复，含 Kimi 审查确认项）：

- 拼写：`Certficate` → `Certificate`、`COmpress` → `Compress`；
- 接管 443 后原生 `tls.*` 字段失效 → GMSSL 分支链式调用原生解析器（仅循环前一次），`tls.*` 与 `GMSSL.*` 字段同帧共存；
- Info 列沿用原生 TLCP 描述（含 SNI），插件不覆写。**注**：最初用的 `fence_set` 在 4.6.9 Column API 中不存在（`-V` 才可见的 Lua 错误，stderr 不显示）；第二次原生调用会重复添加字段（`tls.handshake.type` 变 `1,1`）——两者均已删除（Kimi 审查发现）；
- **跨 TCP 段无重组 → 已加 record 级 desegment 反重组**：跨段 record（如 1604B 证书链）完整解析，"Ignored Unknown Record" 消失；
- 一个 record 含多条握手消息时丢消息 → record 内消息循环 + 每 record 无条件钳位到 recEnd（欠读/过冲都归位）；
- **8 个消息解析器全部 pcall 隔离**（Kimi 审查 A 项）：畸形消息长度（如会话复用 ServerHello 的 32B session_id 触发越界）不再中止整帧解析，按消息头回退推进；
- **CCS 与加密 Finished 分属不同帧**时密文帧会丢状态 → CCS 状态改**会话级**（方向四元组键，消费后清除，上限 4096）；
- 套件查询表外提文件级（原版每次查表重建 ~420 项）；
- CipherSuiteValue 十六进制显示（`0xe011`），ServerHello 帧也登记该字段。

修补后两份真题 pcap 全部帧统一显示 GMSSL、`-V` 深查零 Lua 错误。**回归测试**：`scripts/test_gmssl.py` 一条命令全量验证（21 项：真题帧数/双消息/CKE 前缀/套件号/零错误 + 两个合成 pcap 测试——CCS 分帧状态与 0x30 截断不崩），插件再改动后必跑。保留脾气：

- 默认只挂 443，其他端口要 `-d`（decode-as 名小写 `gmssl`）；字段前缀大写 `GMSSL.*`；
- 检查 Lua 错误要用 `tshark -r f.pcap -V 2>&1 | grep -i "lua"`——stderr 重定向**看不到**解析器内部错误；
- 与原生 TLCP（第 7 节）互补：原生给 record 框架、套件号与单向/双向判定，本插件给 CKE/SKE 载荷字段。GUI 里 Decode As 对话框同样可用。

另有两项 Kimi 清单项同批修复（patch 头第 9/10 条）：**CCS 状态改会话级**（按方向四元组键——CCS 与加密 Finished 分属不同帧时不再丢状态，密文帧正确标注 EncryptedHelloData，状态表上限 4096 防泄漏）；**套件表外提文件级**（原版每次查表重建 ~420 项）。

## 10. 常用组合命令十条（按比赛场景背）

```bash
# 1 总览：文件什么类型、多少包
capinfos -t f.pcap && tshark -r f.pcap -c 3
# 2 谁的流量最大
tshark -r f.pcap -q -z endpoints,ip
# 3 跟读某条流找明文
tshark -r f.pcap -q -z follow,tcp,ascii,0
# 4 关键字直接搜（口令/flag 常藏明文）
tshark -r f.pcap -Y 'frame contains "pass" || frame contains "flag"'
# 5 HTTP 传输的文件全部导出（取证题）
tshark -r f.pcap --export-objects http,httpdir
# 6 DNS 查询列表（外带数据/挖矿域名）
tshark -r f.pcap -T fields -e dns.qry.name -Y "dns.flags.response == 0" | sort -u
# 7 TCP 握手扫描行为（端口扫描取证）
tshark -r f.pcap -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0" | wc -l
# 8 TLS 握手序列（判断协议/认证方式）
tshark -r f.pcap -Y "tls.handshake" -T fields -e frame.number -e tls.handshake.type -e tls.handshake.ciphersuite
# 9 抓包（在线，写文件离线再分析）
tshark -i eth0 -w cap.pcap
# 10 两遍分析（要 tcp.stream/会话统计时更准）
tshark -r f.pcap -2 -q -z conv,tcp
```

## 11. 常见坑

- `-T fields` 忘配 `-e` → 无输出；字段名全小写点分级，写错不报错只是空列。
- `-Y` 里字符串必须带引号；`contains` 匹配字节串，`matches` 才是正则。
- root 运行 tshark 会有 "Running as user root" 警告——正常，忽略即可。
- 国密 record：字段层解析到握手类型/套件号为止，CKE/SKE 载荷显示 `Ciphersuite not implemented`——手工按 7.3 切片，别在这反复试过滤器。
- modified pcap：Wireshark 能读 ≠ scapy 能读 ≠ 流量能解开（SM4 会话密钥需要握手私钥）。
- 抓包 `Permission denied` → Linux 下 `cap_net_raw` 能力或 sudo。
