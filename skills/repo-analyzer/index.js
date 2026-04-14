const { execSync } = require('child_process');
const fs = require('fs');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

function getFiles(ext, max = 100) {
  try {
    return execSync(`find . -name "*.${ext}" -type f 2>/dev/null | head -n ${max}`, { encoding: 'utf8', maxBuffer: 10*1024*1024 });
  } catch {
    return '';
  }
}

module.exports = {
  name: 'repo-analyzer',
  
  // Get directory structure
  structure(maxDepth = 2) {
    return run(`find . -maxdepth ${maxDepth} -type d | head -50`);
  },
  
  // Count lines by language
  lines() {
    return run('find . -type f \\( -name "*.py" -o -name "*.js" -o -name "*.ts" \\) -exec wc -l {} + 2>/dev/null | tail -5');
  },
  
  // List Python files
  pyFiles() {
    return getFiles('py');
  },
  
  // List JS/TS files
  jsFiles() {
    return getFiles('js') + '\n' + getFiles('ts');
  },
  
  // Get package.json contents
  deps() {
    try {
      return fs.readFileSync('package.json', 'utf8');
    } catch {
      return 'No package.json found';
    }
  },
  
  // Get requirements.txt
  pyDeps() {
    try {
      return fs.readFileSync('requirements.txt', 'utf8');
    } catch {
      return 'No requirements.txt found';
    }
  },
  
  // Git repo info
  gitInfo() {
    return {
      branch: run('git branch --show-current').trim(),
      lastCommit: run('git log -1 --oneline').trim(),
      commits: run('git log --oneline -10').trim(),
      status: run('git status --short').trim()
    };
  },
  
  // Full analysis
  analyze() {
    return {
      pyFiles: this.pyFiles().split('\n').length,
      jsFiles: (this.jsFiles().match(/\.js/g) || []).length + (this.jsFiles().match(/\.ts/g) || []).length,
      deps: this.deps(),
      git: this.gitInfo()
    };
  }
};
