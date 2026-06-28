---
name: ucp_quote_create
description: Create a quote with a dynamically resolved UCP merchant after obtaining product IDs and explicit user confirmation.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, quote, cart, commerce, a2a, generic]
---

# Create Quote

Use this skill to create a quote/cart with a UCP merchant.

## Safety requirements

- Ask the user for confirmation before creating a quote.
- Use product IDs returned by catalog/search/product lookup or explicitly provided by the user.
- Respect merchant quantity limits and availability from discovery/results.
- Do not assume prices or totals; read them from the quote response.

## Arguments

```json
{
  "items": [
    {
      "productId": "product_id_from_catalog_or_search",
      "quantity": 1
    }
  ]
}
```

## Preferred A2A invocation

```json
{
  "skillId": "ucp_quote_create",
  "arguments": {
    "items": [
      {
        "productId": "product_id_from_catalog_or_search",
        "quantity": 1
      }
    ]
  }
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered quote endpoint, commonly:

```text
POST {baseUrl}/quote
```

Store the returned `quoteId` for checkout.
