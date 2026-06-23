### 准备工作

- 打开任意受支持的浏览器并安装、启用 Browser 扩展，确保 Codex 中能看到 `type: "extension"` 的已连接浏览器。
- Codex 安装当前 RPA script generator skill 仓库。

#### 安装 Clonbrowser 版本

```python
python C:\Users\{你的用户名}\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
  --repo mosquitood/clonbrowser-rpa-script-generator-skill `
  --ref master `
  --path . `
  --name clonbrowser-rpa-script-generator
```

#### 安装 KuajingVS 版本

```python
python C:\Users\{你的用户名}\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
  --repo mosquitood/clonbrowser-rpa-script-generator-skill `
  --ref kuajingvs `
  --path . `
  --name clonbrowser-rpa-script-generator
```

- 下载 RPA 调试工具和 RPA 调试仓库。

```bash
git clone https://gitlab.kuajingvs.com/clonbrowser-cloud-v3/clonbrowser/rpa-editor-nextgen.git
```

- 安装环境：参照调试仓库 readme。

#### OpenAPI 服务包

- Windows 地址：https://kuajingvs.oss-cn-qingdao.aliyuncs.com/client/resources/open-api-win.zip
- macOS 地址：https://kuajingvs.oss-cn-qingdao.aliyuncs.com/client/resources/openapi-mac-m1.zip
- 服务包内部有帮助文档。可根据帮助文档配置文件，需要 KV 账号下的 session 中存在 mark `OPEN_API`。
- 解压后将内部文件夹放入 `%appdata%/kuajingvsData/services/` 文件夹下，重启客户端，即可在 https://pre.kuajingvs.com/openapi 查看对应服务。

### 如何使用

- 在会话中使用 `@Rpa Developer：{脚本需求}`，回车即可。
- 会话过程中要求的根目录，就是你下载的调试 RPA 仓库根目录，例如 `x:\xxx\rpa-editor-nextgen`。
- 会话过程中要求的脚本输入目录，就是 `scripts\xxxx\xxxx`。
- 也可以提前设置环境变量，Codex 会优先使用会话中明确提供的路径；缺省时读取：
  - `RPA_DEBUG_ROOT`: 调试 RPA 仓库根目录。
  - `RPA_SCRIPT_INPUT_DIR`: 脚本输入目录，可以是绝对路径，也可以是相对 `RPA_DEBUG_ROOT` 的路径。
- 最终生成的 `readme.md` 会包含 `## Original Codex Skill Prompt` 章节，用来记录本次在 Codex 中手动输入给当前 skill 的完整需求原文，方便下次维护或继续生成。
