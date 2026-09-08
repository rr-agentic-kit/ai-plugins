# Playwright E2E Test Reference

## Non-negotiable Rules

### Locators — priority order

Use semantic locators. Never use CSS selectors, class names, `page.$()`, or `page.waitForSelector()`.

```ts
page.getByRole('button', { name: 'Submit' })   // #1 — semantic, resilient
page.getByLabel('Email address')               // #2 — form fields
page.getByPlaceholder('Search...')             // #3 — inputs
page.getByText('Confirm')                      // #4 — visible text
page.getByTestId('submit-btn')                 // #5 — only when semantic locators fail
```

### Assertions — always `expect` from `@playwright/test`

Playwright assertions auto-retry. Never import `expect` from `vitest` or `jest`. Never extract text then assert — assert directly on the locator:

```ts
await expect(page.getByRole('heading')).toHaveText('Hello')
await expect(page).toHaveURL('/dashboard')
```

### One Concern Per Test

Each test validates one user-visible behavior. Group tests with `test.describe` by feature, not by page.

### Page Object Model — required for non-trivial flows

Use POM for pages with more than 3 interactions. Locators are `readonly` constructor properties. Actions are methods. Assertions stay in tests — never in POM.

```ts
export class LoginPage {
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly submitButton: Locator
  readonly errorMessage: Locator

  constructor(private readonly page: Page) {
    this.emailInput = page.getByLabel('Email')
    this.passwordInput = page.getByLabel('Password')
    this.submitButton = page.getByRole('button', { name: 'Sign in' })
    this.errorMessage = page.getByRole('alert')
  }

  async goto() { await this.page.goto('/login') }

  async login(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }
}
```

### Authentication — never via UI per test

Save `storageState` once in `globalSetup` and reuse it. UI login per test is the single most common cause of slow, flaky E2E suites.

### Test Data — API only, never UI

Use the real backend API to set up state. Only the behavior under test touches the UI.

```ts
test('can delete item', async ({ page, request }) => {
  const { id } = await (await request.post('/api/items', { data: { name: 'x' } })).json()

  await page.goto(`/items/${id}`)
  await page.getByRole('button', { name: 'Delete' }).click()
  await page.getByRole('button', { name: 'Confirm' }).click()

  await expect(page.getByText('Item deleted')).toBeVisible()
})
```

### Isolation — tests must not share state

Each test is self-contained. `beforeAll` only for truly read-only shared setup (lookup data). Never for transactional state.

### No Mocking

E2E tests validate the full stack: browser → frontend → backend → database. `page.route()` to mock responses is forbidden — it turns E2E into an integration test. External third-party services use their sandbox environments.

### Configuration

- `retries`: 0 locally, 2 in CI. Never mask flakiness locally.
- `trace` / `screenshot` / `video`: `on-first-retry` only.
- `fullyParallel: true` — only valid if tests are properly isolated.
- `baseURL` from environment variable — never hardcode.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `waitForTimeout(n)` | Machine-speed-dependent | Assert the expected state |
| CSS / DOM path selectors | Breaks on refactor | Semantic locators |
| `page.$` / `page.$$` | Legacy API, no auto-wait | Locator API |
| `page.waitForSelector` | No expect retry integration | `await expect(locator).toBeVisible()` |
| `networkidle` | Undefined in SPAs | Wait for specific response or element |
| `page.route()` mock | Defeats E2E purpose | Fix environment, use sandbox APIs |
| Shared mutable state | Order-dependent failures | Self-contained tests |
| UI for test data setup | Couples tests to unrelated UI | API calls |

## Final Check

Every `await` must be present on async calls. Missing `await` is a silent failure — no error, wrong behavior.
