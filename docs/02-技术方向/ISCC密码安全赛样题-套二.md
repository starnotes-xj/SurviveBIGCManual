# ISCC 密码安全赛 · 备赛样题集（套二）

> 本套侧重工程与实现：真实协议字段（TLS/WPA2）、KDF 派生、反编译源码审计。所有数值用 Python 实算并交叉核验，可直接复现。难度：★ 基础 · ★★ 主力 · ★★★ 拉分。

> **SageMath 说明**：数学/计算类题目的解析内附 SageMath 解法，全部在 **SageMath 10.9**（WSL + conda 环境）实测通过；没有 Sage 时用解析里的纯 Python 版本即可。

## 一、密码算法原理

### S2-A1 RSA dp 泄露：CRT 参数丢失即丢私钥 ★★★

某密码机的密钥备份界面截图泄露了一个 CRT 参数。已知该 RSA 公钥的 `dp = d mod (p−1)`：

```
n  = 53a20a5ef5628baa6d06190a09d0279ea19f788499ca4829800f57f282226f360602cbe85dacf3a02559b87fde31c9bd950414b3423712c05ca27dc100fcadac6b5651360a480ddeef2bea39fa98e6b4e3ad676f4031e7078a1591f5b3d575361a9e461a54a578a4315768a332460670a1f4e2e246ea56c204d75f2f7d0747b5
e  = 65537
dp = c8bebdcb3075ba0f31280c65a7181faa3e4214015ce551d4c5a530bb72e4f6dc1f5c55d0a9acb928eed0e3e9e14559e01f8522fe1f711c2c7046c2a53cc6e45
c  = 61c32fff909ed9a76a01d37948ecfbdf6affc2aad0fda0ae6dfdf3f02142d5924dc650a4ad35349308de5baaa4a543edbf2d8a9dc3fd9b99ccb410ab8ced488c8deb1d582cdd4464a3bea875767c9a00c8b70af752558234fe82242391c04cc3c7db08beeea1945535fd12f3ef701b46bd42b19914b42d1ac7bbe00fa38eeea
```

**任务**：仅凭 `n, e, dp` 分解 n 并解密 c，恢复明文（flag 格式）。

**所需知识**：RSA-CRT 加速结构（dp=d mod (p−1)、dq=d mod (q−1)）、同余式 e·dp ≡ 1 (mod p−1)、小系数枚举（e·dp−1 = t·(p−1)，t < e）、素性整除验证

??? tip "答案与解析"
    **答案：`flag{dp_leak_breaks_rsa}`**

    **同余式 `e·dp ≡ 1 (mod p−1)` 的推导**（两步）：

    1. RSA 密钥生成满足 `e·d ≡ 1 (mod φ(n))`，即 `e·d − 1 = k·(p−1)(q−1)`——右边整体是 `(p−1)` 的倍数，故 `e·d ≡ 1 (mod p−1)`（大模同余可以缩小到自己的因子模）；
    2. 由定义 `dp = d mod (p−1)` 知 `d = dp + j·(p−1)`，两边乘 e：`e·d ≡ e·dp (mod p−1)`。

    两条合起来即 `e·dp ≡ 1 (mod p−1)`。（dp 如此定义的动机：费马小定理 `m^(p−1) ≡ 1 (mod p)` 保证 `m^d ≡ m^(d mod (p−1)) (mod p)`，签名加速就是用它把指数从 2048 位砍到约 1024 位。）

    **t < e 的来源**：由 `e·dp − 1 = t·(p−1)` 和 `0 < dp < p−1` 得 `t·(p−1) < e·dp < e·(p−1)`，故 `t < e`——枚举范围被死死框在 [1, e)。枚举 t：对每个能整除 `e·dp−1` 的 t，候补素数 `p = (e·dp−1)/t + 1`，用 `n mod p == 0` 验证即命中（本题 t = 6279）。

    ```python
    n  = 0x53a2...74b5          # 题干材料
    e, dp, c = 65537, 0xc8be...6e45, 0x61c3...eeea
    p = None
    for t in range(1, e):
        if (e*dp - 1) % t: continue
        pc = (e*dp - 1)//t + 1
        if n % pc == 0: p = pc; break
    q = n // p
    d = pow(e, -1, (p-1)*(q-1))
    m = pow(c, d, n)
    print(m.to_bytes((m.bit_length()+7)//8, 'big').decode())
    # flag{dp_leak_breaks_rsa}
    ```

    识别特征：题目给 `dp`（或 `dq`）就是这题。**教训**：CRT 参数（dp、dq、qinv）与私钥 d 等价泄露，备份界面、日志、调试输出里出现任何一个都要当作私钥泄露处理。

### S2-A2 GHASH 认证码计算（AES-GCM 内部） ★★

AES-GCM 的认证标签 `tag = E_K(J0) ⊕ GHASH(H, A, C)`。GHASH 是 GF(2¹²⁸) 上的多项式哈希，`H` 为认证密钥。块按大端解释为 128 位整数，约减多项式 x¹²⁸+x⁷+x²+x+1 对应常量 `R=0xE1000000000000000000000000000000`；最后一块是 `len(A)`、`len(C)` 的比特数（各 8 字节大端拼接）。

```
H   = f29000b62a499fd0a9f39a6add2e7780
A   = GET /api/transfer
C   = b5f494d63d5d7f2c5301ad730fe2f6070e35847b255d
```

**任务**：计算 `GHASH(H, A, C)`，提交 16 字节十六进制。

**所需知识**：GF(2¹²⁸) 有限域乘法、GCM 认证结构、分组补零、长度块编码、大端字节序

??? tip "答案与解析"
    **答案：`b58a8c02dee68092a7e605d01c2b0e5d`**

    ```python
    R = 0xE1000000000000000000000000000000
    def gf_mul(x, y):
        z = 0; v = y
        for i in range(128):
            if (x >> (127 - i)) & 1: z ^= v
            if v & 1: v = (v >> 1) ^ R
            else: v >>= 1
        return z
    H = 0xf29000b62a499fd0a9f39a6add2e7780
    A = b"GET /api/transfer"
    C = bytes.fromhex("b5f494d63d5d7f2c5301ad730fe2f6070e35847b255d")
    X = 0
    for data in (A, C):
        for i in range(0, len(data), 16):
            blk = data[i:i+16].ljust(16, b'\x00')
            X = gf_mul(X ^ int.from_bytes(blk, 'big'), H)
    L = (len(A)*8).to_bytes(8, 'big') + (len(C)*8).to_bytes(8, 'big')
    X = gf_mul(X ^ int.from_bytes(L, 'big'), H)
    print(X.to_bytes(16, 'big').hex())
    ```

    注意：约减常量是 `0xE1…00`（0x87 的位反转），X 的位从最高位判断。

        **SageMath 解法**（10.9 实测）：商环 `GF(2)[x]/(x^128+x^7+x^2+x+1)` 直接做多项式乘法——约定"块的最高位 = x⁰ 的系数"：

    ```python
    from Crypto.Util.number import long_to_bytes
    R2.<x> = GF(2)[]
    K = R2.quotient(x^128 + x^7 + x^2 + x + 1)
    b2p = lambda v: K(R2([(v >> (127 - i)) & 1 for i in range(128)]))
    p2b = lambda e: long_to_bytes(sum(1 << (127 - c) for c in e.lift().exponents()), 16)
    A, C = b"GET /api/transfer", bytes.fromhex('b5f494d63d5d7f2c5301ad730fe2f6070e35847b255d')
    H, X = b2p(0xF29000B62A499FD0A9F39A6ADD2E7780), K(0)
    for data in (A, C):
        for i in range(0, len(data), 16):
            X += b2p(int.from_bytes(data[i:i+16].ljust(16, b'\x00'), 'big')); X *= H
    X += b2p(len(A)*8*2^64 + len(C)*8); X *= H
    print(p2b(X).hex())     # b58a8c02dee68092a7e605d01c2b0e5d
    ```python
    R2.<x> = GF(2)[]
    K = R2.quotient(x^128 + x^7 + x^2 + x + 1)
    def blk2poly(v):
        return R2([(v >> (127 - i)) & 1 for i in range(128)])
    def poly2blk(e):
        out = 0
        for c in e.lift().exponents():
            out += 1 << (127 - c)
        return int(out).to_bytes(16, 'big')
    H = K(blk2poly(0xF29000B62A499FD0A9F39A6ADD2E7780))
    A = b"GET /api/transfer"
    C = bytes.fromhex('b5f494d63d5d7f2c5301ad730fe2f6070e35847b255d')
    X = K(0)
    for data in (A, C):
        for i in range(0, len(data), 16):
            X += K(blk2poly(int.from_bytes(data[i:i+16].ljust(16, b'\x00'), 'big')))
            X *= H
    v = (len(A)*8).to_bytes(8, 'big') + (len(C)*8).to_bytes(8, 'big')
    X += K(blk2poly(int.from_bytes(v, 'big')))
    X *= H
    print(poly2blk(X).hex())     # b58a8c02dee68092a7e605d01c2b0e5d
    ```

## 二、密码协议设计

### S2-B1 TLS 1.3 的 HKDF-Expand-Label 派生 ★★

TLS 1.3（RFC 8446）用 HKDF 做密钥调度。`Derive-Secret(Secret, Label, Messages) = HKDF-Expand-Label(Secret, Label, Transcript-Hash(Messages), 32)`。给定：

```
handshake_secret = 9d2f1b6c4e7a0d3c5b8e1f204a7c9d3e6b5a4c8f2e1d0b7a3c5e9f1d2b4a6c8f
transcript_hash  = f2e4a6c8d0b1e3f5a7c9d2b4e6f8a1c3d5b7e9f2a4c6d8e0b1f3a5c7d9e2b4f0
label            = "c hs traffic"
```

HKDF-Expand-Label 的 info 编码为：`uint16(length) ‖ 1字节(label长度) ‖ "tls13 "+label ‖ 1字节(context长度) ‖ context`；HKDF-Expand 用 HMAC-SHA256 展开（`T(i)=HMAC(prk, T(i-1)‖info‖byte(i))`）。

**任务**：计算 `client_handshake_traffic_secret`（32 字节十六进制）。

**所需知识**：HMAC-SHA256、HKDF-Extract/Expand、RFC 8446 HkdfLabel 编码、密钥调度层级

??? tip "答案与解析"
    **答案：`3ac31df9f5762aa071ed6904529585d6c5af85a281c59f92dbfeba83a9901958`**

    ```python
    import hmac, hashlib
    def hkdf_expand(prk, info, L):
        out = b''; t = b''; i = 1
        while len(out) < L:
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            out += t; i += 1
        return out[:L]
    hs = bytes.fromhex("9d2f1b6c4e7a0d3c5b8e1f204a7c9d3e6b5a4c8f2e1d0b7a3c5e9f1d2b4a6c8f")
    th = bytes.fromhex("f2e4a6c8d0b1e3f5a7c9d2b4e6f8a1c3d5b7e9f2a4c6d8e0b1f3a5c7d9e2b4f0")
    label = b'tls13 c hs traffic'
    info = (32).to_bytes(2, 'big') + bytes([len(label)]) + label + bytes([len(th)]) + th
    print(hkdf_expand(hs, info, 32).hex())
    ```

    注意：`"tls13 "` 前缀（含空格）与 uint16 长度字段，漏前缀或字节序写反是丢分点。

### S2-B2 WPA2 四次握手 PTK 派生 ★★

WPA2-PSK 四次握手：`PTK = PRF-512(PMK, "Pairwise key expansion", Min(AA,SA)‖Max(AA,SA)‖Min(ANonce,SNonce)‖Max(ANonce,SNonce))`。PRF-512 第 i 轮 `HMAC-SHA1(PMK, "Pairwise key expansion"‖0x00‖B‖chr(i))`，累计 64 字节。已知：

```
PMK    = 83a3b53a28d7227237971272fe65ecfd74745c5e908b5493a4e913451095d4d4
AA(AP) = 001122334455
SA(STA)= 66778899aabb
ANonce = 97820d56d8b1a58913ce97c0d9f43b0aa1be35ec6ed01872776e89e93eca00ab
SNonce = d2564b9f36871a8cc145bc63c66efb993ab4f94996c86fe0147f3ffec0b5ef1e
```

**任务**：计算 PTK 前 16 字节（KCK，用于校验第 2 条握手消息 MIC），提交十六进制。

**所需知识**：WPA2 四次握手、802.11i PRF-512（HMAC-SHA1 逐轮）、min/max 字节字典序比较、PTK 分段（KCK/KEK/TK）

??? tip "答案与解析"
    **答案：`33031d2b1ea6d1bb4dc4a488e70a70f4`**

    ```python
    import hmac, hashlib
    pmk = bytes.fromhex("83a3b53a28d7227237971272fe65ecfd74745c5e908b5493a4e913451095d4d4")
    AA = bytes.fromhex("001122334455"); SA = bytes.fromhex("66778899aabb")
    AN = bytes.fromhex("97820d56d8b1a58913ce97c0d9f43b0aa1be35ec6ed01872776e89e93eca00ab")
    SN = bytes.fromhex("d2564b9f36871a8cc145bc63c66efb993ab4f94996c86fe0147f3ffec0b5ef1e")
    B = min(AA, SA) + max(AA, SA) + min(AN, SN) + max(AN, SN)
    out = b''; i = 0
    while len(out) < 64:
        out += hmac.new(pmk, b"Pairwise key expansion" + b'\x00' + B + bytes([i]), hashlib.sha1).digest()
        i += 1
    print(out[:16].hex())
    ```

    考点：PRF 里的单字节计数器 `chr(i)` 与中间那个 `0x00`，地址/随机数先按字典序排 min/max。

## 三、密码技术部署与运维

### S2-C1 PBKDF2 密钥派生 ★

运维用 PBKDF2-HMAC-SHA256 从口令派生存储加密密钥，参数如下：

```
口令 = bigc@ISCC2026#pass   盐 = 3a9c1e5f7b2d4086
迭代次数 = 100000           输出长度 = 32 字节
```

**任务**：计算派生密钥（32 字节十六进制）。

**所需知识**：PBKDF2/HMAC-SHA256 派生、盐与迭代次数安全取值、慢哈希抗暴力破解

??? tip "答案与解析"
    **答案：`ecfeab0d77adaa2e154f679e60a1eb8f6d3b41283ffb209d9965466c41370063`**

    ```python
    import hashlib
    print(hashlib.pbkdf2_hmac('sha256', b"bigc@ISCC2026#pass",
                              bytes.fromhex("3a9c1e5f7b2d4086"), 100000, 32).hex())
    ```

    要点：盐每口令随机、迭代≥10 万、常量时间比较。

### S2-C2 HMAC-SHA256 网关签名 ★

API 网关对规范报文做 HMAC-SHA256 签名做完整性校验。已知：

```
密钥 = gw-secret-2026-key
报文 = GET/api/v1/orders?uid=1001&ts=1735689600
```

**任务**：计算 HMAC-SHA256 签名（十六进制）。

**所需知识**：HMAC 构造、消息认证码用途、API 签名与重放防护

??? tip "答案与解析"
    **答案：`3d13657d66553464acb0dcc3f3d82fd30f8f6d14889413188dcbc9875588c9d8`**

    ```python
    import hmac, hashlib
    print(hmac.new(b"gw-secret-2026-key",
                   b"GET/api/v1/orders?uid=1001&ts=1735689600",
                   hashlib.sha256).hexdigest())
    ```

    要点：报文带时间戳 `ts` 防重放，签名必须覆盖全部字段。

## 四、密码应用合规检测

### S2-D1 TLS 密码套件合规检测 ★（分析）

testssl.sh 扫描某 HTTPS 站点，启用的密码套件如下：

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
TLS_RSA_WITH_AES_128_CBC_SHA
TLS_RSA_WITH_3DES_EDE_CBC_SHA
TLS_RSA_WITH_RC4_128_SHA
TLS_RSA_WITH_RC4_128_MD5
```

**任务**：指出不符合现行安全基线/密评要求的套件及原因。

**所需知识**：TLS 套件命名规则、前向保密（ECDHE/RSA 密钥交换）、RC4/3DES/SHA-1/MD5 已知弱点、CBC 与 AEAD(GCM)

??? tip "答案与解析"
    不合规项：`RC4_128_SHA`/`RC4_128_MD5`（RC4 废弃、MD5 更甚）；`3DES_EDE_CBC_SHA`（有效密钥 112 位，Sweet32 生日攻击）；`RSA_WITH_AES_128_CBC_SHA`（RSA 密钥交换无前向保密，CBC 无认证易被填充预言机）；`ECDHE_RSA_WITH_AES_256_CBC_SHA`（有前向保密但 CBC+SHA 非 AEAD，不推荐）。

    仅 `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` 合规。

### S2-D2 X.509 证书合规检测 ★★（分析）

一张服务器证书 `openssl x509 -text` 关键字段：

```
Signature Algorithm: sha1WithRSAEncryption
Validity: 2023-01-01 ~ 2033-01-01
Public Key: RSA 1024 bit
Subject Alternative Name: （无）
```

**任务**：逐条指出不合规之处及整改方向。

**所需知识**：X.509 证书字段、SHA-1 弃用时间线、RSA 密钥长度要求、证书有效期上限、SAN 与主机名校验

??? tip "答案与解析"
    ① SHA-1 签名已弃用（碰撞风险）→ 改 SHA-256；② RSA 1024 位强度不足（已被公开分解）→ 至少 2048；③ 有效期 10 年超 CA/B 论坛 398 天上限 → 缩短并轮换；④ 缺 SAN → 客户端按 RFC 2818 校验 SAN，缺失即主机名校验失败。

## 五、密码设备漏洞挖掘

### S2-E1 费马分解：p、q 过近的弱 RSA 密钥 ★★

某密码机生成的 RSA 公钥，审计发现两个素因子 p、q 相差过小（|p−q| ≈ 2¹³⁵），可用费马分解法在数秒内分解。已知：

```
n = c2f173659e957f76c94b8afd7cfbf5d235855c2cbc8b03bbf1bdaf81e012dd449cf39a7a234befced6722dcca9e6b6c4dd7598938a3dc92709f4eb5f6d983ef1
e = 65537
c = 63c06915ad0e354856ff7d8e9a8c7e870830777e2dddef911e966af4938973c41cb9175c9f8440dd6d6db51df593d092e508fa83ab9d546d82ac708f8647bf2
```

**任务**：分解 n，恢复明文（flag 格式）。

**所需知识**：费马分解法、整数平方根、RSA 解密与模逆、密钥生成安全（p、q 差距需足够大）

??? tip "答案与解析"
    **答案：`flag{fermat_close_primes}`**

    令 a=⌈√n⌉ 逐步 +1，直到 a²−n 为完全平方数 b²，则 p=a−b、q=a+b。

    ```python
    import math
    # n, e, c 取题干材料
    a = math.isqrt(n) + 1
    while True:
        b2 = a*a - n
        s = math.isqrt(b2)
        if s*s == b2:
            p, q = a - s, a + s
            break
        a += 1
    d = pow(e, -1, (p-1)*(q-1))
    m = pow(c, d, n)
    print(m.to_bytes((m.bit_length()+7)//8, 'big').decode())
    ```

    费马法迭代次数约 `(p−q)²/(8√n)`。

### S2-E2 功耗轨迹读取：从 S/M 序列恢复私钥指数 ★★（计算）

某密码卡用**从左到右平方-乘**算法实现 RSA 私钥运算（`m^d mod n`）。示波器抓到一次完整运算的功耗轨迹：每个"平方"操作产生一个 S 尖峰，每个"乘法"操作产生一个 M 尖峰。最高位恒为 1，首个平方不伴随乘法。轨迹（S=平方，M=乘，共 760 个操作）：

```
SSMSSMSSMSMSSSMSMSSMSMSMSMSMSSSMSSSSMSMSSSSMSSMSSMSMSMSSSSMS
SMSSSMSMSSMSMSMSSMSMSMSSMSSMSMSMSMSMSSSSMSSSMSSSMSMSSMSSMSSS
MSSSMSSSMSMSSSMSMSSMSSSSMSMSMSSMSMSSMSMSSMSSMSMSSSSSSSMSSMSM
SMSSSSSMSMSSMSMSMSSSMSSSMSSSMSSSSSSMSSSMSSMSSMSMSSSSMSSMSSSM
SSMSSSSSMSMSSSMSMSMSSMSMSSMSMSSMSSMSSMSSMSMSSSSSSSSSMSMSMSMS
SMSMSMSMSMSMSSMSMSMSMSSMSSSSSSMSSSMSMSMSSMSMSMSMSSMSSMSMSSSS
SMSSMSSMSSMSMSMSSSMSSSSMSSSSMSMSMSMSMSSSMSMSMSSMSMSSSMSSMSSM
SMSMSMSSSSMSSMSMSMSSSMSSMSMSMSMSMSMSSSSSMSMSSMSSMSSMSMSMSSSM
SSMSMSSMSMSMSSMSSSSMSSSSMSSSSSMSSMSSSSMSMSMSSSMSMSSMSMSSMSMS
SSMSSSMSMSSSMSMSMSMSSSMSSSMSMSSMSSMSMSMSMSMSSMSSMSMSMSMSSSSS
MSSSMSSSSSMSSSMSSMSMSMSMSMSMSSSSSSMSMSSMSSMSSMSSMSSSMSSSSMSM
SSSSMSSSSSMSSSMSSSSMSSMSSSMSSSMSSSMSMSSSMSSSMSMSSMSSMSSMSMSM
SMSSMSSSMSSSMSMSSSSMSMSSSSMSSSMSSMSMSSSM
```

配套密文（e=65537）：

```
n = 51efd519e63aec5287dd3ab02be88d629c8cebb30a5f4461ca89238c507397ab4356d8883149d2e4c2209bd1dcd6fe385d414ae60a6636a5e0727cbd64d2054f
c = 4bf9a7cbc26cbbd061e6acf1452c0b1705c3c3c69d99dd7fb2e4e230f2605f18be2138945ea97920378963e153a7d35a2d8726d2e5a2cf00ffba25d49bc698a7
```

**任务**：从轨迹恢复私钥指数 d（二进制 510 位），解密 c 得明文（flag 格式）。

**所需知识**：平方-乘（binary exponentiation）算法的位级结构、侧信道"操作序列泄露指数比特"原理、轨迹解析规则（S+M 连写=1、单独 S=0）、模幂解密

??? tip "答案与解析"
    **答案：`flag{power_trace_leak}`**

    从左到右扫描：跳过首位的 S（最高位恒 1），此后每组以 S 开头——**S 后紧跟 M 记 1（消耗两字符），S 后是 S 或结尾记 0（消耗一字符）**。解析出的 510 位即 d 的二进制。

    ```python
    tr = "SSMSSM..."            # 题干轨迹（760 字符）
    rec, i = '1', 1
    while i < len(tr):
        if i + 1 < len(tr) and tr[i+1] == 'M':
            rec += '1'; i += 2
        else:
            rec += '0'; i += 1
    d = int(rec, 2)
    m = pow(c, d, n)            # n, c 取题干材料
    print(m.to_bytes((m.bit_length()+7)//8, 'big').decode())
    # flag{power_trace_leak}
    ```

    考点：这是 SPA（简单功耗分析）的教科书场景——**操作序列与指数比特一一对应**，一条轨迹就泄整个私钥。防御：恒定执行时间的"总是平方+乘"（ Montgomery ladder / 平方且乘无论位值）、盲化指数（d + r·φ(n)）。

## 六、信息安全攻防

### S2-F1 维纳攻击：私钥 d 过小的 RSA ★★★

某系统 RSA 公钥的私钥 d 过小（约 124 位），可用连分数（Wiener 攻击）在多项式时间内恢复 d。已知：

```
n = c5bee7d286558feb05679a5ef879960eefc0c4d5f4fec4ce0d2d625e8fa703745b1433f3cd43e6e843ea8b6782508a0fdc7afc025597545ed53f0c76030dc11f
e = a51e2c46298d363a90b379f8f2ca05661e418c807ad391b319fa1b7387ac6aedcec25b9483414e66e728a17ad828b5e1349a0cc8f18f800552c56ae6231f4957
c = 1422668bf7a79665bddc47ab007df58ca8977d103c2b59d319c423cad148443056ba135ae045a9c8c81691245e07a7dcc1560c3faea0f2427b3082071b323f3a
```

**任务**：恢复私钥 d 并解出明文（flag 格式）。

**所需知识**：连分数与渐近分数、Wiener 条件 d < n^(1/4)/3、e·d ≡ 1 (mod φ(n))、二次方程反解 p、q

??? tip "答案与解析"
    **答案：`flag{wiener_small_d}`**

    e/n 的连分数渐近分数 k/d 中，真实 d 满足 `e·d−1=k·φ(n)`；据此反解 φ(n)，再用 `x²−(n−φ+1)x+n=0` 验证能否分解 n。

    ```python
    import math
    # n, e, c 取题干材料
    def conv(a, b):
        h = [0, 1]; k = [1, 0]
        while b:
            q = a // b
            a, b = b, a - q*b
            h.append(q*h[-1] + h[-2]); k.append(q*k[-1] + k[-2])
            yield h[-1], k[-1]
    d = None
    for K, D in conv(e, n):
        if K == 0: continue
        if (e*D - 1) % K != 0: continue
        phi = (e*D - 1) // K
        b = n - phi + 1
        s = math.isqrt(b*b - 4*n)
        if s*s == b*b - 4*n:
            d = D; break
    m = pow(c, d, n)
    print(m.to_bytes((m.bit_length()+7)//8, 'big').decode())
    ```

    适用条件 `d < n^(1/4)/3`。

    **SageMath 解法**（10.9 实测）：连分数收敛列是内置功能，不用手写递推：

    ```python
    from Crypto.Util.number import long_to_bytes
    for cv in continued_fraction(Integer(e)/Integer(n)).convergents():
        kk, dd = cv.numerator(), cv.denominator()
        if kk and (e*dd - 1) % kk == 0:
            phi = (e*dd - 1)//kk
            s = Integer((n - phi + 1)^2 - 4*n).isqrt()
            if s*s == (n - phi + 1)^2 - 4*n:
                break
    print(long_to_bytes(power_mod(c, dd, n)))   # flag{wiener_small_d}
    ```

### S2-F2 密钥流复用：同密钥两条 RC4 密文 ★★（计算）

某内网监控终端与服务器约定：每条上报报文用 RC4、密钥固定为会话密钥（终端重启不换）。抓包抓到同一会话的两条密文——C1 是固定格式的日报模板（明文已知，114 字节），C2 是 25 字节的机密指令：

```
C1 = 319dc329e77fead9a50fbf751c9a04a4b93930848bd6479dc4afaf43bb7db22c
     fe096191f137e829fb7f2d24b56265a1592ab5c7cdf2900768dd8bd97c7f63ab
     129256b9ed6c2ddaac71c6d35fd65bc108848e12ac8c626615f8cb7cfdc99448
     60daec06f4e9ee4102ba0584a8c4e1778a6f
C2 = 07bef11abc3beed0bf54bf750d9829a2fc0417b5848901dd88

C1 对应明文（模板，服务端文档公开）：
POST /api/report HTTP/1.1\r\nHost: intranet\r\nUser-Agent: monitor/2.1\r\n
X-Report: daily-summary\r\nContent-Length: 0\r\n\r\n
```

**任务**：利用 C1 的已知明文恢复 C2 的明文（flag 格式）。

**所需知识**：流密码密钥流与明文异或的结构、密钥流复用（two-time pad）、已知明文攻击（KS = C1 ⊕ P1）、 crib-dragging 思想、密钥/nonce 一次性原则

??? tip "答案与解析"
    **答案：`flag{keystream_reuse_pwn}`**

    RC4 是流密码：`C = P ⊕ KS(密钥)`。同一密钥 → 同一密钥流。已知 C1 的完整明文 P1，则前 114 字节密钥流 `KS = C1 ⊕ P1`；C2 只有 25 字节，落在这段密钥流范围内，直接 `P2 = C2 ⊕ KS[:25]`：

    ```python
    from Crypto.Cipher import ARC4   # 仅攻击者无需密钥，这里用异或即可
    C1 = bytes.fromhex("319d...a6f")  # 题干材料
    C2 = bytes.fromhex("07be...dd88")
    P1 = (b"POST /api/report HTTP/1.1\r\nHost: intranet\r\n"
          b"User-Agent: monitor/2.1\r\nX-Report: daily-summary\r\n"
          b"Content-Length: 0\r\n\r\n")
    KS = bytes(a ^ b for a, b in zip(C1, P1))
    print(bytes(a ^ b for a, b in zip(C2, KS)))
    # b'flag{keystream_reuse_pwn}'
    ```

    考点：**流密码从不泄露密钥，但密钥流复用等于明文裸奔**——`C1 ⊕ C2 = P1 ⊕ P2`，两条密文的异已是两条明文的异或。若两段明文都未知，则用 crib-dragging（拿猜得到的片段在 C1⊕C2 上滑动）。WEP 被 TKIP 前的破解、MS-PPTP v1 的同钥双通道都是这个原理。防御：每条报文用 CSPRNG 生成 nonce/IV 参与密钥派生，绝不重用密钥流。
