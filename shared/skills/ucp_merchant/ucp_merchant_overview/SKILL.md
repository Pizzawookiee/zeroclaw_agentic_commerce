---
name: ucp-merchant-overview
description: Generic instructions for using any UCP merchant-style agent through its discovered A2A JSON-RPC execution endpoint and UCP merchant descriptor.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, commerce, a2a, json-rpc, sandbox, discovery, generic]
---

# Generic UCP Merchant Skill Bundle

Use this bundle when interacting with any agent that exposes UCP merchant actions through an A2A agent card and/or a UCP merchant descriptor.

This skill is intentionally generic. Do not assume a fixed target agent name, and do not hardcode merchant IDs, product IDs, base URLs, endpoints, or payment behavior unless discovery says so.

## Runtime resolution rules

Before invoking merchant actions, resolve the target dynamically:

1. If the user or task gives an explicit A2A endpoint, use that endpoint.
2. Otherwise, use the target agent card's `metadata.a2aExecution.endpoint` when present.
3. Otherwise, use the target agent card's `url` when present.
4. Otherwise, if the current agent name is known and the local gateway convention applies, construct `http://localhost:42617/a2a/{current_agent_name}`.
5. If the target endpoint or agent name is still ambiguous, ask the user.

Then fetch or use the UCP merchant descriptor from discovery, usually:

```text
{a2a_execution_endpoint}/.well-known/ucp-merchant.json
```

Read merchant-specific facts from discovery, including:

- merchant ID
- merchant name
- sandbox flag
- base URL
- endpoints
- supported UCP actions
- catalog/product IDs
- payment methods
- checkout limitations

## A2A JSON-RPC execution pattern

When the target agent advertises executable A2A skills, prefer JSON-RPC 2.0 `message/send` at the resolved A2A execution endpoint.

Use a data part containing `skillId` and `arguments`:

```json
{
  "jsonrpc": "2.0",
  "id": "req-search-1",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "messageId": "msg-search-1",
      "parts": [
        {
          "kind": "data",
          "data": {
            "skillId": "ucp_catalog_search",
            "arguments": {
              "query": "coffee cup",
              "limit": 5,
              "searchType": "lexical"
            }
          }
        }
      ]
    }
  }
}
```

The response should be an A2A task. Read the merchant result from the task artifact data part.

## Task retrieval

If a task ID is returned and later retrieval is needed, use `tasks/get` at the same resolved A2A endpoint:

```json
{
  "jsonrpc": "2.0",
  "id": "req-task-1",
  "method": "tasks/get",
  "params": {
    "id": "task_id_from_previous_response"
  }
}
```

## Generic skill IDs

Common UCP merchant skill IDs are:

- `ucp_discovery_get`
- `ucp_merchant_get`
- `ucp_catalog_list`
- `ucp_product_get`
- `ucp_catalog_search`
- `ucp_quote_create`
- `ucp_checkout_dummy`
- `ucp_order_get`

Only use a skill if the target agent advertises or supports it. If the agent card maps actions to different skill IDs, follow the discovered card.

## REST fallback

If A2A JSON-RPC skill execution is not available, use the UCP REST endpoints discovered from the merchant descriptor or agent card. Do not invent paths; prefer discovered endpoint URLs.

## Safety rules

- Check whether the merchant is sandbox-only before checkout.
- Ask the user before quote creation, checkout, payment, or order creation.
- Do not represent dummy checkout as a real purchase.
- Do not assume a payment method is supported; read capabilities from discovery.
- Do not assume quote/order persistence; some sandbox merchants keep state in memory only.
