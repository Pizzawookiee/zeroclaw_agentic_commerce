---
name: ucp_catalog_list
description: List the target UCP merchant catalog using dynamically discovered endpoints and without assuming product IDs in advance.
version: 0.1.0
author: ZeroClaw
tags: [ucp, merchant, catalog, products, a2a, generic]
---

# List Merchant Catalog

Use this skill when the buyer needs to know what products the merchant offers.

Do not assume product IDs. Always discover or list the catalog first unless the user supplied a product ID from a trusted prior result.

## Preferred A2A invocation

```json
{
  "skillId": "ucp_catalog_list",
  "arguments": {}
}
```

Send that data part via JSON-RPC `message/send` to the resolved A2A execution endpoint.

## REST fallback

Use the discovered catalog endpoint, commonly:

```text
GET {baseUrl}/catalog
```

Expect a JSON object containing catalog/product data. Preserve returned product IDs for later quote creation.
