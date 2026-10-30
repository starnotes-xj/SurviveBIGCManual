# ISCC 密码安全赛样题 · 套三：理论与数学专练

> **出题模型：GLM-5.3**
> 命题依据：密码安全赛六个赛题方向（A 密码算法原理、B 密码协议设计、C 密码技术部署与运维、D 密码应用合规检测、E 密码设备漏洞挖掘、F 信息安全攻防）。
> **性质：自拟模拟题，非官方样题。** 本套偏理论与数学，全部数值均由 Python 实算校验，可直接复现（标准库 + pycryptodome，无需 sage/gmssl）。
> 难度分布：★×5、★★×7、★★★×3；其中 11 道为"给材料直接算"的计算题，4 道为分析设计题。

> **SageMath 说明**：数学/计算类题目的解析内附 SageMath 解法，全部在 **SageMath 10.9**（WSL + conda 环境）实测通过；没有 Sage 时用解析里的纯 Python 版本即可。

## 使用建议

这套题的考点是**竞赛里最常见的"数学内功"**：有限域运算、椭圆曲线点运算、离散对数分解、秘密共享插值、随机数参数恢复。建议按方向限时训练：A/B 方向每题 25 分钟，E 方向每题 40 分钟；每道题先用代码验证手算结果，再对照解析。

---

# A 密码算法原理（3 题）

### S3-A1 GF(2^8) 上的 AES 乘法 ★

AES 的列混淆在有限域 GF(2^8) 上做字节乘法，不可约多项式为 `m(x) = x⁸ + x⁴ + x³ + x + 1`（0x11B）。某密码实验平台的调试任务要求手工复现一次乘法：

```
被乘数 a = 0xb7
乘数   b = 0x3d
```

**任务**：计算 `a · b`（GF(2^8) 乘法），提交两位十六进制结果。

**所需知识**：GF(2^8) 的多项式表示、不可约多项式 0x11B 约简、xtime（乘 x）运算、倍加分解（乘数按 2 的幂展开）、异或代替加法

??? tip "答案与解析"
    **答案：`0x06`**

    解析：把 0x3d 分解为 2 的幂之和：`0x3d = 2⁰ + 2² + 2³ + 2⁴ + 2⁵`，于是
    $a\cdot b = \text{xtime}^0(a)\oplus\text{xtime}^2(a)\oplus\text{xtime}^3(a)\oplus\text{xtime}^4(a)\oplus\text{xtime}^5(a)$。
    逐次 xtime：0xb7 → 0x75 → 0xea → 0xcf → 0x85 → 0x11（每次左移一位，最高位溢出则异或 0x1b，即 0x11b 的低 8 位）。
    异或求和：0xb7⊕0xea⊕0xcf⊕0x85⊕0x11 = **0x06**。

    ```python
    def xtime(b):
        b <<= 1
        return (b ^ 0x1b) & 0xff if b & 0x100 else b

    def gmul(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            a = xtime(a)
            b >>= 1
        return r

    print("%02x" % gmul(0xb7, 0x3d))   # 06
    ```

    考点：xtime 是 AES 的原子运算，列混淆矩阵里的 {02}、{03} 都靠它实现；"最高位溢出异或 0x1b"对应多项式模 `x⁸ + x⁴ + x³ + x + 1` 约简。逆向出题（给乘积求乘数）则要考 GF(2^8) 求逆，用扩展欧几里得或费马小定理 `a²⁵⁴`。

    **SageMath 解法**（10.9 实测）：直接构造带指定不可约多项式的 GF(2⁸)：

    ```python
    R.<x> = GF(2)[]
    K.<a> = GF(2^8, modulus=x^8 + x^4 + x^3 + x + 1)
    i2f = lambda v: K([(v >> i) & 1 for i in range(8)])
    f2i = lambda e: sum(1 << int(c) for c in e.polynomial().exponents())
    print("%02x" % f2i(i2f(0xb7) * i2f(0x3d)))     # 06
    ```

### S3-A2 椭圆曲线上的点运算 ★★

某门禁系统用小素数域椭圆曲线做演示模块：

```
E: y^2 = x^3 + x + 7 (mod 199)
基点 P = (0, 87)
基点 Q = (15, 51)
```

系统校验码定义为点 `R = 3P + 2Q` 的坐标。

**任务**：计算 R 的坐标，提交 `flag{x,y}`（x、y 为十进制）。

**所需知识**：椭圆曲线点加公式（弦割线斜率 λ）、倍点公式（λ=(3x²+a)/2y）、模逆元（扩展欧几里得或费马小定理）、双倍加标量乘、点在曲线上的判定

??? tip "答案与解析"
    **答案：`flag{135,9}`**

    解析：3P = P+P+P = (118, 148)，2Q = (85, 125)，两者相加得 R = (135, 9)。关键在每一步 λ 的计算：
    倍点时 λ = (3x²+a)·(2y)^{-1} mod p，一般点加时 λ = (y₂−y₁)·(x₂−x₁)^{-1} mod p。

    ```python
    p, a, b = 199, 1, 7

    def padd(P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None                      # P + (-P) = 无穷远点
        if P == Q:
            lam = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam*lam - x1 - x2) % p
        y3 = (lam*(x1 - x3) - y1) % p
        return (x3, y3)

    def pmul(k, P):
        R = None
        while k:
            if k & 1: R = padd(R, P)
            P = padd(P, P); k >>= 1
        return R

    P, Q = (0, 87), (15, 51)
    R = padd(pmul(3, P), pmul(2, Q))
    assert R[1]**2 % p == (R[0]**3 + a*R[0] + b) % p
    print(R)                                 # (135, 9)
    ```

    考点：这条曲线群阶为 200 = 2³·5²，P、Q 的阶都是 100。竞赛里 ECDLP 题第一步永远是"算几个点验证曲线参数没被篡改"，第二步才是解题；本题练的就是点运算的代码化能力，后面 Pohlig-Hellman（S3-A3）在椭圆曲线上同样适用。

    **SageMath 解法**（10.9 实测）：`EllipticCurve` 原生标量乘：

    ```python
    E = EllipticCurve(GF(199), [1, 7])
    P, Q = E(0, 87), E(15, 51)
    print((3*P + 2*Q).xy())                         # (135, 9)
    ```

### S3-A3 光滑群上的离散对数（Pohlig-Hellman） ★★★

某 IoT 设备的固件校验使用小参数的 ElGamal 型校验码。审计提取出参数：

```
p = 2454021571
p - 1 = 2 · 3 · 5 · 7 · 11^2 · 13 · 17 · 19 · 23   （完全光滑）
g = 10        （g 是模 p 的生成元）
h = 1433806032  （h = g^x mod p）
```

**任务**：求出 x（0 ≤ x < p−1），提交 `flag{x}`。

**所需知识**：Pohlig-Hellman 分解思想（把大群 DLP 拆到素数幂阶子群）、子群投影 g_i = g^((p-1)/q^e)、小步大步算法（BSGS）、中国剩余定理合并余数、群阶与生成元判定

??? tip "答案与解析"
    **答案：`flag{578163327}`**

    解析：对 p−1 的每个素数幂因子 q^e（这里最大是 11²=121，其余都是一次因子）：
    令 g_i = g^((p-1)/q^e)、h_i = h^((p-1)/q^e)，则 h_i = g_i^{x mod q^e}，在阶为 q^e 的小群里用 BSGS（复杂度 O(√q^e)≈11 次查表）解出 x mod q^e，最后 CRT 合并 9 个同余方程。整体复杂度由最大素因子 23 决定——**p−1 光滑的群没有安全可言**，这正是本题的结论。

    ```python
    from sympy.ntheory.modular import crt

    p, g, h = 2454021571, 10, 1433806032
    facs = {2:1, 3:1, 5:1, 7:1, 11:2, 13:1, 17:1, 19:1, 23:1}

    def bsgs(g, h, p, order):
        m = int(order ** 0.5) + 1
        tbl, e = {}, 1
        for j in range(m):                    # 小步：g^0..g^(m-1)
            tbl.setdefault(e, j); e = e * g % p
        factor, gamma = pow(g, -m, p), h
        for i in range(m + 1):                # 大步：h·g^(-im)
            if gamma in tbl:
                return (i * m + tbl[gamma]) % order
            gamma = gamma * factor % p

    rems, mods = [], []
    for q, e in facs.items():
        mod = q ** e
        gi = pow(g, (p-1)//mod, p)
        hi = pow(h, (p-1)//mod, p)
        rems.append(bsgs(gi, hi, p, mod)); mods.append(mod)
    x, _ = crt(mods, rems)
    assert pow(g, int(x), p) == h
    print(x)                                  # 578163327
    ```

    考点：DLP 选素数的标准做法就是"p−1 必须有大素因子"（对应强素数），否则 Pohlig-Hellman 直接击穿。竞赛中出现"给 p−1 分解提示"的 DLP 题，几乎必是此考点；椭圆曲线版（小阶光滑曲线）同理，先做阶分解判断可解性。

    **SageMath 解法**（10.9 实测）：`discrete_log` 对光滑阶自动走 Pohlig-Hellman：

    ```python
    p, g, h = 2454021571, 10, 1433806032
    print(discrete_log(Mod(h, p), Mod(g, p), ord=p-1))   # 578163327
    ```

---

# B 密码协议设计（3 题）

### S3-B1 Shamir 门限秘密恢复 ★★

某金库启用 (3, 4) 门限方案托管启动密钥，素域 p = 2^61 − 1 = 2305843009213693951。四名托管人各持一份份额 (x, y)，任意 3 份可恢复秘密。当日演练调出 4 份：

```
p = 2305843009213693951
份额1 = (1, 1024130227976840122)
份额2 = (2, 1221587733125830533)
份额3 = (4, 619489770121560249)
份额4 = (5, 2125777311181993505)
```

**任务**：恢复秘密 S（多项式常数项），提交 `flag{S}`。

**所需知识**：Shamir (t,n) 门限原理（t−1 次多项式、任意 t 点唯一确定）、拉格朗日插值公式、模逆元计算、在 x=0 处求值即常数项、GF(p) 上的多项式运算

??? tip "答案与解析"
    **答案：`flag{1262949401464997326}`**

    解析：秘密 S = f(0)。拉格朗日插值在 x=0 处化简为
    `S = Σ_j y_j · Π_(m≠j) (-x_m)/(x_j - x_m) mod p`。
    取任意 3 份（如 1、2、4）即可算出 S；用第 4 份可交叉验证。少于 3 份时信息论安全——任何 S 都有合法多项式与之吻合。

    ```python
    p = 2305843009213693951
    shares = [(1, 1024130227976840122), (2, 1221587733125830533),
              (4, 619489770121560249)]

    S = 0
    for j, (xj, yj) in enumerate(shares):
        num = den = 1
        for m, (xm, _) in enumerate(shares):
            if m != j:
                num = num * (-xm) % p
                den = den * (xj - xm) % p
        S = (S + yj * num * pow(den, -1, p)) % p
    print(S)      # 1262949401464997326（份额 1、2、5 或 2、4、5 同样得此值）
    ```

    考点：Shamir 是"密码协议设计"方向的高频原型：门限签名、密钥托管、分布式 CA 都是它的变体。竞赛陷阱通常是：份额坐标被换（x 不连续）、GF(2^8) 域上的插值（除法变成乘逆元）、或"给出 t−1 份问能否泄露信息"（不能，完美保密）。

    **SageMath 解法**（10.9 实测）：`lagrange_polynomial` 内置：

    ```python
    F = GF(2305843009213693951)
    Rz.<z> = F[]
    f = Rz.lagrange_polynomial([(1, 1024130227976840122),
                                (2, 1221587733125830533),
                                (4, 619489770121560249)])
    print(f(0))                                     # 1262949401464997326
    ```

### S3-B2 Diffie-Hellman 密钥协商手算 ★

某教学实验用小素数演示 DH 密钥交换：

```
p = 10007 （素数，g 为其原根）
g = 5
Alice 私钥 a = 314
Bob   私钥 b = 159
```

**任务**：计算双方共享密钥 s = g^(ab) mod p，提交 `flag{s}`。

**所需知识**：Diffie-Hellman 协议流程（公开 p、g，交换 A=g^a、B=g^b）、平方-乘快速幂、模算术、共享密钥的两种等价计算式（B^a 与 A^b）、CDH 问题

??? tip "答案与解析"
    **答案：`flag{4806}`**

    解析：A = 5^314 mod 10007 = 3789，B = 5^159 mod 10007 = 5800；
    s = B^a mod p = 5800^314 mod 10007 = A^b mod p = 3789^159 mod 10007 = **4806**。

    ```python
    p, g, a, b = 10007, 5, 314, 159
    A, B = pow(g, a, p), pow(g, b, p)
    assert pow(B, a, p) == pow(A, b, p)
    print(A, B, pow(A, b, p))      # 3789 5800 4806
    ```

    考点：DH 的安全性依赖 CDH（给定 g^a、g^b 求 g^ab）；本题 p 太小可被 BSGS 直接解出私钥。真实协议要防中间人（需签名/证书认证 DH 参数与公开值，即 STS/签名 DH）、防小子群攻击（校验对方公开值的阶）。

### S3-B3 Asmuth-Bloom 中国剩余门限方案 ★★

金库改用基于 CRT 的 Asmuth-Bloom (3, 5) 门限方案，模数序列两两互素且满足门限条件 `m1·m2·m3 > m0·m4·m5`：

```
m0 = 977          （秘密 S < m0）
m1 = 1000003,  m2 = 1000033,  m3 = 1000037
m4 = 1000039,  m5 = 1000081
演练时调出 3 份份额：
(m2, 299613),  (m3, 95868),  (m5, 292527)
```

**任务**：先用前三个模数之积 CRT 恢复 M，再求 S = M mod m0，提交 `flag{S}`。

**所需知识**：Asmuth-Bloom 方案结构（份额 = (M mod m_i)，M = S + α·m0 落在约定区间）、中国剩余定理（同余方程组求唯一解）、模逆元、门限条件的作用（保证任意 t 份的积大于 M、任意 t−1 份的积不足）、素数判定

??? tip "答案与解析"
    **答案：`flag{733}`**

    解析：CRT 解同余方程组
    M ≡ 299613 (mod 1000033)、M ≡ 95868 (mod 1000037)、M ≡ 292527 (mod 1000081)，
    得唯一解 M = 418831117572087446（模数积 P = 1000033·1000037·1000081 ≈ 1.00015×10^18 > M，所以 CRT 直接还原 M 本身）。
    S = M mod 977 = **733**。门限条件保证任意 3 份的模数积都大于 M（可恢复）、任意 2 份的积不足（信息被 m0 的随机倍数 α 掩盖）。

    ```python
    from sympy.ntheory.modular import crt

    m0 = 977
    mods = [1000033, 1000037, 1000081]
    rems = [299613, 95868, 292527]
    M, _ = crt(mods, rems)
    S = int(M) % m0
    print(int(M), S)     # 418831117572087446 733
    ```

    考点：Asmuth-Bloom 与 Shamir 是门限方案的两条技术路线：前者份额天然短（不超过对应模数），后者拉格朗日插值更通用。GB/T 39786 密钥管理要求中的"密钥分量托管"在工程上常用这两类方案组合实现；判断"给了 t−1 份会不会泄露"时，记得检查门限条件是否真的成立。

    **SageMath 解法**（10.9 实测）：`crt` 内置：

    ```python
    M = crt([299613, 95868, 292527], [1000033, 1000037, 1000081])
    print(M % 977)                                  # 733
    ```

---

# C 密码技术部署与运维（2 题）

### S3-C1 信封加密的灾备恢复 ★

某业务系统采用双层信封加密：RSA-OAEP(SHA-256) 包裹 AES-256 会话密钥，再用 AES-256-GCM 加密数据。灾备演练拿到一份备份包：数据密文、被包裹的会话密钥、GCM nonce/tag，以及 KMS 故障后从冷备恢复出的 RSA-2048 私钥（PKCS#1 PEM 格式）。

```
被包裹的会话密钥（hex，256 字节）：
38e37086d2f15b0f01c8a7fe22522e5bddcc23251b6138b28218b36dccba990f7a4431f4d192e8bbd1c965235fbea000bcda0d65e62ddd6925b0615f846c5b775eb1c39b6fe3b6336159927399ab9c465641a800718c6f617da131f1dd6b91b75930b0d64ab21b3a9ffc6a73836d37e9c5c75a36a9897c1156697e108629529fd2e24b99ab33f99c08890557d7b72b7f80b656f671a219fc465dd6c8b67bcc2cdc66f1231975325d7044250d1ae0f71db1f6f11087d1230de4dd0bba82a038861e5fdc19fdc65d547bf5ee6801580da261b64aaf08a4fc5d053a2f38a26502a3f06f260bd158a342b7e3ca784ae1988b04208821f59114629c9b9342cd5586de

nonce（hex）：0f1e2d3c4b5a69788796a5b4c3d2e1f0
数据密文（hex）：08e421afdfecd13b0eb56e2f1950e69a6484675f6221bf58b5fc00e0
GCM tag（hex）：f74af387bd2d01575ec5c9e698799b30

RSA-2048 私钥（PKCS#1）：
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0dfPf381gX2r7Ce4TteFd8bOo5UnhFF3yngLK3D7PLy0+juZ
7lpP/MLqoU7tXYr8/gztQSnGJwGtTRVSnMMTJuqJuyr3cnvD4iNLL/tNx81mWqK2
9Idm1y/whcX12h7xnPdLPnY7wdxn1lJfH0ISXUXvmX1jTjRM0Ng7HePW5NoqFTdO
FTxMyYDt2R/4ZwpZKHA6j+g/hp99j0YgADhnj0qZwks9DRoOKpQ1z9YWXd3PjS0M
JGNT3qg3LwVYoOonUrqCG407Snjx1d8oMrCdO0ux2HTusz3UUN34hwvHCS4orXcD
o/aDqzlmdY9P2gGnMFCKu5qCqZtP0QBQnEE8HwIDAQABAoIBAAmHVEe0w7S5zdBj
x+o/dPwkK5RhBdsiqegWGGMtiNeZkTVjZHXMiepKuPyk5DhFsMjYxGxkuSWHSy4R
rXG9TIWx8FC39WYeFQvvh1gBEowIUFNzt1iohRAwAAZdVoMflQSsvTDhRIz3GbBD
hyPPugouqd/4wiC2MIwzf7VuZaN4eqTTUNKmf9TbvpQQnZQEhRFZMIJcEAOTNVlO
CGZYRUURNjxIsiMMKB3bQmjx0O1WUGgC/G2RK6b4JLDWREXisrQq4D9/2YLPAujM
jwFAsl6x1yMN7L6w+8ECsTMr3oEGOHvf8/3TB5497POtVYcDZG4F3v4M2Ka0PSY9
UBuemHECgYEA1Ii8e3wCh7BKBzN/dOp0guVpAYhxbgR5ZGzxXdj/h1YQIaolSEid
AqzQV6YgF131e+CGVtgDSyYHPlL8DptSRg8yvlKWNjZ2GuriT7ITwDrfYaDpzcvu
s3baysms/+O9QehFOMN+hQq/z48yjfrPKTKqMKjtC5Fkp85TxO6BUJECgYEA/MIu
LmtY7jFxJoec2GYeWuvoP4N5JVBx515LJjDS3268lAvUBoXTZG0cnXY4w1Ea9iUZ
f+KrE7CBPxGYg9wPBWMGysBZF4qLIyz6Bhe5/XqO+INATid81Hm52AqQdbpb9cw6
sfSNq9+Wgea5jyS0fa9LF4DuQR3Z8qGxGw+tGa8CgYBkZvQjocHQOAfAvyNHKDtC
Wv3wK3TqdFKkjpK3svuEA7Q7MxXJwAPsb5c80M34O/rsOnU8MW/c4Gorlyhb/iQv
1J40Ku+rTK8eqDehTo7mEOnWRR4uiliJj2xswDlp6TxPFlsdJb1vPFTAyPUo/YNA
Ax9DPYo+HMFgRKhuL/4HAQKBgGzKZ3YzXiOnxDwBQtEhow8fWud7fzlAVsZvH4lg
mmLxFtnh/XCRSVuAW0CrEeN/lUs8zKzusxPWdMrgl/SpUw3Oga3i/HXVe+23/iWB
MNyZU9BDLfp1pJUPj54dbfA+NjaloN3XlOLVacKfvF6QPd+bA4cqR2Jfpt94GPK8
3JShAoGBAJhsZmpom4XuX9qTkIUhbWEi1fZfhpL3fFXTUwMMaAEBpe1M8vqD8O82
f4hVZHsLCA8PF9hj206PXHSFyctCv51VnfLys2lFnyDTEqDQLyvSPK1TSlGgPSoo
t0VJIES8TW4WWGjp2acUelS1Xun1rWMbxqoU5i6UP/ulEstr25bX
-----END RSA PRIVATE KEY-----
```

**任务**：按信封加密的逆过程恢复数据明文（flag 格式）。

**所需知识**：混合加密/数字信封的两层结构、RSA-OAEP 填充与解密（PKCS1_OAEP）、AES-256-GCM 的解密与认证标签校验、PEM 私钥加载（RSA.import_key）、GCM 中 nonce 与 tag 的角色

??? tip "答案与解析"
    **答案：`flag{envelope_recovery_2026}`**

    解析：三步：① 用私钥 RSA-OAEP(SHA-256) 解包裹得到 32 字节会话密钥；② 以该密钥与 nonce 构造 AES-GCM 解密器；③ `decrypt_and_verify` 同时解出明文并校验 tag——tag 校验失败说明密钥错误或密文被篡改，这是 GCM 的内置完整性保证（前提：同一密钥下 nonce 绝不复用）。

    ```python
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256

    enc_key = bytes.fromhex(
        "38e37086d2f15b0f01c8a7fe22522e5bddcc23251b6138b28218b36dccba990f"
        "7a4431f4d192e8bbd1c965235fbea000bcda0d65e62ddd6925b0615f846c5b77"
        "5eb1c39b6fe3b6336159927399ab9c465641a800718c6f617da131f1dd6b91b7"
        "5930b0d64ab21b3a9ffc6a73836d37e9c5c75a36a9897c1156697e108629529f"
        "d2e24b99ab33f99c08890557d7b72b7f80b656f671a219fc465dd6c8b67bcc2c"
        "dc66f1231975325d7044250d1ae0f71db1f6f11087d1230de4dd0bba82a03886"
        "1e5fdc19fdc65d547bf5ee6801580da261b64aaf08a4fc5d053a2f38a26502a3"
        "f06f260bd158a342b7e3ca784ae1988b04208821f59114629c9b9342cd5586de")
    nonce = bytes.fromhex("0f1e2d3c4b5a69788796a5b4c3d2e1f0")
    ct = bytes.fromhex("08e421afdfecd13b0eb56e2f1950e69a6484675f6221bf58b5fc00e0")
    tag = bytes.fromhex("f74af387bd2d01575ec5c9e698799b30")

    PEM = """-----BEGIN RSA PRIVATE KEY-----
    ...（此处粘贴题面中的私钥，保存为 kms_private.pem）...
    -----END RSA PRIVATE KEY-----"""
    key = RSA.import_key(PEM)
    session = PKCS1_OAEP.new(key, hashAlgo=SHA256).decrypt(enc_key)
    cipher = AES.new(session, AES.MODE_GCM, nonce=nonce)
    print(cipher.decrypt_and_verify(ct, tag))
    # b'flag{envelope_recovery_2026}'
    ```

    考点：信封加密是 KMS/CMK-DEK 架构的数学骨架——数据密钥用主密钥包裹后与密文同存，灾备恢复顺序是"先解信封、再解数据"。工程坑：OAEP 的哈希必须与加密端一致（SHA-1 与 SHA-256 不兼容）、GCM 的 tag 截断会成倍削弱认证强度。

### S3-C2 电子签章系统国密双证书部署设计 ★

某电子签章系统按 GB/T 39786 要求做国密改造，采用 SM2 双证书体系（签名证书 + 加密证书）。方案文档有 4 个待定决策点，每个决策点从 3 个候选中选 1 个（填字母）：

```
决策1 加密密钥对的生成位置：
  A. 在运维人员的笔记本上用 OpenSSL 软生成，再导入服务器
  B. 在密码机（服务器密码机/智能密码钥匙）内生成，私钥不出设备，
     由设备导出证书请求 CSR 交给 CA
  C. 由 CA 统一生成后通过电子邮件分发私钥

决策2 签名证书对应私钥的备份策略：
  A. 不托管、不备份，仅由持有人在自己控制的介质中保存
  B. 在密钥管理中心做三份分量备份
  C. 交给 CA 运营商集中保管

决策3 加密证书对应私钥的备份策略：
  A. 不托管、不备份，丢失后连历史加密数据一起无法解密
  B. 按密钥管理规定分割成多个分量托管备份，可依流程恢复
  C. 明文导出一份数字信封外的私钥文件给运维应急

决策4 数字签名在业务中主要保障的安全属性：
  A. 机密性
  B. 真实性与不可否认性
  C. 数据加密传输的安全性
```

**任务**：按"决策1决策2决策3决策4"的顺序提交 4 个字母（如 `flag{ABCD}`）。

**所需知识**：国密双证书体系（签名证书与加密证书分离的职责划分）、签名私钥与加密私钥的备份差异（签名私钥绝不托管否则不可否认性崩塌、加密私钥必须托管否则数据可恢复性丢失）、密码机内生成与私钥不出设备原则、数字签名的真实性/不可否认性属性

??? tip "答案与解析"
    **答案：`flag{BABB}`**

    解析：
    决策1 选 B——密钥必须在密码设备内生成，私钥永不离开设备，这是 GB/T 39786 对密码产品与密钥管理的基本要求（软生成、邮件分发私钥均违规）。
    决策2 选 A——签名私钥一旦被他人备份，签名就可被他人伪造，签名人对签名的控制权被破坏，"不可否认性"随之失效；所以签名私钥只归持有人。
    决策3 选 B——加密私钥对应的不是签名人身份而是数据的解密能力：若不托管，持有人介质损毁则历史密文永久无法打开；但明文导出（C）违反密钥保护要求，正确做法是分割分量、依流程恢复。
    决策4 选 B——签名保证真实性与不可否认性；机密性靠加密（SM4/数字信封）实现。

    ```python
    print("BABB")
    ```

    考点："签名私钥不托管、加密私钥要托管"是双证书体系最容易混的考点，也是密评现场的高频检查项：核对加密证书私钥分量托管的审批记录、核对签名证书私钥不出介质的管控措施。

---

# D 密码应用合规检测（2 题）

### S3-D1 按安全需求选型密码技术 ★

某政务系统密评整改清单列出 5 个业务需求，要求为每个需求匹配应选用的密码技术类别：

```
A. 不可否认性   B. 完整性   C. 机密性   D. 真实性

需求1 政务外网中传输的敏感统计报表，防止被链路窃听
需求2 电子证照文件入库后，防止内容被悄悄篡改
需求3 办公系统登录环节，确认"操作者确实是登记在册的员工本人"
需求4 电子合同双方签署后，防止任何一方事后否认签署行为
需求5 住院病历落盘归档，防止硬盘被拷走后数据泄露
```

**任务**：按需求 1~5 的顺序提交匹配的字母（如 `flag{ABCDE}`）。

**所需知识**：机密性/完整性/真实性/不可否认性四类安全属性的区分、传输加密与存储加密的适用场景、哈希与消息认证码的完整性保护、数字签名与身份鉴别的对应关系、抗抵赖的实现手段

??? tip "答案与解析"
    **答案：`flag{CBADC}`**

    解析：
    需求1 防窃听 → C 机密性（传输链路加解密，如 SSL VPN/IPSec + SM4）；
    需求2 防篡改 → B 完整性（SM3 摘要 + HMAC 或数字签名）；
    需求3 确认身份 → D 真实性（基于 SM2 的身份鉴别/协同签名、动态口令）；
    需求4 防否认 → A 不可否认性（数字签名 + 可靠时间戳）；
    需求5 防泄露 → C 机密性（存储加密，落盘 SM4）。
    注意区分：需求2 与需求4 都可能用到签名，但需求2 的目标是"发现被改"（完整性），需求4 的目标是"无法抵赖"（不可否认性）——密评选型要看业务诉求而非仅看技术手段。

    ```python
    print("CBADC")
    ```

    考点：GB/T 39786 应用和数据安全层面的指标正是按"机密性、完整性、真实性、不可否认性"逐项要求的；答题时先问"资产怕什么"（被看？被改？被冒充？被赖账？），再定属性，最后选算法。

### S3-D2 GB/T 39786 要求的层面归属 ★★

密评机构对某信息系统做差距分析，摘录 5 条已实施的密码安全措施。GB/T 39786-2021 将密码应用技术要求划分为四个层面（另有密钥管理与管理制度、人员管理、实施流程、应急处置等管理要求）。请把每条措施归入正确的类别：

```
甲. 机房视频监控与门禁记录采用密码技术保证记录完整性
乙. 远程运维终端与业务内网之间建立 SSL VPN 加密通道
丙. 对每台应用服务器启用基于 SM2 的远程登录身份鉴别
丁. 业务 APP 对交易报文计算 SM3 摘要并附 SM2 数字签名
戊. 每半年组织一次密码应用应急预案演练并留存演练记录

类别选项：
1 物理和环境安全   2 网络和通信安全   3 设备和计算安全
4 应用和数据安全   5 管理要求（应急处置）
```

**任务**：按甲、乙、丙、丁、戊的顺序提交类别编号（如 `flag{12345}`）。

**所需知识**：GB/T 39786 四个技术层面的划分边界（物理环境/网络通信/设备计算/应用数据）、"保护对象在哪里"的归类方法、管理要求与技术要求的区分、应急处置在管理要求中的位置

??? tip "答案与解析"
    **答案：`flag{12345}`**

    解析：归类口诀是看**被保护对象所处的位置**，而不是看用了什么算法：
    甲 保护对象是机房的门禁/监控记录（物理场所产生的数据）→ 1 物理和环境安全；
    乙 保护对象是网络通信链路 → 2 网络和通信安全；
    丙 保护对象是服务器本体的登录（设备自身计算环境）→ 3 设备和计算安全；
    丁 保护对象是应用层的业务报文 → 4 应用和数据安全；
    戊 属于管理制度层面的应急演练，不落在任何技术层面 → 5 管理要求（应急处置）。
    易混点：同样是"身份鉴别"，设备登录（丙）属设备和计算安全、业务系统登录属应用和数据安全；同样是"完整性保护"，门禁记录（甲）属物理和环境安全、业务数据（丁）属应用和数据安全。

    ```python
    print("12345")
    ```

    考点：GB/T 39786-2021 的密码应用基本要求按"物理和环境安全、网络和通信安全、设备和计算安全、应用和数据安全"四个技术层面分级展开（第一级至第四级），另含密钥管理与管理要求（管理制度、人员管理、实施流程、应急处置）。密评测评项的结构即按此展开，归类错会导致整改方案挂错层面、漏掉对应测评项。

---

# E 密码设备漏洞挖掘（2 题）

### S3-E1 CRC32 校验的伪造后缀 ★★★

某嵌入式设备的固件配置块共 16 字节，引导程序用标准 CRC-32（即 CRC-32/ISO-HDLC：多项式 0x04C11DB7、初值/输出异或 0xFFFFFFFF、输入输出按位反射，与 zlib.crc32 一致）做完整性校验，只比对 CRC 值本身：

```
出厂配置块（16 字节，hex）：
64656275673d303b6c6f636b3d313b23          即 "debug=0;lock=1;#"
出厂 CRC-32 = e2bc2944

攻击者已改写前 12 字节为（hex）：
64656275673d313b6c6f636b                  即 "debug=1;lock"
（开了调试接口；后 4 字节待定）
```

引导程序逐字节比较整个配置块吗？不——它只比较 CRC-32。请为攻击者构造 4 字节后缀，使恶意配置块的 CRC-32 与出厂值完全相同。

**任务**：提交 4 字节后缀的 hex（8 个字符），使 `crc32(恶意块) = e2bc2944`，格式 `flag{后缀hex}`。

**所需知识**：CRC 的 GF(2) 线性性质（对消息的仿射映射）、把后缀视为 32 个 GF(2) 未知量、用单位基向量差分构造线性映射矩阵、GF(2) 高斯消元解线性方程组、CRC 不能作为密码学完整性机制的原因

??? tip "答案与解析"
    **答案：`flag{98e267e8}`**

    解析：固定前缀下，`crc32(prefix || suffix)` 关于 32 位后缀是**仿射函数**：f(s) = base ⊕ L(s)，base = crc32(prefix‖0⁴)，L 是 GF(2) 线性映射。构造 L 的 32×32 矩阵：对第 i 位单位基向量 e_i（后缀仅该位为 1）计算 col_i = crc32(prefix‖e_i) ⊕ base。解 L(u) = target ⊕ base 这个 GF(2) 线性方程组（高斯消元），把解得的位向量装回 4 字节即得后缀。本题矩阵满秩，解唯一：**98e267e8**。CRC 只能防随机错误，不能防蓄意构造——密码学完整性必须用 HMAC-SM3/SHA-256 或数字签名。

    ```python
    import zlib

    prefix = bytes.fromhex("64656275673d313b6c6f636b")   # "debug=1;lock"
    target = 0xe2bc2944
    base = zlib.crc32(prefix + b"\x00" * 4)

    # 32 个未知量 u_i：u_i = 后缀第 i//8 字节的第 (7-i%8) 位
    cols = []
    for i in range(32):
        s = bytearray(4)
        s[i // 8] |= 1 << (7 - i % 8)
        cols.append(zlib.crc32(prefix + bytes(s)) ^ base)

    def solve_gf2(cols, rhs):
        # 对每个输出位建立方程 parity(coef & u) = b，高斯消元
        rows = []
        for bit in range(32):
            coef = 0
            for i in range(32):
                if (cols[i] >> bit) & 1:
                    coef |= 1 << i
            rows.append((coef, (rhs >> bit) & 1))
        piv = {}
        for coef, b in rows:
            c, bb = coef, b
            for p in sorted(piv, reverse=True):
                if (c >> p) & 1:
                    c ^= piv[p][0]; bb ^= piv[p][1]
            if c:
                piv[c.bit_length() - 1] = (c, bb)
            elif bb:
                return None                      # 无解
        u = 0
        for p in sorted(piv):                     # 升序回代
            c, bb = piv[p]
            s = bb
            for q in range(p):
                if (c >> q) & 1 and (u >> q) & 1:
                    s ^= 1
            if s & 1:
                u |= 1 << p
        return u

    u = solve_gf2(cols, target ^ base)
    suffix = bytearray(4)
    for i in range(32):
        if (u >> i) & 1:
            suffix[i // 8] |= 1 << (7 - i % 8)
    forged = prefix + bytes(suffix)
    assert zlib.crc32(forged) == target == zlib.crc32(bytes.fromhex(
        "64656275673d303b6c6f636b3d313b23"))
    print(suffix.hex(), forged.hex())             # 98e267e8
    ```

    考点：这类"线性校验可伪造"漏洞在固件安全里真实存在（旧版 bootloader 的 CRC 校验、某些 OTA 升级包仅校验 CRC32）。攻击面推广：改前缀任意多位都行，只要留出与 CRC 位宽相同的自由字节；矩阵不满秩时可留 5 字节自由度再约束解空间。

### S3-E2 RSA-CRT 签名的故障攻击（Bellcore） ★★★

某密码卡用 RSA-CRT 方式计算签名：s_p = m^(dp) mod p、s_q = m^(dq) mod q，再 CRT 合成 s。安全团队在电压毛刺注入实验中捕获了一次"签名值异常"的输出，同时截获了一段用同一密钥加密的内部口令。参数与材料：

```
n = 117702647994107750174399906426171023498234482476605519670337289065942936523543047226487389845227027977672329728187914335214109432830330599622918261770864931613264619790901082561483973739460570825833525903269497528443755079572848006873806553882040138956479638430190152681357499059358710059391847718094968746601

e = 65537
m（被签名的固件摘要，hex）= 8f15b981a32f11db2781569b78ee052bc760f76e56ea6dcb30e3c33d8a182c03

故障签名 s~ = 3726772414979223133633791199620906287166544486907876373051482532261107432520320901591979388995164776255057418192205074003487917804737648971598938516300338017059499231428956137413003797136957140047644873114768915721952097416799183475694700683983973525660215257010872932479027613631609507592784593536206117428

内部口令密文 ct = 1439628572252004303158576592574051353196998304377994138970171726470623901992412722121425328025782944996347265114186601036926342642962191746199249159389700550637287039643005091255861378076092275047202591484865877298878074323263471317823946698861102481824762853356767195977151393624040586335884581960054674621
```

（提示：故障使 s_p 或 s_q 之一计算出错，合成结果 s~ 只在模其中一个素数时与正确签名一致。）

**任务**：利用故障签名分解 n，解密口令密文，提交 flag。

**所需知识**：RSA-CRT 签名优化的结构（dp、dq、qinv 与 CRT 合成）、Bellcore 攻击原理（gcd(s~^e − m, n) 泄露素因子）、RSA 密钥参数关系（n=pq、d≡e⁻¹ mod φ(n)）、故障注入导致单分支计算错误的后果、大整数幂模运算

??? tip "答案与解析"
    **答案：`flag{crt_fault_leaks_factor}`**

    解析：正确签名满足 s^e ≡ m (mod n)。故障签名 s~ 只在模 p（或 q）一侧正确：
    s~^e − m ≡ 0 (mod q) 但 ≠ 0 (mod p)（本题故障发生在 p 侧），于是
    `gcd(pow(s~, e, n) − m, n) = q`，直接分解 n。得到 q 后 p = n // q，
    d = e⁻¹ mod (p−1)(q−1)，解密 ct 得口令明文。防御：签名结果输出前必须**先验证再输出**（用公钥检查 s^e ≡ m，计算量约为一次加密），以及密码设备的故障检测/冗余计算。

    ```python
    from math import gcd

    n = 117702647994107750174399906426171023498234482476605519670337289065942936523543047226487389845227027977672329728187914335214109432830330599622918261770864931613264619790901082561483973739460570825833525903269497528443755079572848006873806553882040138956479638430190152681357499059358710059391847718094968746601
    e = 65537
    m = int("8f15b981a32f11db2781569b78ee052bc760f76e56ea6dcb30e3c33d8a182c03", 16)
    s_fault = 3726772414979223133633791199620906287166544486907876373051482532261107432520320901591979388995164776255057418192205074003487917804737648971598938516300338017059499231428956137413003797136957140047644873114768915721952097416799183475694700683983973525660215257010872932479027613631609507592784593536206117428
    ct = 1439628572252004303158576592574051353196998304377994138970171726470623901992412722121425328025782944996347265114186601036926342642962191746199249159389700550637287039643005091255861378076092275047202591484865877298878074323263471317823946698861102481824762853356767195977151393624040586335884581960054674621

    q = gcd(pow(s_fault, e, n) - m, n)      # 故障签名泄露的素因子
    assert 1 < q < n
    p = n // q
    d = pow(e, -1, (p - 1) * (q - 1))
    fi = pow(ct, d, n)
    print(fi.to_bytes((fi.bit_length() + 7) // 8, "big"))
    # b'flag{crt_fault_leaks_factor}'
    ```

    考点：Bellcore（2001）是"故障注入 + 数学"组合攻击的教科书案例：一次错误输出就废掉整个私钥。同类还有 RSA-CRT 的"同一消息两次签名差分攻击"（Lenstra）、以及 ECDSA 错误 nonce 恢复私钥。设备侧必须做签名自校验（recompute/verify before output）。

---

# F 信息安全攻防（3 题）

### S3-F1 LCG 令牌预测 ★★

某内网系统的临时访问令牌由 64 位线性同余发生器直接产生（输出即完整状态，模数固定为 2^64）：

```
s_{i+1} = (a · s_i + c) mod 2^64
token_i = s_i

连续抓到的 6 个令牌（十进制）：
s1 = 10599262563930695512
s2 = 7144939718356587463
s3 = 1572297403331900490
s4 = 5173213554776352849
s5 = 10280456320530892428
s6 = 14344694086705535979
```

a、c 未知。

**任务**：恢复 a、c 并预测下一个令牌 s7，提交 `flag{s7}`（十进制）。

**所需知识**：LCG 状态转移的差分结构（t_i = s_{i+1}−s_i 满足 t_2 = a·t_1）、模 2^64 下求逆需差分为奇数、扩展欧几里得求模逆、由 a 反解 c、用恢复参数外推验证

??? tip "答案与解析"
    **答案：`flag{9264785866354638494}`**（a = 6364136223846793005，c = 1442695040888963407，s8 = 3322267880899175701）

    解析：令 t1 = s2−s1、t2 = s3−s2（均模 2^64）。由转移方程相减得 t2 ≡ a·t1 (mod 2^64)，故 a = t2 · t1⁻¹ mod 2^64（t1 为奇数时可逆，本题满足）；再由 c = s2 − a·s1 mod 2^64 反推增量。把恢复出的 (a, c) 代回去重放 s4~s6 全部吻合后，即可外推 s7 = a·s6 + c mod 2^64。**输出完整状态的 LCG 只需 3 个连续值即可彻底攻破**。

    ```python
    M = 1 << 64
    s = [10599262563930695512, 7144939718356587463, 1572297403331900490,
         5173213554776352849, 10280456320530892428, 14344694086705535979]

    t1 = (s[1] - s[0]) % M
    t2 = (s[2] - s[1]) % M
    a = t2 * pow(t1, -1, M) % M
    c = (s[1] - a * s[0]) % M
    print(a, c)
    # 用 s4~s6 验证参数
    assert all((a * s[i] + c) % M == s[i+1] for i in (3, 4))
    s7 = (a * s[5] + c) % M
    print(s7)              # 9264785866354638494
    ```

    考点：与"爆破弱种子"不同，本题考**参数与状态的代数恢复**。衍生考点：只输出高位截断的 LCG（Truncated LCG）需用格方法（LLL）解线性关系——那是格密码方向的引子；模数未知的 LCG 还可以用 s 序列的行列式关系先求 m。

### S3-F2 Rabin 口令的平方根恢复 ★★

某设备的启动口令用简化 Rabin 加密（单素数模）保护：口令为 4 字节可打印 ASCII，c = m² mod p。

```
p = 3221225473     （注意 p ≡ 1 (mod 4)，(p+1)/4 求根公式失效）
c = 2160226031
```

**任务**：求出 c 的模 p 平方根中"可以作为口令"的那一个（4 字节可打印 ASCII），提交 `flag{口令}`。

**所需知识**：二次剩余判定（欧拉判别法 c^((p-1)/2) ≡ 1）、p ≡ 3 (mod 4) 时的直接求根公式及其失效条件、Tonelli-Shanks 算法（分解 p−1 = q·2^s、找非剩余 z、迭代降阶）、平方根成对性质（±r）、从整数还原 ASCII 口令

??? tip "答案与解析"
    **答案：`flag{r00t}`**

    解析：p = 3·2^30+1，p−1 的 2-adic 赋值高达 30，必须用完整的 Tonelli-Shanks：把 p−1 = 3·2^30，找二次非剩余 z（这里 z=2 即是），维护辅助变量 c、t、R，反复"找最小 i 使 t^(2^i)=1"降阶直到 t=1。得到两个根 {1305464717, 1915760756}，其中 1915760756 = 0x72303074 解码为 `r00t`（另一根 0x4DCFCF8D 不可打印）。Rabin 的加密就是模平方，解密等价于求模平方根——困难性与因子分解等价；但**单素数模**下任何会 Tonelli-Shanks 的人都能求根，等于没有加密。

    ```python
    p, c = 3221225473, 2160226031
    assert pow(c, (p-1)//2, p) == 1          # c 确为二次剩余

    def tonelli(n, p):
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2; s += 1
        z = 2
        while pow(z, (p-1)//2, p) != p - 1:  # 找二次非剩余
            z += 1
        mm, cc = s, pow(z, q, p)
        tt, rr = pow(n, q, p), pow(n, (q+1)//2, p)
        while tt != 1:
            i, cur = 0, tt
            while cur != 1:
                cur = cur * cur % p; i += 1
            b = pow(cc, 1 << (mm - i - 1), p)
            mm, cc = i, b * b % p
            tt, rr = tt * b * b % p, rr * b % p
        return rr

    r = tonelli(c, p)
    assert r * r % p == c
    for root in (r, p - r):
        print(root, root.to_bytes(4, "big"))
        # 1305464717 -> b'M\xcf\xcf\x8d'（不可打印）
        # 1915760756 -> b'r00t'
    ```

    考点：p ≡ 3 (mod 4) 时 r = c^((p+1)/4) 一步到位，本题特意选 p ≡ 1 (mod 4) 且 s=30 的大降阶链，逼出完整 Tonelli-Shanks。Rabin 完整版（n=pq）解密得四个根，需要冗余头/可读性判别真根——与本题"从两根中挑可打印根"是同一思想。

    **SageMath 解法**（10.9 实测）：`GF(p)` 的 `.sqrt()` 就是 Tonelli-Shanks：

    ```python
    r = GF(3221225473)(2160226031).sqrt()
    print(r, 3221225473 - r)   # 1305464717 1915760756，取可打印的 r00t
    ```

### S3-F3 哈希长度扩展的可利用性分析 ★★

某内部 API 采用如下鉴权机制（secret 为服务端与客户端共享的 16 字节密钥，抓包时不可见）：

```python
# 服务端代码（节选）
def sign(body: bytes) -> str:
    return hashlib.sha256(secret + body).hexdigest()   # secret || body 拼接

def verify(body: bytes, sig: str) -> bool:
    return sign(body) == sig
```

```
抓到的一次合法请求：
body  = "amount=100&to=alice"
sig   = 服务端对该 body 的 SHA-256 签名（32 字节 hex）
```

攻击者想把 `&role=admin` 追加到 body 之后并让签名仍然校验通过。

**任务**：回答三个问题（每问都要给出理由）：(1) 不需要知道 secret 的值，攻击者能否构造出 `body || padding || "&role=admin"` 这类新消息的有效签名？(2) 若能，攻击者必须知道或猜测什么信息，为什么？(3) 给出一种修复方案并说明为什么它免疫此类攻击。

**所需知识**：Merkle–Damgård 结构（消息分块+压缩函数迭代）、SHA-256 的 padding 规则（0x80 + 0 填充 + 8 字节比特长度）、长度扩展攻击原理（输出即压缩函数状态、可作新初始状态续算）、hashpump/hash_extender 工具、HMAC 的双哈希结构为何免疫

??? tip "答案与解析"
    **答案（要点式）：**
    (1) **能**。SHA-256 输出的 256 位摘要就是处理完 `secret||body` 后压缩函数的内部状态；Merkle–Damgård 结构允许把这个状态当作新的链接变量继续吸收后续分块。攻击者以已知摘要为初始状态、对追加数据 `&role=admin` 续算压缩函数，即可得到 `SHA256(secret || body || pad || "&role=admin")` 的正确摘要，全程不需要 secret。
    (2) **必须知道（或穷举）secret 的长度**。因为内部填充 `pad = 0x80 ‖ 0^k ‖ len_bits(secret‖body)` 中，长度字段的值取决于 secret 长度，k 的取值也随总长变化；secret 通常为 16/32 字节等少数取值，逐个试长度即可命中（每次尝试一次哈希计算）。
    (3) **改用 HMAC-SHA256(secret, body)**：HMAC 采用 `H((K′⊕opad) ‖ H((K′⊕ipad) ‖ m))` 的内外双层结构，攻击者拿到的外层摘要不再是内层哈希的直接内部状态，长度扩展无处着力。其他可接受方案：`H(body ‖ H(secret))` 这类"把密钥藏进消息末段"的构造、或直接改用 AEAD/数字签名。

    ```python
    # 佐证：手工算出攻击者需要伪造的填充字节（keylen=16 的情形）
    import struct

    original_len = len("amount=100&to=alice".encode()) + 16   # secret 16 字节
    glue = b"\x80" + b"\x00" * ((55 - original_len) % 64)
    glue += struct.pack(">Q", original_len * 8)
    print(glue.hex())
    # 攻击者随后用 hashpump 以已知摘要续算：
    # hashpump -s <sig> -d "amount=100&to=alice" -k 16 -a "&role=admin"
    ```

    考点：`hash(secret ‖ message)` 是密码工程十大陷阱之一（对应 CWE 长度扩展类弱点）；凡是"摘要直接当 MAC"的实现都可被本题手法伪造。判分点：(1) 指出可续算（状态外泄）(2) 指出长度依赖/需枚举 keylen (3) HMAC 修复。与此对照，S3-E1 的 CRC 伪造是"无密钥校验"问题，本题是"有密钥但构造错误"问题。

---

## 附：本套题目与答案速查表

| 题号 | 方向 | 难度 | 类型 | 答案 |
|---|---|---|---|---|
| S3-A1 | 密码算法原理 | ★ | 计算 | `0x06` |
| S3-A2 | 密码算法原理 | ★★ | 计算 | `flag{135,9}` |
| S3-A3 | 密码算法原理 | ★★★ | 计算 | `flag{578163327}` |
| S3-B1 | 密码协议设计 | ★★ | 计算 | `flag{1262949401464997326}` |
| S3-B2 | 密码协议设计 | ★ | 计算 | `flag{4806}` |
| S3-B3 | 密码协议设计 | ★★ | 计算 | `flag{733}` |
| S3-C1 | 部署与运维 | ★ | 计算 | `flag{envelope_recovery_2026}` |
| S3-C2 | 部署与运维 | ★ | 设计 | `flag{BABB}` |
| S3-D1 | 合规检测 | ★ | 分析 | `flag{CBADC}` |
| S3-D2 | 合规检测 | ★★ | 分析 | `flag{12345}` |
| S3-E1 | 设备漏洞挖掘 | ★★★ | 计算 | `flag{98e267e8}` |
| S3-E2 | 设备漏洞挖掘 | ★★★ | 计算 | `flag{crt_fault_leaks_factor}` |
| S3-F1 | 信息安全攻防 | ★★ | 计算 | `flag{9264785866354638494}` |
| S3-F2 | 信息安全攻防 | ★★ | 计算 | `flag{r00t}` |
| S3-F3 | 信息安全攻防 | ★★ | 分析 | 要点式（见解析） |
