---
name: ucp_product_get
description: Fetch one product from a dynamically resolved UCP merchant using a product ID obtained from discovery, catalog listing, search, or the user.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, catalog, product, product-lookup, a2a, generic]
---

# Get Product Details

Use this skill to look up a specific product.

Only use a `productId` obtained from discovery, catalog listing, search results, or explicit user input. Do not invent product IDs.

## Arguments

```json
{
  "productId": "product_id_from_discovery_or_search"
}
```

## Preferred A2A invocation

```json
{
  "skillId": "ucp_product_get",
  "arguments": {
    "productId": "product_id_from_discovery_or_search"
  }
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered product endpoint template, commonly:

```text
GET {baseUrl}/catalog/{productId}
```

Substitute only the product ID. Do not alter other discovered path components.
