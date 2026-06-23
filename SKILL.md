---
name: rpa-developer
description: Develop RPA Editor NextGen automation scripts from Browser upstream exploration results and user goals. Use when the user asks to write, create, inspect, refactor, review, or debug RPA scripts, especially when converting Browser-discovered page interactions or Playwright Python steps into the project-standard RPA script structure.
---

# RPA Developer Skill

## Requirement Intake Gate

Before discovering a Browser backend, opening Browser, navigating to a page, or collecting local-debug paths, decompose the user's current request into a concrete URL-input collection requirement. Do this analysis yourself first; do not ask questions until after you have tried to form a complete requirement from the current message and project context.

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

Default browser route: for this skill, every browser exploration that will become an RPA script must use the upstream Browser skill from `plugin://browser@openai-bundled` and a connected `type: "extension"` backend. The extension-connected browser may come from KV/ClonBrowser, Chrome, or another supported browser; do not require a specific browser vendor or profile manager. Do not replace Browser with Codex In-app Browser, raw CDP, Playwright `connect_over_cdp`, remote debugging port automation, HTTP fetching, or any other non-extension route.

Browser discovery rule: the user is not required to explicitly mention `@浏览器`, `@browser`, or `plugin://browser@openai-bundled` in each task. This skill must discover Browser availability from the current Codex skills/plugins context. Treat Browser as available when the current session lists `browser:browser`, `Browser`, `@browser`, `@浏览器`, or the Browser plugin. Do not claim Browser is unavailable just because the user did not mention it in the prompt.

Use this workflow when the user asks for any browser task that must become an RPA script, for example: open a target site, select a category, fill fields, search, extract page data, or complete another browser workflow and convert the discovered steps into Playwright Python handoff data.

1. Before starting page exploration, check the current Codex skills/plugins context for the upstream Browser skill from `plugin://browser@openai-bundled`. Accept the installed skill names/chips `browser:browser`, `Browser`, `@browser`, `@浏览器`, or the Browser plugin entry. If it is not installed, enabled, or listed in the current session, stop before exploration and tell the user to install or enable `plugin://browser@openai-bundled`. Do not require the user to mention Browser explicitly in the task prompt, and do not continue through raw CDP or any substitute browser route.
2. Use `@浏览器` / `browser:browser` first when page inspection, clicking, typing, screenshots, or element discovery is needed. Do not use generic web search, a separate ad hoc Playwright session, raw CDP, `remote_debugging_port`, Playwright `connect_over_cdp`, or another browser backend as the upstream exploration path.
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

## Extension Browser Rule

For this skill's default browser route, Browser exploration may use any browser that is connected through a Browser extension backend. Do not require KV, ClonBrowser, a fingerprint browser, a particular executable, or a particular profile manager.

Browser backend selection rules:

1. Refresh available Browser backends with `agent.browsers.list()` before opening the target site.
2. Select a backend whose type is exactly `extension`. Do not call `agent.browsers.get("iab")`, create tabs in `type: "iab"`, or use Codex In-app Browser for exploration.
3. If exactly one extension backend is available, select it.
4. If no extension backend is available, stop and ask the user to open the intended browser, install or enable the Browser extension, and connect it. Do not fall back to IAB, raw CDP, a remote debugging port, HTTP requests, or ad hoc Playwright.
5. If multiple extension backends are available and the user's intended browser cannot be identified from safe metadata or current context, stop and ask the user which connected browser to use. Do not guess by array order or silently close browsers.
6. Before opening the target site, include a verified `assert` step in the handoff proving that the selected backend type is `extension`. Record only safe backend metadata needed to distinguish the chosen browser, such as a non-secret backend id, browser name, or visible tab title.
7. The upstream extension backend is discovery infrastructure, not necessarily the RPA runtime browser. Do not derive `main.py` `BrowserConfig` values from extension backend ids unless the local RPA runtime explicitly uses the same identifier.

Privacy and logging rules:

- Browser backend metadata can contain profile information, filesystem paths, URLs, cookies, tokens, or account details.
- Never print, copy into handoff JSON, copy into generated RPA files, or summarize sensitive fields.
- Record only the minimum safe metadata necessary to identify the selected extension backend.

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

After the Requirement Intake Gate has produced a complete URL-input collection requirement, and before checking or opening any browser page, resolve the local debug root and the script input directory. This is a pre-browser setup gate, not a post-handoff decision. Do not ask whether local debugging should be used; this skill's default delivery route is local-debug delivery into the user's script input directory.

The local debug root and script input directory may be supplied either by the user's current message or by environment variables. User-provided values take precedence over environment variables. If a value is not provided in the message, read it from:

- `RPA_DEBUG_ROOT`: local debug root directory.
- `RPA_SCRIPT_INPUT_DIR`: script input directory, either absolute or relative to `RPA_DEBUG_ROOT`.

Treat any user-provided "debug directory", "debug root", "local debug directory", "local project root", "调试目录", "调试根目录", or equivalent path for running the generated script as the local debug root unless the user clearly labels it as the script input directory.

If the user labels a path as the script input directory, generated script directory, or generated script subdirectory, treat that path as the script input directory. The script input directory is the final write location, not a parent directory for another generated folder.

After the local debug root is resolved, resolve the script input directory before browser exploration starts. Do not invent or auto-choose a custom output directory. The generated files must be written directly into the confirmed script input directory.

The local debug root and script input directory must be locked before browser exploration starts. Do not open Browser, discover extension backends, navigate to the target site, or create a handoff until both the requirement and delivery paths are complete. If either path is missing from both the user request and environment variables, or if either path is ambiguous, stop and ask for the missing path value first.

Required local-debug delivery rules:

1. Require a local debug root directory before writing files. If the user has not provided one and `RPA_DEBUG_ROOT` is not set, stop and ask for the local debug root; do not write into the skill `outputs/` directory as a substitute.
2. Require the script input directory before browser exploration starts. If the user has not provided it and `RPA_SCRIPT_INPUT_DIR` is not set, stop and ask for the script input directory; do not choose a task-derived folder or use the skill `outputs/` directory as a substitute.
3. The script input directory may be provided as an absolute path under the local debug root, or as a path relative to the local debug root. Resolve it to a full path before writing files.
4. The actual output directory must be exactly the confirmed script input directory. Write `readme.md`, `script.py`, `source.py`, `main.py`, and `browser-handoff.json` directly inside that directory. Do not create an extra task-named subdirectory under it.
5. The script input directory must be importable as Python package parts relative to the local debug root: each path segment must be a valid Python identifier. If it is not importable, stop and ask for an importable script input directory instead of silently changing it.
6. Derive `main.py`'s `source.py` import from the script input directory relative to the debug root. Split the relative path into Python package parts and append `.source`. For a script input directory `scripts\business\amazon`, `main.py` must use `from scripts.business.amazon.source import <PageClassName>`.
7. The local debug command must be run from the local debug root with `uv run <script_input_directory>\main.py`. Example: from `D:\project`, run `uv run .\scripts\business\amazon\main.py`.
8. When validating local-debug output, run `python scripts/validate_generated_rpa.py <script-input-dir> --debug-root <local-debug-root>` from this skill root before running the local debug command. If the paths came from environment variables, `python scripts/validate_generated_rpa.py` may be run without path arguments because the validator reads `RPA_SCRIPT_INPUT_DIR` and `RPA_DEBUG_ROOT`.
9. If validation passes, run the local debug command and report the command, working directory, and result. If validation fails, fix the generated files first and do not run local debug.

If the user explicitly refuses local-debug delivery, stop and ask for a delivery location that preserves this skill's required local debug root and script input directory contract. Do not silently fall back to the skill `outputs/` directory.

## Completion Gate

A browser-to-RPA task is complete only after the final RPA files have been written and validated. Treat printed product names, extracted page data, screenshots, or a successful Browser handoff as intermediate evidence, not as the final deliverable.

## Original Prompt Documentation Rule

Every generated `readme.md` must include a section titled exactly `## Original Codex Skill Prompt`. In that section, record the complete text the user manually entered in Codex when invoking this skill for the current generation task, including all requirements, URLs, paths, field mappings, follow-up clarifications, and runtime details that shaped the final script.

Preserve the prompt text as a handoff aid for future maintenance. Do not replace it with a summary, paraphrase, or only the parsed requirement. If multiple user messages in the current task refine the same generation request, include them in chronological order under the same section.

After every successful Browser handoff:

1. Choose the output directory before writing files:
   - Use the Local Debug Generation Rule decision made at task start. The output directory must be exactly the confirmed script input directory and must follow the input-directory/import rules in that section.
   - Do not create or use a task-derived `outputs/` folder when local debug root or script input directory is missing. Stop and ask for the missing path instead.
   - Do not write generated RPA files into the caller's unrelated working directory, a temporary directory, or another repo's `outputs/` directory.
2. Write all required files: `readme.md`, `script.py`, `source.py`, `main.py`, and `browser-handoff.json`. The `readme.md` must satisfy the Original Prompt Documentation Rule.
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
    platform="<runtime_platform>",
    id="<runtime_browser_id>",
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

When local debugging is confirmed, the `main.py` import path is not chosen independently. It must be derived from the script input directory relative to the local debug root. Convert path separators to dots and append `.source`; for example, `scripts\business\amazon` becomes `from scripts.business.amazon.source import <PageClassName>`. The local debug command must be run from the debug root as `uv run .\scripts\business\amazon\main.py` for that example.

Set `BROWSER_CONFIG.platform` and `BROWSER_CONFIG.id` from the confirmed local RPA debug runtime. They are runtime configuration, not Browser extension discovery metadata. If the user or debug project does not provide these values, ask for them before generating `main.py`; do not copy an extension backend id into `BrowserConfig` by assumption. Keep default window variables and `timeout=30000` unless the user explicitly requests different runtime settings. Always include input/config variables in `VARIABLE_VALUES` so local developer runs do not depend on external defaults. Never include site-specific or task-specific values in the skill itself; derive them only from the current user request, confirmed runtime, and successful handoff. Never include extracted outputs in `VARIABLE_VALUES`.
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
## Detailed RPA Framework Reference

For detailed RPA Editor NextGen conventions, connector patterns, anti-detection helpers, and examples, read `references/rpa-editor-nextgen-reference.md` only when generating or reviewing final RPA files. Keep the browser route, local-debug gates, handoff schema, and validators in this `SKILL.md` as the hard delivery contract.
