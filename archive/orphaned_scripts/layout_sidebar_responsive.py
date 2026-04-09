#!/usr/bin/env python3
"""Sidebar layout - MOBILE RESPONSIVE"""
import sys
import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup
import re
requests.packages.urllib3.disable_warnings()

def extract(url):
    r = requests.get(url, timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.string.strip() if soup.title else "Website"
    h1 = soup.find('h1')
    h1_text = h1.get_text(strip=True) if h1 else title
    h2s = [h.get_text(strip=True) for h in soup.find_all('h2')[:5]]
    paras = [p.get_text(strip=True) for p in soup.find_all('p') if 30 < len(p.get_text(strip=True)) < 500][:6]
    ctas = [btn.get_text(strip=True) for btn in soup.find_all(['a','button']) if 2 < len(btn.get_text(strip=True)) < 50][:5]
    return {'title': title, 'h1': h1_text, 'h2s': h2s, 'paras': paras, 'ctas': ctas, 'success': True}

def build(dna):
    t, h1, h2s, ps, ctas = dna['title'], dna['h1'], dna['h2s'], dna['paras'], dna['ctas']
    return f'''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{t}</title><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@400;700&display=swap" rel="stylesheet"><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Lato',sans-serif;background:#f5f5f5;color:#222}}.container{{display:flex;min-height:100vh;flex-direction:column}}@media(min-width:768px){{.container{{flex-direction:row}}.left{{width:35%;position:fixed;height:100%}}.right{{width:65%;margin-left:35%}}}}@media(max-width:767px){{.left{{width:100%;padding:3rem 1.5rem}}.right{{width:100%;padding:2rem 1.5rem}}}}.left{{background:#262626;color:#fff;padding:3rem 1.5rem}}.left h1{{font-family:'Playfair Display',serif;font-size:1.8rem;margin-bottom:1rem}}@media(min-width:768px){{.left h1{{font-size:2.5rem;margin-bottom:2rem}}}}.left p{{font-size:0.95rem;opacity:0.9}}@media(min-width:768px){{.left p{{font-size:1.1rem}}}}.right{{padding:2rem 1.5rem}}@media(min-width:768px){{.right{{padding:4rem 2rem}}}}.right h2{{font-family:'Playfair Display',serif;font-size:1.5rem;margin:2rem 0 1rem}}@media(min-width:768px){{.right h2{{font-size:2rem}}}}.right p{{color:#666;line-height:1.8;margin-bottom:1.5rem}}</style></head><body><div class="container"><div class="left"><h1>{h1}</h1><p>{ps[0] if ps else ''}</p></div><div class="right"><h2>{h2s[0] if h2s else 'Info'}</h2><p>{ps[1] if len(ps)>1 else ''}</p><h2>{h2s[1] if len(h2s)>1 else ''}</h2><p>{ps[2] if len(ps)>2 else ''}</p><h2>{h2s[2] if len(h2s)>2 else ''}</h2><p>{ps[3] if len(ps)>3 else ''}</p></div></div></body></html>'''

if __name__ == '__main__':
    dna = extract("https://restaurant38berlin.de")
    with open('/tmp/sidebar-fixed.html', 'w') as f:
        f.write(build(dna))
    print("✅ sidebar-fixed.html")
