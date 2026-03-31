# ============================================================
# Indexing → TF → IDF → TF-IDF
# Icons: Flowbite SVG (https://flowbite.com/icons/)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import math
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from corpus import DOCUMENTS

# ── Sastrawi ──────────────────────────────────────────────
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    _factory = StemmerFactory()
    _stemmer = _factory.create_stemmer()
    SASTRAWI = True
except Exception:
    SASTRAWI = False

# ── Indonesian Stopwords ────────────────────────────────────
STOPWORDS = set([
    "yang","dan","di","ke","dari","pada","adalah","ini","itu","atau","juga",
    "dengan","untuk","dalam","tidak","ada","oleh","mereka","kita","kami","saya",
    "anda","dia","ia","akan","sudah","telah","bisa","dapat","harus","perlu",
    "lebih","paling","sangat","jika","maka","namun","tetapi","tapi","sehingga",
    "karena","saat","ketika","setelah","sebelum","antara","seperti","secara",
    "menjadi","sebagai","salah","banyak","setiap","para","beberapa","berbagai",
    "suatu","satu","dua","tiga","empat","lima","tersebut","hal","maupun",
    "selain","melalui","hingga","kepada","terhadap","baik","bagi","pun","lagi",
    "kembali","masih","belum","pernah","selalu","semua","tiap","apakah",
    "bagaimana","dimana","mengapa","siapa","kapan","berapa","agar","supaya",
    "walaupun","meskipun","serta","sedangkan","lain","juga","pula","lalu",
    "kemudian","sekarang","nanti","tadi","terkait","mampu","mulai","telah",
    "sangat","cukup","belum","sudah","namun","tetap","hanya","bahwa","kini",
    "oleh","atas","bawah","luar","dalam","antara","antar","tanpa","sejak",
    "sampai","hingga","selama","ketika","sebelum","sesudah","bila","kalau",
])

# ── Flowbite SVG Icons ─────────────────────────────────────
ICONS = {
    "database": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6c0 1.657 3.582 3 8 3s8-1.343 8-3M4 6c0-1.657 3.582-3 8-3s8 1.343 8 3M4 6v6m0 0v6m0-6c0 1.657 3.582 3 8 3s8-1.343 8-3m0 0v6m0-6V6m0 12c0 1.657-3.582 3-8 3s-8-1.343-8-3"/></svg>',
    "text":     '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 3v4a1 1 0 0 1-1 1H5m8-2h3m-3 3h3m-4 3h4m-4 3h4M8 21H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7.5L19 7.5V20a1 1 0 0 1-1 1H8Z"/></svg>',
    "scissors": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m7 7 10 10M7 7a3 3 0 1 0-4.243 4.243A3 3 0 0 0 7 7Zm10 10a3 3 0 1 0 4.242 4.243A3 3 0 0 0 17 17ZM15 5l-2.5 2.5M9 11l-4 8m12-8 2 4M7.5 13.5 5 17"/></svg>',
    "filter":   '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v2.172a2 2 0 0 1-.586 1.414l-4.828 4.828A2 2 0 0 0 14 13.828V18l-4 2v-6.172a2 2 0 0 0-.586-1.414L4.586 7.586A2 2 0 0 1 4 6.172V4Z"/></svg>',
    "tree":     '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18Zm0 0v-8m0-5 3 3m-3-3-3 3"/></svg>',
    "chart_bar":'<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v15a1 1 0 0 0 1 1h15M8 16l4-6 3 4 3-6"/></svg>',
    "table":    '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 6h18M3 14h18M3 18h18M9 6v12M15 6v12M3 6a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6Z"/></svg>',
    "sigma":    '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 6h11M8 18h11M5 6l6 6-6 6"/></svg>',
    "matrix":   '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/><rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/></svg>',
    "book":     '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.03v13m0-13c-2.819-.831-4.715-1.076-8.029-1.023A.99.99 0 0 0 3 6v11c0 .563.466 1.014 1.03 1.007 3.122-.043 5.018.212 7.97 1.023m0-13c2.819-.831 4.715-1.076 8.029-1.023A.99.99 0 0 1 21 6v11c0 .563-.466 1.014-1.03 1.007-3.122-.043-5.018.212-7.97 1.023"/></svg>',
    "search":   '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="m21 21-3.5-3.5M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0Z"/></svg>',
    "trophy":   '<svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v5m0 0H8m4 0h4M3 7H1l1 7h1M21 7h2l-1 7h-1M7 14h10M7 7l1 7m0 0h8l1-7M7 7H5M17 7h2M9 7V4h6v3"/></svg>',
    "link":     '<svg class="icon-sm" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.213 9.787a3.391 3.391 0 0 0-4.795 0l-3.425 3.426a3.39 3.39 0 0 0 4.795 4.794l.321-.304m-.321-4.49a3.39 3.39 0 0 0 4.795 0l3.424-3.426a3.39 3.39 0 0 0-4.794-4.795l-1.028.961"/></svg>',
    "check":    '<svg class="icon-sm" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 11.917 9.724 16.5 19 7.5"/></svg>',
    "info":     '<svg class="icon-sm" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 11h2v5m-2 0h4m-2.592-8.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>',
    "formula":  '<svg class="icon-sm" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>',
    "sastrawi": '<svg class="icon-sm" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
}

def icon(name):
    return ICONS.get(name, "")

# ╔══════════════════════════════════════════════════════════╗
#  PAGE CONFIG & CSS
# ╚══════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title=" TF-IDF",
    layout="wide",
)

st.markdown("""
<style>
/* ── IR_ENGINE.PRO Light Theme ──────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root {
    --paper:   #FFFFFF;
    --sidebar: #F9FAFB;
    --ink:     #0F172A;
    --border:  #E2E8F0;
    --accent:  #2563EB;
    --muted:   #64748B;
    --faint:   #F8FAFC;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
    letter-spacing: -0.01em;
}
.stApp { background: var(--paper) !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Icons ───────────────────────────────────────────────── */
.icon    { width:18px; height:18px; display:inline-block; vertical-align:middle; color: var(--accent); }
.icon-sm { width:14px; height:14px; display:inline-block; vertical-align:middle; color: var(--accent); }

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--muted) !important; }
[data-testid="stSidebar"] strong { color: var(--ink) !important; }

.sidebar-brand {
    font-family: 'Inter', sans-serif;
    font-size: 1.15rem;
    font-weight: 900;
    font-style: italic;
    color: var(--ink) !important;
    letter-spacing: -0.03em;
    margin-bottom: 2px;
}
.sidebar-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #94A3B8 !important;
    opacity: 0.7;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 16px 0;
}
.sidebar-section-label {
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent) !important;
    margin-bottom: 10px;
    display: block;
}

/* Stat rows di sidebar */
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    margin-bottom: 6px;
}
.stat-label { font-size: 11px; font-weight: 500; color: var(--muted) !important; }
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px; font-weight: 700;
    color: var(--accent) !important;
}

/* Nav links seperti HTML referensi */
.nav-link-item {
    display: block;
    padding: 9px 12px;
    font-size: 13px;
    font-weight: 600;
    color: var(--muted) !important;
    border-radius: 4px;
    margin-bottom: 3px;
    transition: all 0.15s;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.01em;
}
.nav-link-item:hover {
    background: white;
    color: var(--ink) !important;
}
.nav-link-item.active {
    background: white;
    color: var(--accent) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    border: 1px solid var(--border);
}

/* Tabel referensi slide 3 di sidebar */
.ref-table {
    width: 100%;
    border: 1px solid var(--border);
    font-size: 11px;
    background: white;
    border-collapse: collapse;
}
.ref-table th, .ref-table td {
    border: 1px solid var(--border);
    padding: 7px 10px;
    text-align: left;
    color: var(--ink) !important;
}
.ref-table th {
    background: #F1F5F9;
    font-weight: 800;
    color: #475569 !important;
}
.ref-table td.highlight {
    background: #EFF6FF;
    font-weight: 700;
    color: var(--accent) !important;
    text-decoration: underline;
}

/* ── Main content area ───────────────────────────────────── */
.main-header {
    margin-bottom: 4rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}
.main-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem; display: block;
}
.main-title {
    font-size: 3rem; font-weight: 900;
    color: var(--ink); line-height: 1.1;
    letter-spacing: -0.035em;
    margin: 0 0 1rem 0;
}
.main-desc {
    font-size: 1.05rem; font-weight: 300;
    color: var(--muted); line-height: 1.7;
    max-width: 620px;
}
.main-desc strong { font-weight: 600; color: var(--ink); }

/* ── Section tag (sesuai HTML referensi) ─────────────────── */
.section-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 800;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem; display: block;
}

/* ── Step header ─────────────────────────────────────────── */
.step-hdr {
    margin-bottom: 1.5rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
}
.step-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 800;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--accent);
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 6px;
}
.step-title {
    font-size: 1.75rem; font-weight: 800;
    color: var(--ink); letter-spacing: -0.025em;
}

/* ── Edu info box ────────────────────────────────────────── */
.edu-box {
    background: #EFF6FF;
    border-left: 4px solid var(--accent);
    padding: 1rem 1.3rem;
    margin-bottom: 1.5rem;
    font-size: 0.88rem;
    color: #1E40AF;
    line-height: 1.65;
    display: flex; gap: 10px; align-items: flex-start;
}
.edu-box svg { flex-shrink:0; margin-top:2px; color: var(--accent); }
.edu-box strong { color: #1D4ED8; font-weight: 700; }

/* Formula box - light style sesuai referensi */
.formula-box {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.9rem 1.3rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--ink);
    margin: 1rem 0;
    display: flex; gap: 10px; align-items: flex-start;
}
.formula-box svg { color: var(--accent); flex-shrink:0; margin-top:2px; }

/* ── Document cards ──────────────────────────────────────── */
.doc-card {
    border: 1px solid var(--border);
    padding: 2rem 2.2rem;
    background: #FCFDFF;
    margin-bottom: 1.5rem;
    border-radius: 4px;
}
.doc-card-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem;
    margin-bottom: 1.2rem;
}
.doc-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--accent);
}
.doc-judul {
    font-size: 1rem; font-weight: 700;
    font-style: italic;
    color: var(--ink);
}
.doc-meta  { font-size: 11px; color: #94A3B8; margin-bottom: 10px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
.doc-sumber {
    font-size: 11px; color: var(--accent);
    text-decoration: none;
    display: inline-flex; align-items: center; gap: 4px;
}
.doc-sumber:hover { text-decoration: underline; }
.doc-tema {
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    background: #F1F5F9; color: #475569;
    border-radius: 3px; padding: 2px 7px;
    border: 1px solid var(--border);
}
.doc-teks { font-size: 0.9rem; line-height: 1.75; color: var(--muted); text-align: justify; }

/* ── Token pills ─────────────────────────────────────────── */
.pill-wrap { display:flex; flex-wrap:wrap; gap:5px; margin-top:8px; }
.pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    background: #EFF6FF; color: #1D4ED8;
    border: 1px solid #BFDBFE;
    border-radius: 3px; padding: 3px 8px;
}
.pill.removed { background:#FEF2F2; color:#B91C1C; border-color:#FCA5A5; text-decoration:line-through; }
.pill.kept    { background:#F0FDF4; color:#15803D; border-color:#86EFAC; }
.pill.stemmed { background:#F5F3FF; color:#6D28D9; border-color:#C4B5FD; }

/* ── Similarity result cards ─────────────────────────────── */
.result-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
}
.result-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.result-rank   {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem; font-weight: 700;
    color: #E2E8F0;
}
.result-score  {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 700;
    color: var(--accent);
}
.result-title  { font-size: 1rem; font-weight: 700; color: var(--ink); margin: 4px 0; }
.sim-track { background:#F1F5F9; border-radius:2px; height:4px; margin:8px 0 12px; }
.sim-fill  { background: var(--accent); height:4px; border-radius:2px; }
.result-text { font-size: 0.88rem; line-height:1.75; color:var(--muted); }
mark.qhl { background:#FEF08A; color:#713F12; padding:0 3px; border-radius:2px; font-weight:700; }

/* ── Tables ──────────────────────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] > div { border-radius:4px !important; overflow:hidden; }

/* ── Tabs - sesuai desain referensi ─────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--faint);
    border-radius: 4px;
    border: 1px solid var(--border);
    padding: 4px;
    gap: 2px;
    flex-wrap: wrap;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif;
    font-size: 12px; font-weight: 600;
    border-radius: 3px !important;
    padding: 7px 13px !important;
    color: var(--muted) !important;
    letter-spacing: -0.01em;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: white !important;
    color: var(--accent) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    border: 1px solid var(--border) !important;
}

/* ── Streamlit input overrides ───────────────────────────── */
div[data-testid="stTextInput"] > div > div > input {
    background: white !important;
    color: var(--ink) !important;
    border: 2px solid var(--border) !important;
    border-radius: 4px !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] label {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"] > button {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    padding: 12px 28px !important;
    width: 100% !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
#  PREPROCESSING FUNCTIONS (sesuai PDF)
# ╚══════════════════════════════════════════════════════════╝

def case_folding(text: str) -> str:
    """Step: ubah semua huruf menjadi huruf kecil (lowercase)."""
    return text.lower()

def tokenize(text: str) -> list:
    """Step: pisahkan teks menjadi token kata, hapus tanda baca & angka."""
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [t for t in text.split() if len(t) > 1]

def remove_stopwords(tokens: list) -> list:
    """Step: hapus stopwords bahasa Indonesia."""
    return [t for t in tokens if t not in STOPWORDS]

def stem_tokens(tokens: list) -> list:
    """Step: stemming menggunakan Sastrawi (Nazief-Adriani) atau fallback."""
    if SASTRAWI:
        return [_stemmer.stem(t) for t in tokens]
    # Fallback sederhana jika Sastrawi tidak tersedia
    prefixes = ('me', 'di', 'ke', 'se', 'pe', 'ber', 'ter', 'per', 'men', 'mem', 'meng', 'pem', 'peng')
    suffixes = ('kan', 'an', 'nya', 'i')
    result = []
    for t in tokens:
        w = t
        for p in prefixes:
            if w.startswith(p) and len(w) > len(p) + 3:
                w = w[len(p):]; break
        for s in suffixes:
            if w.endswith(s) and len(w) > len(s) + 3:
                w = w[:-len(s)]; break
        result.append(w)
    return result

def preprocess(text: str) -> list:
    """Pipeline preprocessing lengkap."""
    return stem_tokens(remove_stopwords(tokenize(case_folding(text))))


# ╔══════════════════════════════════════════════════════════╗
#  TF-IDF COMPUTATION (sesuai rumus PDF dosen)
# ╚══════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def build_pipeline(docs):
    """Bangun seluruh pipeline TF-IDF dari corpus dokumen."""
    N = len(docs)
    results = []
    for doc in docs:
        raw         = doc["teks"]
        folded      = case_folding(raw)
        tok_raw     = tokenize(folded)
        tok_sw      = remove_stopwords(tok_raw)
        tok_stem    = stem_tokens(tok_sw)
        results.append({**doc,
            "folded": folded, "tok_raw": tok_raw,
            "tok_sw": tok_sw, "tok_stem": tok_stem,
        })

    # Vocabulary: semua term unik setelah preprocessing
    vocab = sorted(set(t for r in results for t in r["tok_stem"]))

    # TF: jumlah kemunculan term t / total kata dalam dokumen d
    # Rumus: TF(t,d) = freq(t,d) / |d|
    tf_matrix = {}
    for r in results:
        c = Counter(r["tok_stem"])
        total = len(r["tok_stem"]) or 1
        tf_matrix[r["id"]] = {t: round(c.get(t, 0) / total, 4) for t in vocab}

    # DF: jumlah dokumen yang mengandung term t
    df = {t: sum(1 for r in results if t in r["tok_stem"]) for t in vocab}

    # IDF: log10(N / DF(t))
    # Rumus sesuai slide 28 PDF: IDF(t) = log(N/DF(t))
    idf = {}
    for t in vocab:
        idf[t] = round(math.log10(N / df[t]), 4) if df[t] > 0 else 0

    # TF-IDF: TF(t,d) × IDF(t)
    # Rumus sesuai slide 30 PDF: TF-IDF(t,d) = TF(t,d) × IDF(t)
    tfidf_matrix = {}
    for r in results:
        tfidf_matrix[r["id"]] = {t: round(tf_matrix[r["id"]][t] * idf[t], 4) for t in vocab}

    global_freq = Counter(t for r in results for t in r["tok_stem"])

    return {
        "docs": results, "vocab": vocab,
        "tf_matrix": tf_matrix, "df": df, "idf": idf,
        "tfidf_matrix": tfidf_matrix, "global_freq": global_freq, "N": N,
    }


def process_query(query_text, idf, tfidf_matrix, vocab):
    """Proses query dan hitung cosine similarity (sesuai pipeline preprocessing dokumen)."""
    q_fold  = case_folding(query_text)
    q_tok   = tokenize(q_fold)
    q_sw    = remove_stopwords(q_tok)
    q_stem  = stem_tokens(q_sw)

    q_count = Counter(q_stem)
    q_total = len(q_stem) or 1
    q_vec   = {t: round((q_count.get(t, 0) / q_total) * idf.get(t, 0), 4) for t in vocab}

    def cosine(va, vb):
        dot   = sum(va[t] * vb[t] for t in vocab)
        mag_a = math.sqrt(sum(va[t]**2 for t in vocab))
        mag_b = math.sqrt(sum(vb[t]**2 for t in vocab))
        return round(dot / (mag_a * mag_b), 4) if mag_a and mag_b else 0.0

    sims   = {doc_id: cosine(q_vec, tfidf_matrix[doc_id]) for doc_id in tfidf_matrix}
    ranked = sorted(sims.items(), key=lambda x: x[1], reverse=True)
    return {"q_fold": q_fold, "q_tok": q_tok, "q_sw": q_sw, "q_stem": q_stem,
            "q_vec": q_vec, "sims": sims, "ranked": ranked}


def highlight_query(text, stems):
    for w in stems:
        text = re.sub(re.escape(w), lambda m: f'<mark class="qhl">{m.group()}</mark>', text, flags=re.IGNORECASE)
    return text


# ╔══════════════════════════════════════════════════════════╗
#  CHART HELPERS
# ╚══════════════════════════════════════════════════════════╝
C_BG  = "#FFFFFF"; C_PANEL = "#F8FAFC"; C_ACC = "#2563EB"; C_ACC2 = "#60A5FA"; C_TXT = "#475569"

def _style(fig, ax):
    fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_PANEL)
    ax.tick_params(colors=C_TXT, labelsize=8.5)
    for sp in ax.spines.values(): sp.set_edgecolor("#E2E8F0")
    ax.title.set_color("#0F172A"); ax.xaxis.label.set_color(C_TXT); ax.yaxis.label.set_color(C_TXT)
    ax.grid(axis='x', color='#E2E8F0', linewidth=0.6, linestyle='--')
    return fig, ax

def chart_top_terms(freq, top_n=15):
    top = freq.most_common(top_n); terms, counts = zip(*top)
    fig, ax = plt.subplots(figsize=(10, 4.5)); _style(fig, ax)
    colors = [C_ACC if i%2==0 else C_ACC2 for i in range(len(terms))]
    ax.barh(list(reversed(terms)), list(reversed(counts)), color=list(reversed(colors)), height=0.6, edgecolor='none')
    for i, (t, c) in enumerate(zip(reversed(terms), reversed(counts))):
        ax.text(c + 0.3, i, str(c), va='center', fontsize=8.5, color=C_TXT, fontweight='bold')
    ax.set_title(f"Top {top_n} Term Paling Sering (Global Corpus)", pad=12, fontsize=10.5, fontweight='bold')
    ax.set_xlabel("Frekuensi Term"); plt.tight_layout(); return fig

def chart_top_tfidf(tfidf, top_n=15):
    sc = [(f"{t} ({d})", v) for d, vec in tfidf.items() for t, v in vec.items() if v > 0]
    sc.sort(key=lambda x: x[1], reverse=True); sc = sc[:top_n]
    labels, vals = zip(*sc)
    fig, ax = plt.subplots(figsize=(10, 4.5)); _style(fig, ax)
    ax.barh(list(reversed(labels)), list(reversed(vals)), color=C_ACC, height=0.6, edgecolor='none')
    for i, v in enumerate(reversed(vals)):
        ax.text(v + 0.0005, i, f"{v:.4f}", va='center', fontsize=8, color=C_TXT, fontweight='bold')
    ax.set_title(f"Top {top_n} Nilai TF-IDF Tertinggi", pad=12, fontsize=10.5, fontweight='bold')
    ax.set_xlabel("TF-IDF Score"); plt.tight_layout(); return fig



def get_doc_by_id(doc_id, docs_list):
    """Safely get document by ID."""
    for r in docs_list:
        if r["id"] == doc_id:
            return r
    return docs_list[0] if docs_list else None


# ╔══════════════════════════════════════════════════════════╗
#  BUILD PIPELINE
# ╚══════════════════════════════════════════════════════════╝
pipeline = build_pipeline(DOCUMENTS)
docs     = pipeline["docs"]
vocab    = pipeline["vocab"]
tf_mat   = pipeline["tf_matrix"]
df_data  = pipeline["df"]
idf_dat  = pipeline["idf"]
tfidf    = pipeline["tfidf_matrix"]
gfreq    = pipeline["global_freq"]
N        = pipeline["N"]
doc_map  = {r["id"]: r["judul"] for r in docs}
doc_ids  = [r["id"] for r in docs]  # Stable list for selectboxes



# ╔══════════════════════════════════════════════════════════╗
#  HERO
# ╚══════════════════════════════════════════════════════════╝
st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">Langkah-langkah TF-IDF</h1>
    
</div>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
#  TABS
# ╚══════════════════════════════════════════════════════════╝
tabs = st.tabs([
    "Indexing",
    "Struktur Dokumen",
    "Dataset",
    "Case Folding",
    "Tokenizing",
    "Stopword",
    "Stemming",
    "TF",
    "DF",
    "IDF",
    "TF-IDF Matrix",
    "Vocabulary",
    "Query Engine",
])


# ─── TAB 0: INDEXING ─────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">Overview / INDEXING</span>
        <h3 class="step-title">Indexing - Manual vs Automatic</h3>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Indexing?</strong> Proses mengubah dokumen
        menjadi bentuk terstruktur yang mudah dicari. Ada dua jenis indexing.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Indexing Secara Manual (oleh manusia)")
    st.markdown("""
    - **Menentukan kata kunci** dari suatu dokumen berdasarkan perbendaharaan kata yang ada (controlled vocabulary)
    - **Oleh ahli di bidangnya** - memerlukan expertise mendalam
    - **Lama dan mahal** - sangat time-consuming dan expensive
    
    **Contoh:** Librarian menentukan keywords: "AI", "Pendidikan", "Digital Learning"
    """)

    st.markdown("### Indexing Secara Otomatis (oleh komputer)")
    st.markdown("""
    - **Program komputer** untuk menentukan kata atau frase tertentu dari teks pada dokumen
    - **Prosesnya cepat** dan scalable
    - Inilah yang kami implementasikan di aplikasi ini!
    
    **Proses Otomatis (6 tahapen):**
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        1. **Struktur Dokumen** - Parsing elemen dokumen
        2. **Tokenisasi** - Pisahkan teks menjadi token kata
        3. **Buang Stopwords** - Hapus kata umum (dan, atau, yang)
        """)
    with col2:
        st.markdown("""
        4. **Stemming** - Bentuk kata dasar (menjalankan -> jalankan)
        5. **Pembobotan** - Hitung TF-IDF scoring setiap term
        6. **Pembuatan Indeks** - Build vocabulary & search index
        """)

    st.markdown("---")

    st.markdown("### Tabel Perbandingan")
    comparison_data = {
        "Jenis": ["Manual", "Automatic"],
        "Controlled Vocabulary": ["Catalogization", "Categorization"],
        "Free Text": ["Indexing", "Search Engine"],
    }
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)


# ─── TAB 1: STRUKTUR DOKUMEN ──────────────────────────────────────────────────
with tabs[1]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">Step 00 / Struktur Dokumen</span>
        <h3 class="step-title">Struktur Dokumen - Format & Parsing</h3>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Struktur Dokumen?</strong> Tergantung jenis dokumen.
        Format umum menggunakan SGML (Standard Generalized Markup Language).
        Parsing memisahkan elemen dokumen: ID, judul, teks, metadata.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Pertanyaan dalam Parsing Dokumen")
    st.markdown("""
    1. **Tergantung jenis dokumen** - Struktur berbeda untuk artikel, email, PDF, web page
    2. **Format umum: SGML** - Standard Generalized Markup Language untuk markup dokumen
    3. **Perlu pemisahan antar elemen?** - Pisahkan metadata dari content
    4. **Bagian mana saja dari dokumen yang akan diindeks?** - Title, content, tags, atau semua?
    """)

    st.markdown("---")
    st.markdown("### Struktur Dokumen dalam Aplikasi Ini")
    
    example_doc = docs[0]  # D1
    st.markdown("""
    Setiap dokumen di corpus memiliki struktur JSON:
    """)
    
    doc_structure = {
        "id": "D1",
        "judul": "Contoh Judul Artikel",
        "tema": "TEKNOLOGI",
        "penulis": "nama_penulis",
        "tahun": 2024,
        "sumber": "https://example.com",
        "teks": "Isi dokumen lengkap dalam bentuk paragraph...",
    }
    st.json(doc_structure)

    st.markdown("#### Field-field yang Diindeks:")
    st.markdown("""
    | Field | Dindeks? | Keterangan |
    |-------|----------|------------|
    | `id` | Tidak | Identifier unik dokumen |
    | `judul` | Ya | Title field - penting untuk konteks |
    | `tema` | Tidak | Kategori dokumen |
    | `teks` | Ya | **Main content - target indexing utama** |
    | `penulis` | Tidak | Metadata |
    | `tahun` | Tidak | Metadata |
    | `sumber` | Tidak | Reference URL |
    """)

    st.markdown("---")
    st.markdown(f"### Corpus Kita: {N} Dokumen")
    
    corpus_summary = pd.DataFrame([{
        "Doc ID": r["id"],
        "Judul": r["judul"][:50],
        "Tema": r["tema"],
        "Token (Raw)": len(r["tok_raw"]),
        "Token (Setelah Prep)": len(r["tok_stem"]),
        "Reduksi (%)": f"{(1 - len(r['tok_stem'])/max(len(r['tok_raw']), 1))*100:.0f}",
    } for r in docs])
    
    st.dataframe(corpus_summary, use_container_width=True, hide_index=True)


# ─── TAB 2: DATASET ──────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">Step 01 / Corpus Detail</span>
        <h3 class="step-title">Struktur Dokumen (Dataset Artikel)</h3>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Corpus?</strong> Kumpulan dokumen yang diindeks.
        setiap dokumen memiliki ID, judul, dan isi teks. Pada praktikum ini menggunakan
        <strong>{N} artikel nyata</strong> dari sumber internet berbahasa Indonesia.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Dokumen", N)
    c2.metric("Rata-rata Token", int(np.mean([len(r["tok_raw"]) for r in docs])))
    c3.metric("Total Token Corpus", f"{sum(len(r['tok_raw']) for r in docs):,}")
    st.markdown("---")

    for doc in docs:
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-card-header">
                <span class="doc-id">Doc_ID: {doc['id']}</span>
                <span class="doc-judul">{doc['judul']}</span>
            </div>
            <div class="doc-meta">
                <span class="doc-tema">{doc['tema']}</span>
                <span>{doc['penulis']} · {doc['tahun']}</span>
                <a class="doc-sumber" href="{doc['sumber']}" target="_blank">
                    {icon('link')} {doc['sumber'][:60]}
                </a>
            </div>
            <div class="doc-teks">{doc['teks']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Distribusi Token per Dokumen")
    wc = {r["id"]: len(r["tok_raw"]) for r in docs}
    fig, ax = plt.subplots(figsize=(11, 3.5)); _style(fig, ax)
    ax.bar(wc.keys(), wc.values(),
           color=[C_ACC if i%2==0 else C_ACC2 for i in range(N)], width=0.6, edgecolor='none')
    ax.set_title("Jumlah Token per Dokumen (Sebelum Preprocessing)", pad=12, fontsize=10.5, fontweight='bold')
    ax.set_ylabel("Jumlah Token"); plt.tight_layout(); st.pyplot(fig); plt.close()


# ─── TAB 3: CASE FOLDING ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('text')} Step 02 / Case Folding</span>
        <h3 class="step-title">Case Folding - Normalisasi Huruf</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Case Folding?</strong> Proses mengubah semua karakter huruf menjadi huruf kecil.
        Memastikan "Teknologi" dan "teknologi" diperlakukan sebagai term yang sama.</div>
    </div>
    <div class="formula-box">{icon('formula')} text.lower() - semua huruf dikonversi menjadi lowercase</div>
    """, unsafe_allow_html=True)

    sel = st.selectbox("Pilih dokumen:", doc_ids, key="cf_sel")
    dr  = get_doc_by_id(sel, docs)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Sebelum Case Folding:**")
        st.text_area("", dr["teks"], height=500, disabled=True, key=f"cf_b_{sel}")
    with c2:
        st.markdown("**Sesudah Case Folding:**")
        st.text_area("", dr["folded"], height=500, disabled=True, key=f"cf_a_{sel}")

    st.markdown("#### Ringkasan Semua Dokumen")
    st.dataframe(pd.DataFrame([{
        "ID": r["id"], "Judul": r["judul"][:50],
        "Huruf Kapital (diubah)": sum(1 for c in r["teks"] if c.isupper()),
        "Status": "Selesai",
    } for r in docs]), use_container_width=True, hide_index=True)


# ─── TAB 4: TOKENIZING ───────────────────────────────────────────────────────
with tabs[4]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('scissors')} Step 03 / Tokenizing</span>
        <h3 class="step-title">Tokenizing - Pemecahan Teks</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Tokenizing?</strong> Proses memisahkan teks menjadi unit-unit kata individual (token).
        Tanda baca, angka, dan karakter non-alfabet dihapus.</div>
    </div>
    <div class="formula-box">{icon('formula')} re.sub(r'[^a-z\\s]', ' ', text).split() - hapus non-alfabet, pisah per spasi</div>
    """, unsafe_allow_html=True)

    sel2 = st.selectbox("Pilih dokumen:", doc_ids, key="tok_sel")
    dt   = get_doc_by_id(sel2, docs)
    st.markdown(f"**Jumlah token: `{len(dt['tok_raw'])}`**")
    pills = '<div class="pill-wrap">' + "".join(f'<span class="pill">{t}</span>' for t in dt["tok_raw"]) + "</div>"
    st.markdown(pills, unsafe_allow_html=True)

    st.markdown("#### Statistik Tokenisasi Semua Dokumen")
    st.dataframe(pd.DataFrame([{
        "ID": r["id"], "Judul": r["judul"][:45],
        "Jumlah Token": len(r["tok_raw"]),
        "Kata Unik": len(set(r["tok_raw"])),
    } for r in docs]), use_container_width=True, hide_index=True)

    st.markdown("#### Top 15 Kata Sebelum Stopword Removal")
    fig = chart_top_terms(Counter(t for r in docs for t in r["tok_raw"]))
    st.pyplot(fig); plt.close()


# ─── TAB 5: STOPWORD REMOVAL ─────────────────────────────────────────────────
with tabs[5]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('filter')} Step 04 / Stopword</span>
        <h3 class="step-title">Stopword Removal - Buang Kata Tidak Bermakna</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Stopword?</strong> Kata buangan yang
        mempunyai fungsi gramatikal namun tidak memiliki makna substantif - contoh: <em>dan, atau, yang, di, ke</em>.
        Dibuang untuk meningkatkan efisiensi dan akurasi sistem information retrieval.</div>
    </div>
    """, unsafe_allow_html=True)

    sel3  = st.selectbox("Pilih dokumen:", doc_ids, key="sw_sel")
    dsw   = get_doc_by_id(sel3, docs)
    removed = [t for t in dsw["tok_raw"] if t in STOPWORDS]

    c1, c2, c3 = st.columns(3)
    c1.metric("Token Sebelum", len(dsw["tok_raw"]))
    c2.metric("Stopword Dihapus", len(removed))
    c3.metric("Token Setelah",    len(dsw["tok_sw"]))

    st.markdown("**Visualisasi token (merah = stopword dihapus, hijau = dipertahankan):**")
    sw_html = '<div class="pill-wrap">'
    for t in dsw["tok_raw"][:120]:
        cls = "removed" if t in STOPWORDS else "kept"
        sw_html += f'<span class="pill {cls}">{t}</span>'
    sw_html += "</div>"
    st.markdown(sw_html, unsafe_allow_html=True)

    st.markdown("#### Ringkasan Stopword Removal Semua Dokumen")
    st.dataframe(pd.DataFrame([{
        "ID": r["id"], "Sebelum": len(r["tok_raw"]),
        "Dihapus": len(r["tok_raw"]) - len(r["tok_sw"]),
        "Setelah": len(r["tok_sw"]),
        "Reduksi": f"{(len(r['tok_raw'])-len(r['tok_sw']))/max(len(r['tok_raw']),1)*100:.1f}%",
    } for r in docs]), use_container_width=True, hide_index=True)


# ─── TAB 6: STEMMING ─────────────────────────────────────────────────────────
with tabs[6]:
    algo = "Sastrawi (Nazief-Adriani)" if SASTRAWI else "Fallback Sederhana"
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('tree')} Step 05 / Stemming</span>
        <h3 class="step-title">Stemming - Bentuk Kata Dasar</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Stemming?</strong> Proses pembuangan
        prefiks dan sufiks dari kata berimbuhan menjadi kata dasar.
        Contoh: <code>menganalisis → analisis</code>.
        Algoritma yang digunakan: <strong>{algo}</strong>.</div>
    </div>
    """, unsafe_allow_html=True)

    sel4 = st.selectbox("Pilih dokumen:", doc_ids, key="stem_sel")
    dst  = get_doc_by_id(sel4, docs)
    pairs_changed = [(b, s) for b, s in zip(dst["tok_sw"], dst["tok_stem"]) if b != s]

    if pairs_changed:
        st.markdown("**Contoh perubahan stemming:**")
        st.dataframe(pd.DataFrame(pairs_changed[:40], columns=["Sebelum Stemming", "Sesudah Stemming"]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada perubahan stemming pada dokumen ini.")

    st.markdown("**Token hasil akhir setelah stemming:**")
    stem_html = '<div class="pill-wrap">' + "".join(f'<span class="pill stemmed">{t}</span>' for t in dst["tok_stem"]) + "</div>"
    st.markdown(stem_html, unsafe_allow_html=True)

    st.markdown("#### Statistik Stemming Semua Dokumen")
    st.dataframe(pd.DataFrame([{
        "ID": r["id"], "Sebelum Stem": len(r["tok_sw"]),
        "Sesudah Stem": len(r["tok_stem"]),
        "Term Unik": len(set(r["tok_stem"])),
    } for r in docs]), use_container_width=True, hide_index=True)


# ─── TAB 7: TF TABLE ─────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('chart_bar')} Step 06 / TF Calculation</span>
        <h3 class="step-title">Term Frequency (TF)</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu TF?</strong>
        TF mengukur frekuensi kemunculan suatu term t pada dokumen d.
        Semakin sering muncul, semakin penting term tersebut untuk dokumen itu.</div>
    </div>
    <div class="formula-box">{icon('formula')} TF(t, d) = jumlah kemunculan term t dalam dokumen d / total kata dalam dokumen d</div>
    """, unsafe_allow_html=True)

    # Tabel TF - hanya term dengan nilai > 0
    tf_rows = []
    for t in vocab:
        row = {"Term": t}
        any_nonzero = False
        for r in docs:
            v = tf_mat[r["id"]][t]
            row[r["id"]] = round(v, 4) if v > 0 else 0
            if v > 0: any_nonzero = True
        if any_nonzero: tf_rows.append(row)
    df_tf = pd.DataFrame(tf_rows)
    st.markdown(f"**{len(df_tf)} term dengan TF > 0**")
    st.dataframe(df_tf, use_container_width=True, hide_index=True, height=420)

    st.markdown("#### Contoh Perhitungan Manual (sesuai slide PDF)")
    c1, c2 = st.columns(2)
    with c1:
        eg_term = st.selectbox("Pilih term:", vocab[:25], key="tf_eg_t")
    with c2:
        eg_doc  = st.selectbox("Pilih dokumen:", doc_ids, key="tf_eg_d")
    er = get_doc_by_id(eg_doc, docs)
    ct = er["tok_stem"].count(eg_term)
    tt = len(er["tok_stem"])
    rt = ct / tt if tt else 0
    st.markdown(f"""
    <div class="formula-box">{icon('formula')}
    TF('{eg_term}', {eg_doc}) = {ct} / {tt} = <strong style='color:#A78BFA;'>{rt:.4f}</strong>
    </div>
    """, unsafe_allow_html=True)


# ─── TAB 8: DF TABLE ─────────────────────────────────────────────────────────
with tabs[8]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('table')} Step 07 / DF</span>
        <h3 class="step-title">Document Frequency (DF)</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu DF?</strong>
        DF(t) adalah jumlah dokumen yang mengandung term t.
        Term yang muncul di banyak dokumen cenderung kurang informatif (terlalu umum).</div>
    </div>
    <div class="formula-box">{icon('formula')} DF(t) = jumlah dokumen yang mengandung term t dari total N = {N} dokumen</div>
    """, unsafe_allow_html=True)

    df_rows = [{
        "Term": t,
        "DF (Jumlah Dok.)": df_data[t],
        "Dokumen yang Mengandung": ", ".join(r["id"] for r in docs if t in r["tok_stem"]),
        "% Corpus": f"{df_data[t]/N*100:.0f}%",
    } for t in vocab if df_data[t] > 0]
    df_df = pd.DataFrame(df_rows).sort_values("DF (Jumlah Dok.)", ascending=False).reset_index(drop=True)
    st.dataframe(df_df, use_container_width=True, hide_index=True, height=400)

    st.markdown("#### Distribusi Nilai DF")
    df_dist = Counter(df_data[t] for t in vocab)
    fig, ax = plt.subplots(figsize=(8, 3.5)); _style(fig, ax)
    ks = sorted(df_dist.keys())
    ax.bar([f"DF={k}" for k in ks], [df_dist[k] for k in ks], color=C_ACC, width=0.45, edgecolor='none')
    ax.set_title("Distribusi DF - Jumlah Term per Nilai DF", pad=12, fontsize=10.5, fontweight='bold')
    ax.set_xlabel("Nilai DF"); ax.set_ylabel("Jumlah Term")
    plt.tight_layout(); st.pyplot(fig); plt.close()


# ─── TAB 9: IDF TABLE ────────────────────────────────────────────────────────
with tabs[9]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('sigma')} Step 08 / IDF Weighting</span>
        <h3 class="step-title">Inverse Document Frequency (IDF)</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu IDF?</strong>
        IDF memberikan bobot lebih tinggi pada kata yang jarang muncul lintas dokumen.
        Semakin kecil DF → semakin besar IDF → semakin informatif term tersebut.</div>
    </div>
    <div class="formula-box">{icon('formula')} IDF(t) = log10( N / DF(t) ) &nbsp;- dimana N = {N} (total dokumen)</div>
    """, unsafe_allow_html=True)

    idf_rows = [{
        "Term": t,
        "DF": df_data[t],
        f"IDF = log₁₀({N}/DF)": idf_dat[t],
    } for t in vocab if df_data[t] > 0]
    df_idf = pd.DataFrame(idf_rows).sort_values(f"IDF = log₁₀({N}/DF)", ascending=False).reset_index(drop=True)
    st.dataframe(df_idf, use_container_width=True, hide_index=True, height=400)

    st.markdown("#### Contoh Perhitungan Manual IDF (sesuai slide PDF)")
    eg_idf = st.selectbox("Pilih term:", vocab[:30], key="idf_eg")
    dft    = df_data[eg_idf]; idft = idf_dat[eg_idf]
    st.markdown(f"""
    <div class="formula-box">{icon('formula')}
    IDF('{eg_idf}') = log₁₀({N}/{dft}) = log₁₀({N/dft:.4f}) = <strong style='color:#A78BFA;'>{idft:.4f}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Top 20 Term IDF Tertinggi")
    top20 = df_idf.head(20)
    fig, ax = plt.subplots(figsize=(10, 4.5)); _style(fig, ax)
    ax.barh(top20["Term"][::-1], top20[f"IDF = log₁₀({N}/DF)"][::-1], color=C_ACC2, height=0.6, edgecolor='none')
    ax.set_title("Top 20 Term dengan IDF Tertinggi", pad=12, fontsize=10.5, fontweight='bold')
    ax.set_xlabel("IDF Score"); plt.tight_layout(); st.pyplot(fig); plt.close()


# ─── TAB 10: TF-IDF MATRIX ────────────────────────────────────────────────────
with tabs[10]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('matrix')} Step 09 / Final Weighting</span>
        <h3 class="step-title">Final TF-IDF Matrix</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu TF-IDF?</strong>
        TF-IDF = TF × IDF. Kata yang sering muncul di satu dokumen namun jarang di dokumen lain
        mendapat skor tertinggi - kata paling "khas" untuk dokumen tersebut.</div>
    </div>
    <div class="formula-box">{icon('formula')}
    TF-IDF(t, d) = TF(t, d) × IDF(t) = TF(t, d) × log₁₀(N / DF(t))
    <br>Contoh: TF-IDF('kucing', D1) = 0.33 × 0.18 = 0.059 &nbsp;[sesuai slide PDF]
    </div>
    """, unsafe_allow_html=True)

    tfidf_rows = []
    for t in vocab:
        row = {"Term": t}
        nz = False
        for r in docs:
            v = tfidf[r["id"]][t]
            row[r["id"]] = v if v > 0 else 0
            if v > 0: nz = True
        if nz: tfidf_rows.append(row)
    df_tfidf = pd.DataFrame(tfidf_rows)
    st.markdown(f"**Matriks TF-IDF: {len(df_tfidf)} term × {N} dokumen**")
    st.dataframe(df_tfidf, use_container_width=True, hide_index=True, height=420)

    st.markdown("#### Top 15 Nilai TF-IDF Tertinggi")
    fig = chart_top_tfidf(tfidf); st.pyplot(fig); plt.close()

    st.markdown("#### Top 15 Term Paling Sering (Global)")
    fig2 = chart_top_terms(gfreq); st.pyplot(fig2); plt.close()


# ─── TAB 11: VOCABULARY ──────────────────────────────────────────────────────
with tabs[11]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">{icon('book')} Step 10 / Vocabulary Index</span>
        <h3 class="step-title">Vocabulary Index</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Apa itu Vocabulary?</strong>
        Kumpulan semua term unik setelah preprocessing lengkap. Vocabulary membentuk
        dimensi ruang vektor dalam model TF-IDF untuk komputasi similarity.</div>
    </div>
    """, unsafe_allow_html=True)

    st.metric("Total Vocabulary Unik", len(vocab))
    voc_html = '<div class="pill-wrap">' + "".join(f'<span class="pill stemmed">{t}</span>' for t in sorted(vocab)) + "</div>"
    st.markdown(voc_html, unsafe_allow_html=True)

    st.markdown("#### Detail Vocabulary")
    st.dataframe(pd.DataFrame({
        "No": range(1, len(vocab)+1), "Term": vocab,
        "DF": [df_data[t] for t in vocab],
        "IDF": [idf_dat[t] for t in vocab],
        "Frekuensi Global": [gfreq.get(t, 0) for t in vocab],
    }).sort_values("Frekuensi Global", ascending=False).reset_index(drop=True),
    use_container_width=True, hide_index=True, height=420)


# ─── TAB 12: QUERY ENGINE ────────────────────────────────────────────────────
with tabs[12]:
    st.markdown(f"""
    <div class="step-hdr">
        <span class="step-badge">Step 11 / Query Engine</span>
        <h3 class="step-title">Query Engine - Pemrosesan Pencarian</span>
    </div>
    <div class="edu-box">
        {icon('info')}
        <div><strong>Bagaimana Query Diproses?</strong> Ketik kata kunci di kolom pencarian di bawah,
        lalu klik <strong>Cari Dokumen</strong>. Query akan melewati pipeline preprocessing
        yang identik dengan dokumen: case fold → tokenize → stopword → stemming,
        kemudian dicocokkan menggunakan <strong>TF-IDF scoring dan ranking</strong>.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Search bar yang jelas terlihat ──────────────────────────────────────
    st.markdown("""
    <style>
    /* Override Streamlit input agar search bar terlihat jelas */
    div[data-testid="stTextInput"] > div > div > input {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #6B8EFF !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        padding: 14px 18px !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #3B5BDB !important;
        box-shadow: 0 0 0 3px rgba(107,142,255,0.2) !important;
    }
    div[data-testid="stTextInput"] label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        letter-spacing: 0.01em !important;
    }
    /* Tombol Cari */
    div[data-testid="stButton"] > button {
        background: #0F1117 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 13px 32px !important;
        width: 100% !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
        transition: background 0.2s !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #3B5BDB !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Contoh query chips yang bisa diklik
    st.markdown(f"""
    <p style="font-size:12px;font-weight:600;color:#64748B;margin-bottom:8px;letter-spacing:0.04em;text-transform:uppercase;">
        Contoh Query:
    </p>
    """, unsafe_allow_html=True)

    contoh_queries = [
        "kecerdasan buatan pendidikan digital",
        "keamanan siber serangan data",
        "startup fintech investasi Indonesia",
        "cloud computing infrastruktur data",
        "energi terbarukan teknologi hijau",
        "big data machine learning kesehatan",
    ]
    chips_html = '<div class="pill-wrap" style="margin-bottom:18px;">'
    for q in contoh_queries:
        chips_html += f'<span class="pill" style="cursor:pointer;font-size:12px;padding:5px 10px;">{q}</span>'
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)

    # Input dan tombol
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        query_input = st.text_input(
            "Ketik kata kunci pencarian:",
            value=st.session_state.get("query_val", ""),
            placeholder="Contoh: transformasi digital keamanan data cloud ...",
            key="query_field",
        )
    with col_btn:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        cari_btn = st.button("Cari Dokumen", use_container_width=True)

    # Simpan nilai query ke session state
    if query_input:
        st.session_state["query_val"] = query_input

    # Proses query ketika tombol diklik ATAU ada teks
    run_query = cari_btn or bool(query_input.strip())

    if run_query and query_input.strip():
        qr = process_query(query_input, idf_dat, tfidf, vocab)
        st.session_state["last_qr"]   = qr
        st.session_state["last_qtxt"] = query_input

        st.markdown("---")
        st.markdown("#### Proses Preprocessing Query (Step-by-Step)")

        # Step cards
        steps_data = [
            ("01 - Input Asli",          query_input,         "pill"),
            ("02 - Case Folding",         qr["q_fold"],        "pill"),
            ("03 - Tokenizing",           qr["q_tok"],         "pill"),
            ("04 - Stopword Removal",     qr["q_sw"],          "kept"),
            ("05 - Stemming (Final Terms)",qr["q_stem"],       "stemmed"),
        ]

        for step_label, step_data, pill_cls in steps_data:
            if isinstance(step_data, list):
                if not step_data:
                    content_html = '<span style="color:#94A3B8;font-size:12px;font-style:italic;">- tidak ada term tersisa -</span>'
                else:
                    content_html = '<div class="pill-wrap">' + "".join(f'<span class="pill {pill_cls}">{t}</span>' for t in step_data) + "</div>"
            else:
                content_html = f'<code style="font-family:Fira Code,monospace;font-size:13px;color:#6B8EFF;background:#EDF2FF;padding:6px 12px;border-radius:5px;border:1px solid #C7D7FF;">{step_data}</code>'

            st.markdown(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:8px;padding:14px 18px;margin-bottom:10px;">
                <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
                            color:#6B8EFF;margin-bottom:8px;">{step_label}</div>
                {content_html}
            </div>
            """, unsafe_allow_html=True)

        # Query vector TF-IDF
        nz_vec = {t: v for t, v in qr["q_vec"].items() if v > 0}
        if nz_vec:
            st.markdown("#### Vektor TF-IDF Query")
            st.dataframe(
                pd.DataFrame([{"Term": t, "TF-IDF Query": v}
                               for t, v in sorted(nz_vec.items(), key=lambda x: -x[1])]),
                use_container_width=True, hide_index=True
            )
            st.success(f"Query diproses - ditemukan **{len(nz_vec)}** term yang cocok dengan vocabulary.")
        else:
            st.warning("Tidak ada term query yang cocok dengan vocabulary. Coba gunakan kata kunci yang lebih umum.")

    elif not query_input.strip():
        st.markdown("""
        <div style="background:#F8FAFC;border:2px dashed #CBD5E1;border-radius:10px;
                    padding:3rem 2rem;text-align:center;margin-top:1rem;">
            <div style="font-size:2rem;margin-bottom:0.75rem;opacity:0.3;"></div>
            <p style="font-size:1rem;font-weight:600;color:#64748B;margin:0 0 6px;">
                Masukkan query di kolom pencarian di atas
            </p>
            <p style="font-size:0.85rem;color:#94A3B8;margin:0;">
                Masukkan query dengan kata kunci yang relevan
            </p>
        </div>
        """, unsafe_allow_html=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<hr style='margin-top:3.5rem;border-color:#E2E8F0;'>
<div style='text-align:center;padding:1.5rem 0;font-size:11px;color:#94A3B8;'>
        <strong style='color:#0F172A;'>TF-IDF Pipeline</strong> &nbsp;·&nbsp;
</div>
""", unsafe_allow_html=True)
