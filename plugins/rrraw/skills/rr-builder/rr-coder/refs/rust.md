# Rust Patterns

Idiomatic Rust patterns for error handling, async, modules, and type safety.

## Stack Reference

| Component | Tool | Purpose |
|-----------|------|---------|
| Error handling (library) | `thiserror` | Typed, recoverable errors |
| Error handling (app) | `anyhow` | Contextual error chains |
| Async runtime | `tokio` | All async code |
| Serialization | `serde` | JSON, config, IPC |
| Logging | `tracing` | Structured, async-aware |

---

## 1. Error Handling

### Library Code: `thiserror`

Use `thiserror` for errors that callers need to match on. Define one error enum per module/feature.

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ArtifactError {
    #[error("artifact not found: {0}")]
    NotFound(String),
    
    #[error("invalid metadata: {0}")]
    InvalidMetadata(String),
    
    #[error("git operation failed")]
    Git(#[from] git2::Error),
    
    #[error("IO error: {path}")]
    Io {
        path: String,
        #[source]
        source: std::io::Error,
    },
}
```

- `#[from]` for automatic conversion from underlying errors
- `#[source]` to preserve error chain without `From` impl
- Named fields for context (`path`, `id`, etc.)

### Application Code: `anyhow`

Use `anyhow` at application boundaries (CLI, Tauri commands) where you need context but don't need typed matching.

```rust
use anyhow::{Context, Result};

fn sync_artifacts(repo_url: &str) -> Result<()> {
    let repo = clone_repo(repo_url)
        .context("failed to clone artifact repository")?;
    
    let metadata = parse_metadata(&repo)
        .with_context(|| format!("failed to parse metadata from {}", repo_url))?;
    
    Ok(())
}
```

- `context()` for static messages
- `with_context(|| ...)` for dynamic messages (avoids allocation if no error)
- `bail!("message")` for early returns with error
- `ensure!(condition, "message")` for assertions

### Never Use `unwrap()` in Production

```rust
// Bad: panics on None/Err
let value = map.get("key").unwrap();

// Good: propagate error
let value = map.get("key").ok_or_else(|| ArtifactError::NotFound("key".into()))?;

// Good: with expect (only when truly impossible)
let value = map.get("key").expect("key was validated in constructor");

// Good: provide default
let value = map.get("key").unwrap_or(&default);
```

---

## 2. Async Patterns

### Async Function Guidelines

```rust
// Prefer async fn over manual Future
async fn fetch_artifact(id: &str) -> Result<Artifact> {
    // ...
}

// Use join! for parallel independent operations
async fn fetch_all(ids: &[String]) -> Result<Vec<Artifact>> {
    let futures: Vec<_> = ids.iter().map(|id| fetch_artifact(id)).collect();
    let results = futures::future::join_all(futures).await;
    results.into_iter().collect()
}

// Use spawn for concurrent background tasks
fn start_sync_task(state: Arc<AppState>) {
    tokio::spawn(async move {
        loop {
            if let Err(e) = sync_artifacts(&state).await {
                tracing::error!("sync failed: {:#}", e);
            }
            tokio::time::sleep(Duration::from_secs(300)).await;
        }
    });
}
```

### Avoid Blocking in Async

```rust
// Bad: blocks the async runtime
async fn read_large_file(path: &Path) -> Result<Vec<u8>> {
    std::fs::read(path).map_err(Into::into)  // Blocking!
}

// Good: use tokio's async fs
async fn read_large_file(path: &Path) -> Result<Vec<u8>> {
    tokio::fs::read(path).await.map_err(Into::into)
}

// Good: spawn_blocking for CPU-bound work
async fn parse_large_json(data: Vec<u8>) -> Result<Metadata> {
    tokio::task::spawn_blocking(move || {
        serde_json::from_slice(&data).map_err(Into::into)
    })
    .await?
}
```

---

## 3. Module Organization

### Feature-Based Structure

```
crates/core/src/
  artifacts/
    mod.rs           # Public API, re-exports
    sync.rs          # Git clone, pull operations
    metadata.rs      # JSON parsing, validation
    error.rs         # ArtifactError enum
  ai_tools/
    mod.rs
    detection.rs
    installation.rs
    error.rs
  lib.rs             # Crate root, public exports
```

### Module Visibility

```rust
// lib.rs - expose public API only
pub mod artifacts;
pub mod ai_tools;

// Re-export commonly used types
pub use artifacts::{Artifact, ArtifactError};
pub use ai_tools::{AiTool, detect_ai_tools};

// artifacts/mod.rs - internal organization
mod sync;
mod metadata;
mod error;

// Public API
pub use error::ArtifactError;
pub use metadata::Artifact;

pub async fn list_artifacts(repo: &Repository) -> Result<Vec<Artifact>, ArtifactError> {
    sync::ensure_updated(repo).await?;
    metadata::parse_all(repo)
}
```

---

## 4. Type Safety

### Newtype Pattern

Prevent mixing up IDs, paths, and other stringly-typed values:

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ArtifactId(String);

impl ArtifactId {
    pub fn new(id: impl Into<String>) -> Self {
        Self(id.into())
    }
    
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

// Now these can't be confused
fn get_artifact(id: ArtifactId) -> Result<Artifact> { ... }
fn get_tool(id: ToolId) -> Result<AiTool> { ... }
```

### State Machines with Enums

Make invalid states unrepresentable:

```rust
// Bad: boolean flags allow invalid combinations
struct Sync {
    is_running: bool,
    is_paused: bool,  // What if both true?
    error: Option<String>,
}

// Good: enum enforces valid states
enum SyncState {
    Idle,
    Running { started_at: Instant },
    Paused { progress: usize },
    Failed { error: ArtifactError },
    Completed { artifacts: Vec<Artifact> },
}
```

---

## 5. Traits and Composition

### Trait-Based Abstraction

```rust
// Define behavior, not inheritance
#[async_trait]
pub trait ArtifactSource {
    async fn list(&self) -> Result<Vec<Artifact>, ArtifactError>;
    async fn get(&self, id: &ArtifactId) -> Result<Artifact, ArtifactError>;
}

// Implement for different sources
pub struct GitSource { repo: Repository }
pub struct LocalSource { path: PathBuf }

#[async_trait]
impl ArtifactSource for GitSource {
    async fn list(&self) -> Result<Vec<Artifact>, ArtifactError> {
        // Git-specific implementation
    }
}
```

### Composition Over Inheritance

```rust
// Compose capabilities
pub struct ArtifactManager {
    source: Box<dyn ArtifactSource>,
    cache: Cache,
    logger: tracing::Span,
}

impl ArtifactManager {
    pub async fn get_cached(&self, id: &ArtifactId) -> Result<Artifact> {
        if let Some(artifact) = self.cache.get(id) {
            return Ok(artifact);
        }
        let artifact = self.source.get(id).await?;
        self.cache.insert(id.clone(), artifact.clone());
        Ok(artifact)
    }
}
```

---

## 6. Logging with Tracing

Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md).

### Structured Logging

```rust
use tracing::{debug, error, info, instrument, warn};

#[instrument(skip(repo), fields(artifact_count))]
pub async fn sync_artifacts(repo: &Repository) -> Result<Vec<Artifact>> {
    info!("starting artifact sync");
    
    let artifacts = fetch_all(repo).await?;
    tracing::Span::current().record("artifact_count", artifacts.len());
    
    for artifact in &artifacts {
        debug!(id = %artifact.id, name = %artifact.name, "processed artifact");
    }
    
    info!("sync complete");
    Ok(artifacts)
}
```

### Error Logging

```rust
// Log error with full context
if let Err(e) = sync_artifacts(&repo).await {
    error!(error = ?e, "sync failed");  // ?e for Debug format
    // or
    error!(error = %e, "sync failed");  // %e for Display format
}
```

---

## 7. Tauri Patterns

Tauri-specific patterns for desktop apps.

### IPC Commands

```rust
use tauri::State;

#[tauri::command]
async fn list_artifacts(state: State<'_, AppState>) -> Result<Vec<Artifact>, String> {
    state.core
        .list_artifacts()
        .await
        .map_err(|e| format!("{:#}", e))
}
```

**Key rules**:
- Return `Result<T, String>` - Tauri serializes errors as strings
- Use `State<'_, T>` for shared state access
- Mark `async` for any I/O operations
- Use `{:#}` format for error chains (includes causes)

### Command with Parameters

```rust
#[tauri::command]
async fn get_artifact(
    id: String,
    state: State<'_, AppState>,
) -> Result<Artifact, String> {
    let artifact_id = ArtifactId::new(&id);
    state.core
        .get_artifact(&artifact_id)
        .await
        .map_err(|e| format!("{:#}", e))
}
```

### Registering Commands

```rust
fn main() {
    tauri::Builder::default()
        .manage(AppState::new())
        .invoke_handler(tauri::generate_handler![
            list_artifacts,
            get_artifact,
            sync_artifacts,
        ])
        .run(tauri::generate_context!())
        .expect("error running tauri application");
}
```

### State Management

```rust
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct AppState {
    pub core: Arc<AppCore>,
    pub config: Arc<RwLock<AppConfig>>,
    pub sync_status: Arc<RwLock<SyncStatus>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            core: Arc::new(AppCore::new()),
            config: Arc::new(RwLock::new(AppConfig::default())),
            sync_status: Arc::new(RwLock::new(SyncStatus::Idle)),
        }
    }
}
```

### System Tray

```rust
use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem,
};

fn create_tray() -> SystemTray {
    let menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("open", "Open Workbench"))
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("sync", "Sync Now"))
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit", "Quit"));
    
    SystemTray::new().with_menu(menu)
}

fn handle_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick { .. } => {
            if let Some(window) = app.get_window("main") {
                window.show().unwrap();
                window.set_focus().unwrap();
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "open" => {
                if let Some(window) = app.get_window("main") {
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
            }
            "sync" => {
                let app = app.clone();
                tauri::async_runtime::spawn(async move {
                    if let Err(e) = trigger_sync(&app).await {
                        eprintln!("Sync failed: {:#}", e);
                    }
                });
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        },
        _ => {}
    }
}
```

### Multi-Window

```rust
use tauri::{Manager, WindowBuilder, WindowUrl};

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    // Check if window already exists
    if let Some(window) = app.get_window("settings") {
        window.set_focus().map_err(|e| e.to_string())?;
        return Ok(());
    }
    
    // Create new window
    WindowBuilder::new(&app, "settings", WindowUrl::App("settings.html".into()))
        .title("Settings")
        .inner_size(600.0, 400.0)
        .resizable(false)
        .build()
        .map_err(|e| e.to_string())?;
    
    Ok(())
}
```

### Events

```rust
#[tauri::command]
async fn start_long_operation(window: Window) -> Result<(), String> {
    for progress in 0..=100 {
        window.emit("progress", progress)
            .map_err(|e| e.to_string())?;
        tokio::time::sleep(Duration::from_millis(50)).await;
    }
    Ok(())
}
```

### Typed Error Responses

```rust
use serde::Serialize;

#[derive(Serialize)]
pub struct CommandError {
    pub code: String,
    pub message: String,
}

impl From<ArtifactError> for CommandError {
    fn from(e: ArtifactError) -> Self {
        match &e {
            ArtifactError::NotFound(id) => CommandError {
                code: "NOT_FOUND".into(),
                message: format!("Artifact '{}' not found", id),
            },
            ArtifactError::Git(_) => CommandError {
                code: "GIT_ERROR".into(),
                message: "Git operation failed".into(),
            },
            _ => CommandError {
                code: "UNKNOWN".into(),
                message: format!("{:#}", e),
            },
        }
    }
}

#[tauri::command]
async fn get_artifact(
    id: String,
    state: State<'_, AppState>,
) -> Result<Artifact, CommandError> {
    state.core
        .get_artifact(&ArtifactId::new(&id))
        .await
        .map_err(Into::into)
}
```

---

## 8. Testing Patterns

### Unit Tests (In-Module)

```rust
// src/artifacts/metadata.rs

pub fn parse_metadata(json: &str) -> Result<Artifact, ArtifactError> {
    // implementation
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_metadata_valid_json_returns_artifact() {
        // Arrange
        let json = r#"{"name": "test-skill", "version": "1.0.0"}"#;
        
        // Act
        let result = parse_metadata(json);
        
        // Assert
        assert!(result.is_ok());
        let artifact = result.unwrap();
        assert_eq!(artifact.name, "test-skill");
    }

    #[test]
    fn parse_metadata_invalid_json_returns_error() {
        let json = "not valid json";
        
        let result = parse_metadata(json);
        
        assert!(matches!(result, Err(ArtifactError::InvalidMetadata(_))));
    }
}
```

- `#[cfg(test)]` compiles tests only in test mode
- `use super::*` imports parent module
- Arrange-Act-Assert structure
- Test both happy path and error paths

### Integration Tests

```
crates/core/
  src/
    lib.rs
  tests/
    integration.rs
    fixtures/
      valid-artifact.json
```

```rust
// tests/integration.rs
use core::{ArtifactSource, GitSource};

#[tokio::test]
async fn git_source_lists_artifacts_from_repo() {
    let source = GitSource::new("https://github.com/test/artifacts.git")
        .await
        .expect("failed to create source");
    
    let artifacts = source.list().await.expect("failed to list");
    
    assert!(!artifacts.is_empty());
}
```

### Async Tests

```rust
#[tokio::test]
async fn fetch_artifact_returns_data() {
    let result = fetch_artifact("test-id").await;
    assert!(result.is_ok());
}

// With timeout
#[tokio::test(flavor = "multi_thread")]
async fn sync_completes_within_timeout() {
    let result = tokio::time::timeout(
        Duration::from_secs(5),
        sync_artifacts(),
    ).await;
    
    assert!(result.is_ok(), "sync timed out");
}
```

### Parameterized Tests with rstest

```rust
use rstest::rstest;

#[rstest]
#[case("1.0.0", true)]
#[case("1.0", true)]
#[case("invalid", false)]
#[case("", false)]
fn version_validation(#[case] input: &str, #[case] expected: bool) {
    assert_eq!(is_valid_version(input), expected);
}

// With fixtures
#[fixture]
fn test_artifact() -> Artifact {
    Artifact {
        id: ArtifactId::new("test"),
        name: "Test Artifact".into(),
        version: "1.0.0".into(),
    }
}

#[rstest]
fn artifact_has_valid_id(test_artifact: Artifact) {
    assert!(!test_artifact.id.as_str().is_empty());
}
```

### Mocking with mockall

```rust
use mockall::{automock, predicate::*};

#[automock]
#[async_trait]
pub trait ArtifactSource {
    async fn list(&self) -> Result<Vec<Artifact>, ArtifactError>;
    async fn get(&self, id: &ArtifactId) -> Result<Artifact, ArtifactError>;
}

#[tokio::test]
async fn manager_uses_source_to_fetch() {
    let mut mock = MockArtifactSource::new();
    
    mock.expect_get()
        .with(eq(ArtifactId::new("test")))
        .times(1)
        .returning(|_| Ok(Artifact::default()));
    
    let manager = ArtifactManager::new(Box::new(mock));
    let result = manager.get(&ArtifactId::new("test")).await;
    
    assert!(result.is_ok());
}
```

### Test Fixtures

```rust
pub fn fixture_path(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join(name)
}

pub fn load_fixture(name: &str) -> String {
    std::fs::read_to_string(fixture_path(name))
        .expect("failed to load fixture")
}

#[test]
fn parse_fixture_file() {
    let json = load_fixture("valid-artifact.json");
    let result = parse_metadata(&json);
    assert!(result.is_ok());
}
```

### Temporary Directories

```rust
use tempfile::TempDir;

#[test]
fn writes_to_temp_directory() {
    let temp = TempDir::new().expect("failed to create temp dir");
    let path = temp.path().join("output.json");
    
    write_artifact(&path, &artifact).expect("failed to write");
    
    assert!(path.exists());
    // temp dir cleaned up when dropped
}
```

### Error Testing

```rust
#[test]
fn returns_not_found_for_missing_artifact() {
    let result = get_artifact(&ArtifactId::new("nonexistent"));
    
    match result {
        Err(ArtifactError::NotFound(id)) => {
            assert_eq!(id, "nonexistent");
        }
        _ => panic!("expected NotFound error"),
    }
}

// Using matches! macro
#[test]
fn returns_validation_error_for_invalid_input() {
    let result = validate_artifact(&invalid_artifact);
    
    assert!(matches!(result, Err(ArtifactError::InvalidMetadata(_))));
}
```

### Test Commands

```bash
# Run all tests
cargo test

# Run tests in specific crate
cargo test -p core

# Run only unit tests (no integration tests)
cargo test --lib

# Run specific integration test file
cargo test --test integration

# Run tests matching pattern
cargo test artifact

# Show output from passing tests
cargo test -- --nocapture

# Run ignored tests
cargo test -- --ignored
```

### Coverage

```bash
# Install cargo-tarpaulin
cargo install cargo-tarpaulin

# Run coverage
cargo tarpaulin --out Html

# Ignore test code in coverage
cargo tarpaulin --ignore-tests --out Html
```
