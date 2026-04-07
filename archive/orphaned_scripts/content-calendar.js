#!/usr/bin/env node
/**
 * Content Calendar
 * Plans and schedules content
 */

const topics = process.argv.slice(2).join(' ') || 'AI,Tech,Business';

console.log(`
📅 CONTENT CALENDAR

Week 1:
- Monday: Research "${topics}"
- Tuesday: Blog Post
- Wednesday: Twitter Thread
- Thursday: LinkedIn Article
- Friday: Instagram Post
- Saturday: Thread
- Sunday: Recap

Week 2:
- Monday: Research
- Tuesday: Blog
- Wednesday: Twitter
- Thursday: LinkedIn
- Friday: Video Script
- Saturday: Engagement
- Sunday: Planning

Tools:
  node scripts/research.js deep "topic"
  node scripts/content.js all "topic"
  node scripts/social-post.js twitter "content"
`);
