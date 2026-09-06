import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCatalog } from './catalog.mjs';

test('catalog contract', async () => {
  const server = createCatalog();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const response = await fetch(`${base}/products`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), [{ sku: 'book', unit_price: 1200 }, { sku: 'pen', unit_price: 200 }]);
    assert.equal((await fetch(`${base}/missing`)).status, 404);
    assert.equal((await fetch(`${base}/products`, { method: 'POST' })).status, 405);
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});
