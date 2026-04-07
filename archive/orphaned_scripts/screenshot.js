const puppeteer = require('puppeteer-core');
const path = require('path');

async function takeScreenshot(htmlFile) {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium-browser',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800 });
  
  const filePath = 'file://' + path.resolve(htmlFile);
  await page.goto(filePath, { waitUntil: 'networkidle0' });
  
  const outputPath = htmlFile.replace('.html', '.png').replace('screenshots/', 'screenshots/images/');
  await page.screenshot({ path: outputPath, fullPage: true });
  
  console.log('✅ Screenshot:', outputPath);
  await browser.close();
}

const args = process.argv.slice(2);
if (args[0]) {
  takeScreenshot(args[0]);
} else {
  console.log('Usage: node screenshot.js <html-file>');
}
