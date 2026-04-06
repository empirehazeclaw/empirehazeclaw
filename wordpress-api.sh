#!/bin/bash
# WordPress API Integration
# Usage: ./wordpress-api.sh <command> <args>

WP_URL="${1:-http://localhost:8888}"
WP_USER="${2:-admin}"
WP_PASS="${3:-tUqvCfqpEBhXu3g_}"

case "$1" in
  posts)
    curl -s -X GET "$WP_URL/wp-json/wp/v2/posts" -u "$WP_USER:$WP_PASS"
    ;;
  pages)
    curl -s -X GET "$WP_URL/wp-json/wp/v2/pages" -u "$WP_USER:$WP_PASS"
    ;;
  products)
    curl -s -X GET "$WP_URL/wp-json/wc/v3/products" -u "$WP_USER:$WP_PASS"
    ;;
  *)
    echo "Usage: $0 <posts|pages|products> [url] [user] [pass]"
    ;;
esac
