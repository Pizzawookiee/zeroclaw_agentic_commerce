---
name: ucp_merchant_get
description: Get the target UCP merchant profile after resolving the target agent dynamically from discovery or the current agent context.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, profile, capabilities, a2a, generic]
---

# Get Merchant Profile

Use this skill to retrieve merchant identity, sandbox flags, and capabilities.

Do not hardcode the merchant endpoint. Resolve it from the target agent card or UCP merchant descriptor.

## Preferred A2A invocation

```json
{
  "skillId": "ucp_merchant_get",
  "arguments": {}
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered merchant profile endpoint, commonly:

```text
GET {baseUrl}/merchant
```

Read the response as a JSON object. Treat discovery/descriptor data as the source of truth if fields differ.
