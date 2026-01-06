from __future__ import annotations


def index_html() -> str:
    # Uses system color keywords (Canvas/CanvasText/etc.) to avoid hard-coding a theme.
    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>MoodMusic</title>
  <style>
    :root { color-scheme: light dark; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: Canvas;
      color: CanvasText;
      font: 16px/1.45 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    .card {
      width: min(780px, calc(100vw - 32px));
      border: 1px solid color-mix(in oklab, CanvasText 12%, Canvas 88%);
      border-radius: 16px;
      padding: 20px;
      background: color-mix(in oklab, Canvas 94%, CanvasText 6%);
    }
    h1 {
      margin: 0 0 6px 0;
      font-size: 22px;
      letter-spacing: 0.2px;
    }
    .subtitle {
      margin: 0 0 16px 0;
      opacity: 0.8;
    }
    textarea {
      width: 100%;
      min-height: 120px;
      resize: vertical;
      padding: 12px 12px;
      border-radius: 12px;
      border: 1px solid color-mix(in oklab, CanvasText 16%, Canvas 84%);
      background: Canvas;
      color: CanvasText;
      outline: none;
    }
    textarea:focus {
      border-color: color-mix(in oklab, CanvasText 26%, Canvas 74%);
    }
    .row {
      margin-top: 12px;
      display: flex;
      gap: 10px;
      align-items: center;
    }
    button {
      appearance: none;
      border: 1px solid color-mix(in oklab, CanvasText 20%, Canvas 80%);
      background: ButtonFace;
      color: ButtonText;
      border-radius: 12px;
      padding: 10px 14px;
      font-weight: 600;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .status {
      margin-left: auto;
      font-size: 13px;
      opacity: 0.75;
    }
    .results {
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }
    .result {
      border: 1px solid color-mix(in oklab, CanvasText 12%, Canvas 88%);
      border-radius: 12px;
      padding: 12px;
      background: Canvas;
    }
    .title {
      font-weight: 700;
    }
    .meta {
      margin-top: 2px;
      font-size: 13px;
      opacity: 0.8;
    }
    .error {
      margin-top: 10px;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid color-mix(in oklab, CanvasText 18%, Canvas 82%);
      background: color-mix(in oklab, Canvas 92%, CanvasText 8%);
    }
  </style>
</head>
<body>
  <main class=\"card\">
    <h1>MoodMusic</h1>
    <p class=\"subtitle\">Describe your mood. Get song recommendations.</p>

    <textarea id=\"mood\" placeholder=\"Example: I feel calm, reflective, and a bit nostalgic. I want something mellow.\"></textarea>

    <div class=\"row\">
      <button id=\"go\">Recommend</button>
      <div id=\"status\" class=\"status\"></div>
    </div>

    <div id=\"error\" class=\"error\" style=\"display:none\"></div>
    <section id=\"results\" class=\"results\"></section>
  </main>

  <script>
    const mood = document.getElementById('mood');
    const go = document.getElementById('go');
    const statusEl = document.getElementById('status');
    const resultsEl = document.getElementById('results');
    const errorEl = document.getElementById('error');

    function setStatus(text) { statusEl.textContent = text || ''; }
    function setError(text) {
      if (!text) { errorEl.style.display = 'none'; errorEl.textContent = ''; return; }
      errorEl.style.display = 'block';
      errorEl.textContent = text;
    }

    function clearResults() { resultsEl.innerHTML = ''; }

    function renderResults(payload) {
      clearResults();
      const results = payload?.results || [];
      for (const hit of results) {
        const card = document.createElement('div');
        card.className = 'result';

        const title = document.createElement('div');
        title.className = 'title';
        title.textContent = `${hit.song.title} — ${hit.song.artist}`;

        const meta = document.createElement('div');
        meta.className = 'meta';
        const score = (typeof hit.score === 'number') ? hit.score.toFixed(4) : String(hit.score);
        meta.textContent = `score=${score}`;

        card.appendChild(title);
        card.appendChild(meta);
        resultsEl.appendChild(card);
      }
    }

    async function recommend() {
      setError('');
      clearResults();

      const text = (mood.value || '').trim();
      if (!text) {
        setError('Please enter your mood text.');
        return;
      }

      go.disabled = true;
      setStatus('Thinking…');

      try {
        const res = await fetch('/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mood_text: text, k: 5 })
        });

        if (!res.ok) {
          let msg = `Request failed (${res.status})`;
          try {
            const data = await res.json();
            if (data?.detail?.message) msg = data.detail.message;
          } catch {}
          throw new Error(msg);
        }

        const payload = await res.json();
        renderResults(payload);
      } catch (e) {
        setError(e?.message || String(e));
      } finally {
        go.disabled = false;
        setStatus('');
      }
    }

    go.addEventListener('click', recommend);
    mood.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') recommend();
    });
  </script>
</body>
</html>
"""
