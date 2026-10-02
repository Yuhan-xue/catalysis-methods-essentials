# 凭据轮换与历史清理记录（2026-10-02）

对应遗留项：`reviews/2026-09-30-round2/TODO.md` 的 **R2-W01**（凭据处理）。
本文件不复制任何口令值。

## 1 起因与发现

- R2-W01 遗留：`HANDOFF.md` 的认证行与发布示例曾在历史提交中出现明文账户口令。
- 2026-10-02 复核：两处旧口令**仍可登录**（`/api/v1/user` 均返回 200），未失效。
- 本机残留：`~/.netrc`、两个教材仓库的 `.git/config` 远端 URL、若干临时克隆。

## 2 轮换（已完成）

| 账户 | 角色 | 旧值 | 新值存放 |
|---|---|---|---|
| `deepseek` | 本机工具账号（git/curl 用） | 已失效（401） | `~/.netrc`（icacls 去继承，仅当前用户） |
| `yuhanxue` | 主账号（Forgejo 管理员） | 已失效（401） | `C:\Users\53150\.secrets\gitea-credentials-2026-10-02.txt`（受限目录，icacls 仅当前用户） |

验证：轮换后旧口令 API 返回 **401**，新口令返回 **200**；`git ls-remote` 正常。

## 3 历史清理（已完成：本地 + 远端）

- 方法：镜像克隆上 `git filter-repo --replace-text`，替换历史中的 7 处 `用户:口令` 组合；
  未对常见单词做裸替换（避免误伤作者名/包名）；无 base64 形式、无提交信息泄漏。
- 范围与结果：59 个提交、12 个 tag；**27 个提交**哈希变化。
  - `main`：`f94789c` → **`00ef814`**；`v0.6.0-pre`…`v0.6.5-pre` 六个 tag 强推更新；
    `v0.1.0-pre`…`v0.5.0-pre` 未受影响（泄漏出现于 v0.6.0 之后）。
  - 12 个 release 的 `target_commitish` 与正文里的旧哈希已通过 API 更新为清理后提交；附件未动。
  - 本地两个工作树同步到新历史；`git reflog expire --expire=now --all` + `git gc --prune=now`。
- 映射表：[commit-map.txt](commit-map.txt)（old→new；用于解析 2026-10-02 以前文档中的旧哈希）。
- 替换后的占位词为 `ROTATED-2026-10-02`（共 7 处）。

## 4 验证证据

| 项 | 结果 |
|---|---|
| 旧口令登录 | 两账户均 **401** |
| 新口令登录 | 两账户均 **200**；deepseek 的 `git ls-remote` 正常 |
| 重写后对象库扫描 | 旧口令串 **0** 处；替换标记 7 处；HEAD 树哈希不变（`39588d39…`） |
| 远端克隆结构扫描 | `://user:pass@` 0 处、netrc 口令行 0 处；`curl … -u` 的 2 处命中经复核为**替换占位词本身**（`deepseek:ROTATED-2026-10-02`），不是凭据 |
| 发布附件 | `v0.6.5-pre` 下载 HTTP 200，SHA-256 仍为 `d0736a5c…a6e9d` |
| 页面 | tag 页、新提交页、releases 页均 200；release 页指向新提交 `5c1f080` |
| 本机残留 | 6 个 `.git/config` 的嵌入凭据 URL 已去凭据（改用 `~/.netrc`）；`.bak-creds-2026-10-02` 备份已删 |

## 5 残余风险（未闭，需管理员/后续动作）

1. **服务端旧对象**：Forgejo 的 `git_gc_repos` 任务是 `git gc --auto`，不会立即清理刚不可达的旧提交；
   实测旧提交的 raw 文件在服务端**仍可读**（私有仓库，需登录且知道旧 SHA）。
   彻底清理需管理员在服务器仓库目录执行 `git gc --prune=now`（以 forgejo/git 用户运行），
   或等待其自动 prune 窗口（默认 `gc.pruneExpire` ≥ 2 周）。
2. **其他克隆**：本机 `Documents/Codex/2026-09-28/q/work/catalysis-review`、
   `Documents/deepseek-harness/default-workspace` 等旧克隆仍保留清理前历史；
   需 `git fetch --force` + `git reset --hard origin/main`，或重新克隆。
3. **仓库外备份**：`C:\Users\53150\Documents\git\chemical-preclean-2026-10-02.bundle`
   含清理前历史（其中旧口令已失效）；确认无需回滚后可删除。
4. **终端历史**：PowerShell 历史里可能有旧命令；旧口令已失效，未逐条清除。
5. 外部文档如写死 2026-10-02 之前的提交哈希，需按 `commit-map.txt` 换算。

## 6 复跑/复核命令（不涉及口令值）

```powershell
# 旧/新口令有效性（401/200）——用受限文件与 ~/.netrc 读取，勿把口令写进命令行历史
python - <<'PY'
# 见仓库历史中 build/_cred_test.py 的同型脚本；本记录不粘贴口令
PY
# 本地对象库扫描（0 命中断言）
python build/_cred_scan.py        # 该脚本按需重写：扫描 cat-file --batch-all-objects 的 blob
# 远端强推后的引用核对
git ls-remote origin | grep -E 'refs/(heads/main|tags/v0\.6\.5-pre)'
# 发布附件回验
curl.exe -sL --netrc-file "$HOME\.netrc" "http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/releases/download/v0.6.5-pre/catalysis-methods-essentials-v0.6.5-pre.pdf" -o build\_dl.pdf
(Get-FileHash build\_dl.pdf -Algorithm SHA256).Hash   # 期望 D0736A5C…A6E9D
```
