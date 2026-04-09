const { createCanvas } = require('canvas');
const fs = require('fs');

const templates = [
  { name: 'business-planner', title: 'Business Planner MAX', price: '€29', color: '#6366f1' },
  { name: 'content-calendar', title: 'Content Calendar MAX', price: '€24', color: '#ec4899' },
  { name: 'crm', title: 'CRM MAX', price: '€39', color: '#10b981' },
  { name: 'projektmanager', title: 'Projektmanager MAX', price: '€34', color: '#f59e0b' },
  { name: 'goal-tracker', title: 'Goal Tracker MAX', price: '€19', color: '#3b82f6' },
  { name: 'bundle', title: 'KOMPLETT PAKET', price: '€99', color: '#6366f1' }
];

templates.forEach(t => {
  const canvas = createCanvas(1200, 800);
  const ctx = canvas.getContext('2d');
  
  // Background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, 1200, 800);
  
  // Header
  const gradient = ctx.createLinearGradient(0, 0, 1200, 0);
  gradient.addColorStop(0, t.color);
  gradient.addColorStop(1, t.color + '99');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1200, 200);
  
  // Title
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 60px sans-serif';
  ctx.fillText(t.title, 60, 120);
  
  // Price
  ctx.font = 'bold 80px sans-serif';
  ctx.fillText(t.price, 60, 200);
  
  // Features
  ctx.fillStyle = '#1e293b';
  ctx.font = '30px sans-serif';
  ctx.fillText('✓ 100+ Pages', 60, 300);
  ctx.fillText('✓ Deutsch', 60, 350);
  ctx.fillText('✓ Lifetime Updates', 60, 400);
  ctx.fillText('✓ Video Tutorial', 60, 450);
  
  // Footer
  ctx.fillStyle = '#94a3b8';
  ctx.font = '20px sans-serif';
  ctx.fillText('empirehazeclaw.store', 60, 750);
  
  // Save
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(`notion-templates/screenshots/images/${t.name}.png`, buffer);
  console.log('✅ Created:', t.name + '.png');
});
