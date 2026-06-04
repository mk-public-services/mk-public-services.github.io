#!/usr/bin/env python3
"""
Report Generator — reads results.json, writes a polished index.html dashboard
with tabs for MK vs NL and a head-to-head scorecard at the top.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_results(path="results.json"):
    with open(path) as f:
        return json.load(f)


# ── Badge helpers ─────────────────────────────────────────────────────────────

def b(text, cls):
    return f'<span class="badge {cls}">{text}</span>'

def uptime_badge(up):
    return b("● UP", "good") if up else b("● DOWN", "bad")

def ssl_badge(ssl):
    if ssl.get("error"):
        return b("⚠ Invalid", "bad")
    days = ssl.get("days_left")
    if days is None:
        return b("Unknown", "neutral")
    if days > 30:
        return b(f"🔒 {days}d", "good")
    if days > 0:
        return b(f"⚠ {days}d", "warn")
    return b("Expired", "bad")

def cms_badge(r):
    cms = r.get("cms")
    if not cms:
        return b("Unknown", "neutral")
    ver = r.get("cms_version")
    outdated = r.get("cms_outdated")
    label = cms + (f" {ver}" if ver else "")
    if outdated is True:
        return b(label + " ↑", "bad")
    if outdated is False:
        return b(label + " ✓", "good")
    return b(label, "neutral")

def bool_badge(val):
    return b("✓ Yes", "good") if val else b("✗ No", "bad")

def load_badge(ms):
    if ms is None:
        return b("n/a", "neutral")
    if ms < 1000:
        return b(f"{ms:.0f} ms", "good")
    if ms < 3000:
        return b(f"{ms/1000:.1f} s", "warn")
    return b(f"{ms/1000:.1f} s", "bad")

def files_badge(r):
    n = sum([bool(r.get("robots_txt")), bool(r.get("sitemap_xml")),
             bool(r.get("llms_txt")),   bool(r.get("rss_feed"))])
    label = f"{n}/4"
    if n == 4:   return b(label, "good")
    if n >= 2:   return b(label, "warn")
    if n == 1:   return b(label, "warn")
    return b(label, "bad")

def score_site(r):
    s = 0
    if r.get("up"):                                        s += 1
    if r.get("ssl", {}).get("valid"):                      s += 1
    if r.get("cms_outdated") == False:                     s += 1
    if r.get("avg_load_ms") and r["avg_load_ms"] < 2000:   s += 1
    s += sum([bool(r.get("robots_txt")), bool(r.get("sitemap_xml")),
              bool(r.get("llms_txt")),   bool(r.get("rss_feed"))])
    return s  # max 8 (4 binary + 4 files)


def country_stats(results):
    n = len(results)
    if n == 0:
        return {}
    up        = sum(1 for r in results if r.get("up"))
    ssl_ok    = sum(1 for r in results if r.get("ssl", {}).get("valid"))
    robots    = sum(1 for r in results if r.get("robots_txt"))
    sitemap   = sum(1 for r in results if r.get("sitemap_xml"))
    llms      = sum(1 for r in results if r.get("llms_txt"))
    cms_cur   = sum(1 for r in results if r.get("cms_outdated") == False)
    loads     = [r["avg_load_ms"] for r in results if r.get("avg_load_ms")]
    avg_load  = round(sum(loads) / len(loads), 1) if loads else None
    avg_score = round(sum(score_site(r) for r in results) / n, 2)
    return dict(n=n, up=up, ssl_ok=ssl_ok, robots=robots, sitemap=sitemap,
                llms=llms, cms_cur=cms_cur, avg_load=ms_str(avg_load),
                avg_score=avg_score)


def ms_str(ms):
    if ms is None: return "—"
    if ms >= 1000: return f"{ms/1000:.1f}s"
    return f"{ms:.0f}ms"


def pct(n, total):
    if not total: return 0
    return round(n / total * 100)


def render_table(results):
    rows = ""
    for r in sorted(results, key=score_site, reverse=True):
        sc  = score_site(r)
        p   = round(sc / 8 * 100)
        bar = "bar-good" if p >= 70 else ("bar-warn" if p >= 40 else "bar-bad")
        ssl = r.get("ssl", {})
        ssl_detail = ""
        if ssl.get("issuer") and ssl.get("valid"):
            ssl_detail = f'<div class="sub">{ssl["issuer"]}</div>'
        elif ssl.get("error"):
            ssl_detail = f'<div class="sub err">{ssl["error"][:55]}</div>'
        cms_note = ""
        if r.get("cms_outdated") is True:
            cms_note = f'<div class="sub warn-text">Latest: {r.get("cms","")} {r.get("cms_latest","")}</div>'

        rows += f"""<tr class="{'row-down' if not r['up'] else ''}">
          <td class="td-name">
            <a href="{r['url']}" target="_blank" rel="noopener" class="site-link">{r['name']}</a>
            <div class="sub">{r['hostname']}</div>
          </td>
          <td>{uptime_badge(r['up'])}</td>
          <td>{ssl_badge(ssl)}{ssl_detail}</td>
          <td>{load_badge(r.get('avg_load_ms'))}</td>
          <td>{cms_badge(r)}{cms_note}</td>
          <td>{files_badge(r)}</td>
          <td class="td-score">
            <span class="score-num">{sc}/8</span>
            <div class="score-bg"><div class="score-bar {bar}" style="width:{p}%"></div></div>
          </td>
        </tr>"""
    return rows


def render(data):
    results   = data["results"]
    generated = data.get("generated_at", "")
    try:
        dt     = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        pretty = dt.strftime("%B %d, %Y · %H:%M UTC")
    except Exception:
        pretty = generated

    mk = [r for r in results if r.get("country") == "MK"]
    nl = [r for r in results if r.get("country") == "NL"]

    smk = country_stats(mk)
    snl = country_stats(nl)

    mk_rows = render_table(mk)
    nl_rows = render_table(nl)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>State Site Evaluation — MK vs NL</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --bg:        #ffffff;
      --surface:   #f8f9fa;
      --border:    #e5e7eb;
      --accent:    #0066cc;
      --good:      #16a34a; --good-bg: #f0fdf4; --good-bd: #bbf7d0;
      --warn:      #b45309; --warn-bg: #fffbeb; --warn-bd: #fde68a;
      --bad:       #dc2626; --bad-bg:  #fef2f2; --bad-bd:  #fecaca;
      --neutral:   #6b7280; --neut-bg: #f3f4f6; --neut-bd: #e5e7eb;
      --text:      #111827;
      --text2:     #374151;
      --sub:       #6b7280;
      --font:      'Ubuntu', sans-serif;
      --mono:      'Ubuntu Mono', monospace;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: var(--font); font-size: 15px; line-height: 1.5; }}

    /* ── Header ── */
    .header {{ background: var(--bg); border-bottom: 1px solid var(--border); padding: 32px 48px 24px; }}
    h1 {{ font-size: 1.6rem; font-weight: 700; letter-spacing: -0.01em; }}
    .run-date {{ font-family: var(--mono); font-size: 0.73rem; color: var(--sub); margin-top: 5px; }}

    /* ── Tabs ── */
    .tabs-wrap {{ padding: 28px 48px 0; }}
    .tab-bar {{ display: flex; gap: 0; border-bottom: 2px solid var(--border); margin-bottom: 0; }}
    .tab-btn {{
      padding: 10px 24px; font-family: var(--font); font-size: 0.9rem; font-weight: 500;
      background: none; border: none; cursor: pointer; color: var(--sub);
      border-bottom: 2px solid transparent; margin-bottom: -2px;
      transition: color 0.15s, border-color 0.15s;
    }}
    .tab-btn:hover {{ color: var(--text); }}
    .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }}
    .tab-content {{ display: none; padding-top: 24px; }}
    .tab-content.active {{ display: block; }}

    /* ── Table ── */
    .wrap {{ padding: 0 48px 80px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
    thead {{ background: var(--surface); }}
    thead th {{
      font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em;
      color: var(--sub); padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap;
    }}
    tbody tr {{ border-bottom: 1px solid var(--border); transition: background 0.1s; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: #f9fafb; }}
    tbody tr.row-down {{ background: #fff8f8; }}
    tbody td {{ padding: 12px 14px; vertical-align: middle; }}
    .td-name {{ min-width: 200px; }}
    .site-link {{ color: var(--text); text-decoration: none; font-weight: 500; }}
    .site-link:hover {{ color: var(--accent); text-decoration: underline; }}
    .sub {{ font-size: 0.7rem; color: var(--sub); margin-top: 2px; font-family: var(--mono); }}
    .err {{ color: var(--bad); }}
    .warn-text {{ color: var(--warn); }}

    /* ── Badges ── */
    .badge {{
      display: inline-block; font-family: var(--mono); font-size: 0.68rem; font-weight: 700;
      padding: 2px 8px; border-radius: 5px; white-space: nowrap;
    }}
    .good    {{ background: var(--good-bg); color: var(--good); border: 1px solid var(--good-bd); }}
    .warn    {{ background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn-bd); }}
    .bad     {{ background: var(--bad-bg);  color: var(--bad);  border: 1px solid var(--bad-bd);  }}
    .neutral {{ background: var(--neut-bg); color: var(--neutral); border: 1px solid var(--neut-bd); }}

    /* ── Score bar ── */
    .td-score {{ min-width: 105px; }}
    .score-num {{ font-family: var(--mono); font-size: 0.7rem; color: var(--sub); display: block; margin-bottom: 4px; }}
    .score-bg {{ height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }}
    .score-bar {{ height: 100%; border-radius: 2px; }}
    .bar-good {{ background: var(--good); }}
    .bar-warn {{ background: var(--warn); }}
    .bar-bad  {{ background: var(--bad);  }}

    /* ── Legend ── */
    .legend {{
      margin: 0 0 16px; padding: 10px 16px; background: var(--surface);
      border: 1px solid var(--border); border-radius: 7px;
      font-size: 0.76rem; color: var(--sub); display: flex; flex-wrap: wrap; gap: 5px 16px;
    }}
    .legend strong {{ color: var(--text2); font-weight: 500; }}

    footer {{ text-align: center; padding: 24px; font-size: 0.76rem; color: var(--sub); border-top: 1px solid var(--border); }}

    @media (max-width: 768px) {{
      .header, .scorecard-wrap, .tabs-wrap, .wrap {{ padding-left: 16px; padding-right: 16px; }}
    }}
  </style>
</head>
<body>

<div class="header">
  <h1>🇲🇰 North Macedonia &nbsp;vs&nbsp; 🇳🇱 Netherlands — State Site Evaluation</h1>
  <div class="run-date">Generated: {pretty}</div>
</div>

<!-- ── Tabs ── -->
<div class="tabs-wrap">
  <div class="tab-bar">
    <button class="tab-btn active" onclick="switchTab('mk', this)">🇲🇰 North Macedonia ({smk['n']} sites)</button>
    <button class="tab-btn"        onclick="switchTab('nl', this)">🇳🇱 Netherlands ({snl['n']} sites)</button>
  </div>
</div>

<!-- MK tab -->
<div id="tab-mk" class="tab-content active">
  <div class="wrap">
    <div class="legend">
      <strong>Score /8:</strong>
      <span>+1 online</span><span>+1 valid SSL</span><span>+1 CMS up-to-date</span><span>+1 load &lt;2s</span>
      <span>+1 each: robots.txt · sitemap.xml · llms.txt · RSS feed</span>
      <strong style="margin-left:8px">CMS ↑</strong><span>= outdated</span>
    </div>
    <table>
      <thead><tr>
        <th>Site</th><th>Status</th><th>SSL Certificate</th><th>Avg Load</th>
        <th>CMS</th><th>Discoverability</th><th>Score</th>
      </tr></thead>
      <tbody>{mk_rows}</tbody>
    </table>
  </div>
</div>

<!-- NL tab -->
<div id="tab-nl" class="tab-content">
  <div class="wrap">
    <div class="legend">
      <strong>Score /8:</strong>
      <span>+1 online</span><span>+1 valid SSL</span><span>+1 CMS up-to-date</span><span>+1 load &lt;2s</span>
      <span>+1 each: robots.txt · sitemap.xml · llms.txt · RSS feed</span>
      <strong style="margin-left:8px">CMS ↑</strong><span>= outdated</span>
    </div>
    <table>
      <thead><tr>
        <th>Site</th><th>Status</th><th>SSL Certificate</th><th>Avg Load</th>
        <th>CMS</th><th>Discoverability</th><th>Score</th>
      </tr></thead>
      <tbody>{nl_rows}</tbody>
    </table>
  </div>
</div>

<footer>
  Automated monthly evaluation &nbsp;·&nbsp; CMS detection via HTTP headers &amp; HTML meta tags &nbsp;·&nbsp; Sorted best → worst
</footer>

<script>
  function switchTab(id, btn) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + id).classList.add('active');
    btn.classList.add('active');
  }}
</script>
</body>
</html>"""


def main():
    src  = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    dest = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    if not Path(src).exists():
        print(f"Error: {src} not found. Run evaluate.py first.")
        sys.exit(1)
    data = load_results(src)
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    html = render(data)
    with open(dest, "w") as f:
        f.write(html)
    print(f"Report → {dest}  ({len(data['results'])} sites)")


if __name__ == "__main__":
    main()
