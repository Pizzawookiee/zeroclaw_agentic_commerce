---
id: retrieve_product_info
name: Retrieve Product Info
description: Return authoritative product, variant, price, inventory, policy, and fulfillment details in a strict JSON schema.
tags:
  - commerce
  - catalog
  - product-details
  - ucp-compatible
inputModes:
  - application/json
outputModes:
  - application/json
---

# Get Product Details

## Purpose

Use this skill when a buyer agent, auditor agent, or shopping client needs authoritative details for a specific merchant product or variant.

This skill is usually called after `search_catalog`.

This skill must return structured JSON only. Do not return prose, Markdown, explanations, or extra keys outside the schema.

## Input

The caller should provide JSON matching this shape:

```json
{
  "product_id": "string",
  "variant_id": "string | null",
  "include": {
    "variants": "boolean | null",
    "policies": "boolean | null",
    "fulfillment": "boolean | null",
    "reviews_summary": "boolean | null",
    "trust_evidence": "boolean | null"
  }
}
```

If `variant_id` is missing or null, return the product-level details and identify the default variant if one exists.

## Required Behavior

1. Look up only the merchant's real catalog or provided demo catalog.
2. Do not invent missing products.
3. If the product is not found, return a valid `not_found` response.
4. Do not invent prices, stock, shipping, certifications, reviews, return rules, warranty terms, or provenance.
5. Return prices as integer minor units, for example cents for USD.
6. If a field is unknown, use `null`.
7. Always return valid JSON matching the output schema exactly.
8. Make this response suitable for downstream cart and checkout validation.
9. If product detail data conflicts with prior search results, treat this product detail response as authoritative.

## Output Schema

Return exactly this JSON shape:

```json
{
  "schema_version": "merchant.catalog.product_details.v1",
  "merchant": {
    "merchant_id": "string",
    "display_name": "string"
  },
  "lookup": {
    "product_id": "string",
    "variant_id": "string | null",
    "found": "boolean",
    "status": "found | not_found | discontinued | unavailable"
  },
  "product": {
    "product_id": "string",
    "title": "string",
    "brand": "string | null",
    "category": "string | null",
    "description": "string | null",
    "product_url": "string | null",
    "images": [
      {
        "url": "string",
        "alt_text": "string | null",
        "position": "number | null"
      }
    ],
    "attributes": {
      "string": "string | number | boolean | null"
    },
    "tags": [
      "string"
    ]
  },
  "selected_variant": {
    "variant_id": "string",
    "sku": "string | null",
    "title": "string | null",
    "attributes": {
      "string": "string | number | boolean | null"
    },
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
      "quantity_available": "number | null",
      "available_for_checkout": "boolean"
    },
    "limits": {
      "min_quantity": "number | null",
      "max_quantity": "number | null"
    },
    "dimensions": {
      "weight_grams": "number | null",
      "length_mm": "number | null",
      "width_mm": "number | null",
      "height_mm": "number | null"
    }
  },
  "variants": [
    {
      "variant_id": "string",
      "sku": "string | null",
      "title": "string | null",
      "attributes": {
        "string": "string | number | boolean | null"
      },
      "price": {
        "amount_minor": "number",
        "currency": "string"
      },
      "availability": {
        "status": "in_stock | out_of_stock | preorder | discontinued | unknown",
        "quantity_available": "number | null",
        "available_for_checkout": "boolean"
      }
    }
  ],
  "policies": {
    "return_policy": {
      "returnable": "boolean | null",
      "window_days": "number | null",
      "summary": "string | null",
      "policy_url": "string | null"
    },
    "warranty": {
      "included": "boolean | null",
      "duration_days": "number | null",
      "summary": "string | null",
      "policy_url": "string | null"
    },
    "age_restriction": {
      "required": "boolean",
      "minimum_age": "number | null"
    }
  },
  "fulfillment": {
    "ships_to": [
      "string"
    ],
    "shipping_required": "boolean | null",
    "pickup_available": "boolean | null",
    "estimated_handling_days": {
      "min": "number | null",
      "max": "number | null"
    },
    "shipping_notes": "string | null"
  },
  "reviews_summary": {
    "average_rating": "number | null",
    "review_count": "number | null",
    "summary": "string | null"
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
  },
  "warnings": [
    {
      "code": "string",
      "message": "string"
    }
  ]
}
```

## Not Found Output Schema

If the product is not found, return this exact shape:

```json
{
  "schema_version": "merchant.catalog.product_details.v1",
  "merchant": {
    "merchant_id": "string",
    "display_name": "string"
  },
  "lookup": {
    "product_id": "string",
    "variant_id": "string | null",
    "found": false,
    "status": "not_found"
  },
  "product": null,
  "selected_variant": null,
  "variants": [],
  "policies": null,
  "fulfillment": null,
  "reviews_summary": null,
  "trust_evidence": null,
  "warnings": [
    {
      "code": "PRODUCT_NOT_FOUND",
      "message": "No product was found for the supplied product_id."
    }
  ]
}
```

## Output Rules

- `schema_version` must always be `"merchant.catalog.product_details.v1"`.
- `lookup.product_id` must echo the requested `product_id`.
- `lookup.variant_id` must echo the requested `variant_id`, or `null` if none was provided.
- `product.product_id` must match `lookup.product_id` when `found` is true.
- `selected_variant.variant_id` must be the requested variant, the default variant, or the only available variant.
- `compare_at_price` must be `null` if there is no original/list price.
- `variants` may be an empty array if variants were not requested or do not exist.
- `policies`, `fulfillment`, `reviews_summary`, and `trust_evidence` may be `null` if not requested or unknown.
- `warnings` must be an empty array if there are no warnings.
- Do not include checkout session IDs in this response.
- Do not include payment instructions in this response.