import time
import redis
from flask import Flask, render_template_string

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Docker Compose App</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0a0a0f;
      --surface: #12121a;
      --border: #1e1e2e;
      --accent: #00e5ff;
      --accent2: #7c3aed;
      --text: #e2e8f0;
      --muted: #64748b;
      --glow: rgba(0, 229, 255, 0.15);
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Space Mono', monospace;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      position: relative;
    }

    /* Animated grid background */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      animation: gridMove 20s linear infinite;
      pointer-events: none;
    }

    @keyframes gridMove {
      0% { background-position: 0 0; }
      100% { background-position: 40px 40px; }
    }

    /* Glowing orbs */
    body::after {
      content: '';
      position: fixed;
      width: 600px; height: 600px;
      background: radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%);
      top: -100px; right: -100px;
      border-radius: 50%;
      pointer-events: none;
      animation: pulse 8s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 0.8; }
      50% { transform: scale(1.1); opacity: 1; }
    }

    .container {
      position: relative;
      z-index: 1;
      text-align: center;
      padding: 2rem;
      animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(30px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.7rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      border: 1px solid rgba(0,229,255,0.3);
      padding: 0.4rem 1rem;
      border-radius: 999px;
      margin-bottom: 2rem;
      background: rgba(0,229,255,0.05);
      animation: fadeUp 0.8s 0.1s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .badge::before {
      content: '';
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--accent);
      animation: blink 1.5s ease-in-out infinite;
    }

    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.2; }
    }

    h1 {
      font-family: 'Syne', sans-serif;
      font-size: clamp(2.5rem, 6vw, 5rem);
      font-weight: 800;
      line-height: 1;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #ffffff 0%, var(--accent) 50%, var(--accent2) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: fadeUp 0.8s 0.2s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .subtitle {
      font-size: 0.85rem;
      color: var(--muted);
      letter-spacing: 0.05em;
      margin-bottom: 3rem;
      animation: fadeUp 0.8s 0.3s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 2.5rem 3rem;
      max-width: 480px;
      margin: 0 auto;
      position: relative;
      overflow: hidden;
      animation: fadeUp 0.8s 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
      box-shadow:
        0 0 0 1px rgba(0,229,255,0.05),
        0 20px 60px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.05);
    }

    .card::before {
      content: '';
      position: absolute;
      top: -1px; left: 20%; right: 20%;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--accent), transparent);
    }

    .counter-label {
      font-size: 0.7rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 1rem;
    }

    .counter {
      font-family: 'Syne', sans-serif;
      font-size: clamp(4rem, 12vw, 7rem);
      font-weight: 800;
      color: var(--accent);
      line-height: 1;
      text-shadow: 0 0 40px rgba(0,229,255,0.4);
      margin-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }

    .counter-desc {
      font-size: 0.8rem;
      color: var(--muted);
    }

    .divider {
      width: 40px;
      height: 1px;
      background: var(--border);
      margin: 1.5rem auto;
    }

    .stack-info {
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      font-size: 0.7rem;
      color: var(--muted);
      letter-spacing: 0.05em;
    }

    .stack-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .stack-item span {
      width: 6px; height: 6px;
      border-radius: 50%;
      display: inline-block;
    }

    .dot-flask { background: #3b82f6; }
    .dot-redis { background: #ef4444; }
    .dot-docker { background: var(--accent); }

    .footer {
      margin-top: 2.5rem;
      font-size: 0.65rem;
      color: #334155;
      letter-spacing: 0.1em;
      animation: fadeUp 0.8s 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    /* Hover refresh effect */
    .card {
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      cursor: pointer;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow:
        0 0 0 1px rgba(0,229,255,0.15),
        0 30px 80px rgba(0,0,0,0.5),
        0 0 40px rgba(0,229,255,0.05),
        inset 0 1px 0 rgba(255,255,255,0.08);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">Docker Compose &mdash; Get Started</div>

    <h1>Hello, Naina!</h1>
    <p class="subtitle">Flask + Redis · Running in containers</p>

    <div class="card" onclick="location.reload()">
      <p class="counter-label">Total Page Visits</p>
      <div class="counter">{{ count }}</div>
      <p class="counter-desc">{{ "time" if count == 1 else "times" }} this page has been requested</p>

      <div class="divider"></div>

      <div class="stack-info">
        <div class="stack-item">
          <span class="dot-flask"></span> Flask
        </div>
        <div class="stack-item">
          <span class="dot-redis"></span> Redis
        </div>
        <div class="stack-item">
          <span class="dot-docker"></span> Docker
        </div>
      </div>
    </div>

    <p class="footer">CLICK THE CARD TO REFRESH &nbsp;·&nbsp; NIM: {{ nim }}</p>
  </div>
</body>
</html>
"""

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template_string(HTML_TEMPLATE, count=count, nim="123103131")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)