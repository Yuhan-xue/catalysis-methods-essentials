# ================================================================
#  tools/build.ps1 —— 全书构建（唯一入口）
#
#  用法： pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
#         pwsh ... -File tools/build.ps1 -Quick     # 不强制全量，快
#
#  为什么默认强制全量（-g）：
#  分片是通过 \IfFileExists 引入的，latexmk 的依赖数据库不会记录
#  「尚未存在」的文件。新增分片后若只做增量构建，latexmk 会认为
#  无事可做而直接跳过，产出**过期的 PDF**（曾实际发生：ch00-intro 未进书）。
# ================================================================
param(
    [switch]$Quick,
    [switch]$Open
)
$ErrorActionPreference = 'Stop'
$root  = Split-Path -Parent $PSScriptRoot
$build = Join-Path $root 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null

Push-Location $root
$args = @('-xelatex', '-interaction=nonstopmode', '-outdir=build')
if (-not $Quick) { $args += '-g' }
$args += 'main.tex'
& "C:\texlive\2026\bin\windows\latexmk.exe" @args *> $null
$code = $LASTEXITCODE
Pop-Location

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

Write-Host "==== build ====" -ForegroundColor Cyan
Write-Host ("latexmk exit  : {0}" -f $code)
Write-Host ("pages         : {0}" -f $(if ($mm.Success) { $mm.Groups[1].Value } else { '?' }))
Write-Host ("errors        : {0}" -f $errs.Count)
Write-Host ("overfull >5pt : {0}" -f $ovf.Count)
Write-Host ("missing glyphs: {0}" -f $miss.Count) -ForegroundColor $(if ($miss.Count) { 'Red' } else { 'Gray' })
Write-Host ("undefined refs: {0}" -f $undef.Count)
if ($errs.Count) { $errs | Select-Object -First 12 | ForEach-Object { Write-Host "  ERR  $($_.Value)" -ForegroundColor Red } }
if ($ovf.Count)  { $ovf  | Select-Object -First 8  | ForEach-Object { Write-Host "  OVER $($_.Value)" -ForegroundColor Yellow } }
if ($miss.Count) {
    [regex]::Matches($txt, 'Missing character: There is no ([^\s]+) \(U\+([0-9A-Fa-f]+)\) in font ([^/]+)') |
        ForEach-Object { "  MISS U+$($_.Groups[2].Value.ToUpper()) '$($_.Groups[1].Value)' in $($_.Groups[3].Value.Trim())" } |
        Sort-Object -Unique | Select-Object -First 12 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}

if ($Open) { Start-Process (Join-Path $build 'main.pdf') }
if ($code -ne 0 -or $errs.Count -gt 0 -or $miss.Count -gt 0) { exit 1 }
exit 0
