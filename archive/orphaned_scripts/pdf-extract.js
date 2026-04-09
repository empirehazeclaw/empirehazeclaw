#!/usr/bin/env node
/**
 * PDF & File Processing Tool
 * Extracts text from PDFs and images
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Extract text from PDF
async function extractPDF(filePath) {
    return new Promise((resolve, reject) => {
        exec(`pdftotext "${filePath}" -`, (err, stdout) => {
            if (err) reject(err);
            else resolve(stdout);
        });
    });
}

// Extract text from image (OCR)
async function extractImage(filePath) {
    return new Promise((resolve, reject) => {
        exec(`tesseract "${filePath}" stdout`, (err, stdout) => {
            if (err) reject(err);
            else resolve(stdout);
        });
    });
}

// Main
async function main() {
    const filePath = process.argv[2];
    
    if (!filePath) {
        console.log('Usage: node pdf-extract.js <file>');
        console.log('Supported: PDF, PNG, JPG, JPEG');
        process.exit(1);
    }
    
    const ext = path.extname(filePath).toLowerCase();
    
    try {
        let text;
        if (ext === '.pdf') {
            console.log('Extracting from PDF...');
            text = await extractPDF(filePath);
        } else if (['.png', '.jpg', '.jpeg'].includes(ext)) {
            console.log('Extracting from image (OCR)...');
            text = await extractImage(filePath);
        } else {
            console.log('Unsupported format:', ext);
            process.exit(1);
        }
        
        console.log('\n=== EXTRACTED TEXT ===\n');
        console.log(text.slice(0, 5000));
        console.log('\n... (truncated)\n');
        
    } catch (e) {
        console.log('Error:', e.message);
        process.exit(1);
    }
}

main();
