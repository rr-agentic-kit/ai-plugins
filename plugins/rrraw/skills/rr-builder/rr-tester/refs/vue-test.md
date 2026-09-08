# Vue / Nuxt Test Reference (Vitest + Vue Test Utils + MSW)

## Exhaustive assess: what counts as method vs branch (`<script setup>`)

When **Mode: assess** walks production Vue SFCs, treat these as **methods** (callable units): each named function, `const fn = () => {}`, `computed()`, `watch()` callback, and event handler referenced from the template. **Branches** include template expressions without a backing function (e.g. inline `v-if="items.length > 0"`) as branches of the component's render logic. Lifecycle hooks (`onMounted`, `onUnmounted`, etc.) with non-trivial logic count as methods.

## Nuxt: `mountSuspended` and auto-imports

Use **`@nuxt/test-utils`** when `nuxt.config.ts` / `nuxt.config.js` exists. `mountSuspended` wraps the component so Nuxt auto-imports and async setup resolve.

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils'
import MyPage from '~/pages/my-page.vue'

mockNuxtImport('navigateTo', () => vi.fn())

describe('MyPage', () => {
  it('renders after suspense', async () => {
    const wrapper = await mountSuspended(MyPage, {
      route: '/my-page',
    })
    expect(wrapper.text()).toContain('Expected')
  })
})
```

Configure Vitest with Nuxt environment when using Nuxt test utils (see Nuxt docs for `environment: 'nuxt'` / module setup).

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `getByRole` / `getByText` (@testing-library/vue) or `wrapper.find('[data-testid]')` only when necessary | Snapshot overuse; brittle full-DOM snapshots |
| `wrapper.emitted()` for custom events | Asserting Vue internals (`wrapper.vm.$data`, private refs) |
| `flushPromises()` / `await nextTick()` after async template updates | Fixed `setTimeout` delays |
| MSW for API mocking (network level) | `vi.mock` on every HTTP client |
| `mountSuspended` for Nuxt pages/layouts with auto-imports | `mount` without Nuxt context → missing composable errors |
| One behavior per test | Many unrelated assertions in one test |

## API Mocking with MSW

Same pattern as [react-test.md](react-test.md) — intercept at the network layer so components and composables exercise real request code.

## Nuxt-specific mocking

| Need | Approach |
|------|----------|
| `useRuntimeConfig` | `mockNuxtImport('useRuntimeConfig', () => () => ({ public: { apiBase: 'http://test' } }))` or Vitest stub |
| `navigateTo` | `mockNuxtImport('navigateTo', () => vi.fn())` |
| `useFetch` / `useAsyncData` | MSW for HTTP; or mock module returning controlled refs |

Consult current `@nuxt/test-utils` docs for `mockNuxtImport` and `mountSuspended` options (route, props, plugins).

## Common Mistakes (Vue / Nuxt)

### Not awaiting async updates

```typescript
// BAD: DOM not updated yet
wrapper.get('button').trigger('click')
expect(wrapper.text()).toContain('Done')

// GOOD
await wrapper.get('button').trigger('click')
await flushPromises()
expect(wrapper.text()).toContain('Done')
```

### Testing implementation (`wrapper.vm`)

```typescript
// BAD: couples to internal refs
expect((wrapper.vm as any).internalFlag).toBe(true)

// GOOD: user-visible output or emitted events
expect(wrapper.emitted('update:modelValue')).toBeTruthy()
expect(wrapper.get('[role="status"]').text()).toMatch(/saved/i)
```

### Missing Nuxt wrapper

```typescript
// BAD: useFetch / auto-imports fail outside Nuxt test harness
mount(NuxtPageComponent)

// GOOD
await mountSuspended(NuxtPageComponent)
```
