---
id: search_catalog
name: Search Catalog
description: Search the merchant catalog and return UCP-shaped catalog search results.
tags:
  - ucp_merchant_skills_sqlite
  - commerce
  - catalog
  - product-search
  - ucp-compatible
  - sqlite
inputModes:
  - text
outputModes:
  - text
---

# Search Catalog

## Purpose

Use this skill when the caller wants to search or browse the merchant catalog.

This skill maps to the UCP Catalog Search capability:

`dev.ucp.shopping.catalog.search`

Return only valid JSON. Do not return Markdown, prose, code fences, explanations, or extra text.

## SQLite Utility

Use the local SQLite catalog utility as the authoritative data source for searches.

The skill is executed from the agent workspace, so call the utility with workspace-relative paths:

```text
python catalog_sqlite.py build
python catalog_sqlite.py search "<query>"
```

If the SQLite database does not exist yet, build it from `catalog.json`.
Return the utility's JSON output unchanged unless the caller requested a lower result limit.

## Input

The caller may provide a natural language query, such as:

```text
Query: headphones
```

The caller may also provide JSON-like search details in text:

```json
{
  "query": "headphones",
  "filters": {
    "category": "electronics/audio/headphones",
    "price": {
      "min": {
        "amount": 0,
        "currency": "USD"
      },
      "max": {
        "amount": 10000,
        "currency": "USD"
      }
    }
  },
  "pagination": {
    "cursor": null,
    "limit": 10
  }
}
```

If the user provides only natural language, infer a simple `query` string.

## Required Behavior

1. Search only the local SQLite merchant catalog or approved merchant data source.
2. Do not invent products.
3. Do not invent prices, inventory, variants, ratings, certifications, discounts, or shipping claims.
4. Return product and variant IDs exactly as stored in the catalog.
5. Prices must use minor currency units, for example cents for USD.
6. Catalog search is not a transactional commitment. Checkout must revalidate price and availability.
7. If no products match, return an empty `products` array.
8. Return only JSON in the response shape below.

## UCP-Shaped Output

Return exactly this top-level shape:

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.search"
  },
  "products": [],
  "pagination": {
    "has_next_page": false,
    "cursor": null,
    "total_count": 0
  },
  "messages": []
}
```

## Product Shape

Each item in `products` must use this shape:

```json
{
  "id": "string",
  "title": "string",
  "description": "string | null",
  "media": [
    {
      "url": "string",
      "alt_text": "string | null"
    }
  ],
  "categories": [
    {
      "value": "string",
      "label": "string"
    }
  ],
  "rating": {
    "average": "number | null",
    "count": "number | null"
  },
  "variants": [
    {
      "id": "string",
      "sku": "string | null",
      "title": "string | null",
      "price": {
        "amount": "integer",
        "currency": "string"
      },
      "availability": {
        "status": "in_stock | out_of_stock | preorder | discontinued | unknown",
        "quantity": "integer | null"
      },
      "selected_options": [
        {
          "name": "string",
          "value": "string"
        }
      ]
    }
  ]
}
```

## Message Shape

Use `messages` for warnings, errors, and informational notes.

```json
{
  "type": "info | warning | error",
  "code": "string",
  "content": "string"
}
```

If there are no messages, return:

```json
"messages": []
```

## Empty Result Example

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.search"
  },
  "products": [],
  "pagination": {
    "has_next_page": false,
    "cursor": null,
    "total_count": 0
  },
  "messages": [
    {
      "type": "info",
      "code": "no_results",
      "content": "No matching products were found."
    }
  ]
}
```

## Example Successful Result

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.search"
  },
  "products": [
    {
      "id": "prod_headphones_001",
      "title": "Nimbus Wireless Headphones",
      "description": "Lightweight wireless over-ear headphones with active noise cancellation and long battery life.",
      "media": [
        {
          "url": "http://localhost:42617/images/headphones_001.jpg",
          "alt_text": "Black wireless over-ear headphones"
        }
      ],
      "categories": [
        {
          "value": "electronics/audio/headphones",
          "label": "Headphones"
        }
      ],
      "rating": {
        "average": 4.5,
        "count": 128
      },
      "variants": [
        {
          "id": "var_headphones_001_black",
          "sku": "NIM-HDP-001-BLK",
          "title": "Black",
          "price": {
            "amount": 8999,
            "currency": "USD"
          },
          "availability": {
            "status": "in_stock",
            "quantity": 42
          },
          "selected_options": [
            {
              "name": "Color",
              "value": "Black"
            }
          ]
        }
      ]
    }
  ],
  "pagination": {
    "has_next_page": false,
    "cursor": null,
    "total_count": 1
  },
  "messages": []
}
```
