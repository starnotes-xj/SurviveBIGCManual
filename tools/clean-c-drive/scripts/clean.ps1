# C盘清理执行脚本
# 参数：
#   -Modules  "all" 或逗号分隔的模块编号，如 "1,2,4,8"
#   -DisableHibernation  $true 禁用休眠（同时清理模块9）

param(
    [string]$Modules = "all",
    [switch]$DisableHibernation
)

$u = $env:USERPROFILE
$totalFreed = 0L

function Remove-SafeDir($path, $label) {
    if (-not (Test-Path $path)) {
        Write-Host ("[跳过] $label（路径不存在）") -ForegroundColor DarkGray
        return 0L
    }
    $before = (Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue |
               Measure-Object -Property Length -Sum).Sum
    $before = [long]($before ?? 0)
    Remove-Item "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
    $after = (Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue |
              Measure-Object -Property Length -Sum).Sum
    $after = [long]($after ?? 0)
    $freed = $before - $after
    Write-Host ("[OK] {0,-32} 释放 {1,7:F3} GB" -f $label, ($freed/1GB)) -ForegroundColor Green
    return $freed
}

# 解析要清理的模块
$selectedAll = ($Modules -eq "all")
$selectedIds = if ($selectedAll) { 1..9 } else { $Modules -split "," | ForEach-Object { [int]$_.Trim() } }

Write-Host ""
Write-Host "========== 开始清理 ==========" -ForegroundColor Cyan
Write-Host ""

# 模块 1：用户 Temp
if ($selectedAll -or 1 -in $selectedIds) {
    $freed = Remove-SafeDir "$u\AppData\Local\Temp" "用户 Temp 临时文件"
    $totalFreed += $freed
}

# 模块 2：Windows Temp（需要管理员）
if ($selectedAll -or 2 -in $selectedIds) {
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($isAdmin) {
        $freed = Remove-SafeDir "C:\Windows\Temp" "Windows 系统 Temp"
        $totalFreed += $freed
    } else {
        Write-Host ("[!] Windows 系统 Temp — 需要管理员权限，已跳过") -ForegroundColor Yellow
    }
}

# 模块 3：NVIDIA DXCache
if ($selectedAll -or 3 -in $selectedIds) {
    $freed = Remove-SafeDir "$u\AppData\Local\NVIDIA\DXCache" "NVIDIA DXCache"
    $totalFreed += $freed
}

# 模块 4：npm 缓存
if ($selectedAll -or 4 -in $selectedIds) {
    $freed = Remove-SafeDir "$u\AppData\Local\npm-cache" "npm 缓存"
    $totalFreed += $freed
}

# 模块 5：pip 缓存
if ($selectedAll -or 5 -in $selectedIds) {
    $freed = Remove-SafeDir "$u\AppData\Local\pip" "pip 缓存"
    $totalFreed += $freed
}

# 模块 6：崩溃转储
if ($selectedAll -or 6 -in $selectedIds) {
    $freed = Remove-SafeDir "$u\AppData\Local\CrashDumps" "程序崩溃转储"
    $totalFreed += $freed
}

# 模块 7：回收站
if ($selectedAll -or 7 -in $selectedIds) {
    Write-Host "[..] 清空回收站..." -NoNewline
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue
    Write-Host " [OK] 回收站已清空" -ForegroundColor Green
}

# 模块 8：JetBrains 旧版本
if ($selectedAll -or 8 -in $selectedIds) {
    $jbVersions = @(
        "IntelliJIdea2025.2","IntelliJIdea2025.3",
        "CLion2025.2","CLion2025.3",
        "PyCharm2025.2","PyCharm2025.3",
        "PhpStorm2025.2","PhpStorm2025.3",
        "WebStorm2025.2","WebStorm2025.3",
        "GoLand2025.3"
    )
    foreach ($ver in $jbVersions) {
        foreach ($base in @("$u\AppData\Local\JetBrains", "$u\AppData\Roaming\JetBrains")) {
            $p = "$base\$ver"
            if (Test-Path $p) {
                $freed = Remove-SafeDir $p "JetBrains $ver"
                $totalFreed += $freed
            }
        }
    }
}

# 模块 9：休眠文件
if ($DisableHibernation -or ($selectedAll -or 9 -in $selectedIds)) {
    if ($DisableHibernation) {
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if ($isAdmin) {
            Write-Host "[..] 禁用休眠（powercfg -h off）..." -NoNewline
            powercfg -h off
            if (Test-Path "C:\hiberfil.sys") {
                Write-Host " [??] hiberfil.sys 仍存在（重启后删除）" -ForegroundColor Yellow
            } else {
                Write-Host " [OK] hiberfil.sys 已删除" -ForegroundColor Green
            }
        } else {
            Write-Host "[!] 禁用休眠需要管理员权限，已跳过" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host ("========== 清理完成 ==========") -ForegroundColor Cyan
Write-Host ("本次共释放：{0:F2} GB" -f ($totalFreed/1GB)) -ForegroundColor Green
Write-Host ""
Write-Host "当前 C 盘状态：" -ForegroundColor Cyan
$drive = Get-PSDrive C
Write-Host ("  已用：{0:F2} GB  剩余：{1:F2} GB  总计：{2:F2} GB" -f `
    ($drive.Used/1GB), ($drive.Free/1GB), (($drive.Used+$drive.Free)/1GB))
Write-Host ""
