# ================================================================
#  tools/build.ps1 —— 全书构建（唯一入口）
#
#  用法： pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
#         pwsh ... -File tools/build.ps1 -Quick      # 不强制全量，快
#         pwsh ... -File tools/build.ps1 -Release    # 发布验收：加严门禁
#
#  两种门禁（详见表尾 $fail 处）：
#    draft（默认）  拦编译错误与缺字
#    release       额外拦 overfull >5pt、未定义引用、重复标签
#  发布前必须用 -Release 跑一遍。
#
#  为什么默认强制全量（-g）：
#  分片是通过 \IfFileExists 引入的，latexmk 的依赖数据库不会记录
#  「尚未存在」的文件。新增分片后若只做增量构建，latexmk 会认为
#  无事可做而直接跳过，产出**过期的 PDF**（曾实际发生：ch00-intro 未进书）。
# ================================================================
param(
    [switch]$Quick,
    [switch]$Open,
    [switch]$Release
)
$ErrorActionPreference = 'Stop'
# 仓库根由脚本位置推导，不写死——写死会让克隆到别处的副本去构建**另一份**源码。
$root  = Split-Path -Parent $PSScriptRoot
$build = Join-Path $root 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null

# 解析 latexmk：优先 PATH；找不到再退回常见 TeX Live 安装位置（不锁定年份）。
function Resolve-Latexmk {
    $cmd = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cands = @()
    foreach ($base in @('C:\texlive', 'D:\texlive', "$env:USERPROFILE\texlive")) {
        if (Test-Path $base) {
            $cands += Get-ChildItem $base -Directory -ErrorAction SilentlyContinue |
                      Sort-Object Name -Descending |
                      ForEach-Object { Join-Path $_.FullName 'bin\windows\latexmk.exe' }
        }
    }
    foreach ($c in $cands) { if (Test-Path $c) { return $c } }
    throw "找不到 latexmk。请把 TeX Live 的 bin 目录加入 PATH，或安装 TeX Live。"
}
$latexmk = Resolve-Latexmk

Push-Location $root
$args = @('-xelatex', '-interaction=nonstopmode', '-outdir=build')
if (-not $Quick) { $args += '-g' }
$args += 'main.tex'
& $latexmk @args *> $null
$code = $LASTEXITCODE
Pop-Location

Write-Host ("root          : {0}" -f $root)
Write-Host ("latexmk       : {0}" -f $latexmk)

$logPath = Join-Path $build 'main.log'
$txt = if (Test-Path $logPath) { [IO.File]::ReadAllText($logPath) } else { '' }
$errs = [regex]::Matches($txt, '(?m)^! .*')
$ovf  = @([regex]::Matches($txt, 'Overfull \\hbox \((\d+\.\d+)pt too wide') |
          Where-Object { [double]$_.Groups[1].Value -gt 5 })
$undef = @([regex]::Matches($txt, '(?m)LaTeX Warning: (?:Reference|Citation).*undefined'))
# 静默丢字：xeCJK 把某些码位判给西文字体而该字体无此字形时，TeX 不报错、
# 不中断，只在 log 里留一行 Missing character，PDF 上那个字符直接消失。
# 这是企划验收「无缺字」的硬指标，必须当错误处理。
$miss = @([regex]::Matches($txt, 'Missing character: There is no'))
$mm = [regex]::Match($txt, 'Output written on .*?\((\d+) pages?')
# 重复标签：LaTeX 只给 warning，**编译不报错**，但引用会静默跳到别的章
# （本项目实际发生过 4 组：eq:bragg / eq:iss / eq:langmuir / tab:extinction）。
$duplab = @([regex]::Matches($txt, 'LaTeX Warning: Label `([^'']+)'' multiply defined'))

Write-Host "==== build ====" -ForegroundColor Cyan
Write-Host ("mode          : {0}" -f $(if ($Release) { 'release（发布验收）' } else { 'draft（草稿）' }))
Write-Host ("latexmk exit  : {0}" -f $code)
Write-Host ("pages         : {0}" -f $(if ($mm.Success) { $mm.Groups[1].Value } else { '?' }))
Write-Host ("errors        : {0}" -f $errs.Count)
Write-Host ("overfull >5pt : {0}" -f $ovf.Count)
Write-Host ("missing glyphs: {0}" -f $miss.Count) -ForegroundColor $(if ($miss.Count) { 'Red' } else { 'Gray' })
Write-Host ("undefined refs: {0}" -f $undef.Count)
Write-Host ("dup labels    : {0}" -f $duplab.Count)
if ($errs.Count) { $errs | Select-Object -First 12 | ForEach-Object { Write-Host "  ERR  $($_.Value)" -ForegroundColor Red } }
if ($ovf.Count)  { $ovf  | Select-Object -First 8  | ForEach-Object { Write-Host "  OVER $($_.Value)" -ForegroundColor Yellow } }
if ($undef.Count -and $Release) { $undef | Select-Object -First 8 | ForEach-Object { Write-Host "  UNDEF $($_.Value)" -ForegroundColor Red } }
if ($duplab.Count) {
    $duplab | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique |
        Select-Object -First 12 | ForEach-Object { Write-Host "  DUPLAB $_" -ForegroundColor Red }
}
if ($miss.Count) {
    [regex]::Matches($txt, 'Missing character: There is no ([^\s]+) \(U\+([0-9A-Fa-f]+)\) in font ([^/]+)') |
        ForEach-Object { "  MISS U+$($_.Groups[2].Value.ToUpper()) '$($_.Groups[1].Value)' in $($_.Groups[3].Value.Trim())" } |
        Sort-Object -Unique | Select-Object -First 12 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}

if ($Open) { Start-Process (Join-Path $build 'main.pdf') }

# 失败条件。draft 模式只拦「编译不过」与「丢字」；
# release 模式额外拦「超宽 / 未定义引用 / 重复标签」——即 README 声明的发布门禁。
# 两者都拦的条件：latexmk 非零、有 '!' 错误、有缺字。
$fail = @()
if ($code -ne 0)        { $fail += "latexmk 退出码 $code" }
if ($errs.Count)        { $fail += "$($errs.Count) 个编译错误" }
if ($miss.Count)        { $fail += "$($miss.Count) 处缺字" }
if ($Release) {
    if ($ovf.Count)     { $fail += "$($ovf.Count) 处 overfull >5pt" }
    if ($undef.Count)   { $fail += "$($undef.Count) 处未定义引用" }
    if ($duplab.Count)  { $fail += "$($duplab.Count) 处重复标签" }
}
if ($fail.Count) {
    Write-Host ("FAIL: " + ($fail -join '；')) -ForegroundColor Red
    exit 1
}
Write-Host "PASS" -ForegroundColor Green
exit 0
