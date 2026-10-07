# ================================================================
#  tools/build.ps1 —— 全书构建（唯一入口）
#
#  用法： pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1
#         pwsh ... -File tools/build.ps1 -Quick      # 不强制全量，快
#         pwsh ... -File tools/build.ps1 -Release    # 发布验收：加严门禁
#
#  两种门禁（详见表尾 $fail 处）：
#    draft（默认）  拦编译错误、缺字；静态检查只报告，不拦
#    release       额外拦 overfull >5pt、未定义引用、重复标签、版面重叠确认缺陷，
#                  并且**堵住「静态检查根本没跑成」这种假通过**（见下）
#  发布前必须用 -Release 跑一遍。
#
#  第七项「重复引入」是静态检查，与编译无关：分片被 \IfFileExists 引入两次时
#  正文会重复排页，而其余六项门禁**全报 0**（已实测），只能靠 tools/check_includes.py
#  查出来。
#
#  第八项「版面重叠」由 tools/overlap_check.py --gate 判定：只拦**确认缺陷**类
#  （两个描边图形相撞），文字轮廓、数学上下标、合法嵌套框等按类别报告为「候选」，
#  不按总数一刀切阻断（理由与分类见该脚本 docstring）。
#
#  第九项「表格来源标注」由 tools/check_src.py 判定（同为静态检查，与编译无关）：
#  每张表必须带 \src{}，页码对必须自洽（书内-PDF 偏移一致），引了原书表号则该表号
#  必须出现在 OCR 表索引里；台账里有表而正文没有、或正文有表而台账没有，都算
#  「未检查」。报告落在 build/check_src.txt（gitignored）。
#
#  静态检查的状态：ok（查过，无问题）/ FAIL（查过，有问题）/
#  unavailable（**没检查**：python 不可用、脚本缺失、工具自报不可用、调用异常）。
#  draft 允许 unavailable，但输出里必须标成 skipped 并写清原因；
#  release 把 unavailable 判为失败——「没检查」不等于「没问题」（R2-W04）。
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

# ---------------------------------------------------------------
#  静态检查（第七、八项门禁）：三种状态不许混为一谈（R2-W04）
#    ok          查过，无问题
#    FAIL        查过，有问题
#    unavailable 没查成（python 不可用 / 脚本缺失 / 工具自报不可用 / 调用抛异常）
#  native 调用不做管道捕获：PS 5.1 在 $ErrorActionPreference='Stop' 下
#  对 native stderr 走管道会抛 NativeCommandError。
# ---------------------------------------------------------------
function Invoke-PyCheck {
    param([string]$Name, [string]$Script, [string[]]$ScriptArgs = @())
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        return [pscustomobject]@{ State = 'unavailable'; Code = $null; Detail = 'python 不可用' }
    }
    if (-not (Test-Path $Script)) {
        return [pscustomobject]@{ State = 'unavailable'; Code = $null; Detail = "$Script 不存在" }
    }
    # 中文不要经 GBK 控制台：先固定控制台解码与 python 的 stdout 编码。
    [Console]::OutputEncoding = [Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = 'utf-8'
    try {
        & $py.Source $Script @ScriptArgs
        $code = $LASTEXITCODE
    } catch {
        return [pscustomobject]@{ State = 'unavailable'; Code = $null
            Detail = "调用异常：$($_.Exception.Message)" }
    }
    if ($code -eq 0) { return [pscustomobject]@{ State = 'ok'; Code = 0; Detail = '' } }
    if ($code -eq 2) {
        # 工具自己的约定：2 = 我无法检查（缺依赖、读不到 PDF），不是「查过没问题」。
        return [pscustomobject]@{ State = 'unavailable'; Code = 2
            Detail = "$Name 自报无法检查（退出码 2）" }
    }
    return [pscustomobject]@{ State = 'FAIL'; Code = $code; Detail = "$Name 退出码 $code" }
}

# 显示颜色：失败红；「没检查」在发布模式下同样红（它会导致构建失败），草稿模式黄。
function Get-GateColor {
    param($Check, [switch]$ReleaseMode)
    if ($Check.State -eq 'ok')   { return 'Gray' }
    if ($Check.State -eq 'FAIL') { return 'Red' }
    if ($ReleaseMode)            { return 'Red' }
    return 'Yellow'
}

$incScript = Join-Path $PSScriptRoot 'check_includes.py'
$inc = Invoke-PyCheck -Name '重复引入检查' -Script $incScript
$incState = switch ($inc.State) {
    'ok'    { 'ok' }
    'FAIL'  { "FAIL（check_includes.py 退出码 $($inc.Code)）" }
    default { "skipped（$($inc.Detail)）" }
}

# 第八项门禁：版面重叠（--gate）。报告落到 build/ 下（gitignored），
# 不动 tools/ 里已入库的产物文件。
$ovScript = Join-Path $PSScriptRoot 'overlap_check.py'
$ovPdf    = Join-Path $build 'main.pdf'
$ovOut    = Join-Path $build 'overlap_all.txt'
$ovJson   = Join-Path $build 'overlap_gate.json'
$ovStat   = Join-Path $build 'overlap.status.txt'
$ov = Invoke-PyCheck -Name '版面重叠检查' -Script $ovScript -ScriptArgs @(
          '--gate', '--pdf', $ovPdf, '--out', $ovOut, '--json', $ovJson,
          '--status-file', $ovStat)
$ovState = switch ($ov.State) {
    'ok'    { 'ok' }
    'FAIL'  { "BLOCK（图形相撞；明细见 build/overlap_all.txt）" }
    default { "skipped（$($ov.Detail)）" }
}
$ovLine = ''
if (Test-Path $ovStat) {
    $ovLine = ([IO.File]::ReadAllText($ovStat, [Text.Encoding]::UTF8) -split "`r?`n")[0].Trim()
}

# 第九项门禁：表格来源标注（check_src.py）。纯源码静态检查，与编译无关：
# 每张表必须带 \src{}，页码对必须自洽（书内-PDF 偏移一致），引了原书表号则该表号
# 必须出现在 OCR 表索引里；台账里有表而正文没有、或正文有表而台账没有，都算未检查。
# 退出码 2 = 工具自报无法检查，按 R2-W04「未检查 ≠ 通过」处理。
# check_src.py 无 --out 参数，报告路径固定为 build/check_src.txt（见该脚本 :60/:795）。
$csScript = Join-Path $PSScriptRoot 'check_src.py'
$cs = Invoke-PyCheck -Name '表格来源标注检查' -Script $csScript
$csState = switch ($cs.State) {
    'ok'    { 'ok' }
    'FAIL'  { "FAIL（check_src.py 退出码 $($cs.Code)；明细见 build/check_src.txt）" }
    default { "skipped（$($cs.Detail)）" }
}

Write-Host "==== build ====" -ForegroundColor Cyan
Write-Host ("mode          : {0}" -f $(if ($Release) { 'release（发布验收）' } else { 'draft（草稿）' }))
Write-Host ("latexmk exit  : {0}" -f $code)
Write-Host ("pages         : {0}" -f $(if ($mm.Success) { $mm.Groups[1].Value } else { '?' }))
Write-Host ("errors        : {0}" -f $errs.Count)
Write-Host ("overfull >5pt : {0}" -f $ovf.Count)
Write-Host ("missing glyphs: {0}" -f $miss.Count) -ForegroundColor $(if ($miss.Count) { 'Red' } else { 'Gray' })
Write-Host ("undefined refs: {0}" -f $undef.Count)
Write-Host ("dup labels    : {0}" -f $duplab.Count)
$incColor = Get-GateColor $inc -ReleaseMode:$Release
$ovColor  = Get-GateColor $ov  -ReleaseMode:$Release
$csColor  = Get-GateColor $cs  -ReleaseMode:$Release
Write-Host ("dup includes  : {0}" -f $incState) -ForegroundColor $incColor
Write-Host ("overlap       : {0}" -f $ovState) -ForegroundColor $ovColor
Write-Host ("table \src    : {0}" -f $csState) -ForegroundColor $csColor
if ($ovLine) { Write-Host ("  {0}" -f $ovLine) -ForegroundColor $ovColor }
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

# 失败条件。draft 模式拦「编译不过 / 丢字 / 重复引入」；静态检查（重叠）只报告。
# release 模式额外拦「超宽 / 未定义引用 / 重复标签 / 版面重叠确认缺陷」，
# 并把「必需检查没跑成」也判失败——未检查 ≠ 通过（R2-W04）。
# 两者都拦的条件：latexmk 非零、有 '!' 错误、有缺字、有重复引入。
$fail = @()
if ($code -ne 0)        { $fail += "latexmk 退出码 $code" }
if ($errs.Count)        { $fail += "$($errs.Count) 个编译错误" }
if ($miss.Count)        { $fail += "$($miss.Count) 处缺字" }
if ($inc.State -eq 'FAIL') { $fail += "存在重复引入（见上方 check_includes.py 输出）" }
if ($cs.State -eq 'FAIL')  { $fail += "表格来源标注不合格（明细见 build/check_src.txt）" }
if ($Release) {
    if ($ovf.Count)     { $fail += "$($ovf.Count) 处 overfull >5pt" }
    if ($undef.Count)   { $fail += "$($undef.Count) 处未定义引用" }
    if ($duplab.Count)  { $fail += "$($duplab.Count) 处重复标签" }
    if ($ov.State -eq 'FAIL') {
        $fail += "版面重叠命中确认缺陷（图形相撞；明细见 build/overlap_all.txt）"
    }
    # 「没检查」不是「没问题」：发布模式下必需检查跑不成 = 失败（R2-W04）。
    if ($inc.State -eq 'unavailable') {
        $fail += "重复引入检查**未执行**（$($inc.Detail)）—— 未检查 ≠ 通过"
    }
    if ($ov.State -eq 'unavailable') {
        $fail += "版面重叠检查**未执行**（$($ov.Detail)）—— 未检查 ≠ 通过"
    }
    if ($cs.State -eq 'unavailable') {
        $fail += "表格来源标注检查**未执行**（$($cs.Detail)）—— 未检查 ≠ 通过"
    }
}
if ($fail.Count) {
    Write-Host ("FAIL: " + ($fail -join '；')) -ForegroundColor Red
    exit 1
}
Write-Host "PASS" -ForegroundColor Green
exit 0
