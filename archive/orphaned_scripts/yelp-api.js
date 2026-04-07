#!/usr/bin/env node
/**
 * Yelp API Integration
 * For Local Closer Project
 */

const YELP_KEY = process.env.YELP_API_KEY || 'YOUR_KEY_HERE';

async function searchBusinesses(location, category, limit = 10) {
    const url = `https://api.yelp.com/v3/businesses/search?location=${encodeURIComponent(location)}&categories=${category}&limit=${limit}`;
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${YELP_KEY}`,
            'Accept': 'application/json'
        }
    });
    
    return response.json();
}

async function getBusiness(id) {
    const response = await fetch(`https://api.yelp.com/v3/businesses/${id}`, {
        headers: {
            'Authorization': `Bearer ${YELP_KEY}`
        }
    });
    
    return response.json();
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'search') {
    const location = args[1] || 'Berlin';
    const category = args[2] || 'restaurants';
    
    console.log(`\n🔍 Searching Yelp: ${category} in ${location}\n`);
    
    searchBusinesses(location, category).then(data => {
        if (data.businesses) {
            data.businesses.forEach(b => {
                console.log(`📍 ${b.name}`);
                console.log(`   ${b.location.address1}, ${b.location.city}`);
                console.log(`   ⭐ ${b.rating}/5 | 📞 ${b.phone}`);
                console.log('');
            });
            console.log(`Found ${data.businesses.length} businesses`);
        } else {
            console.log('Error:', data);
        }
    });
}
else {
    console.log(`
🔍 YELP API

Usage:
  node scripts/yelp-api.js search "Berlin" "restaurants"
  node scripts/yelp-api.js search "Hamburg" "plumbers"

Note: Need YELP_API_KEY in /home/clawbot/.keys/yelp_key

Sign up: https://www.yelp.com/developers
`);
}
