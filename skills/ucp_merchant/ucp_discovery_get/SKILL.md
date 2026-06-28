---
name: ucp_discovery_get
description: Generic UCP merchant discovery. Resolve the target agent's UCP merchant descriptor and use it as the source of truth for merchant identity, endpoints, actions, and capabilities.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, discovery, descriptor, a2a, generic]
---

# Get UCP Merchant Descriptor

Use this skill to discover a target UCP merchant-style agent.

## Resolve the target first

Do not assume a fixed agent name or endpoint. Resolve the A2A execution endpoint from, in order:

1. explicit user/task endpoint
2. target agent card `metadata.a2aExecution.endpoint`
3. target agent card `url`
4. local fallback `http://localhost:42617/a2a/{current_agent_name}` only when the current agent name is known

## Preferred A2A invocation

If the target supports A2A JSON-RPC, call `message/send` with:

```json
{
  "skillId": "ucp_discovery_get",
  "arguments": {}
}
```

## REST fallback

Fetch the descriptor from the discovered descriptor endpoint, commonly:

```text
{a2a_execution_endpoint}/.well-known/ucp-merchant.json
```

The descriptor response should be a JSON object. Use it to identify merchant ID, name, base URL, endpoint URLs, supported actions, search behavior, payment capabilities, and sandbox status.
