# zitadel_client SDK

Auto-generated Python SDK client for the Zitadel SDK API.

## Requirements

- Python 3.13+
- `pip`

Install runtime and development dependencies:

```bash
pip install -e . --group dev
```

## Format

```bash
ruff format .
```

## Lint

```bash
ruff check .
```

## Type-check

```bash
mypy .
```

## Install

```bash
pip install -e .
```

## Test

```bash
pytest
```

## Package

- Name: `zitadel_client`
- Version: `0.0.1`

## OpenAPI type mapping

This SDK leans on pydantic 2's native typed surfaces:

| OAS `type` / `format`              | Python type                       |
| ---------------------------------- | --------------------------------- |
| `string`                           | `pydantic.StrictStr`              |
| `integer`                          | `pydantic.StrictInt`              |
| `number`                           | `pydantic.StrictFloat`            |
| `boolean`                          | `pydantic.StrictBool`             |
| `string`, `format: uri`            | `pydantic.HttpUrl`                |
| `string`, `format: uri-reference`  | `pydantic.StrictStr` (may be relative) |
| `string`, `format: uri-template`   | `pydantic.StrictStr` (RFC 6570)   |
| `string`, `format: email`          | `pydantic.EmailStr`               |
| `string`, `format: password`       | `pydantic.SecretStr`              |
| `string`, `format: ipv4`           | `ipaddress.IPv4Address`           |
| `string`, `format: ipv6`           | `ipaddress.IPv6Address`           |
| `string`, `format: date-time`      | `pydantic.AwareDatetime` (tz-aware) |
| `string`, `format: date`           | `datetime.date`                   |
| `string`, `format: time`           | `datetime.time`                   |
| `string`, `format: duration`       | `datetime.timedelta`              |
| `string`, `format: uuid`           | `uuid.UUID`                       |
| `string`, `format: byte/binary`    | `bytes`                           |

`Strict*` types reject lax coercion (`"1"` → `1`, `1.0` → `1`, etc.),
matching the strict-type-coercion contract of the other SDKs.
`AwareDatetime` rejects naive datetimes — RFC 3339 mandates a timezone
offset.

## Not supported

### Webhooks and callbacks

This SDK is **client → server** only. Spec entries describing
server-initiated calls — OAS 3.1 top-level `webhooks` and OAS 3.0
per-operation `callbacks` — are intentionally skipped during code
generation. If you need to receive webhook deliveries, write the
handler yourself and use this SDK only to deserialize the incoming
payload (e.g. by reusing the relevant request-body model).

### Conditional-required validation (`dependentRequired` / `dependentSchemas`)

JSON Schema 2019-09 keywords for "if field X is present, field Y is
also required" are **not enforced** by this SDK. No mainstream
OpenAPI client codegen implements them. The server is the authoritative
validator; if you want client-side checking, plug in a JSON Schema
validator library for your language.

### Numeric / string constraint validation

OpenAPI keywords `minLength`, `maxLength`, `pattern`, `minimum`,
`maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`,
`minItems`, `maxItems`, and `uniqueItems` ARE enforced client-side on
generated models via pydantic 2's native `Field(...)` constraints
(`min_length`, `max_length`, `pattern`, `ge`/`gt`, `le`/`lt`,
`multiple_of`). Constraint violations raise `pydantic.ValidationError`,
which the `ObjectSerializer` surfaces as a `SerializationError` /
`DeserializationError` to the caller. The server remains the
authoritative validator; the client-side check is a fast-fail
convenience before the network round trip.

### SOCKS proxies

`TransportOptions.proxy()` accepts only `http://` and `https://` URLs.
Passing a `socks://`, `socks4://`, or `socks5://` scheme throws (or
panics) at construction time with a clear error. SOCKS support would
require enabling extra dependencies / feature flags on the underlying
HTTP library in every one of the 12 SDKs we generate, with non-trivial
API divergence; we explicitly chose not to. If you need SOCKS, route
through a local HTTP-CONNECT bridge or configure it at the OS level.

### Per-call cancellation

No generated operation method accepts a per-call cancellation handle.
In-flight requests can only be terminated by waiting for the configured
`TransportOptions` request timeout to fire — there is no way to abort
mid-flight from the caller side. If you need fine-grained per-call
cancellation, wrap the SDK call in your language's standard concurrency
primitives (a `Future` you cancel externally, a `Task` you orphan, an
`asyncio` task you cancel, etc.) and rely on the timeout to break the
underlying socket.

### `LICENSE` file is not auto-emitted

The package manifest declares MIT, but no `LICENSE` / `LICENSE.md` file
is generated alongside the sources. Drop the appropriate license text
into the generated tree as part of your release pipeline before
publishing to a registry — most registries warn or block on a missing
file, and the GitHub license auto-detect cannot pick up a manifest-only
declaration.
