#!/usr/bin/env node
/**
 * Semantic Search Skill Wrapper
 * Wraps semantic_search.py for Node.js integration
 */

const { execSync } = require('child_process');
const path = require('path');

const SCRIPT = '/home/clawbot/.openclaw/workspace/scripts/semantic_search.py';

function build() {
    console.log('Building semantic index...');
    execSync(`python3 ${SCRIPT} build`, { stdio: 'inherit' });
}

function search(query) {
    console.log(`Searching for: "${query}"`);
    execSync(`python3 ${SCRIPT} search "${query}"`, { stdio: 'inherit' });
}

const [,, command, ...args] = process.argv;

switch (command) {
    case 'build':
        build();
        break;
    case 'search':
        search(args.join(' '));
        break;
    default:
        console.log('Usage: node index.js <build|search> [query]');
}
