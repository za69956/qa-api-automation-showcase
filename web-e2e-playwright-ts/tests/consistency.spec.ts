import { test, expect, createInvoice } from './fixtures';

// The UI and the API must agree: what the user sees is what was saved.
test.describe('UI and API consistency', () => {
  test('invoice added in the UI is stored exactly once with the same values', async ({ invoices, request }) => {
    await invoices.add({ number: 'INV-3001', client: 'Pinewood Hotels', net: '840.40', vatRate: '5' });
    await expect(invoices.row('INV-3001')).toBeVisible();

    const list = await (await request.get('/api/invoices')).json();
    expect(list).toEqual([
      expect.objectContaining({ number: 'INV-3001', client: 'Pinewood Hotels', net: 840.4, vatRate: 5, vat: 42.02, gross: 882.42 }),
    ]);
  });

  test('invoice created via API appears in the UI after reload', async ({ invoices, request, page }) => {
    await createInvoice(request, { number: 'INV-3002', client: 'Harbor Logistics', net: 99.99, vatRate: 20 });
    await page.reload();
    await expect(invoices.row('INV-3002').locator('td').nth(3)).toHaveText('20.00');
    await expect(invoices.row('INV-3002').locator('td').nth(4)).toHaveText('119.99');
    await expect(invoices.summary).toContainText('Gross 119.99');
  });

  test('double-clicking Add does not create a duplicate', async ({ invoices, request }) => {
    await invoices.number.fill('INV-3003');
    await invoices.client.fill('Metro Utilities');
    await invoices.net.fill('10');
    await invoices.submit.dblclick();

    await expect(invoices.rows).toHaveCount(1);
    const list = await (await request.get('/api/invoices')).json();
    expect(list).toHaveLength(1);
  });
});
