# Tauri v2 — React Frontend

Tauri-specific patterns for desktop apps. For general React: see `react-18.md`.
For data fetching: see `react-query.md` (REST) or `react-apollo.md` (GraphQL).

---

## 1. Import Paths (v2 Breaking Changes)

v2 restructured all JS APIs. Core moved, OS features became plugins.

| v1 | v2 |
|----|-----|
| `@tauri-apps/api/tauri` | `@tauri-apps/api/core` |
| `@tauri-apps/api/fs` | `@tauri-apps/plugin-fs` |
| `@tauri-apps/api/dialog` | `@tauri-apps/plugin-dialog` |
| `@tauri-apps/api/shell` | `@tauri-apps/plugin-shell` |
| `@tauri-apps/api/http` | `@tauri-apps/plugin-http` |
| `@tauri-apps/api/clipboard` | `@tauri-apps/plugin-clipboard-manager` |
| `tauri-plugin-store` (Store) | `@tauri-apps/plugin-store` (LazyStore) |

Plugins require Cargo dependency + `tauri::Builder::default().plugin(...)` registration.

---

## 2. Command Invocation

Type-safe `invoke()` wrapper using `ApiResponse<T>` from `react-18.md`.

```typescript
import { invoke } from '@tauri-apps/api/core';

async function tauriCall<TResponse, TRequest = void>(
  command: string,
  args?: TRequest
): Promise<ApiResponse<TResponse>> {
  try {
    const data = await invoke<TResponse>(command, args);
    return { data, error: null };
  } catch (e) {
    return { data: null, error: parseCommandError(e) };
  }
}
```

Tauri errors arrive as **strings from Rust** — parse before use:

```typescript
function parseCommandError(e: unknown): ApiError {
  if (typeof e === 'string') {
    try { return JSON.parse(e); }
    catch { return { code: 'TAURI_ERROR', message: e }; }
  }
  return { code: 'UNKNOWN', message: String(e) };
}
```

### With TanStack Query

Use `tauriCall` as `queryFn`/`mutationFn`. See `react-query.md` for patterns.

```typescript
const { data } = useQuery({
  queryKey: artifactKeys.detail(id),
  queryFn: () => tauriCall<Artifact>('get_artifact', { id }),
  select: (result) => {
    if (result.error) throw new Error(result.error.message);
    return result.data;
  },
});
```

---

## 3. Event System

Tauri events bridge Rust ↔ JS and support multi-window broadcast.

```typescript
import { listen, emit, UnlistenFn } from '@tauri-apps/api/event';

function useTauriEvent<T>(event: string, handler: (payload: T) => void) {
  useEffect(() => {
    let unlisten: UnlistenFn | undefined;
    listen<T>(event, (e) => handler(e.payload)).then((fn) => {
      unlisten = fn;
    });
    return () => { unlisten?.(); };
  }, [event, handler]);
}

async function broadcastEvent<T>(event: string, payload: T) {
  await emit(event, payload);
}
```

For window-scoped events:

```typescript
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';

const appWebview = getCurrentWebviewWindow();
appWebview.emit('route-changed', { url: window.location.href });
```

---

## 4. Window Management

```typescript
import { getCurrentWindow } from '@tauri-apps/api/window';

function useWindowFocus() {
  const [focused, setFocused] = useState(true);

  useEffect(() => {
    const window = getCurrentWindow();
    let unlisten: UnlistenFn | undefined;
    window.onFocusChanged(({ payload }) => {
      setFocused(payload);
    }).then((fn) => { unlisten = fn; });
    return () => { unlisten?.(); };
  }, []);

  return focused;
}
```

Window operations (custom titlebar, multi-window):

```typescript
const appWindow = getCurrentWindow();
await appWindow.setTitle('New Title');
await appWindow.minimize();
await appWindow.toggleMaximize();
await appWindow.close();
await appWindow.center();
```

---

## 5. Backend Persistence (via Commands)

Desktop apps persist to SQLite/filesystem through Rust commands — not `localStorage`.

```typescript
async function loadLayout(): Promise<WorkspaceLayout> {
  const result = await tauriCall<string>('get_layout');
  if (result.error) return DEFAULT_LAYOUT;
  return JSON.parse(result.data);
}

async function saveLayout(layout: WorkspaceLayout): Promise<void> {
  await invoke('save_layout', { layout: JSON.stringify(layout) });
}
```

---

## 6. Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `invoke()` for Rust backend calls | `fetch()` to localhost sidecar |
| `listen()`/`emit()` for cross-window IPC | `BroadcastChannel` or `postMessage` |
| `@tauri-apps/plugin-*` for OS features | `@tauri-apps/api/fs` (v1 paths) |
| `getCurrentWebviewWindow()` for window-scoped events | `getCurrentWindow()` for events (wrong API) |
| Rust commands for persistence (SQLite, files) | `localStorage`/`IndexedDB` for important data |
| `LazyStore` from plugin-store for key-value | Rolling custom config file handling |
| Structured error JSON from Rust commands | Untyped string errors |
| `tauriCall` wrapper + TanStack Query | Raw `invoke()` + `useState`/`useEffect` |

## 7. Common Mistakes

### Forgetting unlisten cleanup
```typescript
// BUG: listener accumulates on re-render, events fire multiple times
useEffect(() => {
  listen('update', handler);
}, []);

// FIX: await and cleanup
useEffect(() => {
  let unlisten: UnlistenFn | undefined;
  listen('update', handler).then((fn) => { unlisten = fn; });
  return () => { unlisten?.(); };
}, [handler]);
```

### Using v1 import paths
```typescript
// BUG: module not found at runtime
import { invoke } from '@tauri-apps/api/tauri';
import { readTextFile } from '@tauri-apps/api/fs';

// FIX: v2 paths
import { invoke } from '@tauri-apps/api/core';
import { readTextFile } from '@tauri-apps/plugin-fs';
```

### Missing plugin permission in capabilities
```json
// BUG: "not allowed" error at runtime — plugin registered but not permitted
// FIX: add to src-tauri/capabilities/default.json
{
  "permissions": [
    "core:default",
    "fs:default",
    "dialog:default",
    "shell:default"
  ]
}
```
