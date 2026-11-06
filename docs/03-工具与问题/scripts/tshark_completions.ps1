# tshark_completions.ps1 —— tshark 命令行字段补全（JetBrains 式候选列表）
#
# 安装（一次性）：在 PowerShell 里执行下面两行（把点源行写进 $PROFILE 永久生效）：
#   . D:\笔记\MD\SurviveBIGCManual\docs\03-工具与问题\scripts\tshark_completions.ps1
#   Add-Content $PROFILE ". D:\笔记\MD\SurviveBIGCManual\docs\03-工具与问题\scripts\tshark_completions.ps1"
#
# 用法：
#   tshark -e tls.handsh<Tab>          → 补全字段名（含 GMSSL.* 插件字段）
#   tshark -Y "tls.<Tab>               → 同上（显示过滤器里也能补）
#   tshark -d "tcp.port==10443,<Tab>   → 补 decode-as 协议名（gmssl/tls/tcp...）
#   Ctrl+Space 也能触发候选（PSReadLine）
#   Get-TsharkField <关键字>            → 独立的字段搜索器（不动命令行）

# ---- 配置：tshark 路径（按需改）----
$script:TsharkExe = if (Test-Path 'D:\ws-tshark\tshark.exe') { 'D:\ws-tshark\tshark.exe' } else { 'tshark' }
$script:FieldCache = Join-Path $env:TEMP 'tshark-fields-cache.txt'
$script:ProtoCache = Join-Path $env:TEMP 'tshark-protocols-cache.txt'

function Update-TsharkCache {
    $ver = (& $script:TsharkExe -v 2>$null | Select-Object -First 1)
    if (-not $ver) { return $false }
    $key = ($ver -replace '\s', '_')

    # fields: 行首 "F\t"，字段名在第 3 列
    $ff = Join-Path $env:TEMP 'tshark-fields-cache.txt'
    if (-not (Test-Path $ff) -or ((Get-Content $ff -TotalCount 1) -ne $key) -or ((Get-Content $ff | Measure-Object).Count -lt 5)) {
        $names = & $script:TsharkExe -G fields 2>$null |
            Where-Object { $_.StartsWith("F`t") } |
            ForEach-Object { ($_ -split "`t")[2] } |
            Where-Object { $_ } | Sort-Object -Unique
        Set-Content -Path $ff -Value (@($key) + @($names)) -Encoding utf8
    }

    # protocols: 每行 name\ttitle\tfiltername...，过滤名在第 3 列
    $pf = Join-Path $env:TEMP 'tshark-protocols-cache.txt'
    if (-not (Test-Path $pf) -or ((Get-Content $pf -TotalCount 1) -ne $key) -or ((Get-Content $pf | Measure-Object).Count -lt 3)) {
        $names = & $script:TsharkExe -G protocols 2>$null |
            ForEach-Object { ($_ -split "`t")[2] } |
            Where-Object { $_ } | Sort-Object -Unique
        Set-Content -Path $pf -Value (@($key) + @($names)) -Encoding utf8
    }
    return $true
}




function Get-TsharkFieldNames {
    Update-TsharkCache | Out-Null
    if (Test-Path $script:FieldCache) { Get-Content $script:FieldCache | Select-Object -Skip 1 }
}

function Get-TsharkProtocolNames {
    Update-TsharkCache | Out-Null
    if (Test-Path $script:ProtoCache) { Get-Content $script:ProtoCache | Select-Object -Skip 1 }
}

# 独立字段搜索器（JetBrains 双 Shift 的感觉）：Get-TsharkField handshake
function Get-TsharkField {
    param([string]$Keyword = '')
    Update-TsharkCache | Out-Null
    Get-Content $script:FieldCache | Select-Object -Skip 1 |
        Where-Object { $_ -like "*$Keyword*" } |
        Select-Object -First 40
}
Set-Alias -Name tsharkfields -Value Get-TsharkField -ErrorAction SilentlyContinue

# ---- 补全逻辑 ----
function script:Get-PrecedingMode($commandAst, $cursorOffset) {
    # 找光标之前最近的相关 flag：-e/-E/-Y/-f → field; -d → decode; 其他已知 flag → other
    $text = $commandAst.Extent.Text
    $before = $text.Substring(0, [Math]::Min($cursorOffset, $text.Length))
    $modes = @(
        @('-e', 'field'), @('-E', 'field'),
        @('-Y', 'field'), @('--display-filter', 'field'),
        @('-f', 'capture'),
        @('-d', 'decode'),
        @('-r', 'file'), @('-w', 'file'), @('-z', 'stats'),
        @('-V', 'other'), @('-x', 'other'), @('-q', 'other'),
        @('-c', 'other'), @('-T', 'other'), @('-n', 'other'), @('-2', 'other'), @('-s', 'other'), @('-i', 'iface')
    )
    $best = $null; $bestPos = -1
    foreach ($m in $modes) {
        $p = $before.LastIndexOf((' ' + $m[0] + ' '), [System.StringComparison]::OrdinalIgnoreCase)
        if ($before.StartsWith($m[0] + ' ')) { $p = 0 }
        if ($p -ge 0 -and $p -gt $bestPos) { $best = $m[1]; $bestPos = $p }
    }
    return $best
}

Register-ArgumentCompleter -CommandName tshark -Native -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $mode = Get-PrecedingMode $commandAst $cursorPosition
    switch ($mode) {
        'field' {
            Get-TsharkFieldNames | Where-Object { $_ -like "$wordToComplete*" } |
                ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        }
        'decode' {
            Get-TsharkProtocolNames | Where-Object { $_ -like "$wordToComplete*" } |
                ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        }
        default {
            @('-r', '-w', '-Y', '-e', '-E', '-T', '-V', '-x', '-q', '-z', '-d', '-n', '-2', '-c', '-s', '-i') |
                Where-Object { $_ -like "$wordToComplete*" } |
                ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_) }
        }
    }
}
