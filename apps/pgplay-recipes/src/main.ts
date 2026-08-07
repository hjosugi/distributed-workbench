import { PGlite } from '@electric-sql/pglite'
import './style.css'
import { recipes, type Recipe } from './recipes'

type Row = Record<string, unknown>
type HistoryItem = { sql: string; at: string; durationMS: number; ok: boolean }
type SchemaRow = {
  table_schema: string
  table_name: string
  column_name: string
  data_type: string
  is_nullable: string
}

const $ = <T extends HTMLElement>(selector: string): T => {
  const element = document.querySelector<T>(selector)
  if (!element) throw new Error(`Missing element: ${selector}`)
  return element
}

const recipeSelect = $<HTMLSelectElement>('#recipe')
const recipeDescription = $<HTMLElement>('#recipe-description')
const sqlEditor = $<HTMLTextAreaElement>('#sql')
const resultElement = $<HTMLElement>('#result')
const resultMeta = $<HTMLElement>('#result-meta')
const executionTime = $<HTMLElement>('#execution-time')
const schemaElement = $<HTMLElement>('#schema')
const checksElement = $<HTMLElement>('#checks')
const historyElement = $<HTMLElement>('#history')
const dbStatus = $<HTMLElement>('#db-status')

let db: PGlite
let queryHistory: HistoryItem[] = loadHistory()
let currentRecipe: Recipe = recipes[0]!

async function init(): Promise<void> {
  setBusy(true)
  renderRecipeOptions()
  restoreSQLFromURLOrStorage()
  renderHistory()
  try {
    db = await PGlite.create('idb://distributed-workbench', { relaxedDurability: true })
    dbStatus.textContent = 'PostgreSQL ready · IndexedDB'
    dbStatus.className = 'status ready'
    await refreshSchema()
  } catch (error) {
    dbStatus.textContent = 'Database startup failed'
    dbStatus.className = 'status error'
    showError(error)
  } finally {
    setBusy(false)
  }
}

function renderRecipeOptions(): void {
  recipeSelect.innerHTML = recipes.map((recipe) => `<option value="${escapeHtml(recipe.id)}">${escapeHtml(recipe.name)}</option>`).join('')
  recipeSelect.value = currentRecipe.id
  recipeDescription.textContent = currentRecipe.description
}

function restoreSQLFromURLOrStorage(): void {
  const params = new URLSearchParams(location.hash.slice(1))
  const shared = params.get('sql')
  if (shared) {
    try {
      sqlEditor.value = decodeText(shared)
      return
    } catch {
      // Fall through to local storage when the hash is invalid.
    }
  }
  sqlEditor.value = localStorage.getItem('distributed-workbench.sql') ?? currentRecipe.starter
}

async function applyRecipe(): Promise<void> {
  if (!confirm(`public schemaを削除して「${currentRecipe.name}」を適用します。続けますか？`)) return
  setBusy(true)
  try {
    await db.exec('DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;')
    if (currentRecipe.schema.trim()) await db.exec(currentRecipe.schema)
    sqlEditor.value = currentRecipe.starter
    saveEditor()
    await refreshSchema()
    checksElement.innerHTML = '<div class="check ok">Recipeを適用しました。</div>'
    await runSQL()
  } catch (error) {
    showError(error)
  } finally {
    setBusy(false)
  }
}

async function runSQL(): Promise<void> {
  const sql = sqlEditor.value.trim()
  if (!sql) return
  const started = performance.now()
  setBusy(true)
  try {
    const results = await db.exec(sql)
    const durationMS = performance.now() - started
    const last = results.at(-1)
    renderResult((last?.rows ?? []) as Row[], last?.fields?.map((field) => field.name) ?? [])
    resultMeta.textContent = `${results.length} statement(s)`
    executionTime.textContent = `${durationMS.toFixed(1)} ms`
    addHistory({ sql, at: new Date().toISOString(), durationMS, ok: true })
    await refreshSchema()
  } catch (error) {
    const durationMS = performance.now() - started
    executionTime.textContent = `${durationMS.toFixed(1)} ms`
    addHistory({ sql, at: new Date().toISOString(), durationMS, ok: false })
    showError(error)
  } finally {
    setBusy(false)
  }
}

async function explainSQL(): Promise<void> {
  const sql = sqlEditor.value.trim().replace(/;\s*$/, '')
  if (!sql || sql.includes(';')) {
    showError(new Error('Explainは単一statementに対して実行してください。'))
    return
  }
  setBusy(true)
  try {
    const result = await db.query<Row>(`EXPLAIN (FORMAT JSON) ${sql}`)
    renderJSON(result.rows)
    resultMeta.textContent = 'EXPLAIN (FORMAT JSON)'
  } catch (error) {
    showError(error)
  } finally {
    setBusy(false)
  }
}

async function refreshSchema(): Promise<void> {
  const result = await db.query<SchemaRow>(`
    SELECT table_schema, table_name, column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY table_schema, table_name, ordinal_position
  `)
  const grouped = new Map<string, SchemaRow[]>()
  for (const row of result.rows) {
    const key = `${row.table_schema}.${row.table_name}`
    grouped.set(key, [...(grouped.get(key) ?? []), row])
  }
  if (!grouped.size) {
    schemaElement.innerHTML = '<p class="muted">public schemaにtableはありません。</p>'
    return
  }
  schemaElement.innerHTML = [...grouped.entries()].map(([table, columns]) => `
    <details open>
      <summary>${escapeHtml(table)}</summary>
      <ul>${columns.map((column) => `<li><code>${escapeHtml(column.column_name)}</code><span>${escapeHtml(column.data_type)}${column.is_nullable === 'NO' ? ' · required' : ''}</span></li>`).join('')}</ul>
    </details>`).join('')
}

async function runSchemaChecks(): Promise<void> {
  setBusy(true)
  try {
    const result = await db.query<{ table_name: string }>(`
      SELECT c.relname AS table_name
      FROM pg_class c
      JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE c.relkind = 'r'
        AND n.nspname = 'public'
        AND NOT EXISTS (
          SELECT 1
          FROM pg_index i
          WHERE i.indrelid = c.oid AND i.indisprimary
        )
      ORDER BY c.relname
    `)
    const withoutPK = result.rows.map((row) => row.table_name)
    checksElement.innerHTML = withoutPK.length
      ? `<div class="check warn"><strong>Primary keyなし</strong><span>${withoutPK.map(escapeHtml).join(', ')}</span></div>`
      : '<div class="check ok"><strong>Primary key</strong><span>すべてのpublic tableにprimary keyがあります。</span></div>'
  } catch (error) {
    showError(error)
  } finally {
    setBusy(false)
  }
}

function renderResult(rows: Row[], fieldNames: string[]): void {
  if (!rows.length) {
    resultElement.innerHTML = '<p class="muted">Command completed. No rows returned.</p>'
    return
  }
  const columns = fieldNames.length ? fieldNames : Object.keys(rows[0] ?? {})
  resultElement.innerHTML = `<div class="table-wrap"><table><thead><tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${columns.map((column) => `<td>${formatValue(row[column])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`
}

function renderJSON(value: unknown): void {
  resultElement.innerHTML = `<pre>${escapeHtml(JSON.stringify(value, null, 2))}</pre>`
}

function showError(error: unknown): void {
  const message = error instanceof Error ? error.message : String(error)
  resultElement.innerHTML = `<div class="error-box"><strong>Error</strong><pre>${escapeHtml(message)}</pre></div>`
  resultMeta.textContent = 'failed'
}

function formatValue(value: unknown): string {
  if (value === null) return '<span class="null">NULL</span>'
  if (typeof value === 'object') return `<code>${escapeHtml(JSON.stringify(value))}</code>`
  return escapeHtml(String(value))
}

function addHistory(item: HistoryItem): void {
  queryHistory = [item, ...queryHistory].slice(0, 20)
  localStorage.setItem('distributed-workbench.history', JSON.stringify(queryHistory))
  renderHistory()
}

function loadHistory(): HistoryItem[] {
  try {
    return JSON.parse(localStorage.getItem('distributed-workbench.history') ?? '[]') as HistoryItem[]
  } catch {
    return []
  }
}

function renderHistory(): void {
  historyElement.innerHTML = queryHistory.length ? queryHistory.map((item, index) => `
    <button class="history-row" data-index="${index}">
      <span class="history-state ${item.ok ? 'ok' : 'error'}"></span>
      <span><strong>${escapeHtml(oneLine(item.sql).slice(0, 90))}</strong><small>${new Date(item.at).toLocaleString()} · ${item.durationMS.toFixed(1)} ms</small></span>
    </button>`).join('') : '<p class="muted">Query historyはありません。</p>'
  document.querySelectorAll<HTMLButtonElement>('.history-row').forEach((button) => {
    button.addEventListener('click', () => {
      const item = queryHistory[Number(button.dataset.index)]
      if (item) sqlEditor.value = item.sql
    })
  })
}

async function shareSQL(): Promise<void> {
  const encoded = encodeText(sqlEditor.value)
  const url = new URL(location.href)
  url.hash = new URLSearchParams({ sql: encoded }).toString()
  try {
    await navigator.clipboard.writeText(url.toString())
    checksElement.innerHTML = `<div class="check ok"><strong>Copied</strong><span>SQL共有URLをclipboardへコピーしました。長さ: ${url.toString().length}</span></div>`
  } catch {
    window.prompt('このURLをコピーしてください。', url.toString())
  }
}

function exportWorkspace(): void {
  const documentValue = {
    version: 1,
    exportedAt: new Date().toISOString(),
    recipe: currentRecipe.id,
    sql: sqlEditor.value,
  }
  const blob = new Blob([JSON.stringify(documentValue, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `pgplay-workspace-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

async function importWorkspace(file: File): Promise<void> {
  const value = JSON.parse(await file.text()) as { recipe?: string; sql?: string }
  if (typeof value.sql !== 'string') throw new Error('workspace JSONにsqlがありません。')
  const recipe = recipes.find((candidate) => candidate.id === value.recipe)
  if (recipe) {
    currentRecipe = recipe
    recipeSelect.value = recipe.id
    recipeDescription.textContent = recipe.description
  }
  sqlEditor.value = value.sql
  saveEditor()
}

function setBusy(busy: boolean): void {
  document.querySelectorAll<HTMLButtonElement>('button').forEach((button) => { button.disabled = busy })
}

function saveEditor(): void {
  localStorage.setItem('distributed-workbench.sql', sqlEditor.value)
}

function encodeText(value: string): string {
  const bytes = new TextEncoder().encode(value)
  let binary = ''
  for (const byte of bytes) binary += String.fromCharCode(byte)
  return btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '')
}

function decodeText(value: string): string {
  const padded = value.replaceAll('-', '+').replaceAll('_', '/') + '='.repeat((4 - value.length % 4) % 4)
  const binary = atob(padded)
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

function oneLine(value: string): string {
  return value.replace(/\s+/g, ' ').trim()
}

function escapeHtml(value: unknown): string {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

recipeSelect.addEventListener('change', () => {
  currentRecipe = recipes.find((recipe) => recipe.id === recipeSelect.value) ?? recipes[0]!
  recipeDescription.textContent = currentRecipe.description
  sqlEditor.value = currentRecipe.starter
  saveEditor()
})
$('#apply-recipe').addEventListener('click', () => void applyRecipe())
$('#run').addEventListener('click', () => void runSQL())
$('#explain').addEventListener('click', () => void explainSQL())
$('#refresh-schema').addEventListener('click', () => void refreshSchema())
$('#schema-checks').addEventListener('click', () => void runSchemaChecks())
$('#share').addEventListener('click', () => void shareSQL())
$('#export').addEventListener('click', exportWorkspace)
$('#import').addEventListener('change', (event) => {
  const input = event.currentTarget as HTMLInputElement
  const file = input.files?.[0]
  if (file) void importWorkspace(file).catch(showError)
  input.value = ''
})
$('#clear-history').addEventListener('click', () => {
  queryHistory = []
  localStorage.removeItem('distributed-workbench.history')
  renderHistory()
})
sqlEditor.addEventListener('input', saveEditor)
sqlEditor.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    void runSQL()
  }
})

void init()
