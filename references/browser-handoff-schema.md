# Browser Handoff Schema

Use this schema when the RPA developer skill needs to consume output from the browser skill.

## Upstream status gate

The RPA developer skill may only consume a handoff whose `status` is exactly `success`.

If the handoff is missing, invalid, or has `status` other than `success`, rerun the upstream browser step and request a fresh handoff. Retry at most 3 total attempts. If the third attempt still does not produce a valid successful handoff, stop and report failure instead of generating RPA files.

## Required fields

- `status`: Must be exactly `success` before RPA generation can continue.
- `attempt`: Current upstream attempt number. Must be an integer from `1` to `3`.
- `max_attempts`: Must be `3`.
- `task`: Human-readable automation goal.
- `start_url`: First URL to open.
- `playwright_python`: Minimal Playwright Python snippet that demonstrates the discovered interactions.
- `steps`: Ordered browser actions.
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
- `fallbacks`: Optional list of alternate locators or recovery notes.

## Quality bar

- Prefer stable Playwright locators: `get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id`, then CSS.
- Include waits for dialogs, navigations, dynamic menus, and address confirmation states.
- Keep selectors specific enough to avoid accidental clicks, but avoid brittle generated class names.
- Do not include secrets, cookies, or personal account data.
- If the browser flow cannot be completed because of captcha, login, region checks, or anti-bot behavior, set `status` to `failed`, record the furthest confirmed state and blocker, and let the RPA developer skill retry or fail according to the 3-attempt rule.