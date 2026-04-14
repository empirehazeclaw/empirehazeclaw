const { execSync } = require('child_process');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

module.exports = {
  name: 'git-manager',
  
  // Get current git status
  status() {
    return run('git status --short');
  },
  
  // Get current branch
  branch() {
    return run('git branch --show-current');
  },
  
  // Get diff
  diff(staged = false) {
    return run(staged ? 'git diff --staged --stat' : 'git diff --stat');
  },
  
  // Get recent commits
  log(n = 10) {
    return run(`git log --oneline -${n}`);
  },
  
  // Create branch
  createBranch(name) {
    return run(`git checkout -b ${name}`);
  },
  
  // Commit with message
  commit(msg) {
    return run(`git add -A && git commit -m "${msg}"`);
  },
  
  // Push
  push(branch = null) {
    return run(branch ? `git push origin ${branch}` : 'git push');
  },
  
  // Pull
  pull() {
    return run('git pull origin ' + this.branch());
  }
};
