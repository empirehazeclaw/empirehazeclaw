#!/usr/bin/env node
/**
 * Blog Post Generator
 * Creates SEO-optimized blog posts
 */

function generateBlog(topic) {
    const slug = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    
    console.log(`\n📝 BLOG POST: ${topic}\n`);
    console.log(`Slug: /blog/${slug}`);
    console.log(`\n--- CONTENT ---`);
    
    const template = `
# ${topic}: The Complete Guide

## Introduction
In this comprehensive guide, we'll explore everything you need to know about ${topic}.

## What is ${topic}?
${topic} is transforming how we work and live. Here's what you need to understand...

## Key Benefits
1. **Benefit 1** - Explanation
2. **Benefit 2** - Explanation  
3. **Benefit 3** - Explanation

## How to Get Started
Step 1: Understand the basics
Step 2: Choose your approach
Step 3: Implement and iterate

## Common Mistakes to Avoid
- Mistake 1
- Mistake 2
- Mistake 3

## Conclusion
${topic} is here to stay. Start today and stay ahead of the curve.

## Frequently Asked Questions

### What is ${topic}?
[Answer]

### How much does it cost?
[Answer]

### Is it right for my business?
[Answer]
`;
    
    console.log(template);
    
    return {
        title: topic,
        slug: slug,
        content: template
    };
}

const args = process.argv.slice(2);
const topic = args.join(' ') || 'AI Chatbots';

generateBlog(topic);
