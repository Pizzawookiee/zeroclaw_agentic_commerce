---
id: search_catalog
name: Search Catalog
description: Search the merchant catalog and return matching products in a strict JSON schema.
tags:
  - commerce
  - catalog
  - product-search
  - ucp-compatible
inputModes:
  - application/json
outputModes:
  - application/json
---

# Search Catalog

## Purpose

Use this skill when a buyer agent, auditor agent, or shopping client asks to search the merchant's catalog for products matching a query, category, price range, attributes, availability, or other filters.

This skill must return structured JSON only. Do not return prose, Markdown, explanations, or extra keys outside the schema.

## Input

The caller should provide JSON matching this shape:

```json
{
  "query": "string",
  "filters": {
    "category": "string | null",
    "min_price": "number | null",
    "max_price": "number | null",
    "currency": "string | null",
    "availability": "in_stock | out_of_stock | preorder | any | null",
    "brand": "string | null",
    "attributes": {
      "string": "string | number | boolean"
    }
  },
  "sort": "relevance | price_asc | price_desc | newest | rating | null",
  "limit": "number | null",
  "cursor": "string | null"
}
```

If optional input fields are missing, treat them as `null`.

## Required Behavior

1. Search only the merchant's real catalog or the provided demo catalog.
2. Do not invent products.
3. Do not invent prices, ratings, inventory, shipping claims, certifications, discounts, or availability.
4. If a field is unknown, use `null`.
5. If no products match, return an empty `items` array.
6. Always return valid JSON matching the output schema exactly.
7. Use stable merchant product IDs that can be passed to `get_product_details`.
8. Return prices as integer minor units, for example cents for USD.
9. Include enough structured evidence for an auditor to understand why each product matched.

## Output Schema

Return exactly this JSON shape:

```json
{
  "schema_version": "merchant.catalog.search.v1",
  "merchant": {
    "merchant_id": "string",
    "display_name": "string"
  },
  "query": {
    "raw": "string",
    "normalized": "string",
    "filters_applied": {
      "category": "string | null",
      "min_price": "number | null",
      "max_price": "number | null",
      "currency": "string | null",
      "availability": "in_stock | out_of_stock | preorder | any | null",
      "brand": "string | null",
      "attributes": {
        "string": "string | number | boolean"
      }
    },
    "sort": "relevance | price_asc | price_desc | newest | rating | null",
    "limit": "number | null",
    "cursor": "string | null"
  },
  "results": {
    "total_estimate": "number | null",
    "returned_count": "number",
    "next_cursor": "string | null",
    "items": [
      {
        "product_id": "string",
        "variant_id": "string | null",
        "title": "string",
        "brand": "string | null",
        "category": "string | null",
        "description_short": "string | null",
        "image_url": "string | null",
        "product_url": "string | null",
        "price": {
          "amount_minor": "number",
          "currency": "string"
        },
        "compare_at_price": {
          "amount_minor": "number",
          "currency": "string"
        },
        "availability": {
          "status": "in_stock | out_of_stock | preorder | discontinued | unknown",
          "quantity_available": "number | null"
        },
        "rating": {
          "average": "number | null",
          "count": "number | null"
        },
        "match": {
          "score": "number | null",
          "reasons": [
            "string"
          ],
          "matched_fields": [
            "title | description | category | brand | attributes | tags | unknown"
          ]
        },
        "attributes": {
          "string": "string | number | boolean | null"
        }
      }
    ]
  },
  "warnings": [
    {
      "code": "string",
      "message": "string"
    }
  ]
}
```

## Output Rules

- `schema_version` must always be `"merchant.catalog.search.v1"`.
- `returned_count` must equal the length of `results.items`.
- `price.amount_minor` must be an integer.
- `compare_at_price` must be `null` if there is no original/list price.
- `warnings` must be an empty array if there are no warnings.
- Do not include checkout URLs in search results.
- Do not claim discounts unless the catalog source explicitly includes them.
- Do not include payment instructions in this response.

## Valid Empty Result Example

```json
{
  "schema_version": "merchant.catalog.search.v1",
  "merchant": {
    "merchant_id": "demo_merchant",
    "display_name": "Demo Merchant"
  },
  "query": {
    "raw": "red leather moon boots",
    "normalized": "red leather moon boots",
    "filters_applied": {
      "category": null,
      "min_price": null,
      "max_price": null,
      "currency": "USD",
      "availability": "any",
      "brand": null,
      "attributes": {}
    },
    "sort": "relevance",
    "limit": 10,
    "cursor": null
  },
  "results": {
    "total_estimate": 0,
    "returned_count": 0,
    "next_cursor": null,
    "items": []
  },
  "warnings": []
}
```