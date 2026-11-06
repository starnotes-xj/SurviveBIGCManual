# _kali_zsh_test.zsh — zsh 补全脚本验证（非交互）
autoload -Uz compinit && compinit -u
source /tmp/tshark-zsh-complete.zsh
print "compdef 已注册: $+functions[_tshark_gmssl]  (2=是)"
words=(tshark -r f.pcap -e tls.handsh); CURRENT=4
local -a fields
fields=(${(f)"$(tshark -G fields 2>/dev/null | awk -F'\t' '$1=="F"{print $3}')"})
print "字段缓存数: ${#fields}"
print "tls.handsh* 前缀匹配:"
print -l ${(M)fields:#tls.handsh*} | head -4
words=(tshark -r f.pcap -Y "GMSSL.Hello."); CURRENT=4
print "GMSSL.Hello.* 前缀匹配数: ${#${(M)fields:#GMSSL.Hello.*}}"
print -l ${(M)fields:#GMSSL.Hello.*} | head -3
