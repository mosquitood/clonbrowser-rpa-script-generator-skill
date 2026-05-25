### 准备工作

- Clonbrowser 登录之后，打开要使用的Profile，安装 Codex 插件 (hehggadaopoacecdllhhajmbjkdcmajg)（切记是ChatGPT支持访问的地域）。
- Codex 安装技能  [https://github.com/mosquitood/clonbrowser-rpa-script-generator-skill.git](https://github.com/mosquitood/clonbrowser-rpa-script-generator-skill.git)

```python
    python C:\Users\{你的用户名}\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
    --repo mosquitood/clonbrowser-rpa-script-generator-skill `
    --path .
```

- 下载 Clonbrowser RPA 调试工具
- clon仓库

```
git clone https://gitlab.kuajingvs.com/clonbrowser-cloud-v3/clonbrowser/rpa-editor-nextgen.git 
```

- 安装环境
  - 参照仓库 readme

- 下载 OpenAPI 服务包
- windows地址：https://kuajingvs.oss-cn-qingdao.aliyuncs.com/client/resources/open-api-win.zip
- mac地址：https://kuajingvs.oss-cn-qingdao.aliyuncs.com/client/resources/openapi-mac-m1.zip
- 内部有帮助文档 可通过帮助文档配置文件 需要KV账号下的session中 存在 mark OPEN_API
- 解压后将内部文件夹放入%appdata%/kuajingvsData/services/ 文件夹下 重启客户端 即可在 https://pre.kuajingvs.com/openapi 查看到对应的服务


### 如何使用

- 使用在会话中 @Rpa Developer：{脚本需求} 回车即可。
  - 会话过程中要求的根目录就是 你下载的调试RPA的仓库根目录   x:\xxx\rpa-editor-nextgen
  - 会话过程中要求的脚本输入目录就是 scripts\xxxx\xxxx

