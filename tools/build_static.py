#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
import html
import unicodedata
from urllib.parse import urlparse, parse_qs
import urllib.request
import urllib.parse
import json

# Project paths (must be defined early)
ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
OUT = ROOT / "static_site"

# External grammar correction toggle (disabled per request)
ENABLE_GRAMMAR_API = False  # keep local corrections only; no external API calls

# --- Normalization utilities ---
REPLACEMENTS = {
    "\u00A0": " ",   # non-breaking space
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201C": '"',  # left double quote
    "\u201D": '"',  # right double quote
    "\u2026": "...",  # ellipsis
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
}


def normalize_text(s: str) -> str:
    if not s:
        return s
    # Decode HTML entities first (e.g., &eacute;)
    s = html.unescape(s)
    # Unicode normalization
    s = unicodedata.normalize("NFKC", s)
    # Common punctuation/space fixes
    for k, v in REPLACEMENTS.items():
        s = s.replace(k, v)
    # Unified French text correction pipeline
    s = text_correction(s)
    # Strip weird control chars
    s = "".join(ch for ch in s if (ch == "\n" or ch == "\t" or unicodedata.category(ch)[0] != 'C'))
    return s.strip()


def _transform_text_nodes(html_str: str, fn) -> str:
    # Split into tags and text, apply fn to text nodes only
    parts = re.split(r'(</?[^>]+>)', html_str)
    for i, part in enumerate(parts):
        if not part:
            continue
        if part.startswith('<') and part.endswith('>'):
            continue  # skip tags
        parts[i] = fn(part)
    return ''.join(parts)


def normalize_html(s: str) -> str:
    if not s:
        return s
    def norm_text(text: str) -> str:
        t = html.unescape(text)
        t = unicodedata.normalize("NFKC", t)

        return t
    return _transform_text_nodes(s, norm_text)


def text_correction(text: str) -> str:
    """Run all French text editing steps in order, on plain text (not HTML tags)."""
    if not text:
        return text
    t = apply_phrase_fixes(text)          # targeted sentence/phrase corrections first
    t = apply_word_map(t)                 # unified word-level replacements (accents + spelling)
    t = apply_preposition_heuristics(t)   # " a " -> " à ", " ou " -> " où " in common contexts
    t = fix_acute_e_heuristics(t)         # feminine participles/adjectives (ee -> ée, etc.)
    t = french_typography(t)              # spacing and punctuation
    if ENABLE_GRAMMAR_API:
        t = grammar_fix_via_languagetool(t)
    return t


# Unified French word replacements (accents + common spelling)
FRENCH_WORDS_MAP = {
    # very safe common words
    "tres": "très",
    "tres-": "très-",
    "deja": "déjà",
    "degagee": "dégagée",
    "degage": "dégagé",
    "ete": "été",
    "eteait": "était",  # common misspelling without accents
    "etait": "était",
    "etais": "étais",
    "etions": "étions",
    "etiez": "étiez",
    "etaient": "étaient",
    "eleve": "élève",
    "eleves": "élèves",
    "garcon": "garçon",
    "garcons": "garçons",
    "francais": "français",
    "francaise": "française",
    "francaises": "françaises",
    "ca": "ça",
    "pere": "père",
    "meres": "mères",
    "mere": "mère",
    "noel": "Noël",
    "aout": "août",
    "decembre": "décembre",
    "fevrier": "février",
    "janvier": "janvier",
    "mars": "mars",
    "avril": "avril",
    "mai": "mai",
    "juin": "juin",
    "juillet": "juillet",
    "octobre": "octobre",
    "novembre": "novembre",
    "australie": "Australie",
    "sao paulo": "São Paulo",
    "apres": "après",
    "depart": "départ",
    "departs": "départs",
    "departement": "département",
    "departements": "départements",
    "soiree": "soirée",
    "soirees": "soirées",
    "cafe": "café",
    "cafes": "cafés",
    "cote": "côté",
    "cotes": "côtés",
    "hotel": "hôtel",
    "hotels": "hôtels",
    # Travel/common terms
    "aeroport": "aéroport",
    "aeroports": "aéroports",
    "aerien": "aérien",
    "aeriens": "aériens",
    "aerienne": "aérienne",
    "aeriennes": "aériennes",
    "aerodrome": "aérodrome",
    "aerodromes": "aérodromes",
    "aeronautique": "aéronautique",
    "aeronaval": "aéronaval",
    "perou": "Pérou",
    "bresil": "Brésil",
    "equateur": "Équateur",
    "ile": "île",
    "iles": "îles",
    # Proper nouns frequently misspelled
    "macchu picchu": "Machu Picchu",
    "macchu": "Machu",
    "cuzco": "Cuzco",
    "ollamtaytambo": "Ollantaytambo",
    "ollanta": "Ollantaytambo",
    "agua calientes": "Aguas Calientes",
    "a. calientes": "Aguas Calientes",
    # Common French words
    "aujoudhui": "aujourd'hui",
    "aujourdhui": "aujourd'hui",
    "aujourd hui": "aujourd'hui",
    "pres": "près",
    "etre": "être",
    "rechauffe": "réchauffé",
    "frere": "frère",
    "soeur": "sœur",
    "coeur": "cœur",
    "elevé": "élevé",
    # Common nouns frequently typed without accents
    "ecole": "école",
    "eglise": "église",
    "etude": "étude",
    "etudier": "étudier",
    "resume": "résumé",
    # Examples reported
    "soldee": "soldée",
    "soldees": "soldées",
    # User-requested fixes
    "realise": "réalise",
    "realises": "réalises",
    "realisee": "réalisée",
    "realisees": "réalisées",
    "quété": "quête",
    "quete": "quête",
    "tot": "tôt",
    "achétér": "acheter",
    "achéter": "acheter",
}


def _apply_word_map(text: str, mapping: dict[str, str]) -> str:
    # Replace whole words with accents, preserving capitalization of the first letter
    def repl_factory(src: str, dst: str):
        pattern = re.compile(rf"\b{re.escape(src)}\b", re.IGNORECASE)

        def repl(m):
            word = m.group(0)
            if word and word[0].isupper():
                return dst[0].upper() + dst[1:]
            return dst

        return pattern, repl

    for src, dst in mapping.items():
        pattern, repl = repl_factory(src, dst)
        text = pattern.sub(repl, text)
    return text


def _regex_replace(text: str, pattern: str, repl: str) -> str:
    return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def apply_preposition_heuristics(text: str) -> str:
    if not text:
        return text
    t = text
    # Heuristics for " a " -> " à " when used as preposition
    t = _regex_replace(t, r"\b a (la|le|les|l'|un|une|cote|droite|gauche|pied|propos|cause|bord|l'endroit)\b", r" à \1")
    # Heuristics for " ou " -> " où " in typical question/relative contexts
    t = _regex_replace(t, r"\b ou (je|tu|il|elle|on|nous|vous|ils|elles|est|etait|etais|etaient|que|qu|se|ca|cela)\b", r" où \1")
    # Common forms with apostrophes missing accents
    t = t.replace("l'ete", "l'été").replace("d'ete", "d'été")
    t = t.replace("ete", "été")  # fallback if missed
    return t


def apply_word_map(text: str) -> str:
    return _apply_word_map(text, FRENCH_WORDS_MAP)


def french_typography(text: str) -> str:
    if not text:
        return text
    t = text
    # Add space before ; : ! ? if missing
    t = re.sub(r"\s*([;:!?])", r" \1", t)
    # Remove extra spaces before commas and periods
    t = re.sub(r"\s+([.,])", r"\1", t)
    # Normalize French quotes
    t = t.replace('"', '"')  # keep straight quotes for simplicity
    # Collapse multiple spaces
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t


def fix_acute_e_heuristics(text: str) -> str:
    if not text:
        return text
    t = text
    # Heuristic: words ending with 'ee' -> 'ée', and plural 'ees' -> 'ées'
    # Limit to letters to avoid URLs
    t = re.sub(r"\b([a-zàâçéèêëîïôùûüÿœæ'-]{2,})ee(s?)\b", lambda m: m.group(1) + "ée" + m.group(2), t, flags=re.IGNORECASE)
    return t



# Targeted phrase fixes based on observed errors (kept minimal and safe)
PHRASE_FIXES = [
    (r"Je n'ai pas dormi d[éè] la nuit", "Je n'ai pas dormi de la nuit"),
    (r"mon site internet ressembl[ée] à quelque chose", "mon site internet ressemble à quelque chose"),
    (r"l[èe]s employ[ée]s d'Iberia se d[ée]patouillent avec le billet tour d[ûu] mond[ée]", "les employés d'Iberia se dépatouillent avec le billet tour du monde"),
    (r"avec l[èe]s agenc[ée]s et comptoirs c'?est l[àa] panade totale", "avec les agences et comptoirs c'est la panade totale"),
    (r"une autre passante qui pass[ée], puis l'heure d[é] l'embarquement arriv[ée] enfin\.", "une autre passante qui passe, puis l'heure de l'embarquement arrive enfin."),
    (r"je n[ée] vais pas l[èe]s revoir", "je ne vais pas les revoir"),
]


def apply_phrase_fixes(text: str) -> str:
    t = text
    for pattern, replacement in PHRASE_FIXES:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    return t


def grammar_fix_via_languagetool(text: str) -> str:
    
    """Use LanguageTool public API to fix French grammar/accents. Best-effort, safe if offline."""
    # Split large text into paragraphs to limit payload and preserve offsets locally
    paragraphs = re.split(r"(\n{2,})", text)
    out = []
    for i in range(0, len(paragraphs)):
        seg = paragraphs[i]
        if not seg or seg.startswith("\n"):
            out.append(seg)
            continue
        fixed = _lt_fix_segment(seg)
        out.append(fixed)
    return "".join(out)


def _lt_fix_segment(seg: str) -> str:
    # LanguageTool endpoint
    url = "https://api.languagetool.org/v2/check"
    data = {
        "language": "fr-FR",
        "text": seg,
    }
    try:
        payload = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return seg  # On any error, return original segment

    matches = result.get("matches", [])
    if not matches:
        return seg
    # Apply replacements from end to start to preserve offsets
    fixed = seg
    # Build a list of tuples (offset, length, replacement)
    repls = []
    for m in matches:
        offset = m.get("offset")
        length = m.get("length")
        reps = m.get("replacements") or []
        if offset is None or length is None or not reps:
            continue
        rep = reps[0].get("value")
        if not rep:
            continue
        repls.append((offset, length, rep))
    # Sort descending by offset
    repls.sort(key=lambda x: x[0], reverse=True)
    for offset, length, rep in repls:
        try:
            fixed = fixed[:offset] + rep + fixed[offset+length:]
        except Exception:
            # If indices out of range due to unexpected chars, skip
            continue
    return fixed

# Regions to scan for city pages
REGIONS = [
    "afrique",
    "amsud",
    "asie",
    "ausnz",
    "europe",
]

# Patterns for content extraction
TITRE_RE = re.compile(r"<div\s+class=\"titre\">", re.IGNORECASE)
FOOTER_REQ_RE = re.compile(r"require\(.*footer\.html\)\s*;", re.IGNORECASE)
HEADER_REQ_RE = re.compile(r"require\(.*header\.html\)\s*;", re.IGNORECASE)
PHP_TAG_RE = re.compile(r"<\?(php)?|\?>", re.IGNORECASE)
REQ_STMT_RE = re.compile(r"require\s*\([^)]*footer\.html[^)]*\)\s*;?", re.IGNORECASE)
REQ_ANY_RE = re.compile(r"^\s*require\s*\([^)]*\)\s*;?\s*$", re.IGNORECASE | re.MULTILINE)

# Menu link regex
MENU_LINK_RE = re.compile(r"<a\s+href=\"([^\"]+)\"[^>]*>([^<]+)</a>", re.IGNORECASE)

# Basic modern responsive CSS
CSS = r"""
:root {
  --bg: #0f172a; /* slate-900 */
  --panel: #111827; /* gray-900 */
  --panel-2: #0b1220;
  --text: #e5e7eb; /* gray-200 */
  --muted: #9ca3af; /* gray-400 */
  --accent: #3b82f6; /* blue-500 */
  --accent-2: #22d3ee; /* cyan-400 */
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  background: radial-gradient(1200px 600px at 0% 0%, #111827 0, var(--bg) 50%, #0a0f1e 100%);
  color: var(--text);
}
.wrapper { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar { background: linear-gradient(180deg, var(--panel), var(--panel-2)); border-right: 1px solid #1f2937; padding: 20px; position: sticky; top: 0; align-self: start; height: 100vh; overflow: auto; }
.brand { font-weight: 700; letter-spacing: .5px; color: white; margin-bottom: 12px; }
.version { color: var(--muted); font-size: 12px; margin-bottom: 16px; }
.nav a { color: #cbd5e1; text-decoration: none; display: block; padding: 6px 8px; border-radius: 6px; }
.nav a:hover { background: rgba(59,130,246,.15); color: white; }
.nav a:visited { color: #a78bfa; }
.nav a.active { background: rgba(34,211,238,.18); color: white; }
.content { padding: 24px; max-width: 1100px; }
.header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px; }
.h1 { font-size: 28px; font-weight: 700; }
.titre { font-size: 36px; font-weight: 800; margin: 6px 0 10px; }
.resume { color: var(--muted); margin-bottom: 20px; font-style: italic; }
.texte { line-height: 1.6; }
.texte h2 { margin-top: 1.2em; color: var(--accent-2); font-size: 22px; }
.backlink { margin: 6px 0 12px; }
.backlink a { color: var(--accent); text-decoration: none; }
.backlink a:hover { text-decoration: underline; }
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; margin: 18px 0 24px; }
.gallery a { display: block; border-radius: 8px; overflow: hidden; background: #0b1220; border: 1px solid #1f2937; }
.gallery img { display: block; width: 100%; height: 140px; object-fit: cover; transition: transform .2s ease-in-out; }
.gallery a:hover img { transform: scale(1.03); }
.footer { border-top: 1px solid #1f2937; margin-top: 28px; padding-top: 14px; color: var(--muted); font-size: 14px; }
.backtop { margin-top: 8px; display: inline-block; color: var(--accent); }
@media (max-width: 900px) { .wrapper { grid-template-columns: 1fr; } .sidebar { height: auto; position: static; } }
"""

BASE_HEAD = """
<!doctype html>
<html lang=\"fr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"{rel}assets/styles.css\" />
</head>
<body>
<div class=\"wrapper\">"""

BASE_SIDEBAR_START = """
  <aside class=\"sidebar\">
    <a class=\"brand\" href=\"{rel}index.html\">Voyages</a>
    <nav class=\"nav\">
"""
BASE_SIDEBAR_END = """
    </nav>
  </aside>
"""

BASE_CONTENT_START = """
  <main class=\"content\">
"""
BASE_CONTENT_END = """
  </main>
</div>
</body>
</html>
"""

# Minimal city coordinates (lon, lat). Extend as needed.
CITY_COORDS = {
    # Europe
    ("europe","madrid"): (-3.7038, 40.4168),
    # AmSud
    ("amsud","lima"): (-77.0428, -12.0464),
    ("amsud","pisco"): (-76.2167, -13.7000),
    ("amsud","arequipa"): (-71.5350, -16.4090),
    ("amsud","cuzco"): (-71.9675, -13.5320),
    ("amsud","lapaz"): (-68.1193, -16.4897),
    ("amsud","uyuni"): (-66.8250, -20.4600),
    ("amsud","salta"): (-65.4232, -24.7821),
    ("amsud","mendoza"): (-68.8458, -32.8895),
    ("amsud","saopaulo"): (-46.6339, -23.5505),
    ("amsud","parati"): (-44.7178, -23.2221),
    ("amsud","rio"): (-43.1729, -22.9068),
    ("amsud","salvador"): (-38.5014, -12.9730),
    ("amsud","olinda"): (-34.8553, -8.0089),
    ("amsud","natal"): (-35.2094, -5.7945),
    ("amsud","rio2"): (-43.1729, -22.9068),
    ("amsud","iguazu"): (-54.5850, -25.6953),
    ("amsud","buenosaires"): (-58.3816, -34.6037),
    ("amsud","santiago"): (-70.6693, -33.4489),
    ("amsud","havana"): (-82.3666, 23.1136),
    ("amsud","cienfuegos"): (-80.4570, 22.1496),
    ("amsud","havana2"): (-82.3666, 23.1136),
    # Aus/NZ
    ("ausnz","auckland"): (174.7633, -36.8485),
    ("ausnz","tororua"): (176.2483, -38.1368),  # assuming Rotorua
    ("ausnz","taupo"): (176.0833, -38.6833),
    ("ausnz","wellington"): (174.7762, -41.2866),
    ("ausnz","picton"): (173.95, -41.2928),
    ("ausnz","melbourne"): (144.9631, -37.8136),
    ("ausnz","darwin"): (130.8456, -12.4634),
    ("ausnz","cairns"): (145.7703, -16.9186),
    ("ausnz","sydney"): (151.2093, -33.8688),
    # Asie
    ("asie","bangkok"): (100.5018, 13.7563),
    ("asie","kohsamui"): (99.9357, 9.5120),
    ("asie","bangkok2"): (100.5018, 13.7563),
    ("asie","kohchang"): (102.367, 12.070),
    ("asie","chiangmai"): (98.993, 18.788),
    ("asie","chiangrai"): (99.8325, 19.9105),
    ("asie","luangprabang"): (102.136, 19.885),
    ("asie","vientiane"): (102.634, 17.975),
    ("asie","pakse"): (105.783, 15.117),
    ("asie","donkhong"): (105.85, 14.0),
    ("asie","stungtreng"): (106.008, 13.525),
    ("asie","phnompenh"): (104.921, 11.565),
    ("asie","angkor"): (103.8667, 13.4125),
    ("asie","colombo"): (79.8612, 6.9271),
    ("asie","kandy"): (80.6337, 7.2906),
    ("asie","nuwaraeliya"): (80.7829, 6.9497),
    ("asie","kandy2"): (80.6337, 7.2906),
    ("asie","sigiriya"): (80.7603, 7.9570),
    ("asie","trincomalee"): (81.233, 8.571),
    ("asie","kandy3"): (80.6337, 7.2906),
    ("asie","chennai"): (80.2707, 13.0827),
    ("asie","bangalore"): (77.5946, 12.9716),
    ("asie","goa"): (74.1240, 15.2993),
    ("asie","mumbay"): (72.8777, 19.0760),
    ("asie","varanasi"): (82.9739, 25.3176),
    ("asie","katmandou"): (85.3240, 27.7172),
    ("asie","bali"): (115.1889, -8.4095),
    ("asie","hongkong"): (114.1694, 22.3193),
    # Afrique
    ("afrique","nairobi"): (36.8219, -1.2921),
    ("afrique","mombasa"): (39.6682, -4.0435),
    ("afrique","tiwi"): (39.55, -4.27),
    ("afrique","zanzibar"): (39.1925, -6.1659),
    ("afrique","capetown"): (18.4241, -33.9249),
}

def ensure_map_assets():
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    files = {
        "world-110m.json": "https://unpkg.com/world-atlas@2/land-110m.json",
        "topojson-client.min.js": "https://unpkg.com/topojson-client@3/dist/topojson-client.min.js",
        "d3-array.min.js": "https://unpkg.com/d3-array@3/dist/d3-array.min.js",
        "d3-geo.min.js": "https://unpkg.com/d3-geo@3/dist/d3-geo.min.js",
    }
    for name, url in files.items():
        dst = assets / name
        if not dst.exists():
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    data = resp.read()
                dst.write_bytes(data)
            except Exception:
                # If download fails, skip; map will not render fully offline
                pass
    # Produce a JS wrapper to avoid fetch() under file://
    wjson = assets / "world-110m.json"
    wjs = assets / "world-110m.js"
    try:
        if wjson.exists():
            data = wjson.read_text(encoding="utf-8")
            # Write as a global variable assignment
            wjs.write_text("window.WORLD = " + data + ";", encoding="utf-8")
    except Exception:
        pass

def generate_map_index(menu_links) -> str:
    # Build ordered city list with coords
    ordered = []
    for region, city, label in menu_links:
        key = (region, city)
        if key in CITY_COORDS:
            lon, lat = CITY_COORDS[key]
            ordered.append({
                "region": region,
                "city": city,
                "label": normalize_text(label),
                "lon": lon,
                "lat": lat,
                "url": f"{region}/{city}/index.html",
            })
    cities_json = json.dumps(ordered)
    html = []
    html.append('<div class="header"><div class="h1">Carte des villes</div></div>')
    html.append('<svg id="worldmap" width="100%" height="600" viewBox="0 0 1100 600"></svg>')
    html.append('<script src="assets/d3-array.min.js"></script>')
    html.append('<script src="assets/d3-geo.min.js"></script>')
    html.append('<script src="assets/topojson-client.min.js"></script>')
    html.append('<script src="assets/world-110m.js"></script>')
    js = """
(function(){
  const svg = document.getElementById('worldmap');
  const width = svg.viewBox.baseVal.width;
  const height = svg.viewBox.baseVal.height;
  const NS = 'http://www.w3.org/2000/svg';
  function el(name, attrs){ const e=document.createElementNS(NS,name); if(attrs){ for(const k in attrs){ e.setAttribute(k, attrs[k]); } } return e; }
  const projection = d3.geoNaturalEarth1().fitExtent([[10,10],[width-10,height-10]], {type:'Sphere'});
  const path = d3.geoPath(projection);
  const root = el('g', { id:'groot' }); svg.appendChild(root);
  let scale=1, tx=0, ty=0;
  function applyTransform(){
    root.setAttribute('transform','translate('+tx.toFixed(1)+' '+ty.toFixed(1)+') scale('+scale.toFixed(3)+')');
    const inv=1/scale;
    if(window.__markers){ window.__markers.forEach(M=>{ M.el.setAttribute('transform','translate('+M.x.toFixed(1)+' '+M.y.toFixed(1)+') scale('+inv.toFixed(3)+')'); }); }
    // Show arrowheads if the scaled segment length exceeds threshold; normalize head size and rotation
    const TH = 150; // pixels
    if(window.__arrowheads){ window.__arrowheads.forEach(A=>{
      const node = A.el || A; const bl = A.bl != null ? A.bl : parseFloat(node.getAttribute('data-bl')||'0');
      const show = (bl*scale)>=TH; node.style.display = show ? '' : 'none';
      if (A.el) { const invs=(1/scale).toFixed(3); node.setAttribute('transform','translate('+A.x.toFixed(1)+' '+A.y.toFixed(1)+') rotate('+A.rot.toFixed(2)+') scale('+invs+')'); }
    }); }
  }
  svg.addEventListener('wheel', (ev)=>{ ev.preventDefault(); const rect=svg.getBoundingClientRect(); const mx=ev.clientX-rect.left, my=ev.clientY-rect.top; const k=Math.exp(-ev.deltaY*0.001); const newScale=Math.min(32, Math.max(0.25, scale*k)); const factor=newScale/scale; tx = mx - factor*(mx - tx); ty = my - factor*(my - ty); scale=newScale; applyTransform(); }, {passive:false});
  let dragging=false, lastX=0, lastY=0; svg.addEventListener('mousedown',(ev)=>{dragging=true; lastX=ev.clientX; lastY=ev.clientY;}); svg.addEventListener('mousemove',(ev)=>{ if(!dragging) return; const dx=ev.clientX-lastX, dy=ev.clientY-lastY; tx+=dx; ty+=dy; lastX=ev.clientX; lastY=ev.clientY; applyTransform(); }); svg.addEventListener('mouseup',()=>{dragging=false;}); svg.addEventListener('mouseleave',()=>{dragging=false;});
  try{
    const world = window.WORLD; const land = topojson.feature(world, world.objects.land); const landPath = el('path', { d: path(land), fill:'#334155', stroke:'#1f2937', 'stroke-width':1 }); root.appendChild(landPath);
    const defs=el('defs'); const marker=el('marker',{id:'arrow',markerWidth:6,markerHeight:6,refX:6,refY:3,orient:'auto',markerUnits:'strokeWidth'}); const arrowPath=el('path',{d:'M 0 0 L 6 3 L 0 6 z', fill:'#22d3ee'}); marker.appendChild(arrowPath); defs.appendChild(marker); svg.appendChild(defs);
    const cities = __CITIES__;
    function drawSegment(px,py,x,y,stroke='#22d3ee',curveScale=0.15,curveSign=1, forceCurve=false){ const dx=x-px, dy=y-py; const len=Math.hypot(dx,dy); const LONG=100; let d,midx,midy; if(forceCurve || len>LONG){ const mx=(px+x)/2, my=(py+y)/2; const nx=-dy/len, ny=dx/len; const ox=mx+nx*len*curveScale*curveSign, oy=my+ny*len*curveScale*curveSign; d='M '+px.toFixed(1)+' '+py.toFixed(1)+' Q '+ox.toFixed(1)+' '+oy.toFixed(1)+' '+x.toFixed(1)+' '+y.toFixed(1); midx=(px+2*ox+x)/4; midy=(py+2*oy+y)/4; } else { d='M '+px.toFixed(1)+' '+py.toFixed(1)+' L '+x.toFixed(1)+' '+y.toFixed(1); midx=(px+x)/2; midy=(py+y)/2; }
      const seg=el('path',{d, fill:'none', stroke, 'stroke-width':2, 'stroke-dasharray':'4 4', 'stroke-linecap':'round', 'vector-effect':'non-scaling-stroke'});
      root.appendChild(seg);
      const ux=dx/len, uy=dy/len; const theta=Math.atan2(uy,ux)*180/Math.PI; const invs=(1/scale).toFixed(3);
      const ah=el('g',{ transform:'translate('+midx.toFixed(1)+' '+midy.toFixed(1)+') rotate('+theta.toFixed(2)+') scale('+invs+')' });
      const tri=el('path',{ d:'M 0 0 L -10 -5 L -10 5 Z', fill:stroke, stroke:'none' }); ah.appendChild(tri); root.appendChild(ah);
      if(!window.__arrowheads) window.__arrowheads=[];
      window.__arrowheads.push({ el:ah, x:midx, y:midy, rot:theta, bl:len }); }
    function drawStraight(px,py,x,y,stroke='#22d3ee'){ const d='M '+px.toFixed(1)+' '+py.toFixed(1)+' L '+x.toFixed(1)+' '+y.toFixed(1); const seg=el('path',{d, fill:'none', stroke, 'stroke-width':2, 'stroke-dasharray':'4 4', 'stroke-linecap':'round', 'vector-effect':'non-scaling-stroke'}); root.appendChild(seg); }
    if(cities.length>1){
      const pts=cities.map(c=>projection([c.lon,c.lat]));
      for(let i=1;i<pts.length;i++){
        const [px,py]=pts[i-1];
        const [x,y]=pts[i];
        const src=cities[i-1];
        const dst=cities[i];
        let cScale=0.15, cSign=1;
        // Existing exceptions
        if(dst.city==='havana'||dst.city==='havana2'){ cScale=0.3; cSign=-1; }
        if(dst.city==='capetown'||dst.city==='varanasi'||dst.city==='darwin'||dst.city==='sydney'){ cScale=Math.max(cScale,0.22);}
        // Curved outward for specific pairs requested
        const pair = src.city+'>'+dst.city;
        const MUST_CURVE = (
          pair==='mendoza>saopaulo' ||
          pair==='natal>rio' ||
          pair==='zanzibar>capetown' ||
          pair==='katmandou>bali' ||
          pair==='bali>hongkong'
        );
        if(MUST_CURVE){
          cScale = Math.max(cScale, 0.28);
          cSign = -1; // curve toward the exterior/opposite side
        }
        drawSegment(px,py,x,y,'#22d3ee', cScale, cSign, MUST_CURVE);
      }
      // Add wrap-around straight link: split the true straight line Havana↔Auckland at the appropriate border (x=0 or x=width)
      function findCity(name){ return cities.find(c=>c.city===name); }
      const H = findCity('havana') || findCity('havana2');
      const A = findCity('auckland');
      if(H || A){
        const hp = H ? projection([H.lon,H.lat]) : null;
        const ap = A ? projection([A.lon,A.lat]) : null;
        if(hp && ap){
          const hx = hp[0], hy = hp[1];
          const ax = ap[0], ay = ap[1];
          // Choose a horizontal shift k∈{-1,0,1} so that ax' = ax + k*width is closest to hx
          function bestShift(ax, hx, W){
            let bestK = 0, bestD = Math.abs((ax) - hx);
            for(const k of [-1,1]){ const d=Math.abs((ax + k*W) - hx); if(d<bestD){ bestD=d; bestK=k; } }
            return bestK;
          }
          const k = bestShift(ax, hx, width);
          if(k === 0){
            // No wrap needed, draw direct straight link
            drawStraight(hx,hy,ax,ay,'#22d3ee');
          } else if(k === -1){
            // Shift Auckland left by width, split at x=0
            const axs = ax - width;
            const denom = (axs - hx);
            if(Math.abs(denom) > 1e-6){
              const t0 = (0 - hx) / denom;
              const y0 = hy + (ay - hy) * t0; // intersection Y at x=0
              // Left piece: Havana → west border
              drawStraight(hx,hy,0,y0,'#22d3ee');
              // Right piece: east border → Auckland
              drawStraight(width,y0,ax,ay,'#22d3ee');
            }
          } else { // k === +1
            // Shift Auckland right by width, split at x=width
            const axs = ax + width;
            const denom = (axs - hx);
            if(Math.abs(denom) > 1e-6){
              const t1 = (width - hx) / denom;
              const y1 = hy + (ay - hy) * t1; // intersection Y at x=width
              // Right piece: Havana → east border
              drawStraight(hx,hy,width,y1,'#22d3ee');
              // Left piece: west border → Auckland
              drawStraight(0,y1,ax,ay,'#22d3ee');
            }
          }
        }
      }
    }
    const paris=[2.3522,48.8566], madrid=[-3.7038,40.4168], capetown=[18.4241,-33.9249]; const [px1,py1]=projection(paris), [mx1,my1]=projection(madrid), [cx1,cy1]=projection(capetown); drawSegment(px1,py1,mx1,my1,'#22d3ee'); drawSegment(cx1,cy1,px1,py1,'#22d3ee');
    window.__markers=[]; const inv0=1/scale; cities.forEach((c,i)=>{ const [x,y]=projection([c.lon,c.lat]); const mg=el('g',{transform:'translate('+x.toFixed(1)+' '+y.toFixed(1)+') scale('+inv0.toFixed(3)+')'}); const circ=el('circle',{cx:0,cy:0,r:4,fill:(i===0?'#22d3ee':'#3b82f6'),stroke:'#0ea5e9','stroke-width':1,'pointer-events':'none'}); const label=el('text',{x:6,y:-6,fill:'#cbd5e1','font-size':'12px','text-anchor':'start','dominant-baseline':'ideographic','pointer-events':'none'}); label.textContent=c.label; mg.appendChild(circ); mg.appendChild(label); const hit=el('circle',{cx:0,cy:0,r:8,fill:'transparent'}); hit.style.cursor='pointer'; hit.addEventListener('click',()=>{ window.location.href=c.url; }); mg.appendChild(hit); root.appendChild(mg); window.__markers.push({el:mg,x:x,y:y}); });
    // Add Paris marker explicitly
    { const p=projection([2.3522,48.8566]); const px=p[0], py=p[1]; const pmg=el('g',{transform:'translate('+px.toFixed(1)+' '+py.toFixed(1)+') scale('+inv0.toFixed(3)+')'}); const pc=el('circle',{cx:0,cy:0,r:4,fill:'#22d3ee',stroke:'#0ea5e9','stroke-width':1,'pointer-events':'none'}); const pl=el('text',{x:6,y:-6,fill:'#cbd5e1','font-size':'12px','text-anchor':'start','dominant-baseline':'ideographic','pointer-events':'none'}); pl.textContent='Paris'; pmg.appendChild(pc); pmg.appendChild(pl); root.appendChild(pmg); if(!window.__markers) window.__markers=[]; window.__markers.push({el:pmg,x:px,y:py}); }
{{ ... }}
    // Ensure initial state of arrowheads matches current scale
    applyTransform();
  } catch(err){ const msg=el('text',{x:20,y:40,fill:'#ef4444'}); msg.textContent='Carte indisponible hors-ligne (assets manquants).'; svg.appendChild(msg); }
})();
"""
    js = js.replace("__CITIES__", cities_json)
    js = js.replace("{{ ... }}", "")
    html.append('<script>')
    html.append(js)
    html.append('</script>')
    return "\n".join(html)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    # Try latin-1 first (original meta), fallback to utf-8
    for enc in ("latin-1", "utf-8"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return path.read_text(errors="ignore")


def extract_menu_links(menu_html: str):
    links = []
    for href, label in MENU_LINK_RE.findall(menu_html):
        href = href.strip()
        # Skip root, bookmarks, and photos dynamic
        if href in ("/", "/~erwanadm"):
            continue
        if "album.php" in href or "myalbums.php" in href:
            continue
        # Expect format like /amsud/lima
        parts = href.strip("/").split("/")
        if len(parts) >= 2:
            region, city = parts[0], "/".join(parts[1:])
            links.append((region, city, label.strip()))
    # De-duplicate while preserving order
    seen = set()
    result = []
    for r, c, l in links:
        key = (r, c)
        if key in seen:
            continue
        seen.add(key)
        result.append((r, c, l))
    return result


def build_sidebar(menu_links, rel_prefix: str, current_rel_url: str | None = None) -> str:
    items = []
    # Group by region, preserving the order of first appearance in menu.html
    groups: dict[str, list[tuple[str, str]]] = {}
    for region, city, label in menu_links:
        if region not in groups:
            groups[region] = []
        groups[region].append((city, label))
    for region, cities in groups.items():  # preserve insertion order
        items.append(f"      <div class=\"section\" style=\"margin:10px 0 6px; color:#9ca3af; font-size:12px; text-transform:uppercase; letter-spacing:.08em;\">{region}</div>")
        for city, label in cities:  # preserve city order as in menu.html
            url_rel = f"{region}/{city}/index.html"
            url = f"{rel_prefix}{url_rel}"
            safe_label = html.escape(normalize_text(label))
            active = " active" if current_rel_url == url_rel else ""
            items.append(f"      <a class=\"link{active}\" href=\"{url}\">{safe_label}</a>")
    return (BASE_SIDEBAR_START.format(rel=rel_prefix) + "\n".join(items) + "\n" + BASE_SIDEBAR_END)


def generate_cities_body(menu_links) -> str:
    # Build a single-column list of all cities in menu order, noting regions when they change, only for existing pages
    parts = []
    parts.append('<div class="header"><div class="h1">Liste des villes</div></div>')
    last_region = None
    for region, city, label in menu_links:
        page_path = OUT / region / city / "index.html"
        if not page_path.exists():
            continue
        if region != last_region:
            parts.append(f'<h2 style="margin-top:18px">{html.escape(region.title())}</h2>')
            last_region = region
        url = f"{region}/{city}/index.html"
        safe_label = html.escape(normalize_text(label))
        parts.append(f'<div style="margin:6px 0"><a href="{url}">{safe_label}</a></div>')
    return "\n".join(parts)


def extract_content(page_html: str) -> dict:
    # Remove PHP tags and requires
    cleaned = PHP_TAG_RE.sub("", page_html)
    cleaned = HEADER_REQ_RE.sub("", cleaned)
    cleaned = FOOTER_REQ_RE.sub("", cleaned)

    # Try to capture from <div class="titre"> onward
    m = TITRE_RE.search(cleaned)
    if m:
        content = cleaned[m.start():]
    else:
        content = cleaned

    # Heuristics: remove trailing closing divs that belong to the old layout
    # Keep up to the last closing of our inner content markers
    # Bound by the last occurrence of </div> followed by optional whitespace and end or php close
    # But safer: stop before any stray </div> after a line containing only </div>
    # We'll just strip trailing </div> lines
    lines = content.splitlines()
    while lines and lines[-1].strip() == "</div>":
        lines.pop()
    content = "\n".join(lines).strip()

    # Remove any stray PHP require statements that may have slipped through
    content = REQ_STMT_RE.sub("", content)
    content = REQ_ANY_RE.sub("", content)

    # Ensure anchors back to top look okay
    content = content.replace("href=\"#top\"", "class=\"backtop\" href=\"#top\"")
    # Normalize body and title
    # First do base HTML-safe normalization, then apply text_correction only to text nodes
    base_body = normalize_html(content)
    norm_body = _transform_text_nodes(base_body, text_correction)
    norm_title = normalize_text(extract_title(content))
    return {"title": norm_title, "body": norm_body}


def is_image_file(name: str) -> bool:
    ext = name.lower().rsplit('.', 1)[-1] if '.' in name else ''
    return ext in {"jpg", "jpeg", "png", "gif"}


def sidecar_caption_for(img_path: Path) -> str:
    base = img_path.stem
    # Try base.txt and base_fr.txt
    for cand in (img_path.with_name(base + ".txt"), img_path.with_name(base + "_fr.txt")):
        if cand.exists():
            try:
                return normalize_text(cand.read_text(encoding="latin-1").splitlines()[0].strip())
            except Exception:
                try:
                    return normalize_text(cand.read_text(encoding="utf-8").splitlines()[0].strip())
                except Exception:
                    return ""
    return ""


def find_city_images(city_dir: Path):
    # Return list of dicts with thumb (Path), full (Path), caption (str)
    images = []
    # Map minis to fulls by removing leading 'mini_'
    for root, _, files in os.walk(city_dir):
        rpath = Path(root)
        thumbs = {}
        fulls = []
        for f in files:
            if not is_image_file(f):
                continue
            if f.lower().startswith("mini_"):
                thumbs[f] = rpath / f
            else:
                fulls.append(rpath / f)
        # Pair minis to corresponding fulls in this folder
        paired = set()
        for full in fulls:
            mini_name = "mini_" + full.name
            thumb = thumbs.get(mini_name)
            caption = sidecar_caption_for(full)
            images.append({
                "full": full,
                "thumb": thumb if thumb else full,
                "caption": caption,
            })
            if thumb:
                paired.add(mini_name)
        # Also include thumbs that have no matching full (rare)
        for name, thumb in thumbs.items():
            if name in paired:
                continue
            images.append({
                "full": thumb,
                "thumb": thumb,
                "caption": sidecar_caption_for(thumb),
            })
    # Stable sort by path
    images.sort(key=lambda x: str(x["full"]).lower())
    return images


def copy_city_media(src_dir: Path, dst_dir: Path):
    for root, _, files in os.walk(src_dir):
        rpath = Path(root)
        rel = rpath.relative_to(src_dir)
        out = dst_dir / rel
        for f in files:
            p = rpath / f
            if is_image_file(f) or f.lower().endswith(".txt"):
                out.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out / f)


def build_gallery_html(images, out_page_dir: Path, src_city_dir: Path) -> str:
    if not images:
        return ""
    # Build relative href/src from out page dir to copied media location
    items = []
    for it in images[:200]:  # cap to keep pages light
        # Resolve output-side paths
        full_rel = os.path.relpath(
            (out_page_dir / os.path.relpath(it["full"], src_city_dir)).resolve(),
            out_page_dir.resolve(),
        ).replace("\\", "/")
        thumb_rel = os.path.relpath(
            (out_page_dir / os.path.relpath(it["thumb"], src_city_dir)).resolve(),
            out_page_dir.resolve(),
        ).replace("\\", "/")
        title = (it.get("caption") or "").replace('"', "&quot;")
        items.append(f'<a href="{full_rel}" target="_blank" title="{title}"><img loading="lazy" src="{thumb_rel}" alt="{title}" /></a>')
    return '<div class="gallery">' + "\n".join(items) + '</div>'


def insert_gallery(body_html: str, gallery_html: str) -> str:
    if not gallery_html:
        return body_html
    # Insert before the main texte block if possible
    anchor_idx = body_html.find('<a id="texte"')
    texte_idx = body_html.find('<div class="texte"')
    insert_at = -1
    if anchor_idx != -1:
        insert_at = anchor_idx
    elif texte_idx != -1:
        insert_at = texte_idx
    if insert_at != -1:
        return body_html[:insert_at] + gallery_html + "\n" + body_html[insert_at:]
    # Else, append after resume if present
    resume_idx = body_html.find('<div class="resume"')
    if resume_idx != -1:
        # find the end of resume div
        end_div = body_html.find('</div>', resume_idx)
        if end_div != -1:
            end_div += len('</div>')
            return body_html[:end_div] + "\n" + gallery_html + body_html[end_div:]
    # Fallback: prepend
    return gallery_html + "\n" + body_html


def list_album_images(album_dir: Path):
    files = []
    if not album_dir.exists():
        return files
    for name in os.listdir(album_dir):
        if not is_image_file(name):
            continue
        # Exclude thumbnails prefixed with mini_
        if name.lower().startswith("mini_"):
            continue
        files.append(name)
    files.sort(key=lambda s: s.lower())
    return files


def rewrite_legacy_picture_links(body_html: str, city_src_dir: Path, city_out_dir: Path) -> str:
    # Find href attributes pointing to picture.php and map to copied media
    def repl(match):
        full = match.group(0)
        url = match.group(1)
        # Allow absolute or relative
        try:
            parsed = urlparse(url)
        except Exception:
            return full
        if not parsed.query:
            return full
        qs = parse_qs(parsed.query)
        album_vals = qs.get('album') or qs.get('Album') or []
        picture_vals = qs.get('picture') or qs.get('Picture') or qs.get('pic') or []
        if not album_vals or not picture_vals:
            return full
        album_rel = album_vals[0].strip('/')
        try:
            idx = int(picture_vals[0])
        except Exception:
            return full
        # Expect the album to be within the current city directory
        candidate = (WEB / album_rel)
        if not str(candidate).startswith(str(city_src_dir)):
            return full
        # Compute path relative to the city src dir
        rel_to_city = candidate.relative_to(city_src_dir)
        album_src = city_src_dir / rel_to_city
        album_out = city_out_dir / rel_to_city
        images = list_album_images(album_src)
        if not images or idx < 0 or idx >= len(images):
            return full
        target = album_out / images[idx]
        try:
            rel_href = os.path.relpath(target.resolve(), city_out_dir.resolve()).replace('\\', '/')
        except Exception:
            return full
        return f'href="{rel_href}"'

    # Regex to catch href="...picture.php?..."
    pattern = re.compile(r'href=\"([^\"]*picture\.php\?[^\"]*)\"', re.IGNORECASE)
    return pattern.sub(repl, body_html)


def extract_title(content: str) -> str:
    m = re.search(r"<div\s+class=\"titre\">(.*?)</div>", content, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    # Fallback
    return "Voyage"


def rel_prefix_for(path_out: Path) -> str:
    # Compute relative path from output file to root of site for linking assets
    depth = len(path_out.relative_to(OUT).parts) - 1  # minus filename
    if depth <= 0:
        return ""
    return "../" * depth


def write_page(path_out: Path, menu_links, content: dict):
    path_out.parent.mkdir(parents=True, exist_ok=True)
    rel = rel_prefix_for(path_out)
    current_rel_url = path_out.relative_to(OUT).as_posix()
    sidebar = build_sidebar(menu_links, rel, current_rel_url)
    # Backlink to the map
    backlink = f'<div class="backlink"><a href="{rel}index.html">← Retour à la carte</a></div>'
    body = ('' if current_rel_url == 'index.html' else backlink) + content["body"]
    html = (
        BASE_HEAD.format(title=content.get("title") or "Voyage", rel=rel)
        + sidebar
        + BASE_CONTENT_START
        + body
        + BASE_CONTENT_END
    )
    path_out.write_text(html, encoding="utf-8")


def copy_assets():
    # Create assets and write CSS
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "styles.css").write_text(CSS, encoding="utf-8")

    # Copy images and other static folders we might reference
    # We'll copy 'distrib' entirely if exists
    for folder in ("distrib",):
        src = WEB / folder
        dst = OUT / folder
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    # Parse menu links
    menu_html = read_text(WEB / "menu.html")
    menu_links = extract_menu_links(menu_html)

    copy_assets()

    # Build city pages
    count = 0
    for region in REGIONS:
        region_dir = WEB / region
        if not region_dir.exists():
            continue
        for root, dirs, files in os.walk(region_dir):
            root_path = Path(root)
            if "inc" in root_path.parts:
                continue
            if "test" in root_path.parts:
                continue
            for fname in files:
                if fname.lower() == "index.php":
                    src = root_path / fname
                    html = read_text(src)
                    content = extract_content(html)
                    rel_sub = root_path.relative_to(WEB)
                    out_dir = OUT / rel_sub
                    out_path = out_dir / "index.html"

                    # Build gallery: find images, copy media, and inject gallery into body
                    images = find_city_images(root_path)
                    if images:
                        copy_city_media(root_path, out_dir)
                        gallery_html = build_gallery_html(images, out_dir, root_path)
                        content["body"] = insert_gallery(content["body"], gallery_html)

                    # Rewrite any legacy picture.php links to local media
                    content["body"] = rewrite_legacy_picture_links(content["body"], root_path, out_dir)

                    write_page(out_path, menu_links, content)
                    count += 1

    # Build home page from web/index.php if present
    index_php = WEB / "index.php"
    # Build index as a zoomable world map
    ensure_map_assets()
    map_body = generate_map_index(menu_links)
    map_content = {"title": "Carte des villes", "body": map_body}
    write_page(OUT / "index.html", menu_links, map_content)

    print(f"Generated {count} city pages + index.html into {OUT}")

if __name__ == "__main__":
    main()
