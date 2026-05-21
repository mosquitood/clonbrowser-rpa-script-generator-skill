---
name: rpa-developer
description: Develop RPA Editor NextGen automation scripts from Browser upstream exploration results and user goals. Use when the user asks to write, create, inspect, refactor, review, or debug RPA scripts, especially when converting Browser-discovered page interactions or Playwright Python steps into the project-standard RPA script structure.
---

# RPA Developer Skill

## Requirement Intake Gate

Before checking Clonbrowser, opening Browser, navigating to a page, or collecting local-debug paths, decompose the user's current request into a concrete URL-input collection requirement. Do this analysis yourself first; do not ask questions until after you have tried to form a complete requirement from the current message and project context.

Supported requirement shape for this skill:

- Input mode: URL input collection. The input is one or more explicit target URLs, a site URL to open directly, or a connector/file/table field that contains URLs. Search-keyword, prompt-only discovery, account-management, upload, posting, and non-URL workflow modes are outside the default supported mode unless the user gives enough detail to define them as a URL-driven collection script.
- Target: the website/page/app URL and the page state to reach before collection.
- Collection scope: which records to collect, such as first N visible items, every item from each input URL, one detail page per URL, or rows until no more results.
- Output fields: the exact fields to extract or produce. Examples: title, author, price, like count, comment count, URL, status, screenshot path, or writeback message.
- Input source details: fixed URL values, connector/table/file path, URL field name, row limit, filtering rule, and any per-row state needed by the script.
- Output destination: business logger by default for exploratory collection; connector, Excel, file, or page writeback only when requested or clearly implied. If writeback is requested, require destination connector/table/file and field mapping.
- Runtime and delivery: local debug root, script input directory, browser route, window settings, and any required login/account context.
- Success criteria: the observable condition that makes the script complete, such as "collect 5 records", "write all extracted fields back to the output table", or "log one result per input URL".

Continue without asking only when the requirement can be safely formed. Safe inference examples:

- A request like "open https://example.com and collect the first 5 posts' title, author, likes, comments" supplies URL, scope, and fields; ask only for missing local-debug delivery paths if they are not already provided.
- A request like "collect title and price from the URLs in this table" supplies URL-input mode and fields, but still requires the connector/table path and URL field if they are missing.

Stop before local-debug setup and browser exploration when any missing or ambiguous item would change the generated script structure, data source, output contract, browser workflow, or success criteria. Ask concise follow-up questions in one batch. Prefer questions in this order:

1. What is the URL input source: fixed URL(s), connector/table field, file, or another URL list?
2. Which fields should the script extract or produce?
3. What collection scope is required: first N items, all visible items, each input URL, pagination, or another rule?
4. Where should results go: business logs, connector/table writeback, Excel/file, or page writeback?
5. What local debug root and script input directory should receive the generated files?

If the user asks for a non-URL workflow with incomplete details, do not invent a URL-input interpretation. Ask them to either provide the URL-input source or describe the non-URL workflow fully enough to define inputs, actions, outputs, and success criteria.

## Browser Handoff Workflow

Start-of-task setup gate: before checking, opening, attaching to, or exploring any browser page, first apply the Requirement Intake Gate. After the URL-input collection requirement is complete, apply the Local Debug Generation Rule and collect both the local debug root and script input directory before browser exploration starts.

Self-contained execution rule: this skill must be executable from the current `SKILL.md`, `references/`, and `scripts/` files alone. Do not depend on Codex memory, prior chat summaries, previous successful runs, or remembered Browser backend state to decide the browser route. If the user says "do not use memory" or "不要使用记忆", that only forbids memory-derived assumptions; it does not relax any rule in this skill.

Default browser route: for this skill, every browser exploration that will become an RPA script must first run the Clonbrowser launched-browser preflight in the "Clonbrowser Launched Browser Rule" below. This is the default even when the user only says "use this local skill", "本地 skill", or asks to open a website without naming Clonbrowser. Use Codex In-app Browser, local Chrome, or any other Browser backend only when the user explicitly says to use that non-Clonbrowser browser route in the current request.

Use this workflow when the user asks for any browser task that must become an RPA script, for example: open a target site, select a category, fill fields, search, extract page data, or complete another browser workflow and convert the discovered steps into Playwright Python handoff data.

1. Before starting page exploration, check that Codex has the upstream Browser skill from `plugin://browser@openai-bundled` available. Accept the installed skill names/chips `browser:browser`, `Browser`, `@browser`, or `@浏览器`. If it is not installed or not available in the current session, stop before exploration and tell the user to install or enable `plugin://browser@openai-bundled`.
2. Use `@浏览器` / `browser:browser` first when page inspection, clicking, typing, screenshots, or element discovery is needed. Do not use generic web search, a separate ad hoc Playwright session, or another browser backend as the upstream exploration path unless the user explicitly asks for a fallback.
3. Force headed mode for every upstream Browser run. Load the Browser skill, create or claim a visible headed browser tab/window before navigation, and keep that visible browser surface as the only source of page observations. Do not complete discovery through headless Playwright, background content fetches, generic web search, HTTP requests, hidden tabs, or any browser backend that the user cannot watch. If headed/visible mode cannot be enabled and confirmed before the first navigation, stop and report that the Browser upstream is unavailable in the required mode.
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
9. Every locator, state assertion, extracted field, and interaction in the Browser handoff must be verified against real elements in the live page. Do not invent selectors, infer nonexistent buttons, or use placeholder locators from memory, documentation, prior runs, or generic site knowledge. If Browser cannot observe the element in the current page, the handoff must mark the attempt as failed or record the uncertainty in `warnings`; it must not report `status: success`.
10. Save or request the handoff in the JSON shape described by `references/browser-handoff-schema.md` when the task has more than a few steps.
11. Validate the handoff with `scripts/validate_browser_handoff.py` before generating final RPA files. This validator must pass before RPA generation starts.
12. After a valid successful handoff, automatically generate the RPA Editor NextGen standard files in the same task: `readme.md`, `script.py`, `source.py`, and `main.py`. Do not stop after printing, logging, summarizing, or reporting Browser results, and do not ask whether to generate scripts unless the user explicitly asks for exploration only.
13. Keep Browser discovery code separate from final RPA code. Do not paste raw exploratory Playwright code directly into the final script unless it matches this framework's page-object conventions.

## Clonbrowser Launched Browser Rule

For this skill's default browser route, Browser exploration must use the single already-started Clonbrowser browser. Use only the launched-browser list. Do not query the full environment list as the source of runnable browsers, and do not launch a profile automatically.

Use this endpoint:

```bash
curl -X GET "http://127.0.0.1:37073/v1/browsers/launched" -H "accept: application/json"
```

Single-browser selection rules:

1. If the launched browser list is empty, stop before exploration and tell the user to start the required Clonbrowser browser first. Then wait for the user's reply. After the user replies, continue only by checking `/v1/browsers/launched` again; "continue" never means switching to another browser path. Do not continue with Browser exploration in the same attempt, and do not use any already-connected Chrome extension backend, Codex In-app Browser, local Chrome profile, CDP endpoint, or generic Browser backend as a substitute.
2. If exactly one launched browser is returned, use that browser.
3. If multiple launched browsers are returned, stop before exploration. Do not choose by name, id, array order, newest process, extension instance, or any other heuristic. Tell the user to close or stop all extra Clonbrowser instances so exactly one launched browser remains, then rerun the task.
4. Do not close extra Clonbrowser instances automatically unless the user explicitly asks you to close them in the current turn. Closing browsers can interrupt logged-in sessions or active work.
5. Read `remote_debugging_port` from the single launched browser and treat `http://127.0.0.1:<remote_debugging_port>` as the CDP endpoint for that browser.
6. Preserve the selected launched browser `id` as safe handoff evidence. This id is not optional; generated `main.py` must use it as `BROWSER_CONFIG.id`.
7. Before Browser exploration starts, verify that the Browser upstream can actually use or attach to the single launched Clonbrowser-backed Browser extension backend. If Browser cannot see or attach to that backend, stop and report that the selected Clonbrowser instance is not available to the Browser upstream; do not fall back to the in-app browser unless the user explicitly allows it.

Browser backend selection rules:

1. For this skill's default browser route, the Browser upstream must not call `agent.browsers.get("iab")`, must not create tabs in `type: "iab"`, and must not use Codex In-app Browser for exploration.
2. Browser backend selection is allowed only after `/v1/browsers/launched` returns exactly one launched Clonbrowser browser. If the launched list is empty or has multiple items, do not inspect, reuse, or select any Browser backend; stop at the launched-list condition and wait for the user to fix the browser state.
3. After reading `/v1/browsers/launched`, refresh Browser backends with `agent.browsers.list()` and select a `type: "extension"` backend that corresponds to the single launched Clonbrowser instance.
4. Before opening the target site, prove that the selected backend is not `type: "iab"` by recording the selected Browser backend type, selected launched browser `id`, and safe metadata in the handoff evidence. Safe metadata only; do not include credentials or profile secrets.
5. If the only available controllable backend is `type: "iab"`, stop immediately and report that the fingerprint browser is not connected to Browser. Do not open the target site in the in-app browser.
6. If multiple non-iab extension backends are visible and the single launched Clonbrowser backend cannot be identified unambiguously, stop and ask the user to leave only the target Clonbrowser window running with the Browser Use extension enabled.

Privacy and logging rules:

- The Clonbrowser launched-browser response can contain accounts, passwords, proxy credentials, 2FA keys, cookies, extension metadata, and other sensitive data.
- Never print, copy into handoff JSON, copy into generated RPA files, or summarize those sensitive fields.
- When reporting launched browser state to the user, show only safe fields: `name`, `id`, `pid`, and `remote_debugging_port`.
- Do not include Clonbrowser credentials, proxy credentials, cookies, tokens, or profile metadata in `SCRIPT_VARIABLES`, `VARIABLE_VALUES`, `readme.md`, logs, or the final response.

## Forced Headed Browser Rule

Every browser-to-RPA task must begin by explicitly opening or claiming a visible headed browser tab/window through the upstream Browser surface. The upstream handoff is not valid unless the live headed page was used for navigation, state-setting, extraction, and evidence collection.

The handoff `playwright_python` example must launch headed mode explicitly when it includes browser launch code, for example `browser = p.chromium.launch(headless=False)`. Handoffs that include `headless=True`, omit headed launch mode while showing a launch call, or rely on non-visual page fetches must be treated as failed and retried, not converted into RPA files.

## Synchronous Runtime Rule

Generated RPA code must use the project's synchronous runtime style. Do not generate `async def`, `await`, async Playwright imports, async context managers, or coroutine-based helper methods in `main.py`, `script.py`, or `source.py`.

The upstream Browser handoff must provide synchronous Playwright Python examples when it includes `playwright_python`. If the Browser exploration tool internally uses asynchronous automation, translate the handoff into synchronous Playwright-style steps before generating RPA code.

Use synchronous framework calls such as `self.page.goto(...)`, `self.page.wait_for_load_state(...)`, `locator.wait_for(...)`, `self.human_click(...)`, and `self.type_text_by_random(...)`. Explicit waits are allowed and expected; fixed hard waits such as `time.sleep(...)` and `page.wait_for_timeout(...)` remain prohibited unless the framework exposes an approved randomized wait helper.

## Interaction Pacing Rule

After every page interaction that clicks, types, fills, presses, selects, checks, or navigates, generated `source.py` must call `self.random_sleep(min_seconds=..., max_seconds=...)` before continuing with the next meaningful browser action. Do not chain multiple element operations back to back without a randomized pause.

Use task-appropriate ranges:

- Lightweight UI interactions: `self.random_sleep(min_seconds=1, max_seconds=3)`
- Navigation, submit, save, apply, or dialog-confirm actions: `self.random_sleep(min_seconds=2, max_seconds=5)`
- Search or result-page transitions: `self.random_sleep(min_seconds=3, max_seconds=6)`

Explicit waits such as `self.page.wait_for_load_state(...)` and `locator.wait_for(...)` are still required when the next page state must be confirmed, but they do not replace `self.random_sleep(...)`. The delivery gate `scripts/validate_generated_rpa.py` rejects generated `source.py` files where common page interaction calls are not followed shortly by `self.random_sleep(...)`.

## Page Load Wait Rule

Any generated code path that may trigger a page load or document navigation must call `self.page.wait_for_load_state(...)` shortly after the operation. This includes `self.page.goto(...)` and clicks, presses, or selections that submit a form, start a search, save/apply settings, confirm a dialog, continue to the next step, log in, or otherwise request a new page state.

Use both mechanisms when both are relevant:

```python
self.human_click(submit_button)
self.page.wait_for_load_state("domcontentloaded")
self.random_sleep(min_seconds=2, max_seconds=5)
```

`self.random_sleep(...)` controls human pacing and anti-detection rhythm. It is not a substitute for `self.page.wait_for_load_state(...)`. `self.page.wait_for_load_state(...)` confirms the browser load lifecycle and is not a substitute for randomized pacing.

## Explicit State-Setting Rule

When the user asks to set any page state, instruct the upstream Browser skill to perform the setting flow even if the page already appears to be in the requested state. This applies generically to language, locale, delivery destination, marketplace, category, sort order, filters, search scope, account context, toggles, form defaults, and similar stateful controls.

Do not accept a pre-existing matching label, selected option, URL parameter, cookie state, or visible header as enough evidence by itself. The Browser handoff must include explicit steps that open the relevant control, choose or re-apply the requested value, submit or confirm the change when the UI provides a confirmation action, and then assert the final state. If the UI does not allow re-applying an already-selected value, the Browser handoff must record the attempted control path, the disabled or unavailable action, and the final authoritative confirmation.

For every requested state-setting goal, require at least one `steps[]` entry whose `intent` says it is re-applying that requested state. A handoff that only reports "already set" without an action attempt is incomplete and must be retried.

## Local Debug Generation Rule

After the Requirement Intake Gate has produced a complete URL-input collection requirement, and before checking or opening any browser page, require the local debug root and the script input directory. This is a pre-browser setup gate, not a post-handoff decision. Do not ask whether local debugging should be used; this skill's default delivery route is local-debug delivery into the user's script input directory.

Treat any user-provided "debug directory", "debug root", "local debug directory", "local project root", "调试目录", "调试根目录", or equivalent path for running the generated script as the local debug root unless the user clearly labels it as the script input directory.

If the user labels a path as the script input directory, generated script directory, or generated script subdirectory, treat that path as the script input directory. The script input directory is the final write location, not a parent directory for another generated folder.

After the local debug root is confirmed, require the user's script input directory before browser exploration starts. Do not invent or auto-choose a custom output directory. The generated files must be written directly into the confirmed script input directory.

The local debug root and script input directory must be locked before browser exploration starts. Do not open Browser, check Clonbrowser, navigate to the target site, or create a handoff until both the requirement and delivery paths are complete. If either path is ambiguous, stop and ask for the missing path value first.

Required local-debug delivery rules:

1. Require a local debug root directory before writing files. If the user has not provided one, stop and ask for the local debug root; do not write into the skill `outputs/` directory as a substitute.
2. Require the script input directory before browser exploration starts. If the user has not provided it, stop and ask for the script input directory; do not choose a task-derived folder or use the skill `outputs/` directory as a substitute.
3. The script input directory may be provided as an absolute path under the local debug root, or as a path relative to the local debug root. Resolve it to a full path before writing files.
4. The actual output directory must be exactly the confirmed script input directory. Write `readme.md`, `script.py`, `source.py`, `main.py`, and `browser-handoff.json` directly inside that directory. Do not create an extra task-named subdirectory under it.
5. The script input directory must be importable as Python package parts relative to the local debug root: each path segment must be a valid Python identifier. If it is not importable, stop and ask for an importable script input directory instead of silently changing it.
6. Derive `main.py`'s `source.py` import from the script input directory relative to the debug root. Split the relative path into Python package parts and append `.source`. For a script input directory `scripts\kuajingvs\amazon`, `main.py` must use `from scripts.kuajingvs.amazon.source import <PageClassName>`.
7. The local debug command must be run from the local debug root with `uv run <script_input_directory>\main.py`. Example: from `D:\project`, run `uv run .\scripts\kuajingvs\amazon\main.py`.
8. When validating local-debug output, run `python scripts/validate_generated_rpa.py <script-input-dir> --debug-root <local-debug-root>` from this skill root before running the local debug command.
9. If validation passes, run the local debug command and report the command, working directory, and result. If validation fails, fix the generated files first and do not run local debug.

If the user explicitly refuses local-debug delivery, stop and ask for a delivery location that preserves this skill's required local debug root and script input directory contract. Do not silently fall back to the skill `outputs/` directory.

## Completion Gate

A browser-to-RPA task is complete only after the final RPA files have been written and validated. Treat printed product names, extracted page data, screenshots, or a successful Browser handoff as intermediate evidence, not as the final deliverable.

After every successful Browser handoff:

1. Choose the output directory before writing files:
   - Use the Local Debug Generation Rule decision made at task start. The output directory must be exactly the confirmed script input directory and must follow the input-directory/import rules in that section.
   - Do not create or use a task-derived `outputs/` folder when local debug root or script input directory is missing. Stop and ask for the missing path instead.
   - Do not write generated RPA files into the caller's unrelated working directory, a temporary directory, or another repo's `outputs/` directory.
2. Write all four required files: `readme.md`, `script.py`, `source.py`, and `main.py`.
3. Ensure `script.py`, `source.py`, and `main.py` all contain the current task inputs and runtime configuration from the successful handoff. Do not hard-code desired result items, extracted result values, product names, titles, IDs, prices, or other page outputs as variables.
4. Run `python scripts/validate_generated_rpa.py <script-input-dir> --debug-root <local-debug-root>` from this skill root. This is the mandatory delivery gate and it must pass before the task can be reported complete. It validates required files, output location, handoff truth evidence, synchronous runtime usage, framework entrypoints, variable consistency, disallowed result variables, and Python syntax.
5. If `validate_generated_rpa.py` fails for any reason, do not deliver the script and do not report success. Fix the generated files or rerun the Browser handoff, then run the validator again.
6. Remove temporary `__pycache__` folders after validation.
7. In the final response, list the generated file paths and the `validate_generated_rpa.py` result. If no files were generated or validation did not pass, explicitly report the task as incomplete.

If a run only prints or returns extracted values after a successful handoff, continue working immediately and generate the RPA files before sending the final answer.

## Expected Browser Handoff

The Browser handoff is an intermediate artifact. It should answer: "how to find the elements and what values to fill". It should not decide the final RPA framework structure.

Each step must include `verified: true` and an `evidence` string describing the real page observation used to confirm that the element or state exists. Evidence can be a visible text snippet, role/name match, selected option state, URL/title confirmation, element count, extracted field sample, or screenshot/trace note. Generic claims such as "selector should exist" or "common Amazon selector" are not valid evidence.

Minimal shape:

```json
{
  "status": "success",
  "attempt": 1,
  "max_attempts": 3,
  "task": "Complete the requested browser workflow and collect the required output",
  "start_url": "https://example.com/",
  "playwright_python": "Synchronous Playwright Python only; no async/await.",
  "steps": [
    {
      "intent": "Open the required control",
      "action": "click",
      "locator": "page.get_by_role('button', name='...')",
      "value": null,
      "wait_for": "the next required UI state is visible",
      "verified": true,
      "evidence": "Browser observed a visible button with the requested accessible name on the live page."
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
- Every step has `verified: true` plus non-empty evidence from the live page; locator-based actions cannot use null or placeholder locators.

If validation fails because the upstream browser step did not succeed, rerun the browser step and request a fresh handoff. Do not merge failed handoff data into the final RPA script. After 3 failed attempts, report failure with the last known blocker from `warnings` or `failure_reason`.
## RPA Generation Contract

After receiving the browser handoff, generate project-standard RPA code according to the rules below. The generated RPA should preserve the browser intent while adapting implementation to `CorePageObject`, framework logging, configuration forms, variables, and local debug entrypoints.

## Input And Output Boundary

Generated variables must represent inputs, runtime configuration, or output destinations only. Examples include start URL, search keywords, requested locale, requested delivery destination, category, sort/filter choices, row limits, window settings, connector settings, and output field mappings.

Do not put desired result items or observed result values into `SCRIPT_VARIABLES`, `SCRIPT_FORMS`, `VARIABLE_VALUES`, `ARGS_SETTINGS`, or `FormateVariableValue` properties. Result values include product names, listing titles, IDs, prices, URLs, extracted text, counts, scraped records, and any other data the RPA script is supposed to discover while running.

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

When local debugging is confirmed, the `main.py` import path is not chosen independently. It must be derived from the script input directory relative to the local debug root. Convert path separators to dots and append `.source`; for example, `scripts\kuajingvs\amazon` becomes `from scripts.kuajingvs.amazon.source import <PageClassName>`. The local debug command must be run from the debug root as `uv run .\scripts\kuajingvs\amazon\main.py` for that example.

Keep `BROWSER_CONFIG.platform`, `BROWSER_CONFIG.id`, default window variables, and `timeout=30000` unless the user explicitly requests different runtime settings. Always include input/config variables in `VARIABLE_VALUES` so local developer runs do not depend on external defaults. Never include site-specific or task-specific values in the skill itself; derive them only from the current user request and the successful handoff. Never include extracted outputs in `VARIABLE_VALUES`.
For this Clonbrowser route, `BROWSER_CONFIG` is not a free choice. Always generate:

```python
BROWSER_CONFIG = BrowserConfig(
    platform="cb-global",
    id="<selected_launched_browser_id>",
)
```

`platform` must be exactly `"cb-global"`. `id` must be the `id` field from the single launched browser returned by `/v1/browsers/launched` and recorded in the successful browser handoff evidence. Do not use Browser extension instance ids, remote debugging ports, profile names, `kv`, or any remembered/default id.
## source.py Variable Standard

Generate `source.py` so runtime variables are read through `self.proxy.use(..., FormateVariableValue).value()` properties instead of declaring variable placeholders inside `ARGS_SETTINGS` or relying on class attributes being injected.

`ARGS_SETTINGS` must contain only framework execution settings:

```python
ARGS_SETTINGS = {
    "timeout": 30000,
    "retry": 1,
}
```

For every generated script variable, add a typed `@property` that reads from `FormateVariableValue`:

```python
from app.core.runtime.core.autobot.component.values import FormateVariableValue

@property
def start_url(self) -> str:
    return self.proxy.use("${start_url}", FormateVariableValue).value()
```

For boolean variables, normalize string and boolean values:

```python
@property
def confirm_required(self) -> bool:
    value = self.proxy.use("${confirm_required}", FormateVariableValue).value()
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")
```

Do not place business variables in `ARGS_SETTINGS`. Input/config variables belong in `script.py` forms, `main.py` `VARIABLE_VALUES`, and typed `@property` accessors in `source.py`. Extracted output values must not be declared as variables; they must be discovered by runtime logic and emitted through logging, connector writes, or the appropriate output channel.

## Window Size Runtime Rule

When generated scripts expose `resolution_options` and `window_size`, do not call `self.set_window_size_by_variable()` and do not call `self.set_window_size(*self.window_size)`. In this project, `window_size` may be delivered as a string such as `"1920x1080"`; unpacking that string passes one character per argument and raises `TypeError: set_window_size() takes 3 positional arguments but 10 were given`.

Generate an explicit helper that parses the string into exactly two integers before calling `self.set_window_size(width, height)`:

```python
def apply_window_size(self) -> None:
    if self.resolution_options != "preset":
        return

    width_text, height_text = str(self.window_size).lower().split("x", 1)
    self.set_window_size(int(width_text), int(height_text))
```

Call that helper from `ready()` before navigation. This rule is enforced by `scripts/validate_generated_rpa.py`.
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

     self.apply_window_size()

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

| `self.set_window_size_by_variable()` | 不要在新生成脚本中调用；当 `${window_size}` 是 `"1920x1080"` 字符串时可能被错误解包为多个字符参数 |

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





