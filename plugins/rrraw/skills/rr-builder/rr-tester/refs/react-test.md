# React Test Reference (Vitest + Testing Library + MSW)

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `userEvent.setup()` then `user.click()` | `fireEvent.click()` (skips browser event sequence) |
| `screen.getByRole('button', { name })` | `screen.getByTestId('submit-btn')` |
| `screen.getByLabelText(/email/i)` | `container.querySelector('input.email')` |
| `waitFor(() => expect(...))` for async | `await new Promise(r => setTimeout(r, 100))` |
| `screen.queryByText(...)` to assert absence | `try { getByText } catch {}` |
| One assertion per behavior | Multiple unrelated assertions in one test |
| MSW for API mocking | `vi.mock()` on fetch/axios |
| Assert what user sees (`getByRole`, `getByText`) | Assert internal state or implementation details |

## API Mocking with MSW

Use MSW (Mock Service Worker) for all HTTP/GraphQL mocking. Intercepts at the network level — components use real fetch/client code. Vue tests use the same pattern (see [vue-test.md](vue-test.md)).

```typescript
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

const server = setupServer(
  http.get('/api/todos', () =>
    HttpResponse.json([{ id: '1', title: 'Test Todo' }]),
  ),
  http.post('/api/todos', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: '2', ...body }, { status: 201 })
  }),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

Override handlers per test for error scenarios:

```typescript
it('should show error on server failure', async () => {
  server.use(
    http.get('/api/todos', () => HttpResponse.json(null, { status: 500 })),
  )

  render(<TodoList />, { wrapper: createWrapper() })

  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
```

## Type-Safe Mock Factories

```typescript
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

function createUserMock(overrides?: DeepPartial<User>): User {
  return {
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    profile: { age: 25, bio: 'Test bio' },
    ...overrides,
  };
}

const user = createUserMock({ name: 'Custom Name' });
```

## Wrapper for Providers

Wrap components that use TanStack Query, Apollo, Router, or other context providers. Create a test-specific wrapper with safe defaults.

```typescript
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

render(<MyComponent />, { wrapper: createWrapper() })
```

For Apollo Client tests, replace `QueryClientProvider` with `MockedProvider` from `@apollo/client/testing`.

## Common Mistakes

### Testing implementation details
```typescript
// BAD: tests internal state, breaks on refactor
expect(component.state.isLoading).toBe(true)

// GOOD: test what user sees
expect(screen.getByRole('progressbar')).toBeInTheDocument()
```

### Snapshot overuse
```typescript
// BAD: brittle, no intent, fails on any markup change
expect(container).toMatchSnapshot()

// GOOD: assert specific behavior
expect(screen.getByText('Welcome, Test User')).toBeInTheDocument()
```

### Missing wrapper for data-fetching components
```typescript
// BUG: "No QueryClient set" or "No ApolloProvider" error
render(<TodoList />)

// FIX: wrap with test provider
render(<TodoList />, { wrapper: createWrapper() })
```
