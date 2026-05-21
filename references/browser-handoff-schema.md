# Browser Handoff Schema

Use this schema when the RPA developer skill needs to consume output from the Browser skill from `plugin://browser@openai-bundled`.

This schema is self-contained and must not depend on Codex memory, previous chat context, or remembered Browser backend state. For this RPA developer skill, Browser exploration defaults to the Clonbrowser launched-browser preflight unless the current user request explicitly asks for a non-Clonbrowser browser route.

Before producing a handoff, the upstream Browser skill must be available in Codex as `browser:browser`, `Browser`, `@browser`, or `@浏览器`, and it must run in headed/visible mode. The upstream run must explicitly open or claim a visible headed tab/window before the first navigation and must keep that visible browser surface as the source of interaction and evidence. Do not produce a successful handoff from headless Playwright, background content fetches, HTTP requests, generic web search, hidden tabs, or any backend the user cannot watch. If headed/visible mode cannot be enabled and confirmed, report the upstream attempt as failed instead of producing a best-effort handoff.

## Upstream status gate

The RPA developer skill may only consume a handoff whose `status` is exactly `success`.

If the handoff is missing, invalid, or has `status` other than `success`, rerun the upstream Browser step and request a fresh handoff. Retry at most 3 total attempts. If the third attempt still does not produce a valid successful handoff, stop and report failure instead of generating RPA files.

## Required fields

- `status`: Must be exactly `success` before RPA generation can continue.
- `attempt`: Current upstream attempt number. Must be an integer from `1` to `3`.
- `max_attempts`: Must be `3`.
- `task`: Human-readable automation goal.
- `start_url`: First URL to open.
- `playwright_python`: Minimal synchronous Playwright Python snippet that demonstrates the discovered interactions. It must not use `async def`, `await`, `async with`, `async for`, or async Playwright imports. When the snippet includes browser launch code, it must explicitly launch headed mode, for example `browser = p.chromium.launch(headless=False)`. It must never include `headless=True`.
- `steps`: Ordered Browser-discovered page actions.
- `assumptions`: Known assumptions, such as logged-out state or marketplace locale.
- `warnings`: Blockers or uncertainty, such as captcha, account login, dynamic selectors, or address validation differences.

For this skill's default browser route, the upstream run must first read `GET http://127.0.0.1:37073/v1/browsers/launched`. If the launched list is empty, stop and tell the user to start the required Clonbrowser browser, then wait for the user's reply. After the user replies, continue only by checking `/v1/browsers/launched` again; do not reinterpret "continue" as permission to use any other browser route. If the launched list contains multiple browsers, stop and tell the user to close or stop extras until exactly one remains. In both stop states, do not continue by using Codex In-app Browser, an already-connected Chrome extension backend, a local Chrome profile, or any other Browser backend.

For every successful handoff produced by this skill's default browser route, prove that the selected upstream Browser backend was not Codex In-app Browser. Include a successful `assert` step whose evidence states the selected backend type, the selected launched browser `id`, and safe metadata. A handoff collected from `type: "iab"` is invalid. The selected launched browser `id` is required so generated `main.py` can set `BROWSER_CONFIG = BrowserConfig(platform="cb-global", id="<selected_launched_browser_id>")`.

Optional failure fields for unsuccessful attempts:

- `failure_reason`: Short explanation of why the browser step failed.
- `last_confirmed_state`: Furthest confirmed page state before failure.

## Step fields

Each `steps[]` entry should contain:

- `intent`: Why this step exists.
- `action`: One of `goto`, `click`, `fill`, `select`, `press`, `wait`, `assert`, `extract`.
- `locator`: Playwright Python locator expression, or `null` for navigation-only steps.
- `value`: Text/value to fill, select, or press; otherwise `null`.
- `wait_for`: Expected page state after the action.
- `verified`: Must be `true` for successful handoffs. It means Browser verified the element, state, or extracted field against the live page during this attempt.
- `evidence`: Non-empty description of the real page observation that proves the step is grounded. Use visible text, accessible name, selected option, URL/title state, element count, extracted sample, screenshot reference, or trace note.
- `fallbacks`: Optional list of alternate locators or recovery notes.

For requested state-setting goals, such as language, locale, delivery destination, marketplace, category, sort order, filters, search scope, account context, toggles, or form defaults, the handoff must include explicit action steps that re-apply the requested value. A final-state assertion alone is not enough, even when the page already starts in the requested state. If the UI blocks re-applying an already-selected value, record the attempted control path and the authoritative final-state confirmation.

## Quality bar

- Prefer stable Playwright locators: `get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id`, then CSS.
- Use only locators and state assertions observed in the current live Browser page. Do not invent selectors, reuse stale selectors from prior tasks, or infer elements from generic site knowledge.
- Do not use Codex In-app Browser for this skill's default browser route. Use a non-`iab` Browser extension backend attached to the single launched Clonbrowser instance, and record the selected launched browser `id` in evidence, or report failure before opening the target site. If the launched Clonbrowser list is empty, report that the user must start the required browser and wait for their reply before retrying; do not fall back to another visible browser.
- Every successful step must include `verified: true` and evidence. If an element cannot be observed, do not mark the handoff successful.
- Keep handoff snippets compatible with the synchronous RPA runtime. Do not include async/coroutine syntax in `playwright_python`.
- Keep handoff snippets explicitly headed when they include a launch call. A launch call without `headless=False` is incomplete evidence for this workflow.
- Include waits for dialogs, navigations, dynamic menus, and address confirmation states.
- Include explicit open/select/apply/assert steps for every requested state-setting goal; do not collapse them into "already set".
- Treat observed result values as evidence only. Product names, listing titles, prices, IDs, URLs, scraped text, counts, or records discovered during Browser exploration must guide runtime extraction logic, not become generated RPA variables or `main.py` input values.
- Keep selectors specific enough to avoid accidental clicks, but avoid brittle generated class names.
- Do not include secrets, cookies, or personal account data.
- If the browser flow cannot be completed because of captcha, login, region checks, or anti-bot behavior, set `status` to `failed`, record the furthest confirmed state and blocker, and let the RPA developer skill retry or fail according to the 3-attempt rule.
