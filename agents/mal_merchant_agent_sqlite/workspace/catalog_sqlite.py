#!/usr/bin/env python3
"""SQLite utilities for the local merchant catalog fixture."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_JSON_PATH = ROOT / "catalog.json"
DEFAULT_DB_PATH = ROOT / "catalog.sqlite"
UCP_VERSION = "2026-04-08"


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_JSON_PATH
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def rebuild_database(json_path: Path | None = None, db_path: Path = DEFAULT_DB_PATH) -> None:
    catalog = load_catalog(json_path)
    products = catalog.get("products", [])

    with connect(db_path) as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS variants;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS catalog_meta;

            CREATE TABLE catalog_meta (
              key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL
            );

            CREATE TABLE products (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              description TEXT,
              category_text TEXT,
              tag_text TEXT,
              product_json TEXT NOT NULL
            );

            CREATE TABLE variants (
              id TEXT PRIMARY KEY,
              product_id TEXT NOT NULL REFERENCES products(id),
              sku TEXT,
              title TEXT,
              variant_json TEXT NOT NULL
            );

            CREATE INDEX idx_products_title ON products(title);
            CREATE INDEX idx_variants_product_id ON variants(product_id);
            """
        )

        conn.execute("INSERT INTO catalog_meta VALUES (?, ?)", ("merchant", json.dumps(catalog.get("merchant"))))
        conn.execute(
            "INSERT INTO catalog_meta VALUES (?, ?)",
            ("schema_notes", json.dumps(catalog.get("schema_notes"))),
        )

        for product in products:
            categories = " ".join(
                " ".join(str(category.get(key, "")) for key in ("value", "label"))
                for category in product.get("categories", [])
            )
            tags = " ".join(str(tag) for tag in product.get("tags", []))
            conn.execute(
                """
                INSERT INTO products (id, title, description, category_text, tag_text, product_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    product["id"],
                    product.get("title") or "",
                    product.get("description"),
                    categories,
                    tags,
                    json.dumps(product),
                ),
            )
            for variant in product.get("variants", []):
                conn.execute(
                    """
                    INSERT INTO variants (id, product_id, sku, title, variant_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        variant["id"],
                        product["id"],
                        variant.get("sku"),
                        variant.get("title"),
                        json.dumps(variant),
                    ),
                )


def ensure_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    if not db_path.exists():
        rebuild_database(db_path=db_path)


def variant_for_output(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": variant["id"],
        "sku": variant.get("sku"),
        "title": variant.get("title"),
        "price": variant.get("price"),
        "availability": variant.get("availability", {"status": "unknown", "quantity": None}),
        "selected_options": variant.get("selected_options", []),
    }


def product_for_search(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": product["id"],
        "title": product.get("title"),
        "description": product.get("description"),
        "media": product.get("media", []),
        "categories": product.get("categories", []),
        "rating": product.get("rating", {"average": None, "count": None}),
        "variants": [variant_for_output(variant) for variant in product.get("variants", [])],
    }


def product_for_detail(product: dict[str, Any], featured: dict[str, Any] | None) -> dict[str, Any]:
    selected = featured.get("selected_options", []) if featured else []
    detail = {
        "id": product["id"],
        "title": product.get("title"),
        "description": product.get("description"),
        "media": product.get("media", []),
        "categories": product.get("categories", []),
        "selected": selected,
        "options": product.get("options", []),
        "featured_variant": variant_for_output(featured) if featured else None,
        "variants": [variant_for_output(variant) for variant in product.get("variants", [])],
        "rating": product.get("rating", {"average": None, "count": None}),
    }
    for optional_key in ("policies", "fulfillment", "trust_evidence"):
        if optional_key in product:
            detail[optional_key] = product[optional_key]
    return detail


def search_catalog(query: str, limit: int = 10, db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any]:
    ensure_database(db_path)
    terms = [term.lower() for term in query.split() if term.strip()]

    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT product_json FROM products ORDER BY title COLLATE NOCASE"
        ).fetchall()

    matches: list[dict[str, Any]] = []
    for row in rows:
        product = json.loads(row["product_json"])
        haystack = " ".join(
            str(value)
            for value in (
                product.get("id"),
                product.get("title"),
                product.get("description"),
                " ".join(product.get("tags", [])),
                json.dumps(product.get("categories", [])),
                json.dumps(product.get("attributes", {})),
            )
        ).lower()
        if not terms or all(term in haystack for term in terms):
            matches.append(product_for_search(product))

    limited = matches[:limit]
    messages = []
    if not limited:
        messages.append(
            {
                "type": "info",
                "code": "no_results",
                "content": "No matching products were found.",
            }
        )

    return {
        "ucp": {"version": UCP_VERSION, "capability": "dev.ucp.shopping.catalog.search"},
        "products": limited,
        "pagination": {
            "has_next_page": len(matches) > limit,
            "cursor": None,
            "total_count": len(matches),
        },
        "messages": messages,
    }


def retrieve_product_info(identifier: str, db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any]:
    ensure_database(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT product_json FROM products WHERE id = ?", (identifier,)).fetchone()
        selected_variant_id = None
        if row is None:
            variant_row = conn.execute(
                """
                SELECT p.product_json, v.id AS variant_id
                FROM variants v
                JOIN products p ON p.id = v.product_id
                WHERE v.id = ?
                """,
                (identifier,),
            ).fetchone()
            if variant_row is not None:
                row = variant_row
                selected_variant_id = variant_row["variant_id"]

    if row is None:
        return {
            "ucp": {
                "version": UCP_VERSION,
                "capability": "dev.ucp.shopping.catalog.lookup",
                "operation": "get_product",
                "status": "error",
            },
            "messages": [
                {
                    "type": "error",
                    "code": "not_found",
                    "content": "The requested product or variant identifier was not found.",
                }
            ],
        }

    product = json.loads(row["product_json"])
    variants = product.get("variants", [])
    featured_id = selected_variant_id or product.get("featured_variant_id")
    featured = next((variant for variant in variants if variant.get("id") == featured_id), variants[0] if variants else None)
    return {
        "ucp": {
            "version": UCP_VERSION,
            "capability": "dev.ucp.shopping.catalog.lookup",
            "operation": "get_product",
        },
        "product": product_for_detail(product, featured),
        "messages": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and query the merchant catalog SQLite database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Convert catalog.json to SQLite.")
    build_parser.add_argument("--json", type=Path, default=None)

    search_parser = subparsers.add_parser("search", help="Search products and return UCP-shaped JSON.")
    search_parser.add_argument("query", nargs="?", default="")
    search_parser.add_argument("--limit", type=int, default=10)

    get_parser = subparsers.add_parser("get", help="Retrieve a product or variant and return UCP-shaped JSON.")
    get_parser.add_argument("id")

    args = parser.parse_args()
    if args.command == "build":
        rebuild_database(args.json, args.db)
        print(json.dumps({"ok": True, "database": str(args.db)}, indent=2))
    elif args.command == "search":
        print(json.dumps(search_catalog(args.query, args.limit, args.db), indent=2))
    elif args.command == "get":
        print(json.dumps(retrieve_product_info(args.id, args.db), indent=2))


if __name__ == "__main__":
    main()
