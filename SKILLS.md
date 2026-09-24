# Zitadel SDK - AI Agent Reference

## Installation

```bash
pip install zitadel_client
```

## Quick Start

```python
from zitadel_client.zitadel import Zitadel

client = Zitadel.with_token("https://api.example.com", "your-token")
```

## Authentication

All authentication is handled via `Authenticator` implementations passed to the client constructor.

### Bearer Token

```python
from zitadel_client.auth.bearer_authenticator import BearerAuthenticator

authenticator = BearerAuthenticator("https://api.example.com", "your-token")
client = Zitadel(authenticator)
```

## Servers

If the OpenAPI spec defines multiple servers, the generated `zitadel_client.servers` module exposes each as a `ServerConfiguration` (e.g., `SERVER_0`, `SERVER_1`, ...) plus an `ALL` list. Pass the desired server's URL to the client:

```python
from zitadel_client.servers import SERVER_0

client = Zitadel.with_token(SERVER_0.get_url(), "your-token")
```

## Testing

The `Authenticator` protocol is the seam for tests: substitute a fake authenticator that returns a known header map, and assert your code calls the API the way you expect.

```python
from zitadel_client.auth.authenticator import Authenticator

class FakeAuthenticator(Authenticator):
    def get_host(self) -> str:
        return "https://api.example.com"

    def get_auth_headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer test-token"}

client = Zitadel(FakeAuthenticator())
```

## Error Handling

All API errors derive from `ApiException`. The error hierarchy is:

- `ApiException` (base)
  - `ClientException` (4xx)
    - `BadRequestException` (400)
    - `UnauthorizedException` (401)
    - `ForbiddenException` (403)
    - `NotFoundException` (404)
    - `ConflictException` (409)
    - `UnprocessableEntityException` (422)
  - `ServerException` (5xx)
    - `InternalServerErrorException` (500)
  - `NetworkException` (no HTTP response, status 0)
    - `NetworkTimeoutException` (the request timed out, status 0)

```python
from zitadel_client.errors import (
    NotFoundException,
    ClientException,
    ServerException,
    ApiException,
)

async def main():
    try:
        result = await client.action_service.activate_public_key(...)
    except NotFoundException as e:
        print(f"Not found: {e}")
    except ClientException as e:
        print(f"Client error {e.status_code}: {e}")
    except ServerException as e:
        print(f"Server error: {e}")
    except ApiException as e:
        print(f"API error: {e}")
```

## Configuration

### Custom Transport Options

```python
from zitadel_client.transport_options import TransportOptions

transport = (
    TransportOptions.builder()
    .proxy("http://proxy:3128")
    .timeout(5000)
    .build()
)

client = Zitadel(authenticator, transport)
```

## API Methods

Each API group is exposed as a typed attribute on the client (e.g., `client.action_service`). API classes have methods that correspond to OpenAPI operations, accepting typed request parameters and returning typed response models.

All API methods are asynchronous; await them.

## Models

Models are generated as pydantic models in `zitadel_client.models`.

```python
from zitadel_client.models.action_service_activate_public_key_request import ActionServiceActivatePublicKeyRequest

model = ActionServiceActivatePublicKeyRequest()
```

## Binary / File Uploads

File upload parameters are typed as `bytes`. Binary response bodies are returned as `bytes`.

## Comment Style

Never place a comment on the same line as code. Use `#` comments; `"""` docstrings are fine.

```good
# This explains the logic
x = 1
```

```bad
x = 1  # This explains the logic
```
