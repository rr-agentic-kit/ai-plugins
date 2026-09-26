# React 18 Standards

## Version
React 18.x with TypeScript. Concurrent features enabled by default with `createRoot`.

## React 18 Features — Use These
- **`createRoot`** — required entry point, enables concurrent features
- **Automatic batching** — state updates in timeouts, promises, native events are batched (no manual `unstable_batchedUpdates`)
- **`useTransition`** — mark non-urgent state updates, keep UI responsive during heavy renders
- **`useDeferredValue`** — defer re-rendering expensive subtrees until urgent work completes
- **`useId`** — generate stable unique IDs for SSR hydration and accessibility
- **`useSyncExternalStore`** — subscribe to external stores safely under concurrent rendering
- **Suspense for data fetching** — `<Suspense fallback={...}>` with lazy components and data libraries
- **`startTransition`** — non-hook version for class components or outside React

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `createRoot(el).render(<App />)` | `ReactDOM.render(<App />, el)` |
| `useTransition` for non-urgent updates | Blocking renders on filter/search input |
| `useDeferredValue(value)` for derived expensive renders | `setTimeout` to defer renders manually |
| `useId()` for form/accessibility IDs | `Math.random()` or counters for SSR-safe IDs |
| `useSyncExternalStore` for external state | `useEffect` + `useState` to sync external stores |
| Discriminated union for async state (`idle \| loading \| success \| error`) | Boolean flags (`isLoading`, `isError`) |
| `<Suspense>` boundaries per data-loading section | Single top-level Suspense |
| Named function components | `React.FC` (adds implicit `children`, poor generics) |
| `useCallback`/`useMemo` when passing to memoized children | Wrapping every function in `useCallback` |
| Controlled forms with `onChange` | Uncontrolled `ref`-based forms (unless perf-justified) |
| `React.lazy()` + Suspense for code splitting | Manual dynamic `import()` with loading state |
| Event handler types from React (`React.MouseEvent<HTMLButtonElement>`) | Generic `any` event types |
| `key` prop on list items from stable IDs | Array index as `key` (breaks on reorder/insert) |
| Cleanup in `useEffect` return | Ignoring cleanup (memory leaks, stale subscriptions) |
| `flushSync` only when DOM measurement required | `flushSync` to work around batching |
| Discriminated union `{ data: T; error: null } \| { data: null; error: ApiError }` for API responses | `try/catch` with thrown errors for API layer responses |
| Feature-specific API modules (`artifactApi.list()`) | Generic `fetch()` calls scattered in components |
| Component registry for dynamic rendering | `switch` statements mapping type → component |
| Event bus for cross-panel communication (no shared ancestor) | Prop drilling through 3+ levels, Context for ephemeral events |
| Zustand or Context for shared state with re-render needs | Event bus for state that drives UI (no reactivity) |

## API Response Type

Standard discriminated union for typed API responses. Used as `queryFn` return type in TanStack Query (see `react-query.md`). Apollo Client uses its own error model via link chain — see `react-apollo.md`.

```typescript
type ApiResponse<T> = { data: T; error: null } | { data: null; error: ApiError };
interface ApiError { code: string; message: string; }
```

Feature-specific API modules wrap this type:

```typescript
export const artifactApi = {
  list: () => apiCall<Artifact[]>('/api/artifacts'),
  get: (id: string) => apiCall<Artifact>(`/api/artifacts/${id}`),
  create: (req: CreateArtifactRequest) =>
    apiCall<Artifact, CreateArtifactRequest>('/api/artifacts', req),
};
```

## Component Registry

Dynamic component rendering via registry pattern. Use when component type is determined at runtime (plugin systems, configurable panels).

```typescript
function createRegistry<TProps>() {
  const components = new Map<string, React.ComponentType<TProps>>();
  return {
    register: (type: string, component: React.ComponentType<TProps>) => {
      components.set(type, component);
    },
    get: (type: string) => components.get(type),
  };
}
```

## Event Bus

**Use when**: Components have no shared ancestor, communication is fire-and-forget (notifications, panel coordination).
**Don't use when**: State must drive re-renders (use Zustand), or components share a parent (lift state or Context).

```typescript
class PanelEventBus {
  private handlers = new Map<string, Set<(payload: unknown) => void>>();

  on<T>(event: string, handler: (payload: T) => void) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event)!.add(handler as (payload: unknown) => void);
    return () => { this.handlers.get(event)?.delete(handler as (payload: unknown) => void); };
  }

  emit<T>(event: string, payload: T) {
    this.handlers.get(event)?.forEach((h) => h(payload));
  }
}

export const panelEvents = new PanelEventBus();
```

## Common Mistakes

### useEffect as data fetcher without cleanup
```typescript
// BUG: race condition — stale response overwrites fresh
useEffect(() => {
  fetch(`/api/${id}`).then(r => r.json()).then(setData);
}, [id]);

// FIX: abort controller
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/${id}`, { signal: controller.signal })
    .then(r => r.json()).then(setData).catch(() => {});
  return () => controller.abort();
}, [id]);
```

### Object/array literals in deps cause infinite loops
```typescript
// BUG: new object every render → infinite useEffect
useEffect(() => { fetchData(filters); }, [{ status: 'active' }]);

// FIX: useMemo or primitive deps
const filters = useMemo(() => ({ status: 'active' }), []);
useEffect(() => { fetchData(filters); }, [filters]);
```

### useState initializer runs every render
```typescript
// BUG: expensive computation on every render
const [data, setData] = useState(parseExpensiveData(raw));

// FIX: lazy initializer — runs once
const [data, setData] = useState(() => parseExpensiveData(raw));
```

### Missing exhaustive deps
```typescript
// BUG: stale closure — callback captures initial props
const handleClick = useCallback(() => {
  onSubmit(formData);
}, []); // Missing formData, onSubmit

// FIX: include all deps
const handleClick = useCallback(() => {
  onSubmit(formData);
}, [onSubmit, formData]);
```

### Suspense boundary too high
```typescript
// BAD: entire page suspends for one slow component
<Suspense fallback={<FullPageSpinner />}>
  <Header /><Sidebar /><SlowDataTable /><Footer />
</Suspense>

// GOOD: granular boundaries — always pair with ErrorBoundary for data fetching
<Header />
<Sidebar />
<ErrorBoundary fallback={<ErrorMessage />}>
  <Suspense fallback={<TableSkeleton />}>
    <SlowDataTable />
  </Suspense>
</ErrorBoundary>
<Footer />
```

### Context causes unnecessary re-renders
```typescript
// BAD: all consumers re-render on any state change
<AppContext.Provider value={{ user, theme, notifications }}>

// GOOD: split by update frequency
<UserContext.Provider value={user}>
  <ThemeContext.Provider value={theme}>
    <NotificationContext.Provider value={notifications}>
```

## Library Choices

| Purpose | Library | Notes |
|---------|---------|-------|
| Data fetching + cache (REST) | TanStack Query | See `react-query.md` |
| Data fetching + cache (GraphQL) | Apollo Client | See `react-apollo.md` |
| Forms | React Hook Form 7.x | + Zod resolver for validation |
| Routing | React Router 6.x | Data router API (`createBrowserRouter`) |
| State (complex) | Zustand 5.x | Simpler than Redux, works with concurrent mode |
| State (server) | TanStack Query | Server state ≠ client state |
| Styling | Tailwind CSS 4.x | CSS-based config for new projects |
| Runtime validation | Zod 3.x | Schema-first, infers TS types |
| Testing | Vitest + Testing Library + MSW | See `react.test.md` |
| Animation | Framer Motion 11.x | Or CSS transitions for simple cases |
| Tables | TanStack Table 8.x | Headless, type-safe |

## Strict Mode Behavior (Development)
- Components mount → unmount → mount (detects missing cleanup)
- Effects run twice (catches side-effect bugs)
- Don't remove `<StrictMode>` to "fix" double-render — fix the effect instead
