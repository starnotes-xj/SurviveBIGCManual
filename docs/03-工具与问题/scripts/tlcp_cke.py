#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tlcp_cke.py — 从 pcap 自动抽取国密 SSL/TLCP 握手信息（无需第三方库）

用法: python tlcp_cke.py 文件.pcap
支持: 标准小端 pcap(d4c3b2a1) 与 modified pcap(34cdb2a1, 每包+8B)、
      Ethernet/IPv4/TCP 流重组、TLCP(0x0101) 与标准 TLS 的握手消息列表；
      ClientKeyExchange(type=16) 自动抽出 65 字节临时 SM2 公钥(04||X||Y)，
      ServerHello(type=2) 自动报选定的密码套件。
"""
import struct, sys

HS = {1: 'ClientHello', 2: 'ServerHello', 11: 'Certificate',
      12: 'ServerKeyExchange', 13: 'CertificateRequest', 14: 'ServerHelloDone',
      15: 'CertVerify', 16: 'ClientKeyExchange', 20: 'Finished'}
SUITES = {b'\xe0\x11': 'ECDHE_SM4_CBC_SM3', b'\xe0\x13': 'ECC_SM4_CBC_SM3',
          b'\xe0\x33': 'ECCC_SM4_CBC_SM3', b'\xe0\x51': 'ECDHE_SM4_GCM_SM3',
          b'\xe0\x53': 'ECC_SM4_GCM_SM3'}

def read_pcap(path):
    raw = open(path, 'rb').read()
    magic = raw[:4]
    if magic == bytes.fromhex('d4c3b2a1'):
        skip = 0                                   # 标准（小端）
    elif magic == bytes.fromhex('34cdb2a1'):
        skip = 8                                   # modified：每包 8B 附加头
    else:
        sys.exit('不支持的魔数 %s（本脚本支持小端标准/modified，可用 Wireshark 先转格式）' % magic.hex())
    pkts, off = [], 24
    while off + 16 <= len(raw):
        incl = int.from_bytes(raw[off+8:off+12], 'little')
        off += 16 + skip
        pkts.append(raw[off:off+incl]); off += incl
    return pkts

def streams(pkts):
    out = {}
    for d in pkts:
        if len(d) < 54 or d[12:14] != b'\x08\x00':
            continue
        ip = d[14:]
        ihl = (ip[0] & 0xF) * 4
        if ip[9] != 6:
            continue
        tcp = ip[ihl:]
        sp, dp = struct.unpack('>HH', tcp[:4])
        key = ('.'.join(map(str, ip[12:16])), sp, '.'.join(map(str, ip[16:20])), dp)
        out.setdefault(key, b'')
        out[key] += tcp[(tcp[12] >> 4) * 4:]
    return out

def handshake_msgs(stream):
    """按 record(5B头) -> 握手消息(1B type + 3B len) 两级切，产出 (ver, type, body)。"""
    i, n = 0, len(stream)
    while i + 5 <= n:
        ctype, ver = stream[i], stream[i+1:i+3].hex()
        rlen = int.from_bytes(stream[i+3:i+5], 'big')
        if rlen > n - i - 5:
            break                                  # 半包/截断，停
        rec = stream[i+5:i+5+rlen]
        if ctype == 0x16:                          # 握手 record
            j = 0
            while j + 4 <= len(rec):
                ht = rec[j]
                hl = int.from_bytes(rec[j+1:j+4], 'big')
                if j + 4 + hl > len(rec):
                    break
                yield ver, HS.get(ht, hex(ht)), ht, rec[j+4:j+4+hl]
                j += 4 + hl
        i += 5 + rlen

def main(path):
    for key, payload in streams(read_pcap(path)).items():
        print('== 流 %s:%s -> %s:%s' % key)
        for ver, name, ht, body in handshake_msgs(payload):
            line = '  [%s] ver=0x%s len=%d' % (name, ver, len(body))
            if ht == 16:                           # CKE：找 04||X||Y 的 65B 点
                cands = [k for k in range(len(body)) if body[k] == 0x04 and k + 65 <= len(body)]
                for k in cands[:3]:
                    line += '\n      临时公钥候选(65B): %s' % body[k:k+65].hex()
                if len(body) <= 200:
                    line += '\n      完整载荷: %s' % body.hex()
            elif ht == 2:                          # ServerHello：扫已知国密套件
                for s, nm in SUITES.items():
                    k = body.find(s)
                    if k >= 0:
                        line += '\n      选定/出现套件: 0x%s(%s) @偏移%d' % (s.hex(), nm, k)
            print(line)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('用法: python tlcp_cke.py <文件.pcap>')
    main(sys.argv[1])
