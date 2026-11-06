#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""GMSSL.lua 插件回归测试套件

用法:
    python test_gmssl.py [tshark路径] [数据1.pcap] [数据2.pcap]
不带参数时使用默认路径(D:\ws-tshark + 本机两份真题)。
真题断言(帧数/公钥前缀/套件号)只对已知真题文件有效; 自定义 pcap 时会先提示。
合成测试(CCS 分帧 / 0xFFFF 截断)不依赖任何外部文件, 始终运行。

退出码: 0=全部通过(允许 SKIP) / 1=有 FAIL / 2=全部跳过
"""
import os, shutil, struct, subprocess, sys, tempfile

DEF_TSHARK = r"D:\ws-tshark\tshark.exe"
DEF_D1 = r"C:\Users\星记\Downloads\2026-11-04 14_51_11----5873acad2375467b8f0d073986c41185.pcap"
DEF_D2 = r"C:\Users\星记\Downloads\2026-11-04 14_51_13----f3b768b9258b40d2b8be2867de5c7384.pcap"

RESULTS = []

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return r.returncode, r.stdout or "", r.stderr or ""

def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS  " if cond else "FAIL  ") + name + (("  | " + detail) if detail and not cond else ""))

def tshark(tshark_path, pcap, *extra):
    return run([tshark_path, "-r", pcap] + list(extra))

# ---------- 合成 pcap 生成 ----------
def build_pcap(records_per_frame):
    # 生成标准小端 pcap: 每个元素是一个 TCP 载荷(由若干 TLCP record 拼成)。
    # 注意: 所有帧共用同一四元组(同一条 TCP 会话)——源端口固定, 否则状态类测试失真
    out = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 262144, 1)
    seq = 1
    for i, payload in enumerate(records_per_frame):
        eth = bytes.fromhex("08002b000001") + bytes.fromhex("08002b000002") + b"\x08\x00"
        tcp = struct.pack(">HHIIBBHHH", 49152, 443, seq, 1, 0x50, 0x18, 8192, 0, 0)
        ip_total = 20 + len(tcp) + len(payload)
        ip = struct.pack(">BBHHHBBH", 0x45, 0, ip_total, i, 0x4000, 64, 6, 0) + bytes([10, 0, 0, 1]) + bytes([10, 0, 0, 2])
        frame = eth + ip + tcp + payload
        out += struct.pack("<IIII", 1700000000 + i, 0, len(frame), len(frame)) + frame
        seq += len(payload)
    return out

def synth_test_ccs_split(tshark_path):
    # Kimi D 项: CCS 单独一帧, 加密 Finished(0x16 record)在下一帧
    # 修前: 密文被当握手消息头解析; 修后: 打上 GMSSL.EncryptedHelloData
    ccs = bytes.fromhex("140101000101")                       # type=CCS len=1 body=01
    ehs = bytes.fromhex("1601010005") + bytes.fromhex("a1b2c3d4e5")  # type=HS len=5 密文
    p = os.path.join(tempfile.gettempdir(), "_gmssl_t_d.pcap")
    open(p, "wb").write(build_pcap([ccs, ehs]))
    _, o, _ = tshark(tshark_path, p, "-Y", "GMSSL.EncryptedHelloData", "-T", "fields", "-e", "frame.number")
    check("[合成D] CCS 分帧后密文帧打上 EncryptedHelloData", o.strip() == "2", "实际: %r" % o.strip())
    _, _, e = tshark(tshark_path, p, "-V")
    check("[合成D] 零 Lua 错误", "Lua Error" not in e and "Lua Error" not in o)
    os.remove(p)

def synth_test_truncated(tshark_path):
    # Kimi B 项: record 头声称 len=0x30 但抓包到此为止(重组永远等不到)
    # 期望: 不崩、不挂起、退出码 0
    trunc = bytes.fromhex("1601010030") + b"\x01" * 5
    p = os.path.join(tempfile.gettempdir(), "_gmssl_t_b.pcap")
    open(p, "wb").write(build_pcap([trunc]))
    rc, o, e = tshark(tshark_path, p, "-c", "1")
    check("[合成B] 0x30 截断 record 不崩溃(rc=0)", rc == 0)
    check("[合成B] 零 Lua 错误", "Lua Error" not in e)
    os.remove(p)

# ---------- 真题回归 ----------
def real_test(tshark_path, tag, pcap, port, frames, suite, cke_prefix, dflag):
    extra = ["-d", "tcp.port==%d,gmssl" % port] if dflag else []
    _, o, _ = tshark(tshark_path, pcap, *extra)
    lines = [l for l in o.splitlines() if l.strip()]
    check("[%s] 帧数=%d" % (tag, frames), len(lines) == frames, "实际 %d" % len(lines))
    check("[%s] 全部帧 GMSSL 署名" % tag, all("GMSSL" in l for l in lines))
    if frames >= 7:
        check("[%s] frame5 双消息(13,14 同 record)" % tag,
              any("Certificate Request" in l and "Server Hello Done" in l for l in lines))
        check("[%s] CKE 帧存在" % tag, any("Client Key Exchange" in l for l in lines))
    _, o, _ = tshark(tshark_path, pcap, *(extra + ["-Y", "tls.handshake.type == 2",
                    "-T", "fields", "-e", "tls.handshake.ciphersuite"]))
    check("[%s] 原生套件字段=%s" % (tag, suite), suite in o, "实际: %r" % o.strip())
    _, o, _ = tshark(tshark_path, pcap, *(extra + ["-Y", "GMSSL.Hello.CipherSuite.CipherSuiteValue",
                    "-T", "fields", "-e", "frame.number", "-e", "GMSSL.Hello.CipherSuite.CipherSuiteValue"]))
    check("[%s] 插件套件 hex=%s" % (tag, suite), suite in o, "实际: %r" % o.strip())
    _, o, _ = tshark(tshark_path, pcap, *(extra + ["-Y", "tls.handshake.type == 16",
                    "-T", "fields", "-e", "GMSSL.Hello.ClientKeyExchangeData"]))
    check("[%s] CKE 载荷前缀 %s" % (tag, cke_prefix[:16]), cke_prefix in o, "实际: %.40r" % o.strip())
    _, o, e = tshark(tshark_path, pcap, *(extra + ["-V"]))
    lua_err = ("Lua Error" in o) or ("Lua Error" in e)
    check("[%s] -V 深查零 Lua 错误" % tag, not lua_err)

def main():
    tshark_path = sys.argv[1] if len(sys.argv) > 1 else (shutil.which("tshark") or DEF_TSHARK)
    if not os.path.exists(tshark_path):                       # 允许只传命令名(如 tshark)
        tshark_path = shutil.which(tshark_path) or DEF_TSHARK
    d1 = sys.argv[2] if len(sys.argv) > 2 else DEF_D1
    d2 = sys.argv[3] if len(sys.argv) > 3 else DEF_D2
    if not os.path.exists(tshark_path):
        print("找不到 tshark: %s" % tshark_path); sys.exit(2)
    _, o, _ = run([tshark_path, "-G", "plugins"])
    check("插件已加载(GMSSL.lua)", "GMSSL.lua" in o)

    synth_test_ccs_split(tshark_path)
    synth_test_truncated(tshark_path)

    for tag, pcap, port, frames, suite, cke, dflag in [
        ("数据1", d1, 10443, 13, "0xe011", "0300004104fc57e6dbc62d06", True),
        ("数据2", d2, 443, 18, "0xe013", "009b30819802207f4b012d", False),
    ]:
        if os.path.exists(pcap):
            real_test(tshark_path, tag, pcap, port, frames, suite, cke, dflag)
        else:
            print("SKIP  %s 文件不存在: %s" % (tag, pcap)); RESULTS.append((tag, None))

    n_pass = sum(1 for _, v in RESULTS if v is True)
    n_fail = sum(1 for _, v in RESULTS if v is False)
    n_skip = sum(1 for _, v in RESULTS if v is None)
    print("\n合计: %d PASS / %d FAIL / %d SKIP" % (n_pass, n_fail, n_skip))
    sys.exit(1 if n_fail else (2 if n_pass == 0 else 0))

if __name__ == "__main__":
    main()
