#!/usr/bin/env bash
# tshark-complete.sh —— tshark 字段名/协议名补全 + tf 字段搜索助手（Kali/bash）
#
# 安装（一次性）：
#   cp tshark-complete.sh ~/gmssl-tools/ && echo 'source ~/gmssl-tools/tshark-complete.sh' >> ~/.bashrc
#   （以 kali 用户执行；root 的 bash 也要装则再对 root 的 .bashrc 做一次）
#
# 用法：
#   tshark -e tls.handsh<Tab>            → 字段名补全（含 GMSSL.* 插件字段）
#   tshark -Y "tls.<Tab>                 → 显示过滤器里的字段名补全
#   tshark -d tcp.port==10443,<Tab>      → decode-as 协议名补全（gmssl/tls/...）
#   tf handshake                          → 交互式搜索字段名（有 fzf 模糊选择，无 fzf 分页）
#   tf <关键字> | grep -i ciphersuite     → 组合过滤

_tshark_cache_file() {
    local ver
    ver=$(tshark -v 2>/dev/null | head -1 | tr ' ' '_')
    local d="$HOME/.cache/tshark-completion"
    mkdir -p "$d"
    echo "$d/fields-$ver.txt"
}

_tshark_build_cache() {
    local f
    f=$(_tshark_cache_file)
    [ -s "$f" ] && return 0
    tshark -G fields 2>/dev/null | awk -F'\t' '$1=="F"{print $3}' > "$f"
}

_tshark_completions() {
    local cur mode i
    cur="${COMP_WORDS[COMP_CWORD]}"
    for ((i = COMP_CWORD - 1; i >= 1; i--)); do
        case "${COMP_WORDS[i]}" in
            -e|-E|-Y|--display-filter|-f) mode=field; break ;;
            -d)                           mode=decode; break ;;
            -r|-w|-z|-q|-V|-x|-c|-T|-n|-2|-s|-i) mode=opt; break ;;
        esac
    done
    _tshark_build_cache
    local cache
    cache=$(_tshark_cache_file)
    case "$mode" in
        field)
            local w="${cur//\"/}"   # 只去掉引号; 点分路径整体参与前缀匹配
            COMPREPLY=( $(compgen -W "$(cat "$cache")" -- "$w") )
            ;;
        decode)
            local p="${cur##*,}"
            COMPREPLY=( $(compgen -W "gmssl tls tcp udp http http2 quic" -- "$p") )
            ;;
        *)
            COMPREPLY=( $(compgen -W "-r -w -Y -e -E -T -V -x -q -z -d -n -2 -c -i -f" -- "$cur") )
            ;;
    esac
}
complete -o nospace -F _tshark_completions tshark

# 交互式字段搜索助手
tf() {
    tshark -G fields 2>/dev/null | awk -F'\t' '$1=="F"{printf "%-60s %s\n", $3, $4}' |
        grep -i "${1:-}" | ${PAGER:-less -S}
}
