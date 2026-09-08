# TanStack Query v5 Standards

## Version
TanStack Query 5.x (`@tanstack/react-query`) with TypeScript. React 18+. Server state only — Zustand/Context for client state. Query keys are cache identity: `['entity', id, { filters }]`. Override `staleTime` / `gcTime` per-query (library defaults: `staleTime: 0`, `gcTime: 5min`).

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `useQuery({ queryKey, queryFn })` | `useEffect` + `useState` for fetching |
| `useSuspenseQuery` with `<Suspense>` | `isPending` checks when Suspense boundaries exist |
| `useMutation` + `invalidateQueries` | Manual cache manipulation after mutations |
| Query key factories (`queryKeys.todos.list(filters)`) | Inline string arrays (`['todos', 'list']`) scattered |
| `select` option to transform/filter | Transforming in component body |
| `enabled: !!id` for dependent queries | Fetching with undefined params then guarding |
| `placeholderData: keepPreviousData` for pagination | Showing spinner on every page change |
| `queryClient.prefetchQuery` on hover/route | Fetching only on mount (perceived latency) |
| Typed `queryFn` returning `Promise<T>` | `queryFn` returning `any` |
| Error boundaries with `throwOnError: true` | Per-component error handling everywhere |

## Query Key Factory Pattern

```typescript
export const todoKeys = {
  all: ['todos'] as const,
  lists: () => [...todoKeys.all, 'list'] as const,
  list: (filters: TodoFilters) => [...todoKeys.lists(), filters] as const,
  details: () => [...todoKeys.all, 'detail'] as const,
  detail: (id: string) => [...todoKeys.details(), id] as const,
};

// Invalidate all todo queries
queryClient.invalidateQueries({ queryKey: todoKeys.all });
// Invalidate only lists
queryClient.invalidateQueries({ queryKey: todoKeys.lists() });
```

## Typed Query with API Wrapper

```typescript
const { data, isPending, error } = useQuery({
  queryKey: todoKeys.detail(id),
  queryFn: () => apiCall<Todo>(`/api/todos/${id}`),
  select: (result) => {
    if (result.error) throw new Error(result.error.message);
    return result.data;
  },
});
```

## Mutations with Cache Invalidation

```typescript
const mutation = useMutation({
  mutationFn: (req: CreateTodoRequest) =>
    apiCall<Todo, CreateTodoRequest>('/api/todos', req),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: todoKeys.lists() });
  },
});
```

## Optimistic Updates

```typescript
useMutation({
  mutationFn: updateTodo,
  onMutate: async (updated) => {
    await queryClient.cancelQueries({ queryKey: todoKeys.detail(updated.id) });
    const previous = queryClient.getQueryData(todoKeys.detail(updated.id));
    queryClient.setQueryData(todoKeys.detail(updated.id), updated);
    return { previous };
  },
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(todoKeys.detail(_vars.id), context?.previous);
  },
  onSettled: (_data, _err, vars) => {
    queryClient.invalidateQueries({ queryKey: todoKeys.detail(vars.id) });
  },
});
```

## Infinite Queries

```typescript
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: todoKeys.lists(),
  queryFn: ({ pageParam }) => fetchTodos({ cursor: pageParam }),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
});

const allItems = data?.pages.flatMap((p) => p.items) ?? [];
```

## Common Mistakes

### Missing query key granularity
```typescript
// BUG: all todo lists share one cache entry regardless of filters
useQuery({ queryKey: ['todos'], queryFn: () => fetchTodos(filters) });

// FIX: include filters in key
useQuery({ queryKey: todoKeys.list(filters), queryFn: () => fetchTodos(filters) });
```

### Mutating without invalidation
```typescript
// BUG: stale list after create — user doesn't see new item
useMutation({ mutationFn: createTodo });

// FIX: invalidate related queries
useMutation({
  mutationFn: createTodo,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: todoKeys.lists() }),
});
```

### staleTime: 0 with expensive queries
```typescript
// BUG: refetches on every mount/focus — hammers API for rarely-changing data
useQuery({ queryKey: ['config'], queryFn: fetchConfig });

// FIX: set staleTime > 0 for rarely-changing data (e.g. 5 * 60_000)
useQuery({ queryKey: ['config'], queryFn: fetchConfig, staleTime: 5 * 60_000 });
```

### Suspense without error boundary
```typescript
// BUG: unhandled rejection crashes app
<Suspense fallback={<Spinner />}>
  <TodoList /> {/* uses useSuspenseQuery */}
</Suspense>

// FIX: wrap with error boundary
<ErrorBoundary fallback={<ErrorMessage />}>
  <Suspense fallback={<Spinner />}>
    <TodoList />
  </Suspense>
</ErrorBoundary>
```
