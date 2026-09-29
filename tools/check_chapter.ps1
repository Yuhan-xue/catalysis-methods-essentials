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
#  注意：测试主文件写在**工程根目录**（chk_<Chap>_<jobid>.tex），而不是 build/。
#  这样章文件里的 \input{chapters/parts/...} 与 main.tex 的解析路径完全一致。
#
#  ------------------------------------------------------------------
#  并发隔离（2026-09-29 修）
#  ------------------------------------------------------------------
#  旧版 jobname 只有 `chk_<Chap>`，且每次启动都按通配符删掉 build\chk_<Chap>.*。
#  于是两个 agent 同时跑同一个 -Chap 时，会互相删掉对方写到一半的 aux/log，
#  表现为 `! File ended while scanning use of \@newl@bel.` 加几十个 undefined ref，
#  而**源文件哈希完全没变** —— 即假失败。本项目已多次因此误判「代码坏了」。
#
#  现在：jobname = `chk_<Chap>_<PID>_<rand>`，每次调用唯一；
#        清理只按本进程这个精确名前缀删自己的文件，绝不碰别人的；
#        若目标文件被别的进程独占（真并发占用），给出明确 WARN 并跳过删除，
#        而不是静默 Remove-Item -ErrorAction SilentlyContinue 地删不动还当没事。
#        若失败日志同时具备「aux 被截断」特征，会额外提示复核，避免把并发干扰
#        当成真实编译错误上报。
#
#  调用方式（-Chap chXX-y）完全不变；-JobName 仅供需要固定名的场景（自担唯一性）。
# ================================================================
param(
    [Parameter(Mandatory = $true)][string]$Chap,
    [switch]$Pages,     # 额外输出每页字符数与墨迹覆盖率
    [switch]$Quiet,
    [switch]$Keep,      # 保留本次 chk_*.tex 与 chk_*.pdf（其余中间产物照清）
    [Alias('Job')][string]$JobName   # 覆盖自动生成的 jobname（默认 chk_<Chap>_<pid>_<rand>）
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

# ---------------------------------------------------------------- jobname
# 唯一性来源：本进程 PID（同进程重入由随机串兜底）。对应文件只有本进程会碰。
$jobSuffix = '{0}_{1}' -f $PID, (Get-Random -Minimum 1679616 -Maximum 16796160).ToString('x5')
$job       = if ($PSBoundParameters.ContainsKey('JobName') -and $JobName) { $JobName } else { "chk_${Chap}_$jobSuffix" }
$texPath   = Join-Path $root "$job.tex"

if ($PSBoundParameters.ContainsKey('JobName') -and $JobName -and $JobName -notmatch '_\d+_[0-9a-f]{4,}$') {
    Write-Host "WARN: -JobName '$JobName' 不含自动唯一后缀；若并发运行同名作业会互相破坏构建产物。" -ForegroundColor Yellow
}

# 本次作业的全部中间产物（与旧版清单一字不差）。.fdb_latexmk 必须在内，
# 否则 latexmk 会拿旧数据库判断「已是最新」而跳过重编译。
$jobExts = @('.tex', '.aux', '.log', '.toc', '.out', '.xdv', '.pdf', '.fls', '.fdb_latexmk')

# 只删本 jobname 精确对应的文件。删不掉 = 被别的进程独占 = 真并发占用，
# 这时必须出声：静默跳过会让人把污染后的结果当成真实结论。
function Remove-OwnedFiles {
    param([string]$Dir, [string[]]$Names)
    $failed = New-Object System.Collections.ArrayList
    foreach ($n in $Names) {
        $p = Join-Path $Dir $n
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $lockHeld = $false
        try {
            $h = [IO.File]::Open($p, 'Open', 'ReadWrite', 'None')   # 独占打开探测
            $h.Close()
        } catch { $lockHeld = $true }
        if ($lockHeld) { [void]$failed.Add($p); continue }
        Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
        if (Test-Path -LiteralPath $p) { [void]$failed.Add($p) }
    }
    return ,$failed
}

# 开场只清自己的名字。刻意不动历史遗留的 build\chk_<Chap>.*：那些是别人
# （或旧版脚本）的文件，旧版通配符删除正是本次并发事故的根因。
$ownBuildNames = $jobExts | ForEach-Object { "$job$_" }
$occupied = Remove-OwnedFiles -Dir $build -Names $ownBuildNames
if ($occupied.Count) {
    Write-Host "WARN: 以下文件被其它进程独占，无法清理（疑似同名并发运行）：" -ForegroundColor Yellow
    $occupied | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
    Write-Host "      本次结果可能受污染；请确认没有并发同名作业，或稍后重跑复核。" -ForegroundColor Yellow
}

$tex = @"
\documentclass[UTF8,10pt,a4paper,twoside,fontset=fandol]{ctexart}
\input{style/preamble}
\input{style/macros}
\begin{document}
\input{$target}
\end{document}
"@
[IO.File]::WriteAllText($texPath, $tex, (New-Object Text.UTF8Encoding $false))

Write-Host "job=$job" -ForegroundColor DarkGray

$code = 1
try {
    Push-Location $root
    # 必须同时清掉 build/ 下的同名 .tex —— latexmk 在 -outdir 下会优先取输出目录里的同名源文件，
    # 残留的旧模板会导致“File `../style/preamble.tex' not found”这类假错误。
    # （本 jobname 唯一，上面已按精确名清理，这里无需再按通配符动别人的文件。）
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

    # 并发干扰指纹：aux 被别的进程删/截断时 latexmk 的第二遍会读到半截 \@newl@bel 行。
    # 命中它 + 一堆 undefined ref + 0 个真错误 = 典型假失败，必须提示复核而不是让人去改代码。
    $truncatedAux = $logText -match 'File ended while scanning use of|File ended while scanning'

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

    $failed = ($code -ne 0 -or $errors.Count -gt 0 -or $miss.Count -gt 0)
    if ($failed -and $errors.Count -eq 0 -and $undef.Count -ge 5) {
        Write-Host ("NOTE: 0 个真错误但有 {0} 个 undefined ref{1}。这通常是交叉引用需要多遍编译，" -f $undef.Count, $(if ($truncatedAux) { '，且日志含 aux 被截断特征' } else { '' })) -ForegroundColor Yellow
        Write-Host "      也可能是并发作业破坏了 aux。源文件未变时请重跑一次再判断，勿径直接改稿。" -ForegroundColor Yellow
        Write-Host "      本次日志：$logPath" -ForegroundColor DarkGray
    }

    if (-not $Quiet) {
        if ($failed) { Write-Host "RESULT: FAIL" -ForegroundColor Red } else { Write-Host "RESULT: PASS" -ForegroundColor Green }
    }
    if ($failed) { exit 1 } else { exit 0 }
}
finally {
    # 只按自己这个唯一 jobname 的精确名清理，绝不触碰别人的文件。
    # -Keep：保留本次的 .tex 与 .pdf（旧版行为：产物留在 build\ 供人翻看、
    #         供 -Pages / qa_pdf.py 复读），其余中间产物照清；
    # 不加 -Keep：全部带走，避免 build\ 随调用次数无限膨胀。
    $keepNames  = if ($Keep) { @("$job.pdf") } else { @() }
    $purgeNames = $ownBuildNames | Where-Object { $_ -notin $keepNames }
    $left = New-Object System.Collections.ArrayList
    [void]$left.AddRange([string[]](Remove-OwnedFiles -Dir $build -Names $purgeNames))
    [void]$left.AddRange([string[]](Remove-OwnedFiles -Dir $root  -Names @("$job.tex")))
    if ($left.Count) {
        Write-Host "WARN: 收尾未能删除 $($left -join ', ')（被占用），请手工确认。" -ForegroundColor Yellow
    }
}
