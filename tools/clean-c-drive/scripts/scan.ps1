# 扫描各清理目标的磁盘占用
# 无需管理员权限，只读操作

function Get-DirSize($path) {
    if (-not (Test-Path $path)) { return -1 }
    $size = (Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum
    return [long]($size ?? 0)
}

function Format-GB($bytes) {
    if ($bytes -lt 0) { return "路径不存在" }
    return "{0:F2} GB" -f ($bytes / 1GB)
}

$u = $env:USERPROFILE

$modules = @(
    @{ Id=1; Name="用户 Temp 临时文件";    Path="$u\AppData\Local\Temp" },
    @{ Id=2; Name="Windows 系统 Temp";      Path="C:\Windows\Temp" },
    @{ Id=3; Name="NVIDIA DXCache";         Path="$u\AppData\Local\NVIDIA\DXCache" },
    @{ Id=4; Name="npm 缓存";               Path="$u\AppData\Local\npm-cache" },
    @{ Id=5; Name="pip 缓存";               Path="$u\AppData\Local\pip" },
    @{ Id=6; Name="程序崩溃转储";           Path="$u\AppData\Local\CrashDumps" },
    @{ Id=7; Name="回收站";                 Path="C:\`$Recycle.Bin" }
)

$jetbrainsVersions = @(
    "IntelliJIdea2025.2","IntelliJIdea2025.3",
    "CLion2025.2","CLion2025.3",
    "PyCharm2025.2","PyCharm2025.3",
    "PhpStorm2025.2","PhpStorm2025.3",
    "WebStorm2025.2","WebStorm2025.3",
    "GoLand2025.3"
)

Write-Host ""
Write-Host "========== C盘清理扫描报告 ==========" -ForegroundColor Cyan
Write-Host ("扫描时间：" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Write-Host ""
Write-Host ("{0,-4} {1,-28} {2,10}" -f "编号", "模块", "占用") -ForegroundColor Yellow
Write-Host ("-" * 50)

$results = @{}

foreach ($m in $modules) {
    $size = Get-DirSize $m.Path
    $results[$m.Id] = $size
    $sizeStr = Format-GB $size
    $color = if ($size -gt 1GB) { "Red" } elseif ($size -gt 100MB) { "Yellow" } else { "White" }
    Write-Host ("[{0}] {1,-28} {2,10}" -f $m.Id, $m.Name, $sizeStr) -ForegroundColor $color
}

# JetBrains 汇总
$jbTotal = 0
$jbPaths = @()
foreach ($ver in $jetbrainsVersions) {
    foreach ($base in @("$u\AppData\Local\JetBrains", "$u\AppData\Roaming\JetBrains")) {
        $p = "$base\$ver"
        if (Test-Path $p) {
            $sz = Get-DirSize $p
            $jbTotal += $sz
            $jbPaths += $p
        }
    }
}
$results[8] = $jbTotal
$jbColor = if ($jbTotal -gt 1GB) { "Red" } elseif ($jbTotal -gt 100MB) { "Yellow" } else { "White" }
Write-Host ("[8] {0,-28} {1,10}" -f "JetBrains 旧版本数据", (Format-GB $jbTotal)) -ForegroundColor $jbColor
Write-Host ("    ({0} 个路径)" -f $jbPaths.Count) -ForegroundColor DarkGray

# 休眠文件
$hibSize = -1
if (Test-Path "C:\hiberfil.sys") {
    $hibSize = (Get-Item "C:\hiberfil.sys" -Force).Length
    Write-Host ("[9] {0,-28} {1,10}  ⚠ 禁用后失去睡眠功能" -f "休眠文件 hiberfil.sys", (Format-GB $hibSize)) -ForegroundColor Magenta
} else {
    Write-Host ("[9] 休眠文件 hiberfil.sys             已禁用/不存在") -ForegroundColor DarkGray
}
$results[9] = $hibSize

Write-Host ""

# 计算可释放总量（不含休眠）
$cleanable = ($results.Values | Where-Object { $_ -gt 0 } | Measure-Object -Sum).Sum - [math]::Max(0, $hibSize)
Write-Host ("可释放空间（不含休眠）：{0:F2} GB" -f ($cleanable / 1GB)) -ForegroundColor Green
if ($hibSize -gt 0) {
    Write-Host ("含休眠文件可释放：{0:F2} GB" -f (($cleanable + $hibSize) / 1GB)) -ForegroundColor Green
}
Write-Host ""

# 当前 C 盘状态
$drive = Get-PSDrive C
Write-Host "当前 C 盘状态：" -ForegroundColor Cyan
Write-Host ("  已用：{0:F2} GB  剩余：{1:F2} GB  总计：{2:F2} GB" -f `
    ($drive.Used/1GB), ($drive.Free/1GB), (($drive.Used+$drive.Free)/1GB))
Write-Host ""
