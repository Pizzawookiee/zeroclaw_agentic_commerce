---
name: ucp_order_get
description: Look up an order from a dynamically resolved UCP merchant using an order ID returned by checkout or supplied by the user.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, order, order-lookup, a2a, generic]
---

# Get Order

Use this skill to retrieve an order status or order object.

Only use an `orderId` returned by checkout or explicitly supplied by the user. Do not invent order IDs.

## Arguments

```json
{
  "orderId": "order_id_from_checkout_response"
}
```

## Preferred A2A invocation

```json
{
  "skillId": "ucp_order_get",
  "arguments": {
    "orderId": "order_id_from_checkout_response"
  }
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered order endpoint template, commonly:

```text
GET {baseUrl}/orders/{orderId}
```

Substitute only the order ID. Do not alter other discovered path components.
