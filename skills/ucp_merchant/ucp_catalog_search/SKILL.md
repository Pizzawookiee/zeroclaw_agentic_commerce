---
name: ucp_catalog_search
description: Search a dynamically resolved UCP merchant catalog using the target merchant's advertised search capabilities and endpoint metadata.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, catalog, search, filters, a2a, generic]
---

# Search Merchant Catalog

Use this skill when the buyer describes what they want and product IDs are not yet known.

Resolve search capabilities from the target agent card or UCP merchant descriptor. Do not assume semantic/vector search; use the merchant's advertised search type.

## Arguments

Generic shape:

```json
{
  "query": "buyer search text",
  "limit": 10,
  "searchType": "advertised_search_type_if_any",
  "filters": {
    "category": "optional",
    "minPrice": 0,
    "maxPrice": 100,
    "availability": "optional",
    "currency": "optional"
  }
}
```

Only include filters the merchant advertises or appears to support.

## Preferred A2A invocation

```json
{
  "skillId": "ucp_catalog_search",
  "arguments": {
    "query": "coffee cup",
    "limit": 5
  }
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered search endpoint and supported method, commonly one of:

```text
GET {baseUrl}/search?q=coffee%20cup&limit=5
POST {baseUrl}/search
```

For POST, use the merchant's advertised request body shape when present.

Use returned product IDs for product lookup or quote creation.
