### 准备工作

- 打开任意受支持的浏览器并安装、启用 Browser 扩展，确保 Codex 中能看到 `type: "extension"` 的已连接浏览器。
- Codex 安装当前 RPA script generator skill 仓库

```python
    python C:\Users\{你的用户名}\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
    --repo <rpa-script-generator-skill-repo> `
    --path .
```

- 下载 RPA 调试工具
- RPA 调试仓库

```
git clone <rpa-editor-nextgen-repo-url>
```

- 安装环境
  - 参照仓库 readme

### 如何使用

- 使用在会话中 @Rpa Developer：{脚本需求} 回车即可。
  - 会话过程中要求的根目录就是 你下载的调试RPA的仓库根目录   x:\xxx\rpa-editor-nextgen
  - 会话过程中要求的脚本输入目录就是 scripts\xxxx\xxxx
  - 也可以提前设置环境变量，Codex 会优先使用会话中明确提供的路径；缺省时读取：
    - `RPA_DEBUG_ROOT`: 调试 RPA 仓库根目录
    - `RPA_SCRIPT_INPUT_DIR`: 脚本输入目录，可以是绝对路径，也可以是相对 `RPA_DEBUG_ROOT` 的路径
  - 最终生成的 `readme.md` 会包含 `## Original Codex Skill Prompt` 章节，用来记录本次在 Codex 中手动输入给当前 skill 的完整需求原文，方便下次维护或继续生成。
