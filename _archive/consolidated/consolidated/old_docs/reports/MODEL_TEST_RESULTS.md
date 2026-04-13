# Model Test Results
*Generated: 2026-04-05 16:02 UTC*

## OpenRouter API Connection
| Test | Status | Details |
|------|--------|---------|
| API Connection | ✅ PASS | Model list retrieved successfully |
| API Key | ✅ VALID | Key: `sk-or-v1-75b9...` |

## Model Tests

| Model | Slug | Status | Response |
|-------|------|--------|----------|
| **Nemotron 3 Super** | `nvidia/nemotron-3-super-120b-a12b:free` | ✅ PASS | Responded correctly in German |
| **Qwen3 Coder** | `qwen/qwen3-coder:free` | ⚠️ RATE_LIMITED | 429 - Temporarily rate-limited upstream |
| **DeepSeek R1** | `deepseek/deepseek-r1:free` | ❌ FAILED | 404 - No endpoints found, model slug may have changed |

## Summary
- **Pass Rate:** 1/3 (33%)
- **API Connection:** ✅ Working
- **Fallback Models Status:**
  - Nemotron 3 Super: ✅ Available
  - Qwen3 Coder: ⚠️ Rate limited (retry later)
  - DeepSeek R1: ❌ Unavailable (check new slug)

## Recommendations
1. DeepSeek R1 slug has changed - check OpenRouter docs for current slug
2. Qwen3 Coder is temporarily rate-limited - retry in a few minutes
3. Nemotron 3 Super is working and can be used as primary fallback

## Next Test (when Qwen3/DeepSeek fixed)
```bash
# Test Qwen3 Coder (retry)
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-or-v1-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen/qwen3-coder:free","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}'

# Test DeepSeek R1 with new slug
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer sk-or-v1-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek/deepseek-r1:free","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}'
```
