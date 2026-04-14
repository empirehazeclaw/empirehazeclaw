const { execSync } = require('child_process');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

module.exports = {
  name: 'code-review',
  
  // Get diff between branches
  diff(from = 'main', to = 'HEAD') {
    return run(`git diff ${from}..${to}`);
  },
  
  // Get diff for specific file
  fileDiff(file) {
    return run(`git diff ${file}`);
  },
  
  // Get staged changes
  staged() {
    return run('git diff --staged');
  },
  
  // Get commit info
  commit(sha) {
    return run(`git show ${sha || 'HEAD'} --stat`);
  },
  
  // Get PR info (GitHub)
  async pr(number) {
    try {
      return execSync(`gh pr view ${number} --json title,body,files`, { encoding: 'utf8' });
    } catch (e) {
      return 'GitHub CLI not available or not authenticated';
    }
  }
};
