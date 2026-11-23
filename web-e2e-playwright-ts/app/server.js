// Tiny invoice service used as the system under test.
// No dependencies: Node's http module, in-memory storage, JSON API + static UI.
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 4173);
const PUBLIC = path.join(__dirname, 'public');
let invoices = [];
let nextId = 1;

const round2 = (n) => Math.round(n * 100) / 100;

function validate(body) {
  const errors = {};
  const number = String(body.number || '').trim();
  const client = String(body.client || '').trim();
  const net = Number(body.net);
  const vatRate = Number(body.vatRate);
  if (!/^INV-\d{3,6}$/.test(number)) errors.number = 'Use the format INV-0001';
  if (client.length < 2) errors.client = 'Client is required';
  if (!Number.isFinite(net) || net <= 0) errors.net = 'Net amount must be greater than 0';
  // Compare in cents with a tolerance: 19.99 * 100 is 1998.9999999999998 in floating point.
  else if (Math.abs(Math.round(net * 100) - net * 100) > 1e-6) errors.net = 'Max 2 decimals';
  if (![0, 5, 20].includes(vatRate)) errors.vatRate = 'VAT rate must be 0, 5 or 20';
  return { errors, value: { number, client, net, vatRate } };
}

function summary() {
  const net = round2(invoices.reduce((s, i) => s + i.net, 0));
  const vat = round2(invoices.reduce((s, i) => s + i.vat, 0));
  return { count: invoices.length, net, vat, gross: round2(net + vat) };
}

function send(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise((resolve) => {
    let raw = '';
    req.on('data', (c) => (raw += c));
    req.on('end', () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch { resolve(null); }
    });
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const p = url.pathname;

  if (p === '/api/invoices' && req.method === 'GET') return send(res, 200, invoices);
  if (p === '/api/summary' && req.method === 'GET') return send(res, 200, summary());

  if (p === '/api/invoices' && req.method === 'POST') {
    const body = await readBody(req);
    if (body === null) return send(res, 400, { errors: { body: 'Invalid JSON' } });
    const { errors, value } = validate(body);
    if (Object.keys(errors).length) return send(res, 400, { errors });
    if (invoices.some((i) => i.number === value.number)) {
      return send(res, 409, { errors: { number: `Invoice ${value.number} already exists` } });
    }
    const vat = round2((value.net * value.vatRate) / 100);
    const inv = { id: nextId++, ...value, vat, gross: round2(value.net + vat) };
    invoices.push(inv);
    return send(res, 201, inv);
  }

  const m = p.match(/^\/api\/invoices\/(\d+)$/);
  if (m && req.method === 'DELETE') {
    const before = invoices.length;
    invoices = invoices.filter((i) => i.id !== Number(m[1]));
    return before === invoices.length ? send(res, 404, { errors: { id: 'Not found' } }) : send(res, 204, {});
  }

  if (p === '/api/reset' && req.method === 'POST') {
    invoices = []; nextId = 1;
    return send(res, 200, { ok: true });
  }

  const file = path.join(PUBLIC, p === '/' ? 'index.html' : p);
  if (file.startsWith(PUBLIC) && fs.existsSync(file) && fs.statSync(file).isFile()) {
    const type = file.endsWith('.js') ? 'text/javascript' : 'text/html';
    res.writeHead(200, { 'Content-Type': type });
    return fs.createReadStream(file).pipe(res);
  }
  send(res, 404, { errors: { path: 'Not found' } });
});

server.listen(PORT, () => console.log(`Invoice app on http://localhost:${PORT}`));
