# ================================================================
#  tools/check_chapter.ps1
#  单独编译一个章文件，验证它能否在全书版式下通过。
#
#  用法：
#    pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch09
#    pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch09 -Pages
#
#  退出码 0 = 通过（无 ! 错误）；1 = 失败；2 = 章文件不存在。
#
#  注意：测试主文件写在**工程根目录**（chk_<Chap>.tex），而不是 build/。
#  这样章文件里的 \input{chapters/parts/...} 与 main.tex 的解析路径完全一致。
# ================================================================
param(
    [Parameter(Mandatory = $true)][string]$Chap,
    [switch]$Pages,     # 额外输出每页字符数与墨迹覆盖率
    [switch]$Quiet,
    [switch]$Keep       # 保留 chk_*.tex
)

# -Chap 既可给章号（ch09，编译整章所有已有分片），也可给分片名（ch09-a，只编译该分片）。
# 分片级编译很重要：同一章的多个分片由不同作者并发编写，互相不能因为对方还没写完而失败。
$root  = Split-Path -Parent $PSScriptRoot
$build = Join-Path $root 'build'
if ($Chap -match '^ch\d{2}-[a-e]$') {
    $target = "chapters/parts/$Chap"
    $src    = Join-Path $root "chapters\parts\$Chap.tex"
} else {
    $target = "chapters/$Chap"
    $src    = Join-Path $root "chapters\$Chap.tex"
}

if (-not (Test-Path $src)) {
    Write-Host "FAIL: $src 不存在" -ForegroundColor Red
    exit 2
}
New-Item -ItemType Directory -Force -Path $build | Out-Null

$job = "chk_$Chap"
$tex = @"
\documentclass[UTF8,10pt,a4paper,twoside,fontset=fandol]{ctexart}
\input{style/preamble}
\input{style/macros}
\begin{document}
\input{$target}
\end{document}
"@
$texPath = Join-Path $root "$job.tex"
[IO.File]::WriteAllText($texPath, $tex, (New-Object Text.UTF8Encoding $false))

# 必须同时清掉 build/ 下的同名 .tex —— latexmk 在 -outdir 下会优先取输出目录里的同名源文件，
# 残留的旧模板会导致“File `../style/preamble.tex' not found”这类假错误。
Get-ChildItem $build -Filter "$job.*" -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in '.tex', '.aux', '.log', '.toc', '.out', '.xdv', '.pdf', '.fls', '.fdb_latexmk' } |
    Remove-Item -Force -ErrorAction SilentlyContinue

Push-Location $root
& "C:\texlive\2026\bin\windows\latexmk.exe" -xelatex -interaction=nonstopmode -halt-on-error -outdir=build "$job.tex" *> $null
$code = $LASTEXITCODE
Pop-Location

$logPath = Join-Path $build "$job.log"
$log = if (Test-Path $logPath) { Get-Content $logPath -Encoding utf8 } else { @() }
$logText = if (Test-Path $logPath) { [IO.File]::ReadAllText($logPath) } else { '' }

$errors = $log | Select-String -Pattern '^! '
$overfull = @()
foreach ($m in [regex]::Matches($logText, 'Overfull \\hbox \((\d+\.\d+)pt too wide')) {
    if ([double]$m.Groups[1].Value -gt 5) { $overfull += $m.Value }
}
$undef = $log | Select-String -Pattern 'LaTeX Warning: (Reference|Citation).*undefined'
# 静默丢字：不报错、不中断，只在 log 留一行 Missing character，PDF 上字符直接消失。
# 这是企划验收「无缺字」的硬指标，必须当错误处理（ch11-a 作者首先发现）。
$miss = @([regex]::Matches($logText, 'Missing character: There is no'))

if (-not $Quiet) {
    Write-Host "==== $Chap ====" -ForegroundColor Cyan
    Write-Host ("errors        : {0}" -f $errors.Count)
    Write-Host ("overfull >5pt : {0}" -f $overfull.Count)
    Write-Host ("missing glyphs: {0}" -f $miss.Count) -ForegroundColor $(if ($miss.Count) { 'Red' } else { 'Gray' })
    Write-Host ("undefined ref : {0}" -f $undef.Count)
    if ($errors.Count)  { $errors  | Select-Object -First 12 | ForEach-Object { Write-Host "  ERR  $($_.Line)" -ForegroundColor Red } }
    if ($overfull.Count) { $overfull | Select-Object -First 8 | ForEach-Object { Write-Host "  OVER $_" -ForegroundColor Yellow } }
    if ($miss.Count) {
        [regex]::Matches($logText, 'Missing character: There is no ([^\s]+) \(U\+([0-9A-Fa-f]+)\) in font ([^/]+)') |
            ForEach-Object { "  MISS U+$($_.Groups[2].Value.ToUpper()) '$($_.Groups[1].Value)' in $($_.Groups[3].Value.Trim())" } |
            Sort-Object -Unique | Select-Object -First 10 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    }
}

$pdf = Join-Path $build "$job.pdf"
if (Test-Path $pdf) {
    $mm = [regex]::Match($logText, 'Output written on .*?\((\d+) pages?')
    # 局部变量不可叫 $pages：PowerShell 变量名大小写不敏感，会与 [switch]$Pages 冲突
    $nPages = if ($mm.Success) { $mm.Groups[1].Value } else { '?' }
    if (-not $Quiet) { Write-Host "pages         : $nPages" }
    if ($Pages) {
        & python (Join-Path $root 'tools\qa_pdf.py') $pdf | Out-Null
        $rep = Join-Path $root 'tools\qa_report.txt'
        if (Test-Path $rep) { Get-Content $rep -Encoding utf8 | Select-Object -Last 40 }
    }
} elseif (-not $Quiet) {
    Write-Host "pages         : (未产出 PDF)" -ForegroundColor Red
}

if (-not $Keep) { Remove-Item $texPath -Force -ErrorAction SilentlyContinue }

if ($code -ne 0 -or $errors.Count -gt 0 -or $miss.Count -gt 0) {
    if (-not $Quiet) { Write-Host "RESULT: FAIL" -ForegroundColor Red }
    exit 1
}
if (-not $Quiet) { Write-Host "RESULT: PASS" -ForegroundColor Green }
exit 0
