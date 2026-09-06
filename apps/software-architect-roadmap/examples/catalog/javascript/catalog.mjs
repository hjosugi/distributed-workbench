import http from 'node:http';

export const products = [{ sku: 'book', unit_price: 1200 }, { sku: 'pen', unit_price: 200 }];
export function createCatalog() {
  return http.createServer({ requestTimeout: 5000, headersTimeout: 5000 }, (request, response) => {
    const path = new URL(request.url, 'http://localhost').pathname;
    let status = 200;
    let body;
    if (request.method !== 'GET') { status = 405; body = { error: 'method not allowed' }; }
    else if (path === '/products') body = products;
    else if (path === '/health') body = { status: 'ok' };
    else { status = 404; body = { error: 'not found' }; }
    response.writeHead(status, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify(body));
  });
}
if (import.meta.main) {
  const server = createCatalog();
  server.listen(Number(process.env.PORT ?? 8081), process.env.BIND_HOST ?? '127.0.0.1', () => {
    console.log(`Catalog listening on ${server.address().port}`);
  });
}
