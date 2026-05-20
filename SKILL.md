---
name: rpa-developer
description: Develop RPA Editor NextGen automation scripts from Browser upstream exploration results and user goals. Use when the user asks to write, create, inspect, refactor, review, or debug RPA scripts, especially when converting Browser-discovered page interactions or Playwright Python steps into the project-standard RPA script structure.
---

# RPA Developer Skill

## Browser Handoff Workflow

Use this workflow when the user asks for any browser task that must become an RPA script, for example: open a target site, select a category, fill fields, search, extract page data, or complete another browser workflow and convert the discovered steps into Playwright Python handoff data.

1. Before starting page exploration, check that Codex has the upstream Browser skill from `plugin://browser@openai-bundled` available. Accept the installed skill names/chips `browser:browser`, `Browser`, `@browser`, or `@浏览器`. If it is not installed or not available in the current session, stop before exploration and tell the user to install or enable `plugin://browser@openai-bundled`.
2. Use `@浏览器` / `browser:browser` first when page inspection, clicking, typing, screenshots, or element discovery is needed. Do not use generic web search, a separate ad hoc Playwright session, or another browser backend as the upstream exploration path unless the user explicitly asks for a fallback.
3. Force headed mode for every upstream Browser run. Load the Browser skill, use the in-app/browser plugin surface, and make the browser visible before navigation by enabling the Browser visibility capability when it is available. If headed/visible mode cannot be enabled, stop and report that the Browser upstream is unavailable in the required mode.
4. Treat the Browser step as an upstream dependency with an explicit status. Continue only when the Browser handoff contains `"status": "success"`.
5. If the Browser handoff is missing, invalid, or has any status other than `success`, rerun the Browser step. Retry at most 3 total attempts.
6. If all 3 Browser attempts fail, stop immediately and report the RPA generation as failed. Do not generate final RPA files from failed or partial Browser output.
7. Ask the Browser step to produce a Playwright Python handoff, not a finished RPA script.
8. The handoff must focus only on reliable Browser-discovered facts:
   - target URL and final page state
   - selectors or locator strategies
   - fill values and click order
   - waits, assertions, and known navigation boundaries
   - screenshots or trace notes when relevant
9. Save or request the handoff in the JSON shape described by `references/browser-handoff-schema.md` when the task has more than a few steps.
10. Validate the handoff with `scripts/validate_browser_handoff.py` before generating final RPA files. This validator must pass before RPA generation starts.
11. After a valid successful handoff, automatically generate the RPA Editor NextGen standard files in the same task: `readme.md`, `script.py`, `source.py`, and `main.py`. Do not stop after printing, logging, summarizing, or reporting Browser results, and do not ask whether to generate scripts unless the user explicitly asks for exploration only.
12. Keep Browser discovery code separate from final RPA code. Do not paste raw exploratory Playwright code directly into the final script unless it matches this framework's page-object conventions.

## Explicit State-Setting Rule

When the user asks to set any page state, instruct the upstream Browser skill to perform the setting flow even if the page already appears to be in the requested state. This applies generically to language, locale, delivery destination, marketplace, category, sort order, filters, search scope, account context, toggles, form defaults, and similar stateful controls.

Do not accept a pre-existing matching label, selected option, URL parameter, cookie state, or visible header as enough evidence by itself. The Browser handoff must include explicit steps that open the relevant control, choose or re-apply the requested value, submit or confirm the change when the UI provides a confirmation action, and then assert the final state. If the UI does not allow re-applying an already-selected value, the Browser handoff must record the attempted control path, the disabled or unavailable action, and the final authoritative confirmation.

For every requested state-setting goal, require at least one `steps[]` entry whose `intent` says it is re-applying that requested state. A handoff that only reports "already set" without an action attempt is incomplete and must be retried.

## Completion Gate

A browser-to-RPA task is complete only after the final RPA files have been written and validated. Treat printed product names, extracted page data, screenshots, or a successful Browser handoff as intermediate evidence, not as the final deliverable.

After every successful Browser handoff:

1. Choose the output directory before writing files:
   - If the user gives a target script directory, write there.
   - Otherwise, create a task-derived folder under the current workspace's `outputs/` directory, using a short lowercase hyphenated script name.
2. Write all four required files: `readme.md`, `script.py`, `source.py`, and `main.py`.
3. Ensure `script.py`, `source.py`, and `main.py` all contain the current task inputs and runtime configuration from the successful handoff. Do not hard-code desired result items, extracted result values, product names, titles, IDs, prices, or other page outputs as variables.
4. Validate generated Python with `python -m py_compile` for `main.py`, `script.py`, and `source.py`; remove temporary `__pycache__` folders after validation.
5. In the final response, list the generated file paths and validation result. If no files were generated, explicitly report the task as incomplete.

If a run only prints or returns extracted values after a successful handoff, continue working immediately and generate the RPA files before sending the final answer.

## Expected Browser Handoff

The Browser handoff is an intermediate artifact. It should answer: "how to find the elements and what values to fill". It should not decide the final RPA framework structure.

Minimal shape:

```json
{
  "status": "success",
  "attempt": 1,
  "max_attempts": 3,
  "task": "Complete the requested browser workflow and collect the required output",
  "start_url": "https://example.com/",
  "playwright_python": "...",
  "steps": [
    {
      "intent": "Open the required control",
      "action": "click",
      "locator": "page.get_by_role('button', name='...')",
      "value": null,
      "wait_for": "the next required UI state is visible"
    }
  ],
  "assumptions": [],
  "warnings": []
}
```

Prefer role/text/test-id/label locators when stable. Use CSS or XPath only when semantic locators are not reliable. Record any locale, login, captcha, cookie, or geolocation blockers in `warnings` instead of hiding them.
## Upstream Success Gate

Before generating any RPA files, validate the browser handoff. The handoff is usable only when all of these are true:

- `status` is exactly `success`.
- `attempt` is between `1` and `3`.
- `max_attempts` is exactly `3`.
- `steps` is non-empty and contains enough locator/action detail to reproduce the browser task.

If validation fails because the upstream browser step did not succeed, rerun the browser step and request a fresh handoff. Do not merge failed handoff data into the final RPA script. After 3 failed attempts, report failure with the last known blocker from `warnings` or `failure_reason`.
## RPA Generation Contract

After receiving the browser handoff, generate project-standard RPA code according to the rules below. The generated RPA should preserve the browser intent while adapting implementation to `CorePageObject`, framework logging, configuration forms, variables, and local debug entrypoints.

## Input And Output Boundary

Generated variables must represent inputs, runtime configuration, or output destinations only. Examples include start URL, search keywords, requested locale, requested delivery destination, category, sort/filter choices, row limits, window settings, connector settings, and output field mappings.

Do not put desired result items or observed result values into `SCRIPT_VARIABLES`, `SCRIPT_FORMS`, `VARIABLE_VALUES`, `ARGS_SETTINGS`, or `VariableValue` properties. Result values include product names, listing titles, IDs, prices, URLs, extracted text, counts, scraped records, and any other data the RPA script is supposed to discover while running.

Use Browser handoff result values only as validation evidence and as guidance for selectors or extraction logic. The final `source.py` must reproduce the extraction at runtime and then report the discovered values through framework logging, business logging, connector output, or the task-appropriate output channel. Local `main.py` may provide input/config values needed to reproduce the run, but it must not pre-fill the expected extracted results.
## main.py Generation Standard

Generate `main.py` with the developer runner entrypoint from `app.core.developer.run`, not the older runtime developer import. The generated file must follow this shape:

```python
from app.core.developer.run import start_main_process_run_by_developer
from scripts.<business_namespace>.<script_name>.source import <PageClassName>
from app.core.developer.browser.models import BrowserConfig

BROWSER_CONFIG = BrowserConfig(
    platform="kv",
    id="1857483922118578205",
)

VARIABLE_VALUES = {
    # Include every input/config variable declared in script.py.
    # Values must come from the user's current request and the validated browser handoff.
    # Do not include desired result items or observed extracted result values here.
    # Do not hard-code examples from prior tasks or from this skill's documentation.
    "<variable_name>": "<task_value>",
    "resolution_options": "preset",
    "window_size": "1920x1080",
}

if __name__ == "__main__":
    start_main_process_run_by_developer(BROWSER_CONFIG, page_class=<PageClassName>, variable_values=VARIABLE_VALUES, timeout=30000)
```

Adapt these placeholders for each generated script:

- `<business_namespace>`: script package namespace under `scripts`, chosen from the user's current project context.
- `<script_name>`: generated script module folder, derived from the current task.
- `<PageClassName>`: page-object class from `source.py`, derived from the current task.
- `<variable_name>` and `<task_value>`: input/config variables required by the generated script, not extracted output values.

Keep `BROWSER_CONFIG.platform`, `BROWSER_CONFIG.id`, default window variables, and `timeout=30000` unless the user explicitly requests different runtime settings. Always include input/config variables in `VARIABLE_VALUES` so local developer runs do not depend on external defaults. Never include site-specific or task-specific values in the skill itself; derive them only from the current user request and the successful handoff. Never include extracted outputs in `VARIABLE_VALUES`.
## source.py Variable Standard

Generate `source.py` so runtime variables are read through `self.proxy.use(..., VariableValue).value()` properties instead of declaring variable placeholders inside `ARGS_SETTINGS` or relying on class attributes being injected.

`ARGS_SETTINGS` must contain only framework execution settings:

```python
ARGS_SETTINGS = {
    "timeout": 30000,
    "retry": 1,
}
```

For every generated script variable, add a typed `@property` that reads from `VariableValue`:

```python
from app.core.runtime.core.autobot.component.values import VariableValue

@property
def start_url(self) -> str:
    return self.proxy.use("${start_url}", VariableValue).value()
```

For boolean variables, normalize string and boolean values:

```python
@property
def confirm_required(self) -> bool:
    value = self.proxy.use("${confirm_required}", VariableValue).value()
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")
```

Do not place business variables in `ARGS_SETTINGS`. Input/config variables belong in `script.py` forms, `main.py` `VARIABLE_VALUES`, and typed `@property` accessors in `source.py`. Extracted output values must not be declared as variables; they must be discovered by runtime logic and emitted through logging, connector writes, or the appropriate output channel.
# RPA Developer Skill 指南



你是一个专业的 RPA (Robotic Process Automation) 脚本开发专家。在当前项目中开发 RPA 脚本时，必须严格遵守以下框架规范和标准结构：



## 一、 脚本目录与结构规范

每个独立的 RPA 脚本模块必须包含以下四个核心文件：

1. `readme.md` **(必不可少)**：记录脚本的功能说明、配置要求和使用注意事项。

2. `script.py`：定义对外暴露的配置表单（`SCRIPT_FORMS`）、变量（`SCRIPT_VARIABLES`）以及发布信息（`AppInfo`）。

3. `source.py`：核心业务逻辑文件。必须包含 `ARGS_SETTINGS` 并定义继承自 `CorePageObject` 的主类。

4. `main.py`：本地调试入口文件。使用 `start_main_process_run_by_developer` 来启动调试。



## 二、 脚本编写规范



### 2.1 日志规范



框架提供两套日志通道，二者用途完全不同，**不能混用**。绝对禁止使用 `print()`。



#### 2.1.1 `self.logger` —— 技术日志 / 调试日志

- **用途**：覆盖整个执行过程中的每个操作（点击、填值、跳转、定位、网络响应等），方便开发与运维通过日志定位问题。

- **粒度**：要求**细粒度、全过程覆盖**，颗粒度越细越好。

- **可见性**：主要面向开发者与脚本维护者。



**示例：**

```python

self.logger.info("正在访问小红书发布页面")

self.logger.info(f"填写标题: {_title_content}")

self.logger.info("点击发布按钮")

self.logger.error(f"Save draft failed: {_response.status} {_response.status_text}")

```



#### 2.1.2 `self.business_logger` —— 业务日志

- **用途**：面向最终业务使用者（运营 / 产品方）展示的高层次执行进度与结论，用于在 RPA 平台前台呈现"这次任务做了什么、结果如何"。

- **粒度**：**只标注关键信息**，不要把每一步细节都写进去。下列场景才使用 `business_logger`：

   - 任务开始 / 关键阶段切换（如"开始访问小红书发布页面"、"开始处理飞书记录，共计 N 条"）

   - 关键数据节点（如"填充封面文字"、"选择卡片样式: xxx"、"成功提取标题/点赞/评论"）

   - 单条记录处理结果汇总（成功 / 失败 / 跳过的原因）

   - 任务结束总结（如"所有飞书记录检查回填完毕"）

- **`business_logger.error` 的特殊语义（重要）**：业务日志中只要出现 `error` 级别，**整个脚本的执行结果会被框架判定为失败**。因此：

   - 仅在确实需要将本次任务标记为"失败"时才调用 `business_logger.error(...)`。

   - 对于"单条记录失败、但整体任务可继续"的场景，请使用 `business_logger.warning(...)` 或仅写入 `self.logger.error(...)`，避免把整个任务误标失败。

   - 不要为了"记录详细错误堆栈"而调用 `business_logger.error`，技术细节请走 `self.logger.error(...)`。



**正确示例：**

```python

self.business_logger.info("开始访问小红书创作者中心检查发布状态")

self.business_logger.info(f"开始处理飞书记录，共计 {len(posts)} 条任务待采集。")

self.business_logger.info(f"成功提取 -> 标题: [{_title}], 点赞: {_likes}, 评论: {_comments}")

self.business_logger.info("所有飞书记录检查回填完毕。")



self.business_logger.warning(f"视频文件不存在, 跳过发布: {video_path}")

```



**错误示例（会把任务误判为失败）：**

```python

for post in posts:

     try:

         self._handle_post(post)

     except Exception as e:

         self.business_logger.error(f"单条记录失败: {e}")

```

**正确写法：** 单条失败用 `warning` 或写入技术日志，整体任务流程仍可继续；只有触发"终止整个任务"的致命错误才使用 `business_logger.error` 或直接 `raise Exception`。

```python

for post in posts:

     try:

         self._handle_post(post)

     except Exception as e:

         self.logger.error(f"单条记录失败: {e}")

         post.post_content[self.reason_field] = f"发布异常: {e}"

```



#### 2.1.3 业务日志与技术日志的搭配

关键节点常见的写法是**两条都写**：`business_logger` 给业务方看结论，`logger` 给开发者看细节。

```python

self.business_logger.info(f"Filling covertext: {_cover_text[:100]}....")

self.logger.info(f"Filling covertext: {_cover_text[:100]}....")

```



### 2.2 类型标注

必须使用类型标注，包括函数参数和返回值。

**示例：**

```python

def is_login(self) -> bool:

     """判断是否登录"""

     ...



def fill_title(self, post: PostModel) -> bool:

     """填写标题"""

     ...

```



### 2.3 避免多层嵌套

代码嵌套层数建议不超过 3 层，超过 3 层应考虑重构或拆分函数。优先使用提前返回（Guard Clauses）。

**不推荐：**

```python

if condition1:

     if condition2:

         if condition3:

             do_something()

```

**推荐：**

```python

def check_conditions():

     if not condition1:

         return ...

     if not condition2:

         return ...

     if not condition3:

         return ...

     do_something()

```



### 2.4 函数长度控制

函数长度尽可能控制在 40 行以内，按动作进行函数封装。

**拆分原则：**

- 每个函数只完成一个动作

- 独立的功能模块应拆分为单独函数

**示例：**

```python

def _clear_content(self) -> bool:

     """清空标题和正文，避免复用页面时残留旧内容"""

     ...



def _fill_title(self, post: PostModel) -> bool:

     """填写标题"""

     ...



def _upload_cover(self, post: PostModel) -> bool:

     """上传封面图片"""

     ...

```



### 2.5 异常处理

错误之后脚本结束的动作直接使用 `raise Exception` 抛出异常即可。

**示例：**

```python

if not _content_content:

     raise Exception("文章内容为空")



if not _response.ok:

     raise Exception(f"Save draft failed: {_response.status} {_response.status_text}")

```



### 2.6 异常优先原则 (Fail-Fast)

先判定异常而不是判定正确，尽早终止错误流程 (Fail-Fast)。



**场景 1：逻辑判定**

**不推荐：**

```python

if _content_text:

     do_something()

else:

     raise Exception("文章内容为空")

```

**推荐：**

```python

if not _content_text:

     raise Exception("文章内容为空")

do_something()

```



**场景 2：数据源表头字段强制校验 (强约束)**

对于依赖连接器表头的脚本，必须在主流程入口 `start()` 阶段（**且在调用浏览器 `ready()` 之前**）进行 Fail-Fast 校验。防止用户配错字段导致白白启动浏览器：

```python

def start(self) -> bool:

     connector = self._get_input_connector()

     # 1. 优先校验表头

     connector.ensure_fields_exist([self.input_browser_field, self.input_content_field])

     

     # 2. 校验通过后，再启动浏览器和执行核心逻辑

     if not self.ready(): 

         return False

     ...

```



### 2.7 元素操作标准

在定位并操作元素时，**应直接进行操作（如 `click()`, `fill()`），不建议使用 `locator.count() > 0` 来提前判断元素是否存在**。Playwright 的操作自带等待和超时机制（自动等待元素可见可交互），如果超时未找到元素会自动抛出异常。



**场景 1：必选元素的操作**

直接操作（明确指定元素，例如使用 `.first`）。如果失败抛出异常，正好可以阻断流程。

**不推荐：**

```python

if _content_locator.count() > 0:

     _content_locator.first.click()

else:

     raise Exception("内容未找到")

```

**推荐：**

```python

# 如果找不到元素，click 动作会在超时后自动抛出 TimeoutError，符合预期

_content_locator.first.click(timeout=5000)

```



**场景 2：可选元素的非阻断处理**

如果不希望因某个可选元素（如促销弹窗、Cookie确认框）找不到而中断脚本，应直接操作并捕获异常，而不是用 `count()` 判断。

**推荐：**

```python

try:

     # 可选操作（如关闭促销弹窗）

     close_button.first.click(timeout=3000)

except Exception as e:

     self.logger.info("未出现促销弹窗，跳过")

```



### 2.8 生命周期与窗口大小设置 (强制准则)

窗口大小设置是每个脚本必须包含的准则，必须添加。另外，`ready()`（负责初始化窗口和页面登录等）应当只在 `start()` 刚开始阶段执行**一次**，严禁将其放入单条记录的处理循环中重复调用。



**`script.py` 表单配置：**

```python

ResolutionOptionsForm(name="resolution_options", required=True, options=[

     {"label": "Original", "value": "original"},

     {"label": "Preset", "value": "preset"},

     {"label": "Custom", "value": "custom"},

], CN="窗口选项", EN="Window Options",

    help_cn="浏览器窗口大小设置：Original-原尺寸，Preset-预设，Custom-自定义",

    group="Window \& Resolution"),



WindowForm(name="window_size", required=True, CN="窗口大小", EN="Window Size",

            help_cn="进行浏览操作之前，会将浏览器窗口设置成该值的大小。",

            group="Window \& Resolution"),

```

**`source.py` 中使用：**

```python

def ready(self) -> bool:

     self.set_window_size_by_variable()  # 必须调用

     self.page.goto(self.start_url)

     ...

```



### 2.9 表单分组规范 (`group`)



`script.py` 中 `SCRIPT_FORMS` 列表里的每一个表单项，都必须通过 `group` 属性按业务意义分组。前端会根据 `group` 把同组的表单聚合成一个折叠面板，**不分组会导致大量参数堆在一起、用户体验极差**。



**分组原则：**

1. **按业务领域分组**，而不是按表单类型分组。

2. **同名 `group` 的表单会被聚合**，因此组名要稳定、可读，建议使用英文，前后保持一致。

3. **窗口与分辨率类表单**统一放在 `Window \& Resolution` 组，作为约定。

4. **涉及输入 / 输出数据的表单**应分别归到 "Input xxx" 和 "Output xxx" 组（详见 2.10）。

5. 同一个组内的表单展示顺序遵循它们在 `SCRIPT_FORMS` 中的声明顺序，**因此声明时也要按"组"集中编排**，不要把同组表单分散到列表的不同位置。



**示例（节选自 `scripts/connector_demo/script.py`）：**

```python

SCRIPT_FORMS = [

     # ===== 输入连接器组 =====

     ConnectorForm(

         name="input_connector", connector_type=["feishu", "excel"],

         CN="输入连接器", EN="Input Connector",

         help_cn="请选择输入数据使用的连接器（支持飞书、Excel）",

         io_direction="input",

     ),

     InputForm(

         name="input_app_token", required=True,

         CN="输入多维表格 Token", EN="Input App Token",

         help_cn="输入数据所在飞书多维表格的 App Token",

         group="Input Feishu Config",

         io_direction="input",

     ),

     InputForm(

         name="input_table_id", required=True,

         CN="输入数据表 ID", EN="Input Table ID",

         group="Input Feishu Config",

         io_direction="input",

     ),

     InputForm(

         name="input_url_field", required=True,

         CN="笔记链接字段", EN="Note URL Field",

         group="Input Field Mapping",

         io_direction="input",

     ),



     # ===== 输出连接器组 =====

     ConnectorForm(

         name="output_connector", connector_type=["feishu", "excel"],

         CN="输出连接器", EN="Output Connector",

         io_direction="output",

     ),

     InputForm(

         name="output_app_token", required=True,

         CN="输出多维表格 Token", EN="Output App Token",

         group="Output Feishu Config",

         io_direction="output",

     ),

     InputForm(

         name="title_field", required=True,

         CN="标题回填字段", EN="Title Backfill Field",

         group="Output Field Mapping",

         io_direction="output",

     ),



     # ===== 窗口与分辨率 =====

     ResolutionOptionsForm(name="resolution_options", required=True, options=[...],

         CN="窗口选项", EN="Window Options",

         group="Window \& Resolution"),

     WindowForm(name="window_size", required=True,

         CN="窗口大小", EN="Window Size",

         group="Window \& Resolution"),

]

```



**常用分组命名建议：**

- `Window \& Resolution`：窗口大小、分辨率相关

- `Input Feishu Config` / `Output Feishu Config`：飞书表格配置

- `Input Field Mapping` / `Output Field Mapping`：飞书 / Excel 字段映射

- `Search Settings`：搜索关键词、文本输入模式等

- `Data Configuration`：数据源（Excel、目录等）

- `Publish Options`：发布相关选项（可见度、原创、话题等）



### 2.10 参数方向规范 (`io_direction`)



`io_direction` 用于声明一个表单参数代表的数据是**流入**脚本还是**流出**脚本，前端会据此渲染不同的标识，连接器（Connector）也会根据该字段做权限与读写校验。**该字段必须显式声明，不要省略**。



**取值与含义：**



| 取值 | 含义 | 典型用途 |

| --- | --- | --- |

| `"input"` | 输入参数，**数据来源** | 读取的飞书表 / 数据源 Excel / 视频目录 / 输入字段映射 / 输入连接器 |

| `"output"` | 输出参数，**数据去向** | 回填飞书表 / 输出 Excel / 已发布目录 / 输出字段映射 / 输出连接器 |



**判断规则（重要）：**

- 当一个表单参数**用于读取数据**（脚本会从它指向的位置取数据）→ `io_direction="input"`。

- 当一个表单参数**用于写出数据**（脚本会把结果写入它指向的位置）→ `io_direction="output"`。

- 当同一份数据同时存在读写两端（例如读源表、写回另一张表）时，**输入与输出的连接器、Token、字段必须各自定义两套**，分别打上 `input` / `output`，不要复用同一个表单项。

- **窗口大小、文本输入模式、搜索关键词等纯运行时配置**与数据来源/去向无关，可以不写 `io_direction`（也不需要按 input/output 分组）。



**示例：**

```python

ConnectorForm(

     name="input_connector",

     connector_type=["feishu", "excel"],

     CN="输入连接器",

     EN="Input Connector",

     help_cn="请选择输入数据使用的连接器",

     io_direction="input",

),

InputForm(

     name="input_url_field",

     required=True,

     CN="笔记链接字段",

     EN="Note URL Field",

     help_cn="提供小红书笔记链接进行采集的字段（输入）",

     group="Input Field Mapping",

     io_direction="input",

),



ConnectorForm(

     name="output_connector",

     connector_type=["feishu", "excel"],

     CN="输出连接器",

     EN="Output Connector",

     help_cn="请选择输出数据使用的连接器",

     io_direction="output",

),

InputForm(

     name="title_field",

     required=True,

     CN="标题回填字段",

     EN="Title Backfill Field",

     help_cn="用来将采集的笔记标题回写至飞书的字段（输出）",

     group="Output Field Mapping",

     io_direction="output",

),

```



**`group` 与 `io_direction` 的协作约定：**

- 凡是带 `io_direction` 的表单，组名前缀必须与方向一致：`io_direction="input"` 的归入 `Input xxx`，`io_direction="output"` 的归入 `Output xxx`，避免出现"输入字段被归到输出组"这种逻辑错误。



## 三、 框架内置工具与反检测准则



> **强约束**：编写脚本时**优先复用 `app/` 目录下已经封装好的方法**，禁止直接使用 Playwright 原生 `locator.click()` / `locator.fill()` / `time.sleep()` 等"裸操作"——这些动作没有任何反检测处理，极易触发风控。下面列出常用模块、API 与对应的反检测意图，开发新脚本时按此清单对号入座。



### 3.1 主类继承体系



主类必须继承自下列基类之一（对应 `app/core/runtime/`）：



| 基类 | 文件 | 适用场景 |

| --- | --- | --- |

| `CorePageObject` | `app/core/runtime/base/page.py` | 通用浏览器自动化脚本 |

| `FeishuPostsPageObject` | `app/core/runtime/feishu/feishu_base_post.py` | 基于飞书多维表格的发帖 / 检测脚本（已封装 `_get_posts`、`save_post_result`、`download_image` 等） |

| `ExcelDataMixin` | `app/core/runtime/base/base.py` | 需要读写 Excel 的脚本，**与上面两个基类组合使用** |



**示例：**

```python

class PostXiaoHongShu(FeishuPostsPageObject):

     """继承 FeishuPostsPageObject，自动获得多维表格读写能力"""

     ...



class CollectByExcel(CorePageObject, ExcelDataMixin):

     """组合 Excel 数据处理能力"""

     ...

```



### 3.2 反机器人检测核心工具（`app/core/runtime/base/page.py`）



`CorePageObject` 已经封装了一整套**模拟真实用户**的交互方法。**所有页面交互必须优先使用下列方法，而不是 Playwright 原生 API**。



#### 3.2.1 文本输入（替代 `locator.fill()` / `locator.type()`）



| 方法 | 反检测要点 | 何时使用 |

| --- | --- | --- |

| `self.type_text_by_random(locator, text)` | 根据 `${text_input_mode}` 变量自动选择"直接 / 模拟人类 / 剪贴板 / 随机"四种输入方式，是默认推荐方式 | 绝大多数文本输入 |

| `self.human_type_text(locator, text)` | 逐字输入 + 随机延迟 + 随机误输+回退修正 | 标题、正文、搜索关键词等需要"看起来真人写"的字段 |

| `self.paste_text(locator, text)` | 通过 `fill` 一次性写入，配合剪贴板模式 | 长文本、特殊字符、富文本编辑器（小红书/CSDN 文本框） |

| `self.direct_type_text(locator, text)` | `fill()` + `wait_for_timeout(500)` | 非敏感字段（如内部表单字段名） |



**正确用法（节选自 `xiaohongshu/post/source.py`）：**

```python

self.type_text_by_random(

     self.page.locator('input[class="d-text"]').first, _title_content

)



_content_locator = self.page.locator('div[role="textbox"]').first

_content_locator.fill("")

self.paste_text(_content_locator, _content_text)

```



#### 3.2.2 鼠标点击（替代 `locator.click()`）



| 方法 | 反检测要点 |

| --- | --- |

| `self.human_click(locator)` | 自动滚动到可见区→在元素 bounding box 的 20%\~80% 范围内随机偏移→鼠标多帧移动→停顿后点击。**默认点击都用这个** |

| `random_click(locator)`（来自 `app.core.runtime.elements`） | 在元素中心 30%\~70% 范围内随机点击坐标，作为 `human_click` 的轻量替代 |

| `simulate_mouse_click(page, locator)`（来自 `app.core.runtime.elements`） | 鼠标先 move 后 click，适用于一些必须先 hover 才响应的元素 |



**正确用法：**

```python

self.human_click(

     self.page.locator('button[type="button"]').get_by_text("发布", exact=True).first

)

```



#### 3.2.3 等待与节奏（替代 `time.sleep()`）



| 方法 | 反检测要点 |

| --- | --- |

| `self.random_sleep(min_seconds=1, max_seconds=3)` | 在区间内取随机 float 秒，**禁止使用 `time.sleep` 或 `page.wait_for_timeout(固定值)`** |

| `self.page.wait_for_load_state()` | 用于跳转后等页面加载完成 |

| `self.page.wait_for_selector(...)` / `locator.wait_for(...)` | 显式等待元素出现，避免硬等待 |



**正确用法：**

```python

self.human_click(_some_button)

self.random_sleep(min_seconds=2, max_seconds=4)

self.page.wait_for_load_state()

```



#### 3.2.4 滚动（替代 `page.mouse.wheel` 单次直滚）



| 方法 | 反检测要点 |

| --- | --- |

| `self.human_scroll()` | 多轮平滑分步滚动 + 偶尔回拉 + 随机停顿，模拟真人翻页 |

| `smooth_scroll(page, distance, duration, scroll_locator=None)`（`elements.py`） | 标准缓入缓出曲线，可针对**指定容器**滚动（用于无限下拉列表如小红书笔记列表） |

| `is_scroll_ending(page, scroll_locator)`（`elements.py`） | 判断滚动是否抵达底部 |

| `element_in_viewport(page, locator)`（`elements.py`） | 判断元素是否进入视口 |



**正确用法（节选自 `xiaohongshu/check_post/source.py`）：**

```python

from app.core.runtime.elements import smooth_scroll

smooth_scroll(

     self.page,

     distance=5000,

     duration=1,

     scroll_locator=self.page.locator("div.content").first,

)

```



#### 3.2.5 元素定位



| 方法 | 用途 |

| --- | --- |

| `self.get_available_locator(selectors)` | 接收一个 selector 列表，返回**第一个 count > 0 的定位器**，用于多版本页面兼容（参考 `connector_demo/source.py` 的标题/正文多 selector 兜底） |



**示例：**

```python

_title_locators = ["#detail-title", "h1.title", "div.title"]

_locator = self.get_available_locator(_title_locators)

if not _locator:

     raise Exception("未能定位到标题元素")

```



#### 3.2.6 文件上传（替代 `locator.set_input_files`）



| 方法 | 反检测要点 |

| --- | --- |

| `self.upload_file_by_cdp(selector, file_path)` | 通过 CDP 协议直接给隐藏的 `<input type=file>` 写入文件，规避部分站点对 `set_input_files` 的拦截 |



#### 3.2.7 窗口与截图



| 方法 | 用途 |

| --- | --- |

| `self.set_window_size_by_variable()` | **每个脚本 `ready()` 必须调用一次**，按 `${window_size}` / `${resolution_options}` 变量设置窗口（见 2.7） |

| `self.set_window_size(width, height)` | 直接通过 CDP 设置窗口大小 |

| `self.task_screenshot()` | 自动按 `${rpa_space}/screenshots/${schedule_id}/{batch}/{task_id}.png` 路径截图 |

| `self.screenshot(path)` | 通过 CDP 截图到指定路径 |

| `self.save_html_content(path)` / `self.save_html_and_screenshot()` | 异常调试时保存现场（HTML + 截图） |

| `self.show_dialog(flag, message)` | 在页面上插入彩色提示框（`info`/`success`/`warning`/`error`） |



### 3.3 `BaseObject` 提供的常用属性（`app/core/runtime/base/base.py`）



继承链中已经定义好的属性，**直接 `self.xxx` 用，不要自己重新去 `proxy.use(...)` 拼装**：



| 属性 | 含义 |

| --- | --- |

| `self.logger` | 技术日志（见 2.1.1） |

| `self.business_logger` | 业务日志（见 2.1.2） |

| `self.proxy` | `ValueProxy`，用于读取 `${var}` |

| `self.profile_name` | 当前浏览器档案名（用于过滤飞书行） |

| `self.task_id` / `self.batch_id` | 任务 / 批次 ID |

| `self.today` | 当前日期 |

| `self.task_token` | 任务 token，调连接器需要 |

| `self.rpa_service_endpoint` | RPA 服务端地址，调连接器需要 |

| `self.thread_lock` | 共享剪贴板的互斥锁，处理 Excel / 剪贴板时使用 |

| `self.window_size` / `self.resolution_options` | 已解析好的窗口大小与分辨率选项 |



**反例（不要这么写）：**

```python

_profile = self.proxy.use("${profile.name}", FormateVariableValue).value()

```



**正例：**

```python

_profile = self.profile_name

```



### 3.4 统一连接器架构 (Connector Architecture)



涉及读写外部数据源（如飞书表格、Excel）时，**禁止硬编码特定平台的基类（如 `FeishuConnector` 或 `FeishuBase`）**，也**禁止自己手写 `requests.post(...)` 调开放接口**。必须使用统一的多态连接器接口：



| 模块 / 接口 | 用途 |

| --- | --- |

| `ConnectorFactory(...).get_connector(id)` | 核心入口：传入连接器 ID，自动识别并实例化对应的 `FeishuDataConnector` 或 `ExcelDataConnector`。|

| `connector.get_all_records()` | 一次性获取全量数据，替代以前手写的 `while has_more:` 分页拉取逻辑。|

| `connector.get_field_text_value(field)` | **核心抽象**：抹平飞书富文本字典与 Excel 字符串的差异，**完全替代旧版的 `FeishuBase.auto_get_field_text_value`**。|

| `connector.ensure_fields_exist(fields)` | 表头 Fail-Fast 校验：检查所需字段是否存在，缺失直接抛出异常终止。|

| `add_record`, `update_record`, `delete_record` | 统一的增删改 API。 |



**规范示例：**

```python

def _get_input_connector(self) -> BaseDataConnector:

     return ConnectorFactory(

         self.rpa_service_endpoint, self.task_token, self.logger

     ).get_connector(self.input_connector)



# 读取字段文本值

_value = connector.get_field_text_value(fields.get(self.input_browser_field))

```



### 3.5 反机器人检测准则速查



| 场景 | 错误做法 | 正确做法 |

| --- | --- | --- |

| 点击按钮 | `locator.click()` | `self.human_click(locator)` |

| 输入文本 | `locator.fill(text)` 或 `locator.type(text)` | `self.type_text_by_random(locator, text)` 或 `self.human_type_text` / `self.paste_text` |

| 等待 | `time.sleep(2)` 或 `page.wait_for_timeout(2000)` | `self.random_sleep(2, 4)` |

| 滚动加载 | `page.mouse.wheel(0, 5000)` | `smooth_scroll(self.page, 5000, 1, scroll_locator=...)` 或 `self.human_scroll()` |

| 多版本 selector 兜底 | 多个 `if/elif locator.count() > 0` | `self.get_available_locator([...])` |

| 文件上传 | `locator.set_input_files(path)` | `self.upload_file_by_cdp(selector, path)` |

| 读写外部数据 | 手写 `requests.post` | 统一 `ConnectorFactory` 与 `BaseDataConnector` |

| 调试输出 | `print(...)` | `self.logger.info(...)` |

| 任务结果上报 | 任意 `business_logger.error` | 仅在确实判定整体失败时才用（见 2.1.2） |



### 3.6 节奏组合（重要）



每一个**关键交互**（点击/输入/跳转）后都应当伴随一次 `random_sleep`，**不要把多次操作连成一气**。这是反检测的关键经验：



```python

self.human_click(_some_button)

self.random_sleep()                      # 节奏停顿



self.type_text_by_random(_input, text)

self.random_sleep(min_seconds=2, max_seconds=4)



self.page.wait_for_load_state()

self.human_click(_next_button)

self.random_sleep(min_seconds=3, max_seconds=5)

```



## 四、 数据处理与依赖规范

1. **Excel 数据处理**：处理 Excel 数据时，优先让主类继承 `ExcelDataMixin`，使用 `read_excel` / `write_excel` / `clear_and_write_excel` / `clear_excel` / `remove_sheet` 等已封装方法（见 `app/core/runtime/base/base.py`）。**禁止直接 `import openpyxl` 重复造轮子**。

2. **数据模型定义**：当涉及数据模型时，优先使用 `dataclasses` 进行结构化定义。涉及飞书发帖 / 采集场景时直接复用 `PostModel`（`app/core/runtime/feishu/feishu_base_post.py`）。

3. **HTTP 请求**：与第三方接口交互时，调用现有 `app/core/runtime/utils/request.py` 中的工具或者继续使用 `requests`，但**不要在脚本里硬编码飞书开放接口**——飞书走 `FeishuBase`。

4. **导入新依赖前**：先在 `app/` 下检索是否已经存在同类工具，避免重复封装。





