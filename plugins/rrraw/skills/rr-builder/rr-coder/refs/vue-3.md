# Vue 3.5 Standards

## Version
Vue 3.5.x with TypeScript. `<script setup>` is the only accepted component syntax. Composition API only — never Options API.

## Vue 3.3–3.5 Features — Use These
- **`<script setup>`** — required SFC syntax, auto-exposes to template
- **`defineProps` with TS generics** — `defineProps<{ count: number }>()`, no runtime declaration needed
- **Reactive props destructure (3.5)** — `const { count = 0 } = defineProps<{ count?: number }>()` stays reactive
- **`defineEmits` with TS** — `const emit = defineEmits<{ submit: [payload: FormData] }>()`
- **`defineModel` (3.3)** — `const model = defineModel<string>()` replaces `modelValue` + `update:modelValue` boilerplate
- **`defineOptions` (3.3)** — set `name`, `inheritAttrs` inside `<script setup>`
- **`defineSlots` (3.3)** — type-safe slot declarations for generic components
- **`useTemplateRef` (3.5)** — `const el = useTemplateRef('my-ref')` replaces string-matched `ref()` pattern
- **`useId` (3.5)** — SSR-safe unique ID generation for forms/accessibility
- **`toValue` (3.3)** — normalizes ref, getter, or plain value — use in composables accepting `MaybeRefOrGetter<T>`
- **`onWatcherCleanup` (3.5)** — cleanup inside `watch`/`watchEffect` callback without return function

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `<script setup lang="ts">` | Options API, `defineComponent()` setup function |
| `ref()` for all state | `reactive()` (loses reactivity on reassign/destructure) |
| `defineProps<{ foo: string }>()` (type-only) | Runtime `defineProps({ foo: { type: String } })` |
| Reactive props destructure with defaults | `withDefaults(defineProps<T>(), { ... })` (3.5+) |
| `defineModel<T>()` for v-model | Manual `modelValue` prop + `update:modelValue` emit |
| `useTemplateRef('name')` | `const myRef = ref<HTMLElement \| null>(null)` matched by variable name |
| `computed()` for derived state | Methods that recalculate on every render |
| `watch(() => obj.prop, cb)` getter for reactive object props | `watch(obj.prop, cb)` (not reactive, captures value) |
| `watchEffect` when tracking all deps automatically | `watch` with manually listed deps that drift |
| `toValue(source)` in composables | `unref()` (doesn't handle getters) |
| `toRefs(reactiveObj)` when destructuring from composable return | Destructuring reactive objects directly |
| `shallowRef` for large objects mutated externally | `ref` wrapping deep objects that don't need deep tracking |
| `provide`/`inject` with `InjectionKey<T>` | Untyped string keys for provide/inject |
| Composables (`useFoo`) for reusable stateful logic | Mixins, renderless components for logic reuse |
| `v-memo` on expensive list items | Re-rendering large lists without memoization |
| `<Suspense>` + async `setup()` for data loading | Manual loading state in every component |
| `<Teleport to="body">` for modals/overlays | Portal workarounds, z-index stacking hacks |
| `<component :is="registry[type]">` dynamic components | `v-if`/`v-else` chains for 3+ component types |
| Feature-based folder structure (`features/auth/`) | File-type grouping (`components/`, `composables/`, `stores/`) |

## Common Mistakes

### Destructuring reactive() loses reactivity
```typescript
const state = reactive({ count: 0 })
// BUG: count is a plain number, not reactive
const { count } = state

// FIX: use toRefs or just use ref
const { count } = toRefs(state)
// BETTER: use ref from the start
const count = ref(0)
```

### Watching reactive object property by value
```typescript
const obj = reactive({ count: 0 })
// BUG: watches the initial value (0), never triggers again
watch(obj.count, (val) => console.log(val))

// FIX: use getter
watch(() => obj.count, (val) => console.log(val))
```

### Replacing reactive object breaks references
```typescript
const state = reactive({ items: [] })
// BUG: watchers/template still reference old object
state = reactive({ items: newItems })

// FIX: mutate properties, or use ref
state.items = newItems
// OR: const state = ref({ items: [] })
```

### Async composable without cleanup
```typescript
// BUG: no abort on unmount — stale response overwrites fresh
export function useFetch(url: MaybeRefOrGetter<string>) {
  const data = ref(null)
  watchEffect(() => {
    fetch(toValue(url)).then(r => r.json()).then(d => data.value = d)
  })
  return { data }
}

// FIX: use onWatcherCleanup (3.5+)
export function useFetch(url: MaybeRefOrGetter<string>) {
  const data = ref(null)
  watchEffect(() => {
    const controller = new AbortController()
    onWatcherCleanup(() => controller.abort())
    fetch(toValue(url), { signal: controller.signal })
      .then(r => r.json()).then(d => data.value = d).catch(() => {})
  })
  return { data }
}
```

### Untyped provide/inject
```typescript
// BUG: inject returns unknown, no type safety
provide('user', currentUser)
const user = inject('user')

// FIX: typed InjectionKey
const UserKey: InjectionKey<User> = Symbol('user')
provide(UserKey, currentUser)
const user = inject(UserKey) // User | undefined
```

### computed with side effects
```typescript
// BUG: computed is for derivation, not side effects — unpredictable timing
const formatted = computed(() => {
  analytics.track('computed')  // side effect
  return format(data.value)
})

// FIX: use watchEffect for side effects, computed for derivation
const formatted = computed(() => format(data.value))
watchEffect(() => analytics.track('formatted', formatted.value))
```

## Library Choices

| Purpose | Library | Notes |
|---------|---------|-------|
| State management | Pinia 3.x | Official, devtools integration, composition stores |
| Routing | Vue Router 4.x | `createRouter` + `createWebHistory` |
| Utilities/composables | VueUse 12.x | 200+ composables, tree-shakeable |
| Forms | VeeValidate 4.x | + Zod for schema validation |
| HTTP | Axios or native `fetch` | Wrap in composables, not raw in components |
| Build tool | Vite 6.x | Only option for new projects, Vue CLI is EOL |
| Testing | Vitest + Vue Test Utils + MSW | See testing reference |
| Styling | Tailwind CSS 4.x or UnoCSS | Scoped `<style>` for component-specific CSS |
| Runtime validation | Zod 3.x | Schema-first, infers TS types |
| Tables | TanStack Table 8.x | Headless adapter: `@tanstack/vue-table` |
| i18n | Vue I18n 10.x | Composition API mode (`useI18n()`) |
| IDE | VS Code + Vue - Official (Volar) | Vetur is deprecated |

## Pinia Store Pattern

Use composition (setup) stores — mirrors component `<script setup>` mental model.

```typescript
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => user.value !== null)

  async function login(credentials: Credentials) {
    user.value = await authApi.login(credentials)
  }

  function logout() {
    user.value = null
  }

  return { user, isAuthenticated, login, logout }
})
```

## Composable Convention

- Name: `useFoo` — always prefix with `use`
- Accept `MaybeRefOrGetter<T>` for flexible inputs, resolve with `toValue()`
- Return plain object of refs (not reactive) — allows destructuring
- Handle cleanup via `onWatcherCleanup` or `onUnmounted`

```typescript
export function useDebounce<T>(source: MaybeRefOrGetter<T>, ms = 300) {
  const debounced = ref(toValue(source)) as Ref<T>
  watchEffect(() => {
    const timer = setTimeout(() => { debounced.value = toValue(source) }, ms)
    onWatcherCleanup(() => clearTimeout(timer))
  })
  return debounced
}
```
