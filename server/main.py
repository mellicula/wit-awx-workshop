import os
from pathlib import Path
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

app = Flask(__name__)

ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")
TOTAL_BUGS = 4

scores: dict[str, dict] = {}
phase = "workshop"

BROKEN_DIR = Path(__file__).parent.parent / "src_broken"


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/phase")
def get_phase():
    return jsonify({"phase": phase})


@app.post("/score")
def post_score():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "anonymous")
    if username not in scores:
        scores[username] = {"coverage": 0.0, "bugs_caught": None}
    if data.get("coverage") is not None:
        scores[username]["coverage"] = data["coverage"]
    if data.get("bugs_caught") is not None:
        scores[username]["bugs_caught"] = data["bugs_caught"]
    return jsonify({"ok": True})


@app.get("/api/scores")
def get_scores():
    rows = [{"username": u, **d} for u, d in scores.items()]
    if phase == "reveal":
        rows.sort(key=lambda r: (r.get("bugs_caught") or 0, r.get("coverage") or 0), reverse=True)
    else:
        rows.sort(key=lambda r: r.get("coverage") or 0, reverse=True)
    return jsonify({"phase": phase, "total_bugs": TOTAL_BUGS, "scores": rows})


@app.post("/admin/reveal")
def start_reveal():
    global phase
    if (request.get_json(silent=True) or {}).get("key") != ADMIN_KEY:
        return jsonify({"error": "Invalid key"}), 403
    phase = "reveal"
    return jsonify({"ok": True, "phase": phase})


@app.post("/admin/reset")
def reset():
    global phase
    if (request.get_json(silent=True) or {}).get("key") != ADMIN_KEY:
        return jsonify({"error": "Invalid key"}), 403
    scores.clear()
    phase = "workshop"
    return jsonify({"ok": True})


@app.get("/broken/<filename>")
def get_broken_file(filename):
    if phase != "reveal":
        return jsonify({"error": "Not in reveal phase"}), 403
    allowed = {"currency.py", "wallet.py", "expense.py", "budget.py"}
    if filename not in allowed:
        return jsonify({"error": "Not found"}), 404
    path = BROKEN_DIR / filename
    if not path.exists():
        return jsonify({"error": "Not found"}), 404
    return Response(path.read_text(), mimetype="text/plain")


# ── Leaderboard page ──────────────────────────────────────────────────────────

@app.get("/")
def leaderboard():
    html = HTML.replace("__ADMIN_KEY__", ADMIN_KEY)
    return Response(html, mimetype="text/html")


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WIT x Airwallex — Leaderboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #0a0a0a;
      color: #f0f0f0;
      font-family: 'SF Mono', 'Fira Code', monospace;
      min-height: 100vh;
      padding: 40px;
    }

    header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 40px;
    }

    h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }

    #phase-badge {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .badge-workshop { background: #1a3a2a; color: #4ade80; border: 1px solid #4ade80; }
    .badge-reveal   { background: #3a1a1a; color: #f87171; border: 1px solid #f87171; }

    #admin-controls {
      margin-left: auto;
      display: flex;
      gap: 10px;
      align-items: center;
    }

    #status-msg {
      font-size: 0.75rem;
      color: #555;
    }

    button {
      padding: 8px 18px;
      border: none;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s;
    }
    button:hover   { opacity: 0.8; }
    button:disabled { opacity: 0.3; cursor: not-allowed; }

    #btn-reveal { background: #f87171; color: #0a0a0a; }
    #btn-reset  { background: #1f1f1f; color: #888; border: 1px solid #333; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 1.1rem;
    }

    th {
      text-align: left;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: #666;
      padding: 8px 16px;
      border-bottom: 1px solid #222;
    }

    td {
      padding: 14px 16px;
      border-bottom: 1px solid #111;
    }

    tr:hover td { background: #111; }

    .rank { color: #666; font-size: 0.9rem; width: 48px; }
    .rank-1 { color: #fbbf24; font-size: 1.2rem; }
    .rank-2 { color: #94a3b8; }
    .rank-3 { color: #b45309; }

    .username { font-weight: 600; }

    .bar-cell { width: 260px; }
    .bar-wrap { background: #1a1a1a; border-radius: 4px; height: 10px; overflow: hidden; }
    .bar-fill  { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
    .bar-coverage { background: #4ade80; }
    .bar-bugs     { background: #f87171; }

    .num { text-align: right; width: 80px; font-variant-numeric: tabular-nums; }
    .dim { color: #444; }

    #updated {
      margin-top: 24px;
      font-size: 0.7rem;
      color: #333;
      text-align: right;
    }
  </style>
</head>
<body>
  <header>
    <h1>WIT x Airwallex</h1>
    <span id="phase-badge">loading</span>
    <div id="admin-controls">
      <span id="status-msg"></span>
      <button id="btn-reveal">Flip to Reveal</button>
      <button id="btn-reset">Reset</button>
    </div>
  </header>

  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Student</th>
        <th class="bar-cell" id="bar-header">Coverage</th>
        <th class="num" id="num-header">%</th>
        <th class="num" id="bugs-header" style="display:none">Bugs caught</th>
      </tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>

  <div id="updated"></div>

  <script>
    const ADMIN_KEY = "__ADMIN_KEY__";

    async function refresh() {
      const res = await fetch('/api/scores');
      const data = await res.json();

      const badge = document.getElementById('phase-badge');
      badge.textContent = data.phase === 'reveal' ? 'Reveal' : 'Live';
      badge.className = 'badge-' + data.phase;

      document.getElementById('btn-reveal').disabled = data.phase === 'reveal';

      const isReveal = data.phase === 'reveal';
      document.getElementById('bar-header').textContent  = isReveal ? 'Bugs caught' : 'Coverage';
      document.getElementById('num-header').textContent  = isReveal ? '' : '%';
      document.getElementById('bugs-header').style.display = isReveal ? '' : 'none';

      const tbody = document.getElementById('rows');
      tbody.innerHTML = '';

      data.scores.forEach((s, i) => {
        const rank = i + 1;
        const rankClass = rank <= 3 ? 'rank-' + rank : '';
        const pct   = (s.coverage ?? 0).toFixed(1);
        const bugs  = s.bugs_caught ?? null;
        const barPct = isReveal
          ? (bugs !== null ? (bugs / data.total_bugs) * 100 : 0)
          : (s.coverage ?? 0);

        tbody.innerHTML += `
          <tr>
            <td class="rank ${rankClass}">${rank}</td>
            <td class="username">${s.username}</td>
            <td class="bar-cell">
              <div class="bar-wrap">
                <div class="bar-fill ${isReveal ? 'bar-bugs' : 'bar-coverage'}"
                     style="width:${barPct}%"></div>
              </div>
            </td>
            <td class="num">${isReveal ? '' : pct + '%'}</td>
            <td class="num" style="display:${isReveal ? '' : 'none'}">
              ${bugs !== null ? bugs + ' / ' + data.total_bugs : '<span class="dim">—</span>'}
            </td>
          </tr>`;
      });

      document.getElementById('updated').textContent =
        'Updated ' + new Date().toLocaleTimeString();
    }

    async function flipReveal() {
      document.getElementById('btn-reveal').disabled = true;
      setStatus('Switching...');
      const res = await fetch('/admin/reveal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: ADMIN_KEY })
      });
      if (res.ok) {
        setStatus('');
        refresh();
      } else {
        setStatus('Failed.');
        document.getElementById('btn-reveal').disabled = false;
      }
    }

    async function resetWorkshop() {
      if (!confirm('Reset all scores and return to workshop mode?')) return;
      setStatus('Resetting...');
      const res = await fetch('/admin/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: ADMIN_KEY })
      });
      if (res.ok) {
        setStatus('');
        refresh();
      } else {
        setStatus('Failed.');
      }
    }

    function setStatus(msg) {
      document.getElementById('status-msg').textContent = msg;
    }

    document.getElementById('btn-reveal').addEventListener('click', flipReveal);
    document.getElementById('btn-reset').addEventListener('click', resetWorkshop);

    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>"""
