---
id: retrieve_product_info
name: Retrieve Product Info
description: Retrieve full UCP-shaped product detail for a product or variant identifier.
tags:
  - ucp_merchant_skills_sqlite
  - commerce
  - catalog
  - product-details
  - ucp-compatible
  - sqlite
inputModes:
  - text
outputModes:
  - text
---

# Retrieve Product Info

## Purpose

Use this skill when the caller already has a product ID or variant ID and wants full product detail.

This skill maps to the UCP Catalog Lookup capability:

`dev.ucp.shopping.catalog.lookup`

For a single product detail request, behave like a UCP `get_product` operation.

Return only valid JSON. Do not return Markdown, prose, code fences, explanations, or extra text.

## SQLite Utility

Use the local SQLite catalog utility as the authoritative data source for product and variant lookup.

The skill is executed from the agent workspace, so call the utility with workspace-relative paths:

```text
python catalog_sqlite.py build
python catalog_sqlite.py get "<product-or-variant-id>"
```

If the SQLite database does not exist yet, build it from `catalog.json`.
Return the utility's JSON output unchanged.

## Input

The caller may provide a product or variant ID in text:

```text
Get product prod_headphones_001
```

or:

```text
Get variant var_headphones_001_black
```

The caller may also provide JSON-like lookup details in text:

```json
{
  "id": "prod_headphones_001",
  "selected": [
    {
      "name": "Color",
      "value": "Black"
    }
  ],
  "preferences": [
    "Color"
  ]
}
```

## Required Behavior

1. Retrieve only from the local SQLite merchant catalog or approved merchant data source.
2. The input `id` may be a product ID or variant ID.
3. Do not invent missing products.
4. If the product or variant is not found, return a UCP-shaped error response.
5. Do not invent prices, inventory, variants, ratings, policies, shipping claims, certifications, or discounts.
6. Return product and variant IDs exactly as stored in the catalog.
7. Prices must use minor currency units, for example cents for USD.
8. If a variant is selected, include it as `featured_variant`.
9. Return only JSON in the response shape below.

## UCP-Shaped Output

Return exactly this top-level shape when found:

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.lookup",
    "operation": "get_product"
  },
  "product": {},
  "messages": []
}
```

## Product Shape

The `product` object must use this shape:

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
  "selected": [
    {
      "name": "string",
      "value": "string"
    }
  ],
  "options": [
    {
      "name": "string",
      "values": [
        {
          "value": "string",
          "available": "boolean",
          "exists": "boolean"
        }
      ]
    }
  ],
  "featured_variant": {
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
  ],
  "rating": {
    "average": "number | null",
    "count": "number | null"
  }
}
```

## Optional Merchant Detail Fields

If known and useful, the product may also include these optional fields:

```json
{
  "policies": {
    "return_policy": {
      "returnable": "boolean | null",
      "window_days": "integer | null",
      "summary": "string | null",
      "policy_url": "string | null"
    },
    "warranty": {
      "included": "boolean | null",
      "duration_days": "integer | null",
      "summary": "string | null",
      "policy_url": "string | null"
    },
    "age_restriction": {
      "required": "boolean",
      "minimum_age": "integer | null"
    }
  },
  "fulfillment": {
    "ships_to": [
      "string"
    ],
    "shipping_required": "boolean | null",
    "pickup_available": "boolean | null",
    "estimated_handling_days": {
      "min": "integer | null",
      "max": "integer | null"
    },
    "shipping_notes": "string | null"
  },
  "trust_evidence": {
    "merchant_assertions": [
      {
        "type": "certification | provenance | authenticity | safety | sustainability | other",
        "claim": "string",
        "evidence_url": "string | null",
        "verified_by": "string | null"
      }
    ]
  }
}
```

Do not include these optional fields if the data is unknown.

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

## Not Found Response

If no matching product or variant is found, return exactly this shape:

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.lookup",
    "operation": "get_product",
    "status": "error"
  },
  "messages": [
    {
      "type": "error",
      "code": "not_found",
      "content": "The requested product or variant identifier was not found."
    }
  ]
}
```

## Example Successful Result

```json
{
  "ucp": {
    "version": "2026-04-08",
    "capability": "dev.ucp.shopping.catalog.lookup",
    "operation": "get_product"
  },
  "product": {
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
    "selected": [
      {
        "name": "Color",
        "value": "Black"
      }
    ],
    "options": [
      {
        "name": "Color",
        "values": [
          {
            "value": "Black",
            "available": true,
            "exists": true
          }
        ]
      }
    ],
    "featured_variant": {
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
    ],
    "rating": {
      "average": 4.5,
      "count": 128
    },
    "policies": {
      "return_policy": {
        "returnable": true,
        "window_days": 30,
        "summary": "Returns accepted within 30 days if the item is unused and in original packaging.",
        "policy_url": "http://localhost:42617/policies/returns"
      },
      "warranty": {
        "included": true,
        "duration_days": 365,
        "summary": "One-year limited manufacturer warranty.",
        "policy_url": "http://localhost:42617/policies/warranty"
      },
      "age_restriction": {
        "required": false,
        "minimum_age": null
      }
    },
    "fulfillment": {
      "ships_to": [
        "US"
      ],
      "shipping_required": true,
      "pickup_available": false,
      "estimated_handling_days": {
        "min": 1,
        "max": 2
      },
      "shipping_notes": "Standard and expedited shipping available at checkout."
    },
    "trust_evidence": {
      "merchant_assertions": [
        {
          "type": "authenticity",
          "claim": "Sold directly by Demo Merchant as a new retail product.",
          "evidence_url": null,
          "verified_by": null
        }
      ]
    }
  },
  "messages": []
}
```
