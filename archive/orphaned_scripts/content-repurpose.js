#!/usr/bin/env node
/**
 * Content Repurpose
 * Converts blog → social posts
 */

const blogContent = process.argv.slice(2).join(' ');

function repurpose(content) {
    if (!content) {
        console.log(`
📝 CONTENT REPURPOSE

Usage:
  node content-repurpose.js "blog content here"

Converts:
  Blog Post → Twitter Thread
  Blog Post → LinkedIn Article  
  Blog Post → Instagram Carousel
`);
        return;
    }
    
    // Extract key points (simplified)
    const points = content.split(/[.\n]/).filter(p => p.length > 20).slice(0, 5);
    
    console.log('\n📱 TWITTER THREAD:');
    points.forEach((p, i) => {
        console.log(`${i+1}/ ${p.substring(0, 200)}...`);
    });
    
    console.log('\n💼 LINKEDIN:');
    console.log(points[0]);
    
    console.log('\n📸 INSTAGRAM:');
    console.log(points[0].substring(0, 100) + '... #content #tips');
}

repurpose(blogContent);
