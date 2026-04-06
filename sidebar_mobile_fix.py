import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

def extract(url):
    r = requests.get(url, timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.string.strip() if soup.title else "Website"
    h1 = soup.find('h1')
    h1_text = h1.get_text(strip=True) if h1 else title
    h2s = [h.get_text(strip=True) for h in soup.find_all('h2')[:5]]
    paras = [p.get_text(strip=True) for p in soup.find_all('p') if 30 < len(p.get_text(strip=True)) < 500][:6]
    return {'title': title, 'h1': h1_text, 'h2s': h2s, 'paras': paras}

def build(dna):
    t, h1, h2s, ps = dna['title'], dna['h1'], dna['h2s'], dna['paras']
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t}</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Lato', sans-serif; background: #f5f5f5; color: #222; }}
        
        /* MOBILE FIRST */
        .sidebar {{ display: flex; flex-direction: column; min-height: 100vh; }}
        .left {{ background: #262626; color: #fff; padding: 2.5rem 1.5rem; order: 1; }}
        .right {{ padding: 2rem 1.5rem; order: 2; }}
        
        .left h1 {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; margin-bottom: 1rem; }}
        .left p {{ font-size: 0.9rem; line-height: 1.6; opacity: 0.9; }}
        
        .right h2 {{ font-family: 'Playfair Display', serif; font-size: 1.3rem; margin: 1.5rem 0 0.8rem; color: #262626; }}
        .right p {{ color: #666; line-height: 1.7; font-size: 0.95rem; }}
        
        /* TABLET */
        @media (min-width: 768px) {{
            .sidebar {{ flex-direction: row; }}
            .left {{ width: 35%; position: fixed; height: 100vh; padding: 4rem 2rem; }}
            .right {{ width: 65%; margin-left: 35%; padding: 4rem 2rem; }}
            .left h1 {{ font-size: 2.2rem; margin-bottom: 1.5rem; }}
            .left p {{ font-size: 1rem; }}
            .right h2 {{ font-size: 1.8rem; margin: 2.5rem 0 1rem; }}
        }}
        
        /* DESKTOP */
        @media (min-width: 1024px) {{
            .left h1 {{ font-size: 2.5rem; }}
            .left p {{ font-size: 1.1rem; }}
            .right h2 {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="left">
            <h1>{h1}</h1>
            <p>{ps[0] if ps else ''}</p>
        </div>
        <div class="right">
            <h2>{h2s[0] if h2s else 'Willkommen'}</h2>
            <p>{ps[1] if len(ps)>1 else ''}</p>
            <h2>{h2s[1] if len(h2s)>1 else ''}</h2>
            <p>{ps[2] if len(ps)>2 else ''}</p>
            <h2>{h2s[2] if len(h2s)>2 else ''}</h2>
            <p>{ps[3] if len(ps)>3 else ''}</p>
        </div>
    </div>
</body>
</html>'''

dna = extract("https://restaurant38berlin.de")
with open('/tmp/sidebar-mobile.html', 'w') as f:
    f.write(build(dna))
print("✅ Done")
