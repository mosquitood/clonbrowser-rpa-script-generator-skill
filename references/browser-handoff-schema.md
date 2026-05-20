# Browser Handoff Schema

Use this schema when the RPA developer skill needs to consume output from the Browser skill from `plugin://browser@openai-bundled`.

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
- Every successful step must include `verified: true` and evidence. If an element cannot be observed, do not mark the handoff successful.
- Keep handoff snippets compatible with the synchronous RPA runtime. Do not include async/coroutine syntax in `playwright_python`.
- Keep handoff snippets explicitly headed when they include a launch call. A launch call without `headless=False` is incomplete evidence for this workflow.
- Include waits for dialogs, navigations, dynamic menus, and address confirmation states.
- Include explicit open/select/apply/assert steps for every requested state-setting goal; do not collapse them into "already set".
- Treat observed result values as evidence only. Product names, listing titles, prices, IDs, URLs, scraped text, counts, or records discovered during Browser exploration must guide runtime extraction logic, not become generated RPA variables or `main.py` input values.
- Keep selectors specific enough to avoid accidental clicks, but avoid brittle generated class names.
- Do not include secrets, cookies, or personal account data.
- If the browser flow cannot be completed because of captcha, login, region checks, or anti-bot behavior, set `status` to `failed`, record the furthest confirmed state and blocker, and let the RPA developer skill retry or fail according to the 3-attempt rule.
