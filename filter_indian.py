import json
import re
import collections

with open('movie.md', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

all_entries = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('#EXTINF:'):
        tvg_id = ""
        tvg_logo = ""
        group_title = "Movies"
        
        m_id = re.search(r'tvg-id="([^"]*)"', line)
        if m_id:
            tvg_id = m_id.group(1)
            
        m_logo = re.search(r'tvg-logo="([^"]*)"', line)
        if m_logo:
            tvg_logo = m_logo.group(1)
            
        m_group = re.search(r'group-title="([^"]*)"', line)
        if m_group:
            group_title = m_group.group(1)
            
        comma_idx = line.rfind(',')
        raw_name = line[comma_idx + 1:].strip() if comma_idx != -1 else "Movie Channel"
        if ',' in raw_name:
            raw_name = raw_name.split(',')[-1].strip()
            
        res_match = re.search(r'\b(1080p|720p|576p|576i|480p|360p|4K|HD|SD)\b', raw_name, re.IGNORECASE)
        resolution = res_match.group(1).upper() if res_match else "HD"
        
        clean_name = re.sub(r'\s*\((?:1080p|720p|576p|576i|480p|360p|4K|HD|SD|Not 24/7|Geo-blocked|United States|Ukraine|Sweden|Poland|Czech Republic|Brazil|Hungary|Romania|Portugal|Russia|France|Spain|Magyar|India)\)', '', raw_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\s*\[(?:Not 24/7|Geo-blocked)\]', '', clean_name, flags=re.IGNORECASE).strip()
        if not clean_name:
            clean_name = raw_name
            
        if i + 1 < len(lines):
            stream_url = lines[i + 1].strip()
            if stream_url.startswith('http'):
                all_entries.append({
                    "id": tvg_id,
                    "name": clean_name,
                    "raw_name": raw_name,
                    "resolution": resolution,
                    "logo": tvg_logo,
                    "group": group_title,
                    "url": stream_url,
                    "extinf_line": line
                })
                i += 1
    i += 1

indian_keywords = [
    'zee', 'star', 'colors', 'sony', 'b4u', 'goldmines', 'bhojpuri', 'bollywood', 
    'bollygold', 'jalsha', 'alankar', 'etv', 'kairali', 'bflix', 'epic', 
    'shemaroo', 'dangal', 'manoranjan', 'cinema tv', 'box cinema', 'dhamaal', 
    'maha', 'filamchi', 'mastiii', 'surya', 'asianet', 'gemini', 'maa tv', 
    'sun tv', 'vijay', 'raj tv', 'polimer', 'tarang', 'prarthana', 'indrila',
    'tulsi', 'shubh', 'divya', 'aastha', 'sanskar', 'sadhna', 'arihant',
    'punjabi', 'marathi', 'bengali', 'tamil', 'telugu', 'kannada', 'malayalam',
    'gujarati', 'odia', 'bhojpuri', 'urdu', 'hindi', 'india', 'bharat', 'deshi',
    'tangotv', 'tarangplus', 'yupptv', 'cricodi', 'amg02159'
]

non_indian_markers = [
    '.ua@', '.ru@', '.us@', '.uk@', '.fr@', '.de@', '.es@', '.it@', '.pl@', 
    '.cz@', '.sk@', '.ro@', '.hu@', '.bg@', '.gr@', '.tr@', '.ar@', '.br@',
    '.mx@', '.cl@', '.co@', '.pe@', '.pt@', '.nl@', '.se@', '.no@', '.dk@',
    '.fi@', '.cn@', '.tw@', '.jp@', '.kr@', '.ir@', '.il@', '.sa@', '.eg@',
    '.cm@', '.gt@', '.do@', '.uz@', '.al@', '.hr@', '.rs@', '.ba@', '.me@',
    'pluto.tv', 'catcast.tv', 'mcquack.net', 'mangora1', 'antik.sk', 'tvstitch.com',
    'wns.live', 'presstv.co.uk', 'linkintel.ru', 'siliconweb.com', 'antenaplay.ro'
]

def assign_category(text_str):
    s = text_str.lower()
    if any(k in s for k in ['bhojpuri', 'bflix', 'oscar']):
        return 'bhojpuri'
    elif any(k in s for k in ['tamil', 'telugu', 'kannada', 'malayalam', 'south', 'suriyan', 'thalaa', 'tolly', 'raj digital', 'kairali', 'etv', 'maa movies', 'public movies']):
        return 'south'
    elif any(k in s for k in ['bangla', 'jalsha', 'pitaara', 'punjabi', 'talkies', 'marathi', 'alankar', 'odia', 'bengali', 'mh one']):
        return 'regional'
    elif any(k in s for k in ['action', 'kadak', 'pix']):
        return 'action'
    else:
        return 'bollywood'

indian_channels = []
seen_urls = set()

for ch in all_entries:
    tid = ch['id'].lower()
    name = ch['name'].lower()
    raw = ch['raw_name'].lower()
    url = ch['url'].lower()
    
    is_explicit_indian = (
        '.in@' in tid or 
        '@india' in tid or 
        '@apac' in tid or
        '.in/' in url or
        '.in:' in url or
        'tangotv.in' in url or
        'tarangplus.in' in url or
        'yupptv' in url or
        'yuppcdn.net' in url or
        'cricodi' in url or
        'samsung-in' in url
    )
    
    has_keyword = any(k in name or k in raw or k in tid for k in indian_keywords)
    is_foreign_id = any(tid.endswith(m) or m in tid for m in non_indian_markers)
    is_foreign_host = any(m in url for m in ['mcquack.net', 'wns.live', 'antik.sk', 'siliconweb.com', 'catcast.tv', 'presstv.co.uk'])
    
    if 'russia' in raw or 'russian' in raw or 'ru@' in tid or 'ua@' in tid or 'cinerama_edge01' in url:
        continue
    if 'spain' in raw or 'es@' in tid or 'czech' in raw or 'hungary' in raw or 'poland' in raw:
        continue
    if 'taiwan' in raw or 'tw' in tid:
        continue
        
    if is_explicit_indian or (has_keyword and not is_foreign_id and not is_foreign_host):
        if ch['url'] not in seen_urls:
            seen_urls.add(ch['url'])
            ch['category'] = assign_category(ch['name'] + ' ' + ch['raw_name'] + ' ' + ch['id'])
            indian_channels.append(ch)

counts = collections.Counter(c['category'] for c in indian_channels)
print(f"Total Indian channels: {len(indian_channels)}")
print("Categories:", counts)

# Save clean JSON without internal helper fields
json_export = []
for c in indian_channels:
    entry = {k: v for k, v in c.items() if k != 'extinf_line'}
    json_export.append(entry)

with open('static/channels.json', 'w', encoding='utf-8') as f:
    json.dump(json_export, f, indent=2, ensure_ascii=False)
print("Saved cleanly to static/channels.json")

# Write clean movie.md containing ONLY Indian channels
m3u_lines = [
    "#EXTM3U",
    "#PLAYLIST:Indian Live Movie Channels - StreamBox",
    ""
]
for ch in indian_channels:
    m3u_lines.append(ch['extinf_line'])
    m3u_lines.append(ch['url'])
    m3u_lines.append("")

with open('movie.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(m3u_lines).rstrip() + "\n")
print("Saved cleanly to movie.md (only Indian channels)")
