import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

app = FastAPI()

ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")
TOTAL_BUGS = 4  # number of bugs planted in src_broken/

scores: dict[str, dict] = {}  # {username: {coverage, bugs_caught}}
phase = "workshop"  # "workshop" or "reveal"


# ── Models ────────────────────────────────────────────────────────────────────

class ScorePayload(BaseModel):
    username: str
    coverage: float | None = None
    bugs_caught: int | None = None


class AdminPayload(BaseModel):
    key: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/phase")
def get_phase():
    return {"phase": phase}


@app.post("/score")
def post_score(payload: ScorePayload):
    if payload.username not in scores:
        scores[payload.username] = {"coverage": 0.0, "bugs_caught": None}
    if payload.coverage is not None:
        scores[payload.username]["coverage"] = payload.coverage
    if payload.bugs_caught is not None:
        scores[payload.username]["bugs_caught"] = payload.bugs_caught
    return {"ok": True}


@app.get("/api/scores")
def get_scores():
    rows = []
    for username, data in scores.items():
        rows.append({"username": username, **data})

    if phase == "reveal":
        rows.sort(key=lambda r: (r.get("bugs_caught") or 0, r.get("coverage") or 0), reverse=True)
    else:
        rows.sort(key=lambda r: r.get("coverage") or 0, reverse=True)

    return {"phase": phase, "total_bugs": TOTAL_BUGS, "scores": rows}


@app.post("/admin/reveal")
def start_reveal(payload: AdminPayload):
    global phase
    if payload.key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    phase = "reveal"
    return {"ok": True, "phase": phase}


@app.post("/admin/reset")
def reset(payload: AdminPayload):
    global phase
    if payload.key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    scores.clear()
    phase = "workshop"
    return {"ok": True}


# ── Broken source files (served only during reveal) ──────────────────────────

BROKEN_DIR = Path(__file__).parent.parent / "src_broken"

@app.get("/broken/{filename}", response_class=PlainTextResponse)
def get_broken_file(filename: str):
    if phase != "reveal":
        raise HTTPException(status_code=403, detail="Not in reveal phase")
    allowed = {"currency.py", "wallet.py", "expense.py", "budget.py"}
    if filename not in allowed:
        raise HTTPException(status_code=404)
    path = BROKEN_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404)
    return path.read_text()


# ── Leaderboard page ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def leaderboard():
    return HTML


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
      align-items: baseline;
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
    async function refresh() {
      const res = await fetch('/api/scores');
      const data = await res.json();

      const badge = document.getElementById('phase-badge');
      badge.textContent = data.phase === 'reveal' ? 'Reveal' : 'Live';
      badge.className = 'badge-' + data.phase;

      const isReveal = data.phase === 'reveal';
      document.getElementById('bar-header').textContent  = isReveal ? 'Bugs caught' : 'Coverage';
      document.getElementById('num-header').textContent  = isReveal ? '' : '%';
      document.getElementById('bugs-header').style.display = isReveal ? '' : 'none';

      const tbody = document.getElementById('rows');
      tbody.innerHTML = '';

      data.scores.forEach((s, i) => {
        const rank = i + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : '';
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

    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>"""
