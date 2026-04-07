#!/usr/bin/env node
/**
 * OpenStreetMap Business Finder - Final
 */

const https = require('https');

const OVERPASS_SERVERS = [
    'https://overpass-api.de/api/interpreter',
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
    'https://overpass.openstreetmap.ru/api/interpreter'
];

async function tryQuery(server, lat, lon, category, limit) {
    const categoryMap = {
        restaurant: 'amenity=restaurant',
        cafe: 'amenity=cafe',
        bar: 'amenity=bar',
        fast_food: 'amenity=fast_food',
        gym: 'leisure=fitness_centre',
        salon: 'shop=hairdresser',
        supermarket: 'shop=supermarket'
    };
    
    const tag = categoryMap[category] || 'shop=*';
    const query = `[out:json][timeout:30];
(
  node["${tag}"](around:5000,${lat},${lon});
);
out ${limit};`;

    return new Promise((resolve) => {
        const postData = JSON.stringify({ data: query });
        const [host, ...path] = server.replace('https://', '').split('/');
        
        const options = {
            hostname: host,
            port: 443,
            path: '/' + path.join('/'),
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    const businesses = (json.elements || []).map(el => ({
                        name: el.tags?.name || 'Unnamed',
                        lat: el.lat,
                        lon: el.lon,
                        address: el.tags?.['addr:street'] ? `${el.tags['addr:housenumber']||''} ${el.tags['addr:street']}`.trim() : '',
                        phone: el.tags?.phone || ''
                    }));
                    resolve(businesses);
                } catch(e) { resolve([]); }
            });
        });
        
        req.on('error', () => resolve([]));
        req.write(postData);
        req.end();
    });
}

async function search(city, category, limit = 20) {
    // Get city coordinates
    return new Promise((resolve) => {
        https.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}&limit=1`, 
        { headers: { 'User-Agent': 'EmpireHazeClaw/1.0' } }, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', async () => {
                try {
                    const json = JSON.parse(data);
                    if (!json[0]) { resolve([]); return; }
                    
                    const { lat, lon } = json[0];
                    
                    // Try each server
                    for (const server of OVERPASS_SERVERS) {
                        const businesses = await tryQuery(server, lat, lon, category, limit);
                        if (businesses.length > 0) {
                            resolve(businesses);
                            return;
                        }
                    }
                    resolve([]);
                } catch(e) { resolve([]); }
            });
        }).on('error', () => resolve([]));
    });
}

const args = process.argv.slice(2);
if (args[0] === 'search') {
    const city = args[1] || 'Berlin';
    const category = args[2] || 'restaurant';
    const limit = parseInt(args[3]) || 20;
    
    console.log(`\n🗺️  ${category} in ${city}...\n`);
    
    search(city, category, limit).then(businesses => {
        if (businesses.length === 0) {
            console.log('No results. All OSM servers busy.');
            return;
        }
        console.log(`Found ${businesses.length}:\n`);
        businesses.slice(0, 10).forEach((b, i) => {
            console.log(`${i+1}. ${b.name}`);
            if (b.address) console.log(`   📍 ${b.address}`);
            if (b.phone) console.log(`   📞 ${b.phone}`);
            console.log('');
        });
    });
}
else {
    console.log('Usage: node osm-business.js search "Berlin" "restaurant"');
}
