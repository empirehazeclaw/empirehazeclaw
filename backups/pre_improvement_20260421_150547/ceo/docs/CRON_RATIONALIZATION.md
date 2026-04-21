# Cron Rationalization Report — Phase 8

**Generated:** 2026-04-21
**Total Active Crons:** 34

## Schedule Distribution

| Schedule | Count | Crons |
|----------|-------|-------|
| `0 */6 * * *` | 3 | System Maintenance, Mad-Dog Evolver, Ralph Maintenance |
| `0 * * * *` | 2 | Learning Core, Smart Evolver Hourly |
| `0 3 * * *` | 2 | Cache Cleanup, KG Orphan Cleaner |
| Other | 7 | Various daily/weekly |

## Analysis

### Health Monitoring (3 crons)
- `integration health check` (0 */3 * * *) — Integration Dashboard
- `health monitor self-healing` (?) — Health Monitor
- `run gateway recovery check` (?) — Gateway Recovery

**Finding:** These serve different aspects (integration, general health, gateway)

### Maintenance (5 crons)
- `cache cleanup daily` (0 3 * * *) — Cache cleanup
- `kg orphan cleaner daily` (0 3 * * *) — KG maintenance
- `ralph maintenance loop` (0 */6 * * *) — Ralph-specific maintenance
- `system maintenance cron` (0 */6 * * *) — General system maintenance
- `weekly maintenance sunday` (0 4 * * 0) — Sunday full maintenance

**Finding:** KG Orphan Cleaner and Ralph Maintenance serve different purposes (KG-specific vs general Ralph)

## Recommendations

1. **Keep as-is** — Current structure is logically separated
2. **Potential merge:** System Maintenance + Ralph Maintenance (both 6h) could be combined into one "Maintenance Loop" script that handles both
3. **Low priority** — No critical issues found

## Active Cron Summary

| Category | Count | Notes |
|----------|-------|-------|
| Learning/Evolution | 8 | Loop, Evolver, Meta, Ralph |
| Health/Monitoring | 6 | Dashboard, Health, Gateway |
| Maintenance | 5 | Cache, KG, System, Weekly |
| Research | 3 | Innovation, Scanner, Benchmark |
| Reporting | 4 | Morning, Dreaming, Feedback |
| Other | 8 | Backup, Documentation, etc |

**Conclusion:** Cron structure is reasonably optimized. No urgent consolidation needed.
