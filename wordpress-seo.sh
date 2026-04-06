#!/bin/bash
# Quick WordPress SEO Check

WP_URL="${1:-http://localhost:8888}"

echo "=== WordPress SEO Check ==="
echo ""
echo "Checking: $WP_URL"
echo ""

echo "1. Posts:"
curl -s "$WP_URL/wp-json/wp/v2/posts?per_page=5" | grep -o '"title":{[^}]*"rendered":"[^"]*"' | head -3

echo ""
echo "2. Pages:"
curl -s "$WP_URL/wp-json/wp/v2/pages?per_page=5" | grep -o '"title":{[^}]*"rendered":"[^"]*"' | head -3

echo ""
echo "3. Products (WooCommerce):"
curl -s "$WP_URL/wp-json/wc/v3/products" | grep -o '"name":"[^"]*"' | head -5

echo ""
echo "=== Done ==="
