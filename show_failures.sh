#!/bin/bash
cd /home/clawbot/.openclaw/workspace/skills/capability-evolver
node --test test/strategy.test.js 2>&1 | tail -15
