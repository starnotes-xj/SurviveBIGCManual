#!/usr/bin/env bash
source /tmp/tshark-complete.sh
echo "=== 字段补全(tls.handsh) ==="
COMP_WORDS=(tshark -r D1.pcap -e tls.handsh); COMP_CWORD=4; _tshark_completions
printf '%s\n' "${COMPREPLY[@]:0:4}"
echo "=== 字段补全(GMSSL.Hello.) ==="
COMP_WORDS=(tshark -r D1.pcap -Y "GMSSL.Hello."); COMP_CWORD=3; _tshark_completions
printf '%s\n' "${COMPREPLY[@]:0:4}"
echo "=== decode-as 补全(g) ==="
COMP_WORDS=(tshark -d tcp.port==10443,g); COMP_CWORD=3; _tshark_completions
printf '%s\n' "${COMPREPLY[@]}"
echo "=== tf 搜索(ciphersuite, 限3行) ==="
tshark -G fields 2>/dev/null | awk -F'\t' '$1=="F"{printf "%-60s %s\n", $3, $4}' | grep -i ciphersuite | head -3
