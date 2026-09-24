# AGENTS — zitadel/client-python

## What this is

This SDK is **generated**. It is one of six Zitadel client SDKs produced from the same
OpenAPI spec by [openapi-generator-plus](https://github.com/mridang/openapi-generator-plus),
which emits the same SDK in twelve languages. Almost nothing here is written by hand, and
almost every change belongs in the generator, not in this repo.

- Generator: `python-plus`, run from the `openapi-generator-plus:enhanced` image.
- Spec: `../sdk/spec/client/$(VERSION)/index.json` — see `VERSION` in the `Makefile`.
- Generator options for this SDK: `proc.yml`.

## Project structure: generated versus hand-written

`.openapi-generator-ignore` is the **keep-list**: every path in it is hand-written and the
generator will not overwrite it. Everything else is generator-owned and is replaced wholesale
on the next run, so an edit to it is lost silently.

Hand-written here: the bespoke authenticators under `zitadel_client/auth/`, their tests, the
integration specs, and this repo's own tooling config.

**Before editing any file, check whether it is on the keep-list.** If it is not, the fix
belongs in the generator's templates.

## Commands

```bash
devbox run -- make generate   # regenerate from the spec, then format
devbox run -- make test       # pytest
devbox run -- make lint
```

`make generate` rewrites a large part of the tree; review the diff rather than assuming it
is noise. Save long output to a file and grep it instead of piping to `tail`.

## The error contract

Every Zitadel SDK raises the same error for the same failure, and so do the twelve languages
the generator supports. The types live in `zitadel_client.errors`:

```
ZitadelException                        root
├── ApiException                        an HTTP response came back
│   ├── ClientException  → BadRequest(400) Unauthorized(401) Forbidden(403)
│   │                  NotFound(404) Conflict(409) UnprocessableEntity(422)
│   ├── ServerException  → InternalServerError(500)
│   └── NetworkException                no response: refused, DNS, TLS, reset. status 0
│       └── NetworkTimeoutException     the request timed out. status 0
├── SerializationException              every encode/decode failure
├── OAuth2ServerException               token endpoint answered non-2xx
└── OAuth2TokenException                token endpoint answered 2xx but unusably
```

- A caller mistake is **not** an SDK error: a bad proxy URL, a missing CA file, empty
  credentials, a token requested before the auth code was exchanged, or use after close
  raises the language's own argument or state error.
- Hand-written code must use these types, never invent its own, and never catch a failure
  only to rewrap it as something else.
- `ApiException.fromResponse(status, headers, body)` maps a status to the right subclass. Use it
  rather than writing another status table — the OIDC discovery code already does.

## Adding a dependency

The generator emits tests that need dev dependencies (for example the OpenTelemetry SDK for
the trace-context tests). This repo keeps its own `pyproject.toml`, so the generator cannot add
them: when a regeneration brings in a test that needs something new, add it there, or the
suite dies at collection.

## Where to fix what

| Symptom | Fix it in |
|---|---|
| Wrong behaviour in generated code | the generator's templates for this language |
| Wrong behaviour in a bespoke authenticator | here, on the keep-list |
| A difference between this SDK and another Zitadel SDK | the generator — they are meant to be identical |
| A lint config fighting generated code | the generator, then regenerate |
