import { test, expect, createInvoice } from './fixtures';

test.describe('Invoices API', () => {
  test('POST creates an invoice with calculated VAT and gross', async ({ request }) => {
    const inv = await createInvoice(request, { number: 'INV-1001', client: 'Acme Retail', net: 250.5, vatRate: 20 });
    expect(inv).toMatchObject({ id: 1, number: 'INV-1001', net: 250.5, vat: 50.1, gross: 300.6 });
  });

  test('400 with per-field errors for invalid payload', async ({ request }) => {
    const res = await request.post('/api/invoices', { data: { number: 'X', client: '', net: 0, vatRate: 7 } });
    expect(res.status()).toBe(400);
    const { errors } = await res.json();
    expect(Object.keys(errors).sort()).toEqual(['client', 'net', 'number', 'vatRate']);
  });

  test('400 for more than 2 decimals and for malformed JSON', async ({ request }) => {
    const r1 = await request.post('/api/invoices', { data: { number: 'INV-1002', client: 'Acme', net: 10.005, vatRate: 0 } });
    expect(r1.status()).toBe(400);
    expect((await r1.json()).errors.net).toBe('Max 2 decimals');

    const r2 = await request.post('/api/invoices', { data: '{bad json', headers: { 'Content-Type': 'application/json' } });
    expect(r2.status()).toBe(400);
  });

  test('409 on duplicate number, original record unchanged', async ({ request }) => {
    await createInvoice(request, { number: 'INV-1003', client: 'Acme', net: 10, vatRate: 0 });
    const dup = await request.post('/api/invoices', { data: { number: 'INV-1003', client: 'Other', net: 99, vatRate: 20 } });
    expect(dup.status()).toBe(409);

    const list = await (await request.get('/api/invoices')).json();
    expect(list).toHaveLength(1);
    expect(list[0]).toMatchObject({ client: 'Acme', net: 10 });
  });

  test('DELETE unknown id returns 404', async ({ request }) => {
    expect((await request.delete('/api/invoices/999')).status()).toBe(404);
  });

  test('summary equals the sum of stored invoices', async ({ request }) => {
    const nets = [19.99, 0.01, 1234.56, 7];
    for (const [i, net] of nets.entries()) {
      await createInvoice(request, { number: `INV-20${i}0`, client: 'Client', net, vatRate: 20 });
    }
    const list: { net: number; vat: number; gross: number }[] = await (await request.get('/api/invoices')).json();
    const sum = await (await request.get('/api/summary')).json();
    const cents = (xs: number[]) => xs.reduce((s, x) => s + Math.round(x * 100), 0) / 100;
    expect(sum.count).toBe(nets.length);
    expect(sum.net).toBe(cents(list.map((i) => i.net)));
    expect(sum.vat).toBe(cents(list.map((i) => i.vat)));
    expect(sum.gross).toBe(cents(list.map((i) => i.gross)));
  });
});
