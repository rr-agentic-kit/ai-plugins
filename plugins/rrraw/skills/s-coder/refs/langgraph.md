# LangGraph Standards

## Version
LangGraph 0.2.x+. Pin exact version.

## Core Concepts — Apply Correctly
- **State**: single typed dict shared across all nodes — define explicitly with `TypedDict`
- **Nodes**: pure functions `(state) -> partial_state_update` — no side effects except tools
- **Edges**: deterministic or conditional routing — keep routing logic simple and testable
- **Checkpointer**: persistence layer — required for long-running or resumable workflows

## State Design
- Define state as `TypedDict` with explicit types — never use untyped dicts
- Use `Annotated` with reducers for fields that accumulate: `Annotated[list, operator.add]`
- Keep state flat where possible — nested state makes debugging hard
- Never store sensitive data in state that gets checkpointed without encryption
- Include `error` and `iteration_count` fields in state for loop control

```python
from typing import TypedDict, Annotated
import operator


class WorkflowState(TypedDict):
    messages: Annotated[list, operator.add]
    iteration_count: int
    error: str | None
    result: str | None
```

## Node Design
- Nodes must be pure functions — given same state, return same partial update
- One responsibility per node — split complex logic into multiple nodes
- Return only the fields being updated — not the full state
- Handle exceptions inside nodes — return error state rather than raising
- Never hardcode model/tool config inside nodes — pass via state or graph config

## Edge / Routing Design
- Conditional edges must be exhaustive — handle all possible state values
- Name conditional routing functions clearly: `should_retry`, `route_by_intent`
- Always include a terminal or error route — never leave a path that loops forever
- Guard infinite loops: check `iteration_count` in conditional edges

```python
def should_retry(state: WorkflowState) -> str:
    if state["error"] and state["iteration_count"] < 3:
        return "retry"
    elif state["error"]:
        return "fail"
    return "continue"
```

## Loop Control (Critical)
- Every loop must have a max iteration guard — no exceptions
- Track iterations in state, not in node local variables
- On max iterations reached: transition to a failure node, not silent termination
- Log each iteration with iteration number and state summary

## Tools / Agents
- Define tools with `@tool` decorator and full docstrings — LLM uses docstring for selection
- Validate tool inputs with Pydantic before execution
- Tool errors must be caught and returned as tool messages — never raise uncaught
- Use `ToolNode` for standardized tool execution — don't implement manually
- Audit log all tool calls in regulated contexts

## Checkpointing / Persistence
- Use `MemorySaver` for development only — never in production
- Production: use `PostgresSaver` or `SqliteSaver` with proper connection management
- Encrypt checkpoint data at rest if state contains sensitive fields
- Set TTL/cleanup policy for checkpoints — unbounded growth is a production risk
- Use thread IDs consistently — losing thread ID means losing conversation state

## Human-in-the-Loop
- Use `interrupt_before` / `interrupt_after` for explicit human checkpoints
- Document which nodes require human approval in graph design
- Never auto-resume from interrupt without explicit signal
- Log interrupt events with context for audit trail

## Observability
- Enable LangSmith tracing in dev/staging: `LANGSMITH_TRACING=true`
- Log state transitions with node name, input summary, output summary
- Track: total tokens, latency per node, tool call count, iteration count
- Production: pipe traces to your own observability stack — not LangSmith

## Testing
- Unit test each node function in isolation with mock state
- Test all conditional edge paths — especially error and max-iteration paths
- Integration test full graph with `MemorySaver` and controlled LLM responses
- Test adversarial inputs and malformed tool responses
- Verify loop termination for every cycle in the graph