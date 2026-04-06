# Server Configuration

## Hostinger Firewall

Date: 2026-03-18

### Rules (in order):

| # | Rule | Protocol | Port | Source | Status |
|---|------|----------|------|--------|--------|
| 1 | Deny | any | any | any | ❌ |
| 2 | Accept | tcp | 443 | any | ✅ |
| 3 | Accept | tcp | 80 | any | ✅ |
| 4 | Accept | tcp | 18789 | any | ✅ |
| 5 | Accept | ssh | 22 | any | ✅ |

### Summary:
- **Deny All** by default
- Only HTTPS (443), HTTP (80), SSH (22), Custom (18789) allowed
