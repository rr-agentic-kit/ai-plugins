# Apollo Client v3 Standards

## Version
Apollo Client 3.x (`@apollo/client`) with TypeScript. React 18+. **GraphQL only** — do not use for REST APIs.

## When to Use
- Backend exposes a GraphQL API (or you're adding one)
- Need normalized client-side cache keyed by `__typename` + `id`
- Multiple components read overlapping graph data (cache dedup shines)

**If backend is REST/RPC**: use TanStack Query instead. See `react-query.md`.

## Setup Decisions

- Default `fetchPolicy: 'cache-and-network'` globally via `defaultOptions.watchQuery`
- Link chain order: `errorLink` → `authLink` → `httpLink` (use `ApolloLink.from([...])`)
- Set `typePolicies` merge behavior explicitly: `merge: false` for non-paginated lists
- Use `@graphql-codegen/cli` with `client` preset for typed hooks + `TypedDocumentNode`
- Auth: inject `Authorization` header via custom `ApolloLink` middleware

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `useQuery(DOC, { variables })` | `client.query()` in components |
| `useSuspenseQuery` with `<Suspense>` | `loading` checks when Suspense boundaries exist |
| `useMutation` with `update` or `refetchQueries` | Manual `client.writeQuery` after mutations |
| `cache.modify` for surgical updates | `cache.writeQuery` overwriting entire lists |
| `fetchPolicy: 'cache-and-network'` | `fetchPolicy: 'cache-first'` for frequently changing data |
| `ErrorLink` for global error handling | Per-query `onError` for auth/network errors |
| `TypedDocumentNode` from codegen | Untyped `gql` template literals |
| `@graphql-codegen/cli` for types | Hand-written GraphQL types |
| Fragments for shared fields | Duplicating field selections across queries |
| `useFragment` for component-scoped reads | Over-fetching in parent then prop-drilling |

For Suspense boundary placement patterns, see `react-18.md` § Common Mistakes → Suspense boundary too high.

## Error Handling with Link Chain

```typescript
import { ErrorLink } from '@apollo/client/link/error';

const errorLink = new ErrorLink(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) =>
      console.error(`[GraphQL error]: ${message}, Path: ${path}`),
    );
  }
  if (networkError) {
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      logout();
    }
  }
});

// Link order: errorLink -> authLink -> httpLink
const link = ApolloLink.from([errorLink, authLink, httpLink]);
```

## Mutations with Cache Update

```typescript
const [addTodo] = useMutation(ADD_TODO, {
  update(cache, { data: { addTodo } }) {
    cache.modify({
      fields: {
        todos(existing = []) {
          const ref = cache.writeFragment({
            data: addTodo,
            fragment: gql`fragment NewTodo on Todo { id title }`,
          });
          return [...existing, ref];
        },
      },
    });
  },
});
```

## Optimistic Updates

```typescript
const [toggleTodo] = useMutation(TOGGLE_TODO, {
  optimisticResponse: {
    toggleTodo: {
      __typename: 'Todo',
      id: todo.id,
      completed: !todo.completed,
    },
  },
});
```

## Fetch Policies

| Policy | Behavior | Use When |
|--------|----------|----------|
| `cache-first` | Cache hit → no network | Static/rarely-changing data |
| `cache-and-network` | Return cache, then update from network | Default for most queries |
| `network-only` | Always fetch, update cache | After mutations, real-time data |
| `cache-only` | Never fetch | Local state, offline |
| `no-cache` | Always fetch, skip cache | One-off requests, sensitive data |

## Common Mistakes

### Missing `__typename` in optimistic response
```typescript
// BUG: cache can't normalize — optimistic update silently fails
optimisticResponse: { toggleTodo: { id: '1', completed: true } }

// FIX: always include __typename
optimisticResponse: { toggleTodo: { __typename: 'Todo', id: '1', completed: true } }
```

### Stale cache after list mutation
```typescript
// BUG: new item not in list — cache has item but list query doesn't reference it
const [addTodo] = useMutation(ADD_TODO);

// FIX: use refetchQueries or update cache manually
const [addTodo] = useMutation(ADD_TODO, {
  refetchQueries: [{ query: GET_TODOS }],
});
```

### Over-fetching with no fragments
```typescript
// BAD: 3 queries repeat the same 15 fields
query GetTodo { todo { id title desc status assignee { id name email avatar } } }
query GetTodos { todos { id title desc status assignee { id name email avatar } } }

// GOOD: shared fragment
fragment TodoFields on Todo { id title desc status assignee { ...UserFields } }
```

### Wrong typePolicies merge behavior
```typescript
// BUG: paginated list appends duplicate items on refetch
typePolicies: { Query: { fields: { todos: { merge: true } } } }

// FIX: replace for non-paginated, custom merge for paginated
todos: { merge: false } // non-paginated: replace
todos: {
  keyArgs: ['status'],
  merge(existing = [], incoming) { return [...existing, ...incoming]; },
} // paginated: append
```

## Type Generation (Required)
```bash
npm i -D @graphql-codegen/cli @graphql-codegen/client-preset
npx graphql-codegen --config codegen.ts
```

```typescript
import type { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  schema: 'http://localhost:4000/graphql',
  documents: ['src/**/*.tsx', 'src/**/*.ts'],
  generates: {
    './src/gql/': { preset: 'client' },
  },
};
export default config;
```
