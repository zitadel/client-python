
## Guardrails — do not let a regeneration re-break CI

This repo's CI runs gates the generator's own petstore build does not: dependency
hygiene, analyzers, type checks. After `make generate`, run this repo's real CI gates
locally (not just `make test`) before pushing. Specifically:

- **Declare only the dependencies THIS repo's emitted tests actually use.** Do NOT add
  dependencies to match the generator's `.openapi-generator/DEV-DEPENDENCIES` file: that
  file lists deps for the generator's full petstore test suite, most of which this repo
  does not receive. An unused declared dependency fails the dependency-analysis gate; a
  used-but-undeclared one fails it too. Check with the repo's own dependency gate.
- **Fix a failing gate in the generator, not by hand-editing generated files** — a hand
  edit is lost on the next regeneration. Only keep-listed (hand-written) files are safe
  to edit here.
- **A green `make test` is not a green CI.** The tests can pass while a lint/analyze/
  type gate fails; verify each gate this repo's CI defines.
