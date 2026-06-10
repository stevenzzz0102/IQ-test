import html
from http.server import BaseHTTPRequestHandler, HTTPServer

HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Ten Sum Grid</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #08111f;
      --panel: #111c30;
      --panel-2: #18283d;
      --accent: #6ee7f9;
      --good: #4ade80;
      --bad: #fb7185;
      --text: #eff6ff;
      --muted: #bfdbfe;
      --cell: #17324f;
      --cell-hover: #22456c;
      --cell-selected: #1d4ed8;
    }

    * { box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top, rgba(110, 231, 249, 0.12), transparent 20%),
        linear-gradient(135deg, var(--bg), #020617 65%);
      color: var(--text);
      display: grid;
      place-items: center;
      padding: 18px;
    }

    .app {
      width: min(980px, 100%);
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 16px;
      align-items: stretch;
    }

    .panel {
      background: rgba(17, 28, 48, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 24px;
      padding: 16px;
      box-shadow: 0 18px 40px rgba(15, 23, 42, 0.35);
      backdrop-filter: blur(12px);
    }

    h1 { margin: 0 0 6px; font-size: 1.9rem; }
    p { color: var(--muted); line-height: 1.4; }

    .stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 16px;
    }

    .stat-card {
      background: linear-gradient(180deg, rgba(24, 40, 61, 0.98), rgba(15, 23, 42, 0.98));
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 18px;
      padding: 12px;
    }
    .stat-label { color: var(--muted); font-size: 0.92rem; }
    .stat-value { font-size: 1.7rem; font-weight: 700; margin-top: 4px; }

    .tip-box {
      margin-top: 16px;
      padding: 12px;
      border-radius: 16px;
      background: rgba(30, 41, 59, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.14);
      color: var(--text);
      font-size: 0.95rem;
    }

    .board-wrap {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .board-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(30, 41, 59, 0.95);
      border: 1px solid rgba(148, 163, 184, 0.14);
      color: var(--muted);
      font-size: 0.95rem;
    }

    .pill strong { color: var(--text); }

    #message {
      padding: 10px 14px;
      border-radius: 14px;
      background: rgba(30, 41, 59, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.14);
      color: var(--muted);
      min-height: 48px;
    }
    #message.good { color: #bbf7d0; border-color: rgba(74, 222, 128, 0.35); }
    #message.bad { color: #fecdd3; border-color: rgba(251, 113, 133, 0.35); }

    .board {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 4px;
      user-select: none;
      touch-action: none;
      background: rgba(8, 17, 31, 0.92);
      border-radius: 24px;
      padding: 6px;
      border: 1px solid rgba(148, 163, 184, 0.16);
      width: min(100%, 430px);
      max-height: 62vh;
    }

    .cell {
      aspect-ratio: 1 / 1;
      border: 1px solid rgba(148, 163, 184, 0.14);
      border-radius: 12px;
      background: linear-gradient(180deg, var(--cell), #10253c);
      color: var(--text);
      font-size: 0.86rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.08s ease, background 0.12s ease, opacity 0.12s ease;
    }
    .cell:hover { background: linear-gradient(180deg, var(--cell-hover), #17304a); transform: translateY(-1px); }
    .cell.selected { background: linear-gradient(180deg, #1e40af, #2563eb); border-color: rgba(191, 219, 254, 0.4); }
    .cell.removed { opacity: 0; pointer-events: none; transform: scale(0.92); }

    @media (max-width: 1080px) {
      .app { grid-template-columns: 1fr; }
      .panel { order: 2; }
    }
  </style>
</head>
<body>
  <main class=\"app\">
    <section class=\"panel\">
      <h1>Ten Sum Grid</h1>
      <p>Drag a rectangle over the board. If the sum of every number inside it equals 10, the tiles vanish and your score goes up.</p>
      <div class=\"stats\">
        <article class=\"stat-card\"><div class=\"stat-label\">Score</div><div id=\"score\" class=\"stat-value\">0</div></article>
        <article class=\"stat-card\"><div class=\"stat-label\">Time left</div><div id=\"timer\" class=\"stat-value\">02:00</div></article>
      </div>
      <div class="tip-box">Tip: the rectangle can be 1×2, 2×2, 3×4, or any other rectangular size — as long as the total inside is exactly 10.</div>
      <button id="restartBtn" type="button" style="margin-top:14px; width:100%; padding:10px 12px; border-radius:12px; border:1px solid rgba(148,163,184,0.18); background:linear-gradient(180deg,#1d4ed8,#2563eb); color:#eff6ff; font-weight:700; cursor:pointer;">Restart Game</button>
      <div class="tip-box">How to play: click and drag from one tile to another to create the rectangle, then release. Invalid selections are rejected.</div>
    </section>

    <section class=\"panel board-wrap\">
      <div class=\"board-header\">
        <div class="pill">Grid: <strong>8 × 6</strong></div>
        <div class=\"pill\">Numbers: <strong>1–9</strong></div>
      </div>
      <div id=\"message\">Select a rectangle to begin.</div>
      <div id=\"board\" class=\"board\" aria-label=\"Game board\"></div>
    </section>
  </main>

  <script>
    const rows = 8;
    const cols = 6;
    const totalTime = 120;

    const board = document.getElementById('board');
    const scoreEl = document.getElementById('score');
    const timerEl = document.getElementById('timer');
    const messageEl = document.getElementById('message');
    const restartBtn = document.getElementById('restartBtn');

    let grid = [];
    let score = 0;
    let timeLeft = totalTime;
    let timerId = null;
    let dragActive = false;
    let startCell = null;
    let hoverCell = null;
    let isGameOver = false;

    function randomNumber() {
      return Math.floor(Math.random() * 9) + 1;
    }

    function createGrid() {
      grid = Array.from({ length: rows }, () => Array.from({ length: cols }, () => randomNumber()));
      renderGrid();
      setMessage('Drag a rectangle and release to remove its tiles if the sum is 10.', '');
    }

    function restartGame() {
      if (timerId) clearInterval(timerId);
      score = 0;
      timeLeft = totalTime;
      isGameOver = false;
      scoreEl.textContent = '0';
      updateTimerDisplay();
      board.style.opacity = '1';
      createGrid();
      startTimer();
      setMessage('New game started! Drag a rectangle and try to remove tiles that sum to 10.', 'good');
    }

    function renderGrid() {
      board.innerHTML = '';
      for (let r = 0; r < rows; r += 1) {
        for (let c = 0; c < cols; c += 1) {
          const cell = document.createElement('button');
          cell.type = 'button';
          cell.className = 'cell';
          cell.textContent = grid[r][c] || '';
          cell.dataset.row = String(r);
          cell.dataset.col = String(c);
          cell.addEventListener('pointerdown', onPointerDown);
          cell.addEventListener('pointerenter', onPointerEnter);
          board.appendChild(cell);
        }
      }
    }

    function setMessage(text, tone = '') {
      messageEl.textContent = text;
      messageEl.className = tone ? tone : '';
    }

    function formatTime(seconds) {
      const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
      const secs = String(seconds % 60).padStart(2, '0');
      return `${mins}:${secs}`;
    }

    function updateTimerDisplay() {
      timerEl.textContent = formatTime(timeLeft);
    }

    function startTimer() {
      if (timerId) clearInterval(timerId);
      timerId = setInterval(() => {
        timeLeft -= 1;
        updateTimerDisplay();
        if (timeLeft <= 0) {
          timeLeft = 0;
          updateTimerDisplay();
          clearInterval(timerId);
          isGameOver = true;
          setMessage(`Time is up! Final score: ${score}. Refresh to play again.`, 'bad');
          board.style.opacity = '0.75';
        }
      }, 1000);
    }

    function getSelectionRectangle(start, end) {
      const r1 = Math.min(start.row, end.row);
      const r2 = Math.max(start.row, end.row);
      const c1 = Math.min(start.col, end.col);
      const c2 = Math.max(start.col, end.col);
      return { r1, r2, c1, c2 };
    }

    function sumRect(rect) {
      let total = 0;
      for (let r = rect.r1; r <= rect.r2; r += 1) {
        for (let c = rect.c1; c <= rect.c2; c += 1) {
          total += grid[r]?.[c] || 0;
        }
      }
      return total;
    }

    function area(rect) {
      return (rect.r2 - rect.r1 + 1) * (rect.c2 - rect.c1 + 1);
    }

    function clearSelection() {
      document.querySelectorAll('.cell.selected').forEach((node) => node.classList.remove('selected'));
    }

    function highlightSelection(start, end) {
      clearSelection();
      const rect = getSelectionRectangle(start, end);
      for (let r = rect.r1; r <= rect.r2; r += 1) {
        for (let c = rect.c1; c <= rect.c2; c += 1) {
          const cell = board.querySelector(`[data-row=\"${r}\"][data-col=\"${c}\"]`);
          if (cell) cell.classList.add('selected');
        }
      }
    }

    function removeSelection(rect) {
      let removedCount = 0;
      for (let r = rect.r1; r <= rect.r2; r += 1) {
        for (let c = rect.c1; c <= rect.c2; c += 1) {
          if (grid[r]?.[c]) {
            grid[r][c] = 0;
            removedCount += 1;
            const cell = board.querySelector(`[data-row=\"${r}\"][data-col=\"${c}\"]`);
            if (cell) {
              cell.classList.add('removed');
              cell.textContent = '';
            }
          }
        }
      }
      score += removedCount;
      scoreEl.textContent = String(score);
      setMessage(`Removed ${removedCount} tile(s) for a score boost of ${removedCount}.`, 'good');
    }

    function trySelection(start, end) {
      if (isGameOver) return;
      const rect = getSelectionRectangle(start, end);
      const total = sumRect(rect);
      const count = area(rect);
      if (total === 10 && count > 0) {
        removeSelection(rect);
        if (!grid.flat().some((value) => value > 0)) {
          setTimeout(() => {
            createGrid();
            setMessage('The board is clear. A fresh grid has been generated.', 'good');
          }, 350);
        }
      } else {
        clearSelection();
        setMessage('That rectangle does not sum to 10. Try another selection.', 'bad');
      }
    }

    function onPointerDown(event) {
      if (isGameOver) return;
      const row = Number(event.currentTarget.dataset.row);
      const col = Number(event.currentTarget.dataset.col);
      startCell = { row, col };
      hoverCell = { row, col };
      dragActive = true;
      highlightSelection(startCell, hoverCell);
      event.preventDefault();
    }

    function onPointerEnter(event) {
      if (!dragActive || isGameOver) return;
      hoverCell = { row: Number(event.currentTarget.dataset.row), col: Number(event.currentTarget.dataset.col) };
      highlightSelection(startCell, hoverCell);
    }

    document.addEventListener('pointerup', (event) => {
      if (!dragActive || !startCell || isGameOver) return;
      const target = event.target.closest('.cell');
      const endCell = target ? { row: Number(target.dataset.row), col: Number(target.dataset.col) } : hoverCell;
      trySelection(startCell, endCell);
      dragActive = false;
      startCell = null;
      hoverCell = null;
      clearSelection();
    });

    document.addEventListener('pointercancel', () => {
      dragActive = false;
      startCell = null;
      hoverCell = null;
      clearSelection();
    });

    restartBtn.addEventListener('click', restartGame);

    createGrid();
    updateTimerDisplay();
    startTimer();
  </script>
</body>
</html>
"""


class GameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(HTML.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    server = HTTPServer(('0.0.0.0', 8000), GameHandler)
    print('Ten Sum Grid is ready at http://localhost:8000/')
    server.serve_forever()


if __name__ == '__main__':
    main()
