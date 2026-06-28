---
name: ucp_checkout_dummy
description: Complete dummy/sandbox checkout for a dynamically resolved UCP merchant only when discovery says dummy checkout is supported and the user confirms.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, checkout, payment, dummy, order, sandbox, a2a, generic]
---

# Dummy Checkout

Use this skill only for merchants that advertise dummy/sandbox checkout support.

## Safety requirements

- Ask the user for confirmation before checkout.
- Confirm the merchant supports dummy payment or sandbox checkout.
- Do not represent dummy checkout as a real purchase.
- Do not use this skill for real payment flows.

## Arguments

```json
{
  "quoteId": "quote_id_from_quote_response",
  "paymentMethod": {
    "type": "dummy"
  }
}
```

## Preferred A2A invocation

```json
{
  "skillId": "ucp_checkout_dummy",
  "arguments": {
    "quoteId": "quote_id_from_quote_response",
    "paymentMethod": {
      "type": "dummy"
    }
  }
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered checkout endpoint, commonly:

```text
POST {baseUrl}/checkout
```

Store the returned `orderId` for order lookup.
