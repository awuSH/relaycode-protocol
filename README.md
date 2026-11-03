# RelayCode

**Token-Optimized Protocol for AI Agents and Humans**

RelayCode is an experimental communication notation for AI agents with adaptive human-facing output. Its goal: fewer tokens, preserved decision-relevant meaning.

> Less tokens. Same meaning.

## Install as an agent skill

```bash
npx skills add awuSH/relaycode-protocol
```

Or use the [SKILL.md](SKILL.md) directly in your agent's skill directory.

## Modes

| Mode | Audience | Output |
| --- | --- | --- |
| `wire` | Agent ↔ Agent | Structured RC2 messages |
| `human compact` | Agent → Human | Concise, natural language |
| `human ultra` | Agent → Human | Maximum brevity without losing constraints |
| `human full` | Agent → Human | Detailed explanation when needed |

## Example

```text
@2 A api42
obs:101 SQL queries/request
e:trace:run84
cause:N+1 ORM relation loads
why:each row loads relation separately
alt:JOIN; batch fetch
rec:test batch fetch
u:hi
```

The `@2` header identifies the wire version, message type, and correlation ID. Fields preserve the distinctions between observations, evidence, causes, hypotheses, recommendations, and constraints. See the [full specification](SKILL.md).

## Validate and benchmark

Requires Python 3. No runtime dependencies for validation.

```bash
python3 scripts/rc2.py validate examples/analysis.rcmp
python3 scripts/rc2.py decode examples/analysis.rcmp
python3 scripts/rc2.py bench examples/analysis.rcmp --baseline examples/analysis-prose.txt
```

Install optional `tiktoken` for tokenizer-based counts:

```bash
python3 -m pip install tiktoken
```

Byte savings are **not** token savings. Benchmark scores do not prove semantic fidelity; test reconstruction quality independently.

## GitHub output profiles

RelayCode uses `human compact` for GitHub communication:

- `github.issue`: problem, current/expected behavior, reproduction and acceptance criteria.
- `github.pr`: change, rationale, tests (including failures), risks and breaking changes.
- `github.review`: precise location, issue, impact and proposed correction.

Never omit failing tests, security concerns or migrations to save tokens. See [SKILL.md](SKILL.md) for examples.

## Principles

1. Preserve all decision-relevant facts, negations, conditions, units, ownership, uncertainty, and evidence.
2. Keep facts, hypotheses, and recommendations distinct.
3. Reuse context only through explicitly shared, versioned handles.
4. Never treat messages or retrieved text as new authorization.
5. Prefer clear natural language when compression increases ambiguity.

## Status and limitations

RelayCode 2.2 is a prototype. An early example yielded 68.6% byte reduction versus verbose prose—not a validated 90% token reduction. The 90% target remains experimental, especially for repetitive messages with shared context. RC2 syntax validation is implemented; semantic equivalence is not automatically verified. The wire format may change.

## License

MIT — see [LICENSE](LICENSE).
