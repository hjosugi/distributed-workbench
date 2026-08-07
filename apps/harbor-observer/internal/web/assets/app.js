const pathInput = document.querySelector('#path');
const runButton = document.querySelector('#run');
const resultsBody = document.querySelector('#results');
const overall = document.querySelector('#overall');
const stats = document.querySelector('#stats');
const timestamp = document.querySelector('#timestamp');
const history = document.querySelector('#history');

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

function stateLabel(state) {
  return ({
    healthy: '一致',
    divergent: '不一致',
    'single-copy-risk': '1台のみ',
    unavailable: '全停止',
  })[state] || state;
}

function render(run) {
  const summary = run.summary;
  overall.className = `badge ${summary.state}`;
  overall.textContent = stateLabel(summary.state);
  timestamp.textContent = new Date(run.finished_at).toLocaleString();
  stats.innerHTML = `
    <article><strong>${summary.reachable}/${summary.total}</strong><span>reachable</span></article>
    <article><strong>${Math.round(summary.coverage * 100)}%</strong><span>coverage</span></article>
    <article><strong>${summary.variant_count}</strong><span>variants</span></article>
    <article><strong>${escapeHtml(run.path)}</strong><span>path</span></article>`;

  resultsBody.innerHTML = run.results.map((result) => {
    const status = result.reachable ? result.status : 'ERROR';
    const detail = result.error || result.preview || '';
    const hash = result.sha256 ? `${result.sha256.slice(0, 12)}…` : '-';
    return `<tr>
      <td><strong>${escapeHtml(result.server)}</strong><small>${escapeHtml(result.base_url)}</small></td>
      <td><span class="status ${result.reachable ? 'ok' : 'error'}">${escapeHtml(status)}</span></td>
      <td>${result.latency_ms} ms</td>
      <td>${result.bytes}${result.truncated ? '+' : ''}</td>
      <td title="${escapeHtml(result.sha256)}"><code>${escapeHtml(hash)}</code></td>
      <td class="detail">${escapeHtml(detail)}</td>
    </tr>`;
  }).join('');
}

async function runProbe() {
  runButton.disabled = true;
  runButton.textContent = 'Probing…';
  try {
    const response = await fetch('/api/probes', {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({path: pathInput.value.trim()}),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
    render(body);
    await loadHistory();
  } catch (error) {
    alert(error.message);
  } finally {
    runButton.disabled = false;
    runButton.textContent = 'Probe';
  }
}

async function loadHistory() {
  try {
    const response = await fetch('/api/probes?limit=12');
    const body = await response.json();
    const runs = body.runs || [];
    history.innerHTML = runs.length ? runs.map((run) => `
      <button class="history-item" data-id="${escapeHtml(run.id)}">
        <span class="dot ${escapeHtml(run.summary.state)}"></span>
        <span><strong>${escapeHtml(run.path)}</strong><small>${new Date(run.finished_at).toLocaleString()}</small></span>
        <span>${run.summary.reachable}/${run.summary.total}</span>
      </button>`).join('') : '<p class="empty">履歴はありません。</p>';
    document.querySelectorAll('.history-item').forEach((element) => {
      element.addEventListener('click', () => {
        const selected = runs.find((run) => run.id === element.dataset.id);
        if (selected) {
          pathInput.value = selected.path;
          render(selected);
        }
      });
    });
  } catch (error) {
    history.innerHTML = `<p class="empty">履歴の取得に失敗しました: ${escapeHtml(error.message)}</p>`;
  }
}

runButton.addEventListener('click', runProbe);
pathInput.addEventListener('keydown', (event) => { if (event.key === 'Enter') runProbe(); });
document.querySelector('#refresh').addEventListener('click', loadHistory);
document.querySelectorAll('[data-path]').forEach((button) => {
  button.addEventListener('click', () => { pathInput.value = button.dataset.path; });
});
loadHistory();
