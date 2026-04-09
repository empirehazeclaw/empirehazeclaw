
// Rebuild semantic index after memory sync
const { execSync } = require('child_process');
try {
    console.log('Building semantic search index...');
    execSync('python3 scripts/semantic_search.py build', { cwd: '/home/clawbot/.openclaw/workspace' });
    console.log('Semantic index updated');
} catch (e) {
    console.log('Semantic index update failed:', e.message);
}
