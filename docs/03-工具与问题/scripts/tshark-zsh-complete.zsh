# tshark-zsh-complete.zsh —— tshark 字段名补全（zsh 原生版）
#
# 安装（一次性，kali 用户）：
#   mkdir -p ~/.zsh && cp tshark-zsh-complete.zsh ~/.zsh/
#   echo 'source ~/.zsh/tshark-zsh-complete.zsh' >> ~/.zshrc && source ~/.zshrc
#
# 用法：
#   tshark -r f.pcap -e tls.handsh<Tab>        → 字段名候选（含 GMSSL.* 插件字段）
#   tshark -r f.pcap -Y "GMSSL.Hello.<Tab>     → 同上（显示过滤器内）
#   tshark -r f.pcap -d "tcp.port==10443,<Tab> → decode-as 协议名候选（gmssl/tls/...）

# 确保 zsh 补全系统已初始化（root 下 zsh 无此限制，本脚本亦以 kali 用户为推荐环境）
if (( ! $+functions[compdef] )); then
    autoload -Uz compinit && compinit -u
fi

_tshark_cache_file() {
    local d="$HOME/.cache/tshark-completion"
    mkdir -p "$d"
    print -- "$d/fields-$(tshark -v 2>/dev/null | head -1 | tr ' ' '_').txt"
}

_tshark_build_cache() {
    local f
    f=$(_tshark_cache_file)
    [[ -s "$f" ]] && return 0
    tshark -G fields 2>/dev/null | awk -F'\t' '$1=="F"{print $3}' > "$f"
}

_tshark_gmssl() {
    local i mode="" cur
    cur=${words[CURRENT]}
    local j
    for ((j = CURRENT - 1; j > 0; j--)); do
        case "${words[j]}" in
            -e|-Y|-f)          mode=field;  break ;;
            -d)                mode=decode; break ;;
            -r|-w|-z|-q|-V|-x|-c|-T|-n|-2|-s|-i) mode=opt; break ;;
        esac
    done

    if [[ "$mode" == "field" ]]; then
        _tshark_build_cache
        local f
        f=$(_tshark_cache_file)
        local -a fields
        fields=(${(f)"$(cat $f)"})
        _describe -V '国密/TLCP 字段' fields -S ''
    elif [[ "$mode" == "decode" ]]; then
        _values -s , 'decode-as 协议' gmssl tls tcp udp http http2 quic
    else
        _default
    fi
}

compdef _tshark_gmssl tshark
