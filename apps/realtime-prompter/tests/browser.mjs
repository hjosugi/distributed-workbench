import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { fileURLToPath } from "node:url";
import { setTimeout as delay } from "node:timers/promises";
import { chromium } from "playwright";

const cwd = fileURLToPath(new URL("..", import.meta.url));
const port = 8799;
const server = spawn(process.env.PROMPTER_PYTHON || "python", [
  "-m", "uvicorn", "prompter.app:app", "--host", "127.0.0.1", "--port", String(port),
  "--ws", "websockets-sansio", "--ws-max-size", "32768",
], { cwd, env: { ...process.env, PROMPTER_LLM: "demo", VOSK_MODEL_PATH: "", DEBOUNCE_MS: "30" }, stdio: ["ignore", "pipe", "pipe"] });
let logs = "", browser;
server.stdout.on("data", (data) => { logs += data; });
server.stderr.on("data", (data) => { logs += data; });
server.on("error", (error) => { logs += error.message; });

try {
  let healthy = false;
  for (let i = 0; i < 100; i++) {
    if (server.exitCode != null) throw new Error(`Server exited: ${logs}`);
    try { healthy = (await fetch(`http://127.0.0.1:${port}/health`)).ok; } catch {}
    if (healthy) break;
    await delay(100);
  }
  assert.ok(healthy, `Server not ready: ${logs}`);
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [], remoteRequests = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (new URL(request.url()).hostname !== "127.0.0.1") remoteRequests.push(request.url());
  });
  await page.goto(`http://127.0.0.1:${port}`);
  await page.waitForFunction(() => !document.getElementById("demo").disabled);
  assert.ok(await page.locator("#mic").isDisabled());
  await page.locator("#text-input").fill("今日は高温について");
  await page.locator("#partial-send").click();
  await page.waitForFunction(() => document.getElementById("answer").textContent.includes("発言の要点"));
  await page.locator("#text-input").fill("今日は交通について");
  await page.locator("#final-send").click();
  await page.waitForFunction(() => document.getElementById("generation-state").textContent === "完了");
  assert.match(await page.locator("#answer").innerText(), /交通/);
  assert.doesNotMatch(await page.locator("#answer").innerText(), /高温/);
  assert.equal(await page.locator("#partial").innerText(), "");
  await page.locator("#reset").click();
  await page.waitForFunction(() => document.getElementById("confirmed").textContent === "");
  await page.locator("#demo").click();
  await page.waitForFunction(() => Number(document.getElementById("revision").textContent) >= 4);
  await page.locator("#stop").click();
  await page.waitForFunction(() => !document.getElementById("demo").disabled);
  await page.locator("#reset").click();
  await page.locator("#text-input").fill("<img src=x onerror=alert(1)> 東京");
  await page.locator("#final-send").click();
  await page.waitForFunction(() => document.getElementById("generation-state").textContent === "完了");
  assert.equal(await page.locator("#answer img").count(), 0);
  assert.match(await page.locator("#answer").innerText(), /<img/);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  assert.deepEqual(errors, []);
  assert.deepEqual(remoteRequests, []);
  console.log("Browser passed: partial correction, final text, cancellation, escaped output, mobile layout, local-only requests.");
} catch (error) {
  console.error(logs);
  throw error;
} finally {
  await browser?.close();
  if (server.exitCode == null && server.pid) {
    const exited = once(server, "exit");
    server.kill("SIGTERM");
    await Promise.race([exited, delay(5000)]);
    if (server.exitCode == null) server.kill("SIGKILL");
  }
}
